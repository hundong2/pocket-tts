# Pocket TTS 한국어 학습 가이드

CPU 기반 음성 합성을 처음 실행하는 단계부터 streaming pipeline, Flow Matching, Mimi codec, 성능·동시성·안전한 배포까지 학습한다.

## 학습 순서

1. [설치와 첫 음성 생성](01_getting_started.md)
2. [핵심 구조와 Python API](02_core_concepts.md)
3. [고급 성능·배포·안전](03_advanced.md)
4. [실행 예제](examples/README.md)

## 한눈에 보는 pipeline

```text
text
  → SentencePiece + LUT conditioner
  → FlowLM이 audio latent를 frame 단위로 생성
  → Mimi neural codec decoder
  → PCM chunk stream
  → WAV / playback / HTTP response

voice WAV
  → Mimi encoder + speaker conditioning
  → 재사용 가능한 voice state 또는 safetensors
```

## 프로젝트 목적

Pocket TTS는 약 1억 parameter, batch size 1, CPU core 2개를 중심으로 low-latency voice cloning TTS를 제공한다. first chunk를 빠르게 내보내고 긴 text를 sentence chunk로 분할해 memory를 제한한다. model weight, tokenizer와 기본 voice는 첫 사용 때 Hugging Face에서 내려받아 cache한다.

## 저장소 지도

| 경로 | 역할 |
|---|---|
| `pocket_tts/main.py` | Typer CLI `generate`, `serve`, `export-voice` |
| `models/tts_model.py` | model load, voice state, streaming generation orchestration |
| `models/flow_lm.py` | Transformer 기반 latent flow model과 EOS |
| `models/mimi.py` | Mimi neural audio codec |
| `conditioners/text.py` | SentencePiece tokenizer와 embedding conditioner |
| `modules/stateful_module.py` | streaming state와 cache 수명주기 |
| `modules/transformer.py` | streaming attention, KV cache, RoPE |
| `data/audio.py` | audio read/write와 streaming utility |
| `quantization.py` | CPU dynamic int8 적용 |
| `config/*.yaml` | 언어별 architecture, weight, generation 기본값 |
| `static/` | local server web UI |
| `tests/` | Python API, CLI, audio, 긴 text, 회귀 테스트 |

## 빠른 선택

| 목표 | 권장 경로 |
|---|---|
| 설치 없이 체험 | Kyutai web demo |
| 한 파일 생성 | `uvx pocket-tts generate` |
| 반복 실험 | `pocket-tts serve` 또는 model/voice state 재사용 |
| application 통합 | `TTSModel.generate_audio_stream()` |
| voice 시작 지연 단축 | `export-voice` safetensors |
| x86 CPU memory·속도 개선 | `quantize=True`, 실제 품질·속도 측정 |
| 약한 CPU + 지원 GPU | model을 CUDA로 옮겨 직접 benchmark |

## 원문과 번역

- [원본 README](../README.md)
- [한국어 README](../README_kor.md)

## 기여 전 확인

- Python 3.10~3.14와 PyTorch 2.5+ 계약 유지
- public export는 `TTSModel`, `export_model_state`
- streaming 변경 시 state와 KV cache 초기화·복사 검증
- CPU path, batch 1, thread-safety 제약 문서화
- `uv run pytest -n 3 -v`, Ruff/pre-commit, `git diff --check`
- voice consent와 금지 사용 정책 훼손 금지
