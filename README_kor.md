# Pocket TTS

[English](README.md) · [한국어 학습 가이드](guide/README.md)

<img width="1446" height="622" alt="Pocket TTS 로고" src="https://github.com/user-attachments/assets/637b5ed6-831f-4023-9b4c-741be21ab238" />

Pocket TTS는 CPU에서 효율적으로 실행하도록 설계한 경량 TTS(Text-to-Speech, 음성 합성) 애플리케이션이다. GPU와 별도 웹 API 서버 없이도 패키지를 설치하고 함수 하나를 호출해 음성을 생성할 수 있다.

Python 3.10~3.14와 PyTorch 2.5 이상을 지원하며 GPU용 PyTorch가 필수는 아니다.

[🔊 데모](https://kyutai.org/pocket-tts) · [GitHub 원본 저장소](https://github.com/kyutai-labs/pocket-tts) · [Hugging Face 모델 카드](https://huggingface.co/kyutai/pocket-tts) · [기술 보고서](https://kyutai.org/blog/2026-01-13-pocket-tts) · [논문](https://arxiv.org/abs/2509.06926) · [공식 문서](https://kyutai-labs.github.io/pocket-tts/)

> 이 문서는 원본 README의 한국어 번역·재구성본이다. 명령과 성능 수치는 원문의 조건을 보존했으며, 음성 복제는 당사자의 명시적이고 적법한 동의가 있을 때만 사용해야 한다.

## 주요 특징

- CPU 실행
- 1억 parameter의 작은 모델
- audio streaming과 약 200ms의 첫 chunk 지연
- MacBook Air M4 CPU에서 약 6배 real-time 속도
- CPU core 2개 사용
- Python API와 CLI
- voice cloning
- 영어, 프랑스어, 독일어, 포르투갈어, 이탈리아어, 스페인어
- 매우 긴 text를 문장 단위로 나누어 처리
- 커뮤니티 구현을 통한 browser client-side 실행

추가 언어는 향후 지원될 수 있다.

## 설치 없이 웹에서 사용하기

[Kyutai Pocket TTS 웹사이트](https://kyutai.org/pocket-tts)에서 text와 voice를 선택해 설치 없이 음성을 만들 수 있다.

## CLI로 사용하기

### `generate` 명령

격리 환경과 의존성을 자동 관리하는 `uv` 사용을 권장한다. 수동으로 `pip install pocket-tts`를 설치할 수도 있다.

```bash
uvx pocket-tts generate
# 또는 pip 설치 후
pocket-tts generate
```

기본 text와 voice로 `./tts_output.wav`를 만들고 속도 통계를 표시한다. `--voice`와 `--text`로 입력을 바꾸고, `generate`, `export-voice`, `serve`에서 `--language`로 사전 학습 모델을 선택한다. 기본 언어는 `english`다. 비영어권에는 품질이 더 높고 느린 24-layer variant도 있다. 예: `--language italian_24l`. `--config`는 로컬 YAML 경로만 받는다.

제공 voice에는 `alba`, `giovanni`, `lola`, `juergen`, `rafael`, `estelle`, `anna`, `azelma`, `bill_boerst`, `caro_davy`, `charles`, `cosette`, `eponine`, `eve`, `fantine`, `george`, `jane`, `jean`, `javert`, `marius`, `mary`, `michael`, `paul`, `peter_yearsley`, `stuart_bell`, `vera`가 있다. 각 voice의 license는 [Kyutai voice repository](https://huggingface.co/kyutai/tts-voices)에서 반드시 확인한다.

`--voice`에는 로컬 WAV를 전달해 voice cloning을 할 수도 있다. 입력 녹음의 잡음과 음질도 출력에 재현되므로 깨끗하고, 사용 권한이 분명하며, 본인이 동의한 sample을 사용한다. 세부 옵션은 [generate 문서](https://kyutai-labs.github.io/pocket-tts/CLI%20Commands/generate/)를 참고한다.

```bash
uvx pocket-tts generate \
  --voice alba \
  --text "Hello from Pocket TTS." \
  --language english
```

### `serve` 명령

로컬 HTTP server와 web UI를 실행한다.

```bash
uvx pocket-tts serve
# 또는 pip 설치 후
pocket-tts serve
```

`http://localhost:8000`에 접속한다. model을 요청 사이에 memory에 유지하므로 여러 voice와 prompt를 시험할 때 CLI one-shot보다 빠르다. 현재 구현은 thread-safe하지 않고 concurrent request를 지원하지 않으므로 public service로 바로 노출하지 않는다. 세부 내용은 [serve 문서](https://kyutai-labs.github.io/pocket-tts/CLI%20Commands/serve/)를 참고한다.

### `export-voice` 명령

voice cloning용 audio를 매번 encoding하면 느리다. `export-voice`는 WAV/MP3를 voice state safetensors로 변환해 이후 로드를 빠르게 한다. [export-voice 문서](https://kyutai-labs.github.io/pocket-tts/CLI%20Commands/export_voice/)에서 사용법을 확인한다.

## Python library로 사용하기

[Colab notebook](https://colab.research.google.com/github/kyutai-labs/pocket-tts/blob/main/docs/pocket-tts-example.ipynb)에서도 시험할 수 있다.

```bash
pip install pocket-tts
# 또는
uv add pocket-tts
```

```python
import scipy.io.wavfile
from pocket_tts import TTSModel

model = TTSModel.load_model()
voice_state = model.get_state_for_audio_prompt("alba")
audio = model.generate_audio(voice_state, "Hello world, this is a test.")

# audio는 PCM sample이 담긴 1차원 torch Tensor다.
scipy.io.wavfile.write("output.wav", model.sample_rate, audio.numpy())
```

`load_model()`과 `get_state_for_audio_prompt()`는 상대적으로 느리므로 model과 여러 voice state를 memory에 유지해 재사용하는 것이 좋다. 기본 `copy_state=True`는 generation마다 state를 복사해 같은 voice state를 안전하게 재사용한다.

voice state를 safetensors로 미리 export할 수도 있다.

```python
from pocket_tts import TTSModel, export_model_state

model = TTSModel.load_model()
voice_state = model.get_state_for_audio_prompt("some_voice.wav")
export_model_state(voice_state, "./some_voice.safetensors")

saved_voice = model.get_state_for_audio_prompt("./some_voice.safetensors")
audio = model.generate_audio(saved_voice, "Hello world!")
```

자세한 내용은 [Python API 문서](https://kyutai-labs.github.io/pocket-tts/API%20Reference/python-api/)를 참고한다.

### streaming generation

`generate_audio_stream()`은 decoding되는 sample chunk를 차례로 yield한다. 긴 text는 tokenizer 기준으로 sentence chunk에 나뉘고 각 chunk를 순서대로 생성한다.

```python
for chunk in model.generate_audio_stream(voice_state, "A long text to synthesize..."):
    print(chunk.shape[0])
```

model은 batch size 1을 전제로 하며 API는 thread-safe하지 않다. 동시에 생성해야 한다면 요청마다 별도 model instance 또는 직렬화 queue를 사용한다.

## GPU에서 실행하기

Pocket TTS는 CPU를 목표로 한다. Apple Silicon처럼 single-thread CPU가 강한 장비에서는 GPU 이점이 관측되지 않았지만, 4 vCPU cloud VM과 Tesla T4에서는 GPU가 CPU보다 약 2.6배 빨랐다. RTF는 CPU 약 2.3~2.5배, GPU 약 6.28배였다. 따라서 CPU가 약한 환경에서는 직접 측정해 볼 가치가 있다.

Python API의 `TTSModel.load_model()`에는 공식 `device` 인자가 없지만 일반 `nn.Module`이므로 옮길 수 있다.

```python
model = TTSModel.load_model()
model.to("cuda")
audio = model.generate_audio(voice_state, "Hello world.")

# GPU Tensor는 CPU로 이동한 뒤 NumPy로 변환한다.
scipy.io.wavfile.write(
    "output.wav",
    model.sample_rate,
    audio.detach().cpu().numpy(),
)
```

주의 사항:

- `generate` CLI는 `--device`를 제공하지만 `serve`와 Docker image는 CPU 전용이다.
- PyPI가 설치한 최신 PyTorch의 CUDA version과 driver가 맞지 않으면 `torch.cuda.is_available()`이 `False`가 될 수 있다. driver에 맞는 PyTorch index를 명시한다.
- `quantize=True`의 dynamic int8은 CPU 전용이며 CUDA에서 `NotImplementedError`가 발생한다.
- `pocket-tts[quantize]`의 `torchao`가 요구하는 PyTorch version과 사용자가 고정한 CUDA용 PyTorch version을 맞춰야 한다.
- GPU model이 반환한 audio에는 `.detach().cpu().numpy()`를 사용한다.

## 지원하지 않는 기능

현재 text 안에 silence를 삽입해 pause를 생성하는 기능은 지원하지 않는다. 관련 논의는 [issue #6](https://github.com/kyutai-labs/pocket-tts/issues/6)에 있다.

GPU 성능은 hardware에 따라 달라 공식 기본 경로가 아니다. 강한 single-thread CPU에서는 batch size 1과 작은 model 특성상 이점이 없을 수 있다.

## 개발과 로컬 설정

기여 방법은 [CONTRIBUTING.md](CONTRIBUTING.md)를 따른다.

```bash
uv sync --dev
uvx pre-commit install
uv run pytest -n 3 -v
```

Python 3.10 이상 3.15 미만, PyTorch 2.5 이상이 필요하다. Ruff line length는 100이며 LF line ending을 사용한다. 프로젝트는 순수 Python package이고 학습용 audio 처리에만 별도 Rust extension이 있다.

## Browser 구현

Pocket TTS는 작아서 WebAssembly/JavaScript browser 구현도 가능하다. 공식 지원은 아니지만 다음 community project가 있다.

- [wasm-pocket-tts](https://github.com/LaurentMazare/xn/tree/main/wasm-pocket-tts): XN 기반 Rust port와 [demo](https://laurentmazare.github.io/pocket-tts/)
- [pocket-tts-onnx-export](https://github.com/KevinAHM/pocket-tts-onnx-export): ONNX Runtime Web와 [demo](https://huggingface.co/spaces/KevinAHM/pocket-tts-web)
- [babybirdprd/pocket-tts](https://github.com/babybirdprd/pocket-tts): Candle, WebAssembly, PyO3
- [jax-js TTS](https://github.com/ekzhang/jax-js/tree/main/website/src/routes/tts): browser ML library와 [demo](https://jax-js.com/tts)

## 대체 구현

- [pocket-tts-mlx](https://github.com/jishnuvenugopal/pocket-tts-mlx): Apple Silicon MLX
- [pocket-tts-xn](https://github.com/LaurentMazare/xn/tree/main/pocket-tts): XN Rust port
- [pocket-tts-candle](https://github.com/babybirdprd/pocket-tts): Candle Rust port
- [PocketTTS.cpp](https://github.com/VolgaGerm/PocketTTS.cpp): ONNX Runtime 기반 C++ runtime
- [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx): desktop·embedded·WebAssembly와 다양한 언어 binding
- [pocket-tts-csharp](https://github.com/TheAjaykrishnanR/pocket-tts-csharp): TorchSharp 기반 C# port

## Pocket TTS를 사용하는 프로젝트

원문에는 screen reader인 [pocket-reader](https://github.com/lukasmwerner/pocket-reader), Home Assistant용 [pocket-tts-wyoming](https://github.com/ikidd/pocket-tts-wyoming), OpenAI-compatible server, Unity/ComfyUI integration, Discord bot, audiobook·접근성 도구, macOS app 등 다양한 community project가 정리되어 있다. 배포 목적과 protocol, license, 보안 요구에 맞는 구현을 선택한다.

## 금지된 사용

model 사용은 모든 관련 법률과 규정을 준수해야 한다. 불법·유해·기만·사기·무단 활동을 생성하거나 촉진해서는 안 된다. 특히 다음을 금지한다.

- 명시적이고 적법한 동의 없는 음성 사칭 또는 복제
- 가짜 뉴스, 사기 전화, 실제 녹음으로 위장하는 misinformation·disinformation·deception
- 불법·유해·명예훼손·학대·괴롭힘·차별·혐오·privacy 침해 content

생성물임을 명확히 표시하고, voice sample의 동의·license·보관 기간·삭제 절차를 기록한다.

## 저자

Manu Orsini*, Simon Rouard*, Gabriel De Marmiesse*, Václav Volhejn, Neil Zeghidour, Alexandre Défossez

\* 공동 기여

## 더 학습하기

architecture, streaming, voice state, 성능 측정과 안전한 배포는 [한국어 학습 가이드](guide/README.md)를 따른다.
