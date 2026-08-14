"""같은 model과 voice state를 재사용해 Pocket TTS streaming latency를 측정한다."""

from __future__ import annotations

import argparse
import statistics
import time

from pocket_tts import TTSModel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", required=True)
    parser.add_argument("--voice", default="alba")
    parser.add_argument("--language", default="english")
    parser.add_argument("--runs", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.runs < 1:
        raise SystemExit("--runs는 1 이상이어야 합니다.")

    load_started = time.perf_counter()
    model = TTSModel.load_model(language=args.language)
    voice_state = model.get_state_for_audio_prompt(args.voice)
    print(f"model + voice 준비: {time.perf_counter() - load_started:.2f}s")

    rtfs: list[float] = []
    first_chunk_times: list[float] = []
    for run in range(1, args.runs + 1):
        started = time.perf_counter()
        first_chunk_at: float | None = None
        total_samples = 0

        for chunk in model.generate_audio_stream(voice_state, args.text):
            if first_chunk_at is None:
                first_chunk_at = time.perf_counter()
            total_samples += chunk.numel()

        finished = time.perf_counter()
        generation_seconds = finished - started
        audio_seconds = total_samples / model.sample_rate
        rtf = audio_seconds / generation_seconds
        first_latency = (first_chunk_at or finished) - started
        rtfs.append(rtf)
        first_chunk_times.append(first_latency)
        print(
            f"run {run}: first={first_latency:.3f}s, generation={generation_seconds:.3f}s, "
            f"audio={audio_seconds:.3f}s, RTF={rtf:.2f}x"
        )

    print(f"평균 first chunk: {statistics.mean(first_chunk_times):.3f}s")
    print(f"평균 RTF: {statistics.mean(rtfs):.2f}x")


if __name__ == "__main__":
    main()
