# app/scripts/train_sft.py
from __future__ import annotations

import os
import random
import math
import inspect
from typing import Any, Dict

import numpy as np
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    DataCollatorForLanguageModeling,
    TrainingArguments,
)
from trl import SFTTrainer
from peft import LoraConfig, get_peft_model
from app.utils.progress import AliveTrainerCallback


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def enable_torch_perf():
    try:
        torch.set_float32_matmul_precision("high")
        if torch.cuda.is_available():
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
    except Exception:
        pass


def bf16_available():
    return torch.cuda.is_available() and torch.cuda.is_bf16_supported()


def detect_lora_targets(model) -> list[str]:
    names = [n for n, _ in model.named_modules()]
    if any(".q_proj" in n for n in names):
        return ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    if any("query_key_value" in n for n in names):
        return ["query_key_value", "dense_h_to_4h", "dense_4h_to_h"]
    return ["q_proj", "k_proj", "v_proj", "o_proj"]


def to_text(example: Dict[str, Any], tok):
    # qa_runs.jsonl에서 messages 기반 -> 단일 문자열로 합치기
    msgs = example.get("messages", [])
    sys = next((m.get("content", "") for m in msgs if m.get("role") == "system"), "너는 ESG 보고서 보조자다.")
    user = next((m.get("content", "") for m in msgs if m.get("role") == "user"), "")
    ans = next((m.get("content", "") for m in msgs if m.get("role") == "assistant"), "")
    text = f"<SYS>\n{sys}\n</SYS>\n<USER>\n{user}\n</USER>\n<ASSISTANT>\n{ans}\n</ASSISTANT>"
    # 반드시 문자열만 남기기
    return {"text": str(text)}


