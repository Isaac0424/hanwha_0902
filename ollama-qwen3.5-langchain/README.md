# ollama-qwen3.5-langchain

Docker로 띄운 로컬 Ollama(Qwen3.5) 서버를 LangChain에서 사용하는 실습 예제.

## 왜 Qwen3.5:9b 인가

내 PC 사양:

| 항목 | 사양 |
|---|---|
| CPU | Intel Core i7-10875H (8C/16T, 2.30GHz) |
| 메모리 | 64GB |
| GPU0 | Intel UHD Graphics (공유 메모리) |
| GPU1 | NVIDIA RTX 2070 with Max-Q Design (**VRAM 8GB**) |

Qwen3.5는 2026년 2월 공개된 최신 세대로, 대형 397B(MoE, 활성 17B) 모델 외에
`0.8b / 2b / 4b / 9b` 소형 라인업을 Ollama에서 바로 받을 수 있다. 이 소형 모델들은
툴 콜링(tool calling)과 사고 과정(thinking)을 기본 지원한다.

RTX 2070 Max-Q는 VRAM이 8GB라 대형 모델은 무리지만, **`qwen3.5:9b`를 4bit 양자화로
받으면 VRAM에 거의 다 올라가서** CPU/공유 메모리로 오프로딩 없이 빠르게 추론할 수 있는
경계선이다. 품질보다 속도가 더 중요하면 `qwen3.5:4b`, 반대로 느려도 되면 GPU+CPU
오프로딩을 감수하고 더 큰 모델을 시도해도 된다.

임베딩은 VRAM 점유가 작은 `nomic-embed-text`를 같이 상주시켜 RAG 예제에 사용한다.

## 사전 준비: Docker + NVIDIA GPU 패스스루

Windows에서 GPU를 쓰는 Ollama 컨테이너를 띄우는 방법은 두 가지가 있다. 이 프로젝트는
**B안(WSL 네이티브 Docker Engine)**으로 실제 구동을 검증했다.

### WSL(Ubuntu) 안에 Docker Engine 직접 설치 (Docker Desktop 없이, 실제 검증됨)

```bash
# WSL(Ubuntu) 셸에서
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER

# GPU 패스스루용 NVIDIA Container Toolkit (드라이버는 Windows 쪽에 이미 있으면 됨)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo service docker start   # 또는 systemd 활성화 후 systemctl enable --now docker
```

공통 확인 사항:
- Windows 쪽 NVIDIA 드라이버는 이미 설치되어 있으면 충분함 (`nvidia-smi`로 GPU 확인, WSL은
  드라이버를 따로 설치하지 않고 Windows 드라이버를 그대로 통과시켜 씀).
- GPU 패스스루 확인: `docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi`
- Python(LangChain) 스크립트는 Windows에서 실행해도 된다. WSL2가 `localhost:11434`를
  Windows로 자동 포워딩하므로 `.env`의 `OLLAMA_BASE_URL=http://localhost:11434` 그대로 접속된다.

## 1. Ollama 서버 기동 (Docker)

```powershell
docker compose up -d
docker compose ps
```

`docker-compose.yml`은 `ollama/ollama` 공식 이미지를 사용하고, GPU 전체를 컨테이너에
예약(`deploy.resources.reservations.devices`)하며, 모델 가중치는 named volume
(`ollama_data`)에 영구 저장한다.

## 2. 모델 다운로드

```powershell
./scripts/pull-models.ps1
```

또는 수동으로:

```powershell
docker compose exec ollama ollama pull qwen3.5:9b
docker compose exec ollama ollama pull nomic-embed-text
```

GPU가 컨테이너 안에서 실제로 잡히는지 확인:

```powershell
docker compose exec ollama nvidia-smi
```

## 3. Python 환경 준비

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## 4. 예제 실행

