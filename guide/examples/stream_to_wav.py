"""생성되는 float audio chunk를 16-bit PCM WAV에 즉시 기록하는 예제."""

from __future__ import annotations

import argparse
import wave
from pathlib import Path

import torch

from pocket_tts import TTSModel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", required=True)
    parser.add_argument("--voice", default="alba")
    parser.add_argument("--language", default="english")
    parser.add_argument("--output", type=Path, default=Path("outputs/stream.wav"))
    return parser.parse_args()


def float_to_pcm16(chunk: torch.Tensor) -> bytes:
    """[-1, 1] float sample을 little-endian signed PCM16 byte로 바꾼다."""
    pcm = chunk.detach().cpu().clamp(-1.0, 1.0).mul(32767).to(torch.int16)
    return pcm.numpy().astype("<i2", copy=False).tobytes()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    model = TTSModel.load_model(language=args.language)
    voice_state = model.get_state_for_audio_prompt(args.voice)

    total_samples = 0
    with wave.open(str(args.output), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(model.sample_rate)

        for index, chunk in enumerate(model.generate_audio_stream(voice_state, args.text), start=1):
            output.writeframesraw(float_to_pcm16(chunk))
            total_samples += chunk.numel()
            print(f"chunk {index}: {chunk.numel()} samples")

    print(f"저장: {args.output} ({total_samples / model.sample_rate:.2f}s)")


if __name__ == "__main__":
    main()