def main(
    train_file,
    val_file,
    base_model=None,
    output_dir=None,
    lr=2e-5,
    epochs=2,
    bsz=2,
    grad_accum=8,
    max_seq_len=2048,
    weight_decay=0.01,
    warmup_ratio=0.05,
    lr_scheduler="cosine",
    lora_r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    qlora=False,
    grad_ckpt=True,
    grad_clip=1.0,
    use_bf16=None,
    use_fp16=None,
    seed=42,
    compile_model=False,
):
    set_seed(seed)
    enable_torch_perf()

    BASE_MODEL = base_model or os.getenv("BASE_MODEL", "EleutherAI/polyglot-ko-3.8b")
    OUTPUT_DIR = output_dir or os.getenv("SFT_OUTPUT", "./lora_out")

    tok = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
    if tok.pad_token is None and tok.eos_token is not None:
        tok.pad_token = tok.eos_token
    try:
        # 너무 작은 model_max_length를 덮어쓰기
        if getattr(tok, "model_max_length", None) and tok.model_max_length < max_seq_len:
            tok.model_max_length = max_seq_len
    except Exception:
        pass

    # ===== 데이터 로드 & "text" 단일 문자열 컬럼만 남기기 =====
    ds_tr = load_dataset("json", data_files=train_file, split="train").map(lambda ex: to_text(ex, tok))
    ds_tr = ds_tr.remove_columns([c for c in ds_tr.column_names if c != "text"])
    ds_va = load_dataset("json", data_files=val_file, split="train").map(lambda ex: to_text(ex, tok))
    ds_va = ds_va.remove_columns([c for c in ds_va.column_names if c != "text"])

    # 혹시 모를 타입문제 방지: 전부 str 보장
    def _ensure_str(example):
        v = example.get("text", "")
        if isinstance(v, list):
            v = "\n".join([str(x) for x in v])
        return {"text": str(v)}

    ds_tr = ds_tr.map(_ensure_str)
    ds_va = ds_va.map(_ensure_str)

    # ===== 모델 로드 (QLoRA 선택적) =====
    load_kwargs = {}
    if qlora:
        compute_dtype = torch.bfloat16 if (use_bf16 if use_bf16 is not None else bf16_available()) else torch.float16
        load_kwargs.update(dict(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=compute_dtype))

    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype="auto", **load_kwargs)

    if grad_ckpt and hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()

    targets = detect_lora_targets(model)
    lora = LoraConfig(r=lora_r, lora_alpha=lora_alpha, lora_dropout=lora_dropout, target_modules=targets)
    model = get_peft_model(model, lora)

    if compile_model and hasattr(torch, "compile"):
        try:
            model = torch.compile(model)
        except Exception as e:
            print(f"[warn] torch.compile 실패: {e}")

    # 혼합정밀 자동결정
    if use_bf16 is None and use_fp16 is None:
        use_bf16 = bf16_available()
        use_fp16 = not use_bf16 and torch.cuda.is_available()

    # ===== TrainingArguments =====
    common_kwargs = dict(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=bsz,
        gradient_accumulation_steps=grad_accum,
        learning_rate=lr,
        num_train_epochs=epochs,
        logging_steps=50,
        save_strategy="epoch",
        lr_scheduler_type=lr_scheduler,
        warmup_ratio=warmup_ratio,
        weight_decay=weight_decay,
        bf16=bool(use_bf16),
        fp16=bool(use_fp16),
        gradient_checkpointing=grad_ckpt,
        max_grad_norm=grad_clip,
        report_to="none",
    )
    try:
        args = TrainingArguments(evaluation_strategy="epoch", **common_kwargs)
    except TypeError:
        args = TrainingArguments(eval_strategy="epoch", **common_kwargs)

    collator = DataCollatorForLanguageModeling(tok, mlm=False)

    # ===== TRL SFTTrainer 시그니처 호환 처리 =====
    sig = inspect.signature(SFTTrainer.__init__).parameters
    sft_kwargs = dict(
        model=model,
        train_dataset=ds_tr,
        eval_dataset=ds_va,
        args=args,
        data_collator=collator,
    )

    # 최대 길이 키 호환
    if "max_seq_length" in sig:
        sft_kwargs["max_seq_length"] = max_seq_len
    elif "max_seq_len" in sig:
        sft_kwargs["max_seq_len"] = max_seq_len

    # tokenizer / processing_class 호환
    if "tokenizer" in sig:
        sft_kwargs["tokenizer"] = tok
    elif "processing_class" in sig:
        sft_kwargs["processing_class"] = tok

    # 1) 최신/권장 경로: dataset_text_field 사용 (예시가 문자열임을 보장)
    if "dataset_text_field" in sig:
        sft_kwargs["dataset_text_field"] = "text"
    # 2) 구버전 경로: formatting_func 사용. 반드시 "문자열"을 반환하게 함!
    elif "formatting_func" in sig:
        def _fmt(ex: Dict[str, Any]) -> str:
            # SFTTrainer는 formatting_func를 "단일 예시" 기준으로 호출하는 버전이 있음.
            # 어떤 경우엔 ex["text"]가 list[str]일 수 있으니 문자열로 평탄화.
            v = ex.get("text", "")
            if isinstance(v, list):
                v = "\n".join([str(x) for x in v])
            return str(v)
        sft_kwargs["formatting_func"] = _fmt
    else:
        # 매우 이례적 시그니처: 이미 토크나이즈된 데이터만 허용하는 케이스.
        # 여기선 fallback 없이 진행(현 환경에선 위 두 경로 중 하나는 무조건 잡힘)
        pass

    # 절대 넣지 말 것들(버전마다 충돌): packing, dataset_num_proc 등은 생략
    trainer = SFTTrainer(**sft_kwargs)

    # 콜백/학습/저장/평가
    trainer.add_callback(AliveTrainerCallback())
    trainer.train()
    trainer.save_model(OUTPUT_DIR)
    tok.save_pretrained(OUTPUT_DIR)
    print(f"[train_sft] saved -> {OUTPUT_DIR}")
    metrics = trainer.evaluate()
    print("[SFT] eval_loss:", metrics.get("eval_loss"))
    if "eval_loss" in metrics and metrics["eval_loss"] is not None:
        try:
            print("[SFT] perplexity:", math.exp(metrics["eval_loss"]))
        except Exception:
            pass


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--train_file", default="./data/datasets/train_sft.jsonl")
    p.add_argument("--val_file",   default="./data/datasets/val_sft.jsonl")
    p.add_argument("--base_model", default=None)
    p.add_argument("--output_dir", default=None)
    p.add_argument("--lr", type=float, default=2e-5)
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--bsz", type=int, default=2)
    p.add_argument("--grad_accum", type=int, default=8)
    p.add_argument("--max_seq_len", type=int, default=2048)
    p.add_argument("--weight_decay", type=float, default=0.01)
    p.add_argument("--warmup_ratio", type=float, default=0.05)
    p.add_argument("--lr_scheduler", default="cosine")
    p.add_argument("--lora_r", type=int, default=16)
    p.add_argument("--lora_alpha", type=int, default=32)
    p.add_argument("--lora_dropout", type=float, default=0.05)
    p.add_argument("--qlora", action="store_true")
    p.add_argument("--grad_ckpt", action="store_true")
    p.add_argument("--no_grad_ckpt", action="store_true")
    p.add_argument("--grad_clip", type=float, default=1.0)
    p.add_argument("--bf16", dest="use_bf16", action="store_true")
    p.add_argument("--fp16", dest="use_fp16", action="store_true")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--compile", dest="compile_model", action="store_true")
    a = p.parse_args()
    if a.no_grad_ckpt:
        a.grad_ckpt = False
    main(
        a.train_file, a.val_file, a.base_model, a.output_dir, a.lr, a.epochs, a.bsz, a.grad_accum,
        a.max_seq_len, a.weight_decay, a.warmup_ratio, a.lr_scheduler,
        a.lora_r, a.lora_alpha, a.lora_dropout, a.qlora, a.grad_ckpt, a.grad_clip,
        a.use_bf16, a.use_fp16, a.seed, a.compile_model
    )