| 파일 | 내용 |
|---|---|
| `examples/01_basic_chat.py` | 가장 단순한 `ChatOllama.invoke` 호출 |
| `examples/02_prompt_template.py` | `ChatPromptTemplate` + LCEL 체인 |
| `examples/03_streaming_chat.py` | 토큰 스트리밍 출력 |
| `examples/04_conversation_memory.py` | `RunnableWithMessageHistory`로 대화 맥락 유지 |
| `examples/05_rag_local_docs.py` | `data/sample.txt`를 임베딩해 검색 후 답변하는 RAG (파라미터 튜닝은 [docs/rag-optimization.md](docs/rag-optimization.md) 참고) |
| `examples/06_llm_caching.py` | `SQLiteCache`로 동일 질문 재호출 시 응답 속도 비교 |
| `examples/07_pickle_json_io.py` | 체인 결과를 pickle/JSON으로 저장 후 다시 읽어 검증 |
| `examples/08_timing_decorator.py` | 추론 시간 측정 3가지 방법(데코레이터/콜백/Ollama 응답 메타데이터) 비교 + 클라우드 대비 절약액/전기요금 누적 기록(`data/outputs/savings.json`) |

```powershell
python examples/01_basic_chat.py
```

## Docker 관리 명령어 치트시트

| 명령어 | 설명 |
|---|---|
| `docker compose up -d` | 컨테이너 기동 (백그라운드) |
| `docker compose ps` | 컨테이너 상태 확인 |
| `docker compose logs -f ollama` | 실시간 로그 확인 |
| `docker compose exec ollama ollama list` | 다운로드된 모델 목록 |
| `docker compose exec ollama ollama ps` | 현재 로드되어 응답 중인 모델 확인 |
| `docker compose exec ollama ollama pull <model>` | 새 모델 다운로드 |
| `docker compose exec ollama ollama rm <model>` | 모델 삭제 (디스크 용량 확보) |
| `docker compose exec ollama nvidia-smi` | 컨테이너 안에서 GPU 인식 확인 |
| `docker compose restart ollama` | 컨테이너 재시작 |
| `docker compose down` | 컨테이너 중지 및 제거 (모델은 volume에 남음) |
| `docker compose down -v` | 컨테이너 + volume까지 삭제 (모델 전부 재다운로드 필요, 초기화용) |
| `docker stats ollama-qwen` | 실시간 CPU/메모리/네트워크 사용량 확인 |

## 문제 해결

- `docker compose exec ollama nvidia-smi`에서 GPU가 안 보이면 →
  (WSL) `sudo service docker restart` 후 재시도, `nvidia-container-toolkit` 재설치 확인 /
  (Docker Desktop) 재시작 및 WSL Integration 설정 재확인.
- 모델 응답이 너무 느리면 → `docker compose exec ollama ollama ps`로 모델이 GPU에
  올라갔는지(`100% GPU`) 확인. CPU로 내려가 있으면 더 작은 모델(`qwen3.5:4b`)로 교체.
- 포트 충돌 시 → `docker-compose.yml`의 `11434:11434` 포트 매핑과 `.env`의
  `OLLAMA_BASE_URL`을 함께 수정.
- WSL을 새로 켤 때마다 docker가 꺼져 있으면 → `sudo service docker start` (systemd를 켰다면
  `sudo systemctl enable --now docker`로 자동 시작 가능).
- `docker`, `docker compose`, `sudo service docker ...` 명령은 반드시 **WSL(Ubuntu) 셸 안에서**
  실행해야 한다 (Windows Terminal에서 `wsl` 또는 `wsl -d Ubuntu`로 진입). Windows
  PowerShell/cmd 프롬프트에서 그대로 실행하면:
  - `docker ps`가 `failed to connect to the docker API at
    npipe:////./pipe/dockerDesktopLinuxEngine`로 실패한다 — Windows용 `docker` CLI가 기본적으로
    Docker Desktop의 named pipe를 찾는데, 이 프로젝트는 Docker Desktop을 쓰지 않기 때문이다.
  - `sudo service docker start`는 Windows 11 내장 `sudo`(기본 비활성화)로 잘못 실행되어
    "Sudo가 이 컴퓨터에서 사용하지 않도록 설정되어 있습니다" 오류가 난다 — WSL의 Linux `sudo`와는
    다른 명령이다.
