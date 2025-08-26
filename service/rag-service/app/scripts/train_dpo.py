# app/scripts/train_dpo.py
from __future__ import annotations
import os, random, numpy as np, torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from trl import DPOTrainer
from peft import LoraConfig, get_peft_model
from app.utils.progress import AliveTrainerCallback

def set_seed(seed:int=42):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
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
    names = [n for n,_ in model.named_modules()]
    if any(".q_proj" in n for n in names):
        return ["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"]
    if any("query_key_value" in n for n in names):
        return ["query_key_value","dense_h_to_4h","dense_4h_to_h"]
    return ["q_proj","k_proj","v_proj","o_proj"]

def main(
    dpo_file, base_model=None, output_dir=None,
    lr=5e-6, epochs=1, bsz=1, grad_accum=8,
    beta=0.1, max_len=2048, max_target_len=256, max_prompt_len=1792,
    weight_decay=0.01, warmup_ratio=0.05, lr_scheduler="cosine",
    lora_r=16, lora_alpha=32, lora_dropout=0.05,
    qlora=False, grad_ckpt=True, grad_clip=1.0,
    use_bf16=None, use_fp16=None, seed=42, compile_model=False
):
    set_seed(seed); enable_torch_perf()

    BASE_MODEL = base_model or os.getenv("BASE_MODEL","EleutherAI/polyglot-ko-3.8b")
    OUTPUT_DIR = output_dir or os.getenv("DPO_OUTPUT","./lora_out_dpo")

    tok=AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
    if tok.pad_token is None and tok.eos_token is not None:
        tok.pad_token=tok.eos_token

    ds=load_dataset("json", data_files=dpo_file, split="train")

    load_kwargs={}
    if qlora:
        compute_dtype = torch.bfloat16 if (use_bf16 if use_bf16 is not None else bf16_available()) else torch.float16
        load_kwargs.update(dict(
            load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=compute_dtype
        ))
    model=AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype="auto", **load_kwargs)
    if grad_ckpt:
        model.gradient_checkpointing_enable()

    targets=detect_lora_targets(model)
    lora=LoraConfig(r=lora_r, lora_alpha=lora_alpha, lora_dropout=lora_dropout, target_modules=targets)
    model=get_peft_model(model,lora)

    if compile_model and hasattr(torch, "compile"):
        try:
            model = torch.compile(model)
        except Exception as e:
            print(f"[warn] torch.compile 실패: {e}")

    if use_bf16 is None and use_fp16 is None:
        use_bf16 = bf16_available()
        use_fp16 = not use_bf16 and torch.cuda.is_available()

    args=TrainingArguments(
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

    trainer=DPOTrainer(
        model=model, args=args, tokenizer=tok, train_dataset=ds,
        beta=beta, max_length=max_len, max_target_length=max_target_len, max_prompt_length=max_prompt_len
    )
    trainer.add_callback(AliveTrainerCallback())
    trainer.train()
    trainer.save_model(OUTPUT_DIR); tok.save_pretrained(OUTPUT_DIR)
    print(f"[train_dpo] saved -> {OUTPUT_DIR}")

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--dpo_file", default="./data/datasets/train_dpo.jsonl")
    p.add_argument("--base_model", default=None)
    p.add_argument("--output_dir", default=None)
    p.add_argument("--lr", type=float, default=5e-6)
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--bsz", type=int, default=1)
    p.add_argument("--grad_accum", type=int, default=8)
    p.add_argument("--beta", type=float, default=0.1)
    p.add_argument("--max_len", type=int, default=2048)
    p.add_argument("--max_target_len", type=int, default=256)
    p.add_argument("--max_prompt_len", type=int, default=1792)
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
    a=p.parse_args()
    if a.no_grad_ckpt: a.grad_ckpt=False
    main(a.dpo_file, a.base_model, a.output_dir, a.lr, a.epochs, a.bsz, a.grad_accum,
         a.beta, a.max_len, a.max_target_len, a.max_prompt_len,
         a.weight_decay, a.warmup_ratio, a.lr_scheduler,
         a.lora_r, a.lora_alpha, a.lora_dropout, a.qlora, a.grad_ckpt, a.grad_clip,
         a.use_bf16, a.use_fp16, a.seed, a.compile)
