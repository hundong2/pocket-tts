# 03. 고급 성능·배포·안전

## 성능 측정

load, voice encoding, first-chunk latency, total generation, audio duration을 분리한다.

```text
RTF = 생성한 audio 길이 / 생성 wall time
```

RTF가 1보다 크면 real-time보다 빠르다. 첫 실행은 download와 filesystem cache가 포함되므로 warm run과 구분한다. text, voice, language, temperature, LSD step, hardware, PyTorch version, thread 수를 함께 기록한다.

## 품질·속도 제어

- `lsd_decode_steps`: 더 많은 flow step은 느리지만 품질을 높일 수 있다.
- `temp`: 다양성과 안정성 trade-off. config 권장값부터 시작한다.
- `noise_clamp`: 극단적 noise sample을 제한하는 진단 knob다.
- `eos_threshold`, `frames_after_eos`: 잘림과 불필요한 tail 사이를 조절한다.
- 24-layer language model: 품질과 latency/memory를 실제 언어별로 비교한다.
- `quantize=True`: x86 FBGEMM에서 memory 약 48%, 속도 약 27% 개선이 보고됐지만 CPU 전용이다.

한 번에 하나의 변수만 바꾸고 동일 text·voice로 청취 및 자동 metric을 비교한다.

## CPU와 GPU

기본 CPU path는 `torch.set_num_threads(1)`을 사용한다. process를 여러 개 띄워 throughput을 높이면 각 model의 memory와 Hugging Face cache contention을 고려한다.

GPU는 공식 server path가 아니며 hardware별 차이가 크다. `.to("cuda")` 뒤 voice state와 입력 Tensor가 올바른 device에 있는지, output을 CPU로 옮기는지 확인한다. dynamic int8 quantization과 CUDA를 섞지 않는다.

## 동시성과 server

현재 model은 stateful하고 thread-safe하지 않으며 batch size는 1이다. FastAPI endpoint를 외부에 노출할 때 concurrent handler가 같은 model을 동시에 실행하지 않도록 queue/lock 또는 worker별 model을 사용한다. worker 수를 늘리면 model memory도 늘어난다.

운영 server에는 다음을 추가한다.

- authentication, authorization, rate limit, request size와 text length 제한
- timeout와 bounded queue
- voice upload의 MIME·size·duration 검사와 malware scanning
- temporary file의 격리, 암호화, 보존 기간과 삭제
- generated audio 표시와 audit log
- public network 앞 TLS와 reverse proxy

## streaming backpressure

generator가 만드는 chunk보다 consumer/network가 느리면 memory가 쌓이지 않도록 bounded queue와 cancellation을 전파한다. client disconnect 시 generation worker를 종료하고 file handle/thread를 회수한다. WAV header는 길이를 나중에 확정해야 하므로 seek 가능한 file 또는 streaming에 맞는 container/protocol을 선택한다.

## voice state cache

audio prompt encoding은 느려 `_cached_get_state_for_audio_prompt()`가 작은 LRU cache를 사용한다. cache key에 source와 변경 상태가 정확히 반영되는지 확인하고, 민감 voice data가 process memory나 disk safetensors에 남는 시간을 제한한다. multi-tenant service에서 사용자 간 cache가 섞이지 않게 tenant boundary를 둔다.

## 안전한 voice cloning

기술적으로 가능한 것과 허용되는 것은 다르다.

1. 명시적 동의와 voice sample license를 확인한다.
2. 목적, 기간, 배포 범위, 철회·삭제 방법을 기록한다.
3. 실존 인물 사칭, 인증 우회, 사기와 misinformation을 차단한다.
4. 생성 음성임을 표시하고 필요하면 watermark/provenance를 추가한다.
5. raw sample과 embedding 모두 biometric-like sensitive data로 취급한다.

## 테스트와 디버깅

```bash
uv run pytest tests/test_split_sentences.py -v
uv run pytest tests/test_python_api.py -v
uv run pytest -n 3 -v
```

문제 범위를 text normalization/splitting, voice encoding, FlowLM latent, Mimi decode, WAV/network output 순으로 좁힌다. regression test는 seed와 작은 fixture를 사용하고 model download가 필요한 integration test와 pure unit test를 분리한다.

## 확장 지점

- 새 language: YAML config, tokenizer/weight, default voice/text와 품질 평가
- 새 CLI option: Typer command, public API default, docs와 test 동기화
- 새 streaming sink: sample rate/dtype/channel 계약과 cancellation 구현
- 새 quantization backend: 지원 device guard, reference quality와 memory/RTF 비교
- 학습용 Rust audio extension: inference package와 build 요구 사항을 섞지 않음
