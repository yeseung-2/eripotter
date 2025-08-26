# app/pipeline/oop_pipeline.py
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


from app.scripts.batch_rag import main as batch_rag_main
from app.scripts.prepare_sft import main as prepare_sft_main
from app.scripts.apply_review import main as apply_review_main
from app.scripts.train_sft import main as train_sft_main
from app.scripts.train_dpo import main as train_dpo_main
from app.scripts.eval_quick import eval_questions as eval_quick_fn

# ---------- 프로젝트 루트 경로 설정 (eripotter 프로젝트 구조에 맞게 수정) ----------
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # service/rag-service/app/pipeline -> eripotter 루트
DOCUMENT_ROOT = PROJECT_ROOT / "document"
SUSTAINABILITY_DIR = DOCUMENT_ROOT / "sustainability"

DEFAULT_ENV_PATH = Path(".env")

@dataclass
class Paths:
    csv_questions: Optional[Path] = SUSTAINABILITY_DIR / "질문.xlsx"  # 기본값으로 질문.xlsx 설정
    qa_runs: Path = Path("./data/logs/qa_runs.jsonl")
    out_dir: Path = Path("./data/datasets")
    train_file: Optional[Path] = None
    val_file: Optional[Path] = None
    reviewed_train: Optional[Path] = None
    reviewed_val: Optional[Path] = None
    review_queue: Optional[Path] = None
    dpo_file: Optional[Path] = None
    lora_out: Path = Path("./lora_out")
    lora_out_dpo: Path = Path("./lora_out_dpo")

@dataclass
class Options:
    do_batch_rag: bool = True  # 기본값을 True로 변경하여 RAG 실행
    rag_top_k: int = 5
    rag_collections: List[str] = field(default_factory=lambda: ["sustainability_reports"])  # 지속가능경영보고서 컬렉션으로 변경
    rag_out_log: Optional[Path] = None
    rag_sleep: float = 0.0

    val_ratio: float = 0.1
    auto_use_review_if_exists: bool = True

    sft_epochs: int = 2
    sft_bsz: int = 2
    sft_grad_accum: int = 8
    sft_fp16: bool = True
    sft_qlora: bool = False
    sft_grad_ckpt: bool = True
    sft_max_seq_len: int = 2048
    sft_base_model: Optional[str] = None

    do_dpo: bool = False
    dpo_epochs: int = 1
    dpo_bsz: int = 1
    dpo_grad_accum: int = 8
    dpo_fp16: bool = True
    dpo_grad_ckpt: bool = True

    eval_csv: Optional[Path] = None
    eval_top_k: int = 5

    set_lora_to_env: bool = True
    prefer_dpo_on_env: bool = True

