# Pocket TTS Python 실습

모든 예제는 저장소 root에서 실행한다. 첫 실제 생성은 model과 voice를 Hugging Face에서 다운로드할 수 있다.

## 1. 기본 WAV 생성

```bash
uv run python guide/examples/basic_generate.py \
  --language english \
  --voice alba \
  --text "Hello from Pocket TTS." \
  --output outputs/basic.wav
```

학습 목표는 model load, voice state 준비, full audio 생성, CPU NumPy 변환과 WAV 저장 수명주기다. 예상 결과는 지정한 path의 mono WAV와 load/generation/audio duration 출력이다.

## 2. streaming WAV 생성

```bash
uv run python guide/examples/stream_to_wav.py \
  --voice alba \
  --text "This is a longer streaming example. Each decoded chunk is written immediately." \
  --output outputs/stream.wav
```

`generate_audio_stream()`의 각 float sample chunk를 16-bit PCM으로 바꾸어 `wave` file에 즉시 쓴다. 전체 audio Tensor를 memory에 모으지 않지만 model 내부 state와 decoder queue는 유지된다.

## 3. 성능 비교

```bash
uv run python guide/examples/benchmark.py \
  --voice alba \
  --text "Measure this sentence several times." \
  --runs 3
```

model과 voice state 준비 시간은 한 번만 측정하고, 같은 state를 재사용해 generation wall time, first chunk latency, audio duration과 RTF를 분리한다. 실제 비교에서는 process를 새로 시작하는 cold run과 같은 process의 warm run을 따로 기록한다.

## 연습 과제

1. `--language italian_24l`과 작은 variant를 동일 text/voice 조건에서 비교한다.
2. `lsd_decode_steps`를 CLI option으로 노출하고 latency와 품질을 비교한다.
3. streaming 예제에서 client cancellation을 모사해 file이 정상 종료되는지 확인한다.
4. 동의받은 local voice WAV를 safetensors로 export하고 load 시간을 비교한다.
5. 생성물 metadata에 model/config/voice consent record ID를 남기는 sidecar JSON을 추가한다.

## 안전 주의

예제에 타인의 voice recording을 넣지 않는다. 본인 또는 명시적 동의를 받은 sample만 사용하고, 생성 음성임을 명확히 표시한다. API key나 private Hugging Face token을 source에 저장하지 않는다.
