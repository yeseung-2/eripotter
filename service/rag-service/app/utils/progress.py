# app/utils/progress.py
from __future__ import annotations

from typing import Iterable, Union
try:
    from alive_progress import alive_it  # 설치되어 있어야 함: pip install alive-progress
except Exception:
    alive_it = None

# 트레이너 콜백은 오류 없이 가볍게 로그만 출력하도록 구현
from transformers import TrainerCallback


def alive_range(x: Union[int, Iterable], title: str | None = None):
    """
    alive-progress의 alive_it 래퍼.
    - 정수 n이면 range(n)에 alive 이펙트를 입혀 반환
    - 이터러블이면 그대로 alive 이펙트를 입혀 반환
    - alive-progress 사용 불가한 환경에서는 원래 이터러블을 그대로 반환
    """
    if isinstance(x, int):
        iterable = range(x)
    else:
        iterable = x

    if alive_it is None:
        # alive-progress 미설치/불가 시 폴백
        return iterable
    # alive_it은 iterator를 반환하므로 그대로 사용
    kwargs = {}
    if title is not None:
        kwargs["title"] = title
    return alive_it(iterable, **kwargs)


class AliveTrainerCallback(TrainerCallback):
    """
    alive-progress의 상태바를 Trainer 내부 루프에 길게 붙이는 것은
    콜백 수명/컨텍스트 관리가 까다로워 간략 로그만 안전하게 출력합니다.
    """
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs is None:
            return
        # 멀티프로세스 시 마스터만 출력
        if getattr(state, "is_local_process_zero", True):
            parts = []
            if "loss" in logs:
                parts.append(f"loss={logs['loss']:.4f}")
            if "eval_loss" in logs:
                parts.append(f"eval_loss={logs['eval_loss']:.4f}")
            if "learning_rate" in logs:
                parts.append(f"lr={logs['learning_rate']:.2e}")
            if "epoch" in logs:
                parts.append(f"epoch={logs['epoch']:.2f}")
            if parts:
                step = int(getattr(state, "global_step", 0) or 0)
                print(f"[train] step={step} | " + " ".join(parts), flush=True)