class RagFineTunePipeline:
    def __init__(self, paths: Paths, opts: Options, env_path: Path = DEFAULT_ENV_PATH):
        self.paths = paths
        self.opts = opts
        self.env_path = env_path

    def _ensure_dirs(self):
        self.paths.out_dir.mkdir(parents=True, exist_ok=True)
        self.paths.lora_out.parent.mkdir(parents=True, exist_ok=True)
        self.paths.lora_out_dpo.parent.mkdir(parents=True, exist_ok=True)

    def _update_env(self, key: str, value: str):
        p = self.env_path
        lines = []
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        updated = False
        new_lines = []
        for ln in lines:
            if not ln or ln.strip().startswith("#"):
                new_lines.append(ln); continue
            if ln.startswith(f"{key}="):
                new_lines.append(f"{key}={value}")
                updated = True
            else:
                new_lines.append(ln)
        if not updated:
            new_lines.append(f"{key}={value}")
        with p.open("w", encoding="utf-8") as f:
            f.write("\n".join(new_lines) + "\n")
        print(f"[.env] set {key}={value}")

    def _detect_review_ready(self) -> bool:
        p = self.paths.review_queue
        if not p or not p.exists():
            return False
        try:
            import pandas as pd
            df = pd.read_csv(p, encoding="utf-8")
            if "keep_YN" in df.columns and "edited_answer" in df.columns:
                edited = df["keep_YN"].astype(str).str.upper().eq("Y") & df["edited_answer"].astype(str).str.strip().ne("")
                return bool(edited.sum() > 0)
        except Exception:
            pass
        return False

    def step_batch_rag(self):
        if not self.opts.do_batch_rag:
            print("[batch_rag] skip"); return
        if not self.paths.csv_questions:
            raise ValueError("opts.do_batch_rag=True 이면 paths.csv_questions가 필요합니다.")
        out_log = str(self.opts.rag_out_log) if self.opts.rag_out_log else ""
        batch_rag_main(
            csv_path=str(self.paths.csv_questions),
            top_k=self.opts.rag_top_k,
            collections=self.opts.rag_collections,
            out_log_path=out_log or None,
            sleep_sec=self.opts.rag_sleep
        )

    def step_prepare(self):
        prepare_sft_main(
            src_path=str(self.paths.qa_runs),
            out_dir=str(self.paths.out_dir),
            val_ratio=self.opts.val_ratio
        )
        train_sft = self.paths.out_dir / "train_sft.jsonl"
        val_sft   = self.paths.out_dir / "val_sft.jsonl"
        review_csv = self.paths.out_dir / "review_queue.csv"
        if not train_sft.exists():
            alt = self.paths.out_dir / "train_sft.from_upload.jsonl"
            if alt.exists(): train_sft = alt
        if not val_sft.exists():
            alt = self.paths.out_dir / "val_sft.from_upload.jsonl"
            if alt.exists(): val_sft = alt
        self.paths.train_file = train_sft
        self.paths.val_file = val_sft
        self.paths.review_queue = review_csv if review_csv.exists() else None

    def step_apply_review(self):
        if not self.opts.auto_use_review_if_exists:
            print("[apply_review] skip"); return
        if not self._detect_review_ready():
            print("[apply_review] skip (편집 없음)"); return
        reviewed_train = self.paths.out_dir / "train_sft_reviewed.jsonl"
        reviewed_val   = self.paths.out_dir / "val_sft_reviewed.jsonl"
        dpo_file       = self.paths.out_dir / "train_dpo.jsonl"
        apply_review_main(
            review_csv=str(self.paths.review_queue),
            base_train=str(self.paths.train_file),
            base_val=str(self.paths.val_file),
            out_train_sft=str(reviewed_train),
            out_val_sft=str(reviewed_val),
            out_dpo=str(dpo_file)
        )
        if reviewed_train.exists() and reviewed_val.exists():
            self.paths.reviewed_train = reviewed_train
            self.paths.reviewed_val   = reviewed_val
            self.paths.train_file = reviewed_train
            self.paths.val_file   = reviewed_val
        if dpo_file.exists():
            self.paths.dpo_file = dpo_file

    def step_train_sft(self):
        if not (self.paths.train_file and self.paths.val_file):
            raise FileNotFoundError("SFT 학습에 필요한 train/val 파일이 없습니다.")
        train_sft_main(
            train_file=str(self.paths.train_file),
            val_file=str(self.paths.val_file),
            base_model=self.opts.sft_base_model,
            output_dir=str(self.paths.lora_out),
            epochs=self.opts.sft_epochs,
            bsz=self.opts.sft_bsz,
            grad_accum=self.opts.sft_grad_accum,
            max_seq_len=self.opts.sft_max_seq_len,
            qlora=self.opts.sft_qlora,
            grad_ckpt=self.opts.sft_grad_ckpt,
            use_fp16=self.opts.sft_fp16
        )

    def step_train_dpo(self):
        if not self.opts.do_dpo:
            print("[train_dpo] skip"); return
        if not self.paths.dpo_file or not self.paths.dpo_file.exists():
            print("[train_dpo] skip (dpo_file 없음)"); return
        train_dpo_main(
            dpo_file=str(self.paths.dpo_file),
            output_dir=str(self.paths.lora_out_dpo),
            epochs=self.opts.dpo_epochs,
            bsz=self.opts.dpo_bsz,
            grad_accum=self.opts.dpo_grad_accum,
            use_fp16=self.opts.dpo_fp16,
            grad_ckpt=self.opts.dpo_grad_ckpt
        )

    def step_eval(self):
        if not self.opts.eval_csv:
            print("[eval] skip"); return
        res = eval_quick_fn(csv_path=str(self.opts.eval_csv), top_k=self.opts.eval_top_k, collections=None, max_n=100)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    def step_set_env(self):
        if not self.opts.set_lora_to_env:
            print("[env] skip"); return
        if self.opts.prefer_dpo_on_env and self.paths.lora_out_dpo.exists() and any(self.paths.lora_out_dpo.iterdir()):
            self._update_env("LORA_DIR", str(self.paths.lora_out_dpo))
        else:
            self._update_env("LORA_DIR", str(self.paths.lora_out))

    def run_all(self):
        self._ensure_dirs()
        steps = [
            ("batch_rag", self.step_batch_rag),
            ("prepare", self.step_prepare),
            ("apply_review", self.step_apply_review),
            ("train_sft", self.step_train_sft),
            ("train_dpo", self.step_train_dpo),
            ("set_env", self.step_set_env),
            ("eval", self.step_eval),
        ]
        for i, (name, fn) in enumerate(steps, start=1):
            print(f"\n>>> [{i}/{len(steps)}] {name}")
            fn()
        print("[pipeline] ALL DONE 🎉")

