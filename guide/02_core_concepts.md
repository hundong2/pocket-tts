# 02. 핵심 구조와 Python API

## 1. FlowLM

FlowLM은 text condition을 받아 audio latent를 생성하는 Transformer 기반 flow language model이다. LSD(Lagrangian Self Distillation) decode step으로 flow prediction을 반복한다. step을 늘리면 계산량이 커지고 품질이 개선될 수 있으므로 실제 voice와 text로 비교한다.

model은 frame rate 12.5Hz, 즉 약 80ms 단위로 latent를 진행한다. EOS head가 발화 종료를 예측하고 `frames_after_eos`만큼 더 생성해 끝부분이 잘리는 것을 막는다.

## 2. Mimi codec

Mimi encoder는 voice prompt waveform을 작은 latent와 speaker conditioning으로 바꾼다. decoder는 FlowLM이 생성한 latent를 PCM waveform으로 복원한다. latent 생성과 decode worker를 queue/thread로 겹쳐 first audio chunk latency를 줄인다.

## 3. Stateful streaming

Transformer module은 `StatefulModule`을 통해 KV cache와 position state를 유지한다. generation 전에 voice state를 준비하고 text chunk마다 state를 복사하거나 이어서 사용한다.

- `copy_state=True`: 원본 voice state 보존, 반복 생성에 안전한 기본값
- `copy_state=False`: copy 비용을 줄이지만 입력 state가 변해 재사용 결과가 달라질 수 있음
- model instance는 thread-safe하지 않음

## 4. 공개 API 수명주기

```python
from pocket_tts import TTSModel, export_model_state

model = TTSModel.load_model(language="english")
voice = model.get_state_for_audio_prompt("alba")
audio = model.generate_audio(voice, "Hello.")
```

주요 API:

| API | 역할 |
|---|---|
| `TTSModel.load_model()` | config와 weight를 읽고 CPU model 준비 |
| `get_state_for_audio_prompt()` | WAV/URL/voice 이름/safetensors를 voice state로 변환 |
| `generate_audio()` | 모든 streaming chunk를 모아 하나의 Tensor 반환 |
| `generate_audio_stream()` | 준비되는 audio chunk를 즉시 yield |
| `sample_rate` | WAV 저장·재생에 사용할 sample rate |
| `device` | model parameter가 있는 torch device |
| `export_model_state()` | voice state를 safetensors로 저장 |

## 5. 긴 text

긴 입력은 tokenizer token 수와 문장 경계를 기준으로 분할한다. oversized sentence는 comma, semicolon, colon도 후보로 사용한다. chunk마다 text를 정규화하고 EOS 뒤 여분 frame을 정해 생성한다. 현재 chunk 간 teacher forcing 대신 같은 voice state를 사용하므로 매우 긴 문서에서는 prosody 연결을 직접 평가한다.

## 6. config와 weight

언어별 YAML은 Transformer dimension/layer, Mimi, tokenizer, weight URL, default temperature 등을 정의한다. `language`과 `config`는 동시에 넘길 수 없다. custom config는 local `.yaml`/`.yml`만 받는다.

weight·tokenizer·voice의 `hf://` URL은 `download_if_necessary()`가 local cache로 가져온다. remote content와 config version을 함께 고정해야 재현 가능한 결과를 얻는다.

## 7. output Tensor

CPU output은 `.numpy()`로 WAV에 쓸 수 있다. GPU output은 autograd와 device를 분리해야 한다.

```python
samples = audio.detach().cpu().numpy()
scipy.io.wavfile.write("output.wav", model.sample_rate, samples)
```

stream chunk는 일반적으로 1차원 sample Tensor다. callback이나 network로 넘길 때 dtype, range, sample rate, channel 수를 명시한다.
