# 01. 설치와 첫 음성 생성

## 요구 사항

- Python 3.10 이상 3.15 미만
- PyTorch 2.5 이상
- model과 voice를 처음 받을 network 및 cache disk 공간
- 기본 실행은 CPU만으로 가능

`uv`를 사용하면 project와 독립된 환경을 간단히 만들 수 있다.

```bash
uvx pocket-tts generate
```

개발 저장소에서는 다음을 사용한다.

```bash
uv sync --dev
uv run pocket-tts generate
```

## 첫 생성

```bash
uvx pocket-tts generate \
  --language english \
  --voice alba \
  --text "Hello. This is my first Pocket TTS sample."
```

처음에는 model weight, tokenizer, voice file 다운로드 때문에 느리다. 다음 실행부터 Hugging Face cache를 재사용한다. 출력 WAV와 CLI의 generation speed/RTF를 확인한다.

## 언어와 voice

기본은 `english`다. `french_24l`, `german_24l`, `italian_24l`처럼 24-layer variant는 더 느리지만 품질이 높을 수 있다. config 목록은 `pocket_tts/config/*.yaml`을 기준으로 확인한다.

voice는 catalog 이름, local audio path, `hf://` URL, export한 `.safetensors`를 받을 수 있다. 음성 복제 전 다음을 확인한다.

1. 화자의 명시적 동의를 받았는가?
2. sample과 생성물의 사용 범위·보관 기간을 합의했는가?
3. 생성 음성임을 청취자에게 알리는가?
4. sample의 배경음·반향·잡음을 줄였는가?

## Python API 첫 실행

```bash
uv run python guide/examples/basic_generate.py \
  --voice alba \
  --text "Hello from the Python API." \
  --output outputs/basic.wav
```

model과 voice state를 한 번만 만들고 여러 문장을 생성한다. one-shot script를 반복 실행하면 load 비용을 매번 낸다.

## 환경 변수는 필요한가?

일반 generation에 필수 custom 환경 변수는 없다. Hugging Face download/cache가 필요한 환경에서는 표준 Hugging Face 설정이나 proxy가 필요할 수 있다. credential을 `.env`나 source에 hard-code하지 않는다. model 선택은 `--language` 또는 local `--config`로 한다.

## 문제 해결

- **Python version 오류**: `uv python install 3.13` 등 지원 version을 사용한다.
- **잘못된 audio**: PyTorch 2.4가 아닌 2.5 이상인지 확인한다.
- **download 실패**: network, Hugging Face 접근, cache write 권한과 disk를 확인한다.
- **voice 품질 저하**: consent가 있는 깨끗한 sample로 교체한다.
- **긴 첫 실행**: load와 생성 시간을 분리해 측정한다.
- **CUDA 미감지**: driver와 설치한 PyTorch CUDA build가 맞는지 확인한다.