def main():
    import argparse
    p = argparse.ArgumentParser(description="End-to-End OOP RAG→SFT→DPO Pipeline")
    p.add_argument("--csv_questions", default=str(SUSTAINABILITY_DIR / "질문.xlsx"))
    p.add_argument("--qa_runs", default="./data/logs/qa_runs.jsonl")
    p.add_argument("--out_dir", default="./data/datasets")
    p.add_argument("--lora_out", default="./lora_out")
    p.add_argument("--lora_out_dpo", default="./lora_out_dpo")
    p.add_argument("--env_path", default=".env")
    p.add_argument("--do_batch_rag", action="store_true", default=True)
    p.add_argument("--rag_top_k", type=int, default=5)
    p.add_argument("--rag_collections", nargs="*", default=["sustainability_reports"])
    p.add_argument("--rag_out_log", default="")
    p.add_argument("--rag_sleep", type=float, default=0.0)
    p.add_argument("--val_ratio", type=float, default=0.1)
    p.add_argument("--no_auto_review", action="store_true")
    p.add_argument("--sft_epochs", type=int, default=2)
    p.add_argument("--sft_bsz", type=int, default=2)
    p.add_argument("--sft_grad_accum", type=int, default=8)
    p.add_argument("--sft_fp16", action="store_true")
    p.add_argument("--sft_qlora", action="store_true")
    p.add_argument("--sft_grad_ckpt", action="store_true")
    p.add_argument("--sft_max_seq_len", type=int, default=2048)
    p.add_argument("--sft_base_model", default=None)
    p.add_argument("--do_dpo", action="store_true")
    p.add_argument("--dpo_epochs", type=int, default=1)
    p.add_argument("--dpo_bsz", type=int, default=1)
    p.add_argument("--dpo_grad_accum", type=int, default=8)
    p.add_argument("--dpo_fp16", action="store_true")
    p.add_argument("--dpo_grad_ckpt", action="store_true")
    p.add_argument("--eval_csv", default="")
    p.add_argument("--eval_top_k", type=int, default=5)
    p.add_argument("--no_set_env", action="store_true")
    p.add_argument("--prefer_dpo_on_env", action="store_true")
    a = p.parse_args()

    paths = Paths(
        csv_questions=Path(a.csv_questions) if a.csv_questions and Path(a.csv_questions).exists() else SUSTAINABILITY_DIR / "질문.xlsx",
        qa_runs=Path(a.qa_runs),
        out_dir=Path(a.out_dir),
        lora_out=Path(a.lora_out),
        lora_out_dpo=Path(a.lora_out_dpo),
    )
    opts = Options(
        do_batch_rag=bool(a.do_batch_rag and paths.csv_questions and paths.csv_questions.exists()),
        rag_top_k=a.rag_top_k,
        rag_collections=a.rag_collections,
        rag_out_log=Path(a.rag_out_log) if a.rag_out_log else None,
        rag_sleep=a.rag_sleep,
        val_ratio=a.val_ratio,
        auto_use_review_if_exists=not a.no_auto_review,
        sft_epochs=a.sft_epochs,
        sft_bsz=a.sft_bsz,
        sft_grad_accum=a.sft_grad_accum,
        sft_fp16=a.sft_fp16,
        sft_qlora=a.sft_qlora,
        sft_grad_ckpt=a.sft_grad_ckpt,
        sft_max_seq_len=a.sft_max_seq_len,
        sft_base_model=a.sft_base_model if a.sft_base_model else None,
        do_dpo=a.do_dpo,
        dpo_epochs=a.dpo_epochs,
        dpo_bsz=a.dpo_bsz,
        dpo_grad_accum=a.dpo_grad_accum,
        dpo_fp16=a.dpo_fp16,
        dpo_grad_ckpt=a.dpo_grad_ckpt,
        eval_csv=Path(a.eval_csv) if a.eval_csv else None,
        eval_top_k=a.eval_top_k,
        set_lora_to_env=not a.no_set_env,
        prefer_dpo_on_env=a.prefer_dpo_on_env,
    )
    pipeline = RagFineTunePipeline(paths, opts, env_path=Path(a.env_path))
    pipeline.run_all()

if __name__ == "__main__":
    main()
