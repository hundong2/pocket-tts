"""Pocket TTS의 기본 load → voice state → generate → WAV 저장 예제."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import scipy.io.wavfile

from pocket_tts import TTSModel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", required=True, help="합성할 text")
    parser.add_argument("--voice", default="alba", help="동의받은 voice 이름 또는 audio path")
    parser.add_argument("--language", default="english", help="언어 config 이름")
    parser.add_argument("--output", type=Path, default=Path("outputs/basic.wav"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    model = TTSModel.load_model(language=args.language)
    voice_state = model.get_state_for_audio_prompt(args.voice)
    ready = time.perf_counter()

    audio = model.generate_audio(voice_state, args.text)
    finished = time.perf_counter()

    # CPU가 기본이지만 device에 무관하게 안전하도록 명시적으로 CPU로 옮긴다.
    samples = audio.detach().cpu().numpy()
    scipy.io.wavfile.write(args.output, model.sample_rate, samples)

    audio_seconds = audio.shape[-1] / model.sample_rate
    generation_seconds = finished - ready
    print(f"model + voice 준비: {ready - started:.2f}s")
    print(f"생성: {generation_seconds:.2f}s, audio: {audio_seconds:.2f}s")
    print(f"RTF: {audio_seconds / generation_seconds:.2f}x")
    print(f"저장: {args.output}")


if __name__ == "__main__":
    main()
