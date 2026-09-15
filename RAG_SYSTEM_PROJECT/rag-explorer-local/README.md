# RAG Explorer — 로컬 실행판

내 컴퓨터에서 실행하는 단일 사용자 RAG 학습 실험실입니다. 원문을 청크로 나누고, 질문에 맞는 근거를 검색한 뒤, A/B 설정에 따른 답변과 비용을 비교합니다.

**실행 순서: Node.js 확인 → 의존성 설치 → `.env` 설정 → 서버 실행 → 모델 연결 확인 → A/B 실험**

Sites 계정, Cloudflare, 별도 DB 서버는 필요하지 않습니다. API 키는 서버의 환경변수에서 읽으며 웹페이지에 입력하지 않습니다.

## 1. 실행 환경과 의존성

### 직접 준비할 것

| 항목 | 요구사항 / 용도 |
|---|---|
| Node.js | **22.13.0 이상** (`package.json`의 `engines` 기준). 내장 `node:sqlite` 사용 |
| npm | Node.js와 함께 설치되는 패키지 관리자 |
| 터미널 | Windows PowerShell 또는 WSL |
| 브라우저 | 로컬 웹페이지 접속 |
| Google API 키 | Gemini 연결 확인과 실제 답변 생성에 필요 |
| 인터넷 | 최초 패키지 설치, Google 연결 확인 및 답변 생성에 필요 |

키 없이도 청킹·검색·설정 비교 등 로컬 기능을 살펴볼 수 있습니다. 실제 답변 생성에는 키가 필요합니다. Windows와 WSL의 `node_modules`는 공유하지 말고 사용할 환경에서 설치하세요.

### npm으로 설치되는 주요 패키지

아래는 `package.json`에 고정된 버전입니다. 각각 설치할 필요 없이 다음 절의 설치 명령 한 번으로 함께 설치됩니다.

| 구분 | 주요 의존성 | 역할 |
|---|---|---|
| 웹 프레임워크 | Next.js `16.3.4` | 페이지, 서버 API, 개발·빌드 실행 |
| 화면 | React / React DOM `19.2.6` | 사용자 인터페이스 |
| 스타일 | Tailwind CSS / PostCSS 플러그인 `4.2.1` | 스타일 처리 |
| UI 구성 | Base UI, Radix UI, shadcn, Lucide, Recharts 등 | 컴포넌트, 아이콘, 차트 |
| 폼·검증 | React Hook Form `7.85.0`, Zod `3.25.76` | 입력과 데이터 검증 |
| 개발 도구 | TypeScript `5.9.3`, ESLint `9.39.4` | 타입 검사와 코드 분석 도구 |

전체 목록은 [package.json](package.json), 하위 의존성을 포함한 설치 버전은 [package-lock.json](package-lock.json)을 참고하세요.

- **DB:** Node.js 내장 SQLite를 사용하므로 SQLite 서버나 별도 DB 패키지 설치가 필요하지 않습니다.
- **모델:** 서버에서 Google REST API를 직접 호출합니다. Python이나 별도 Google SDK 설치는 필요하지 않습니다.
- **검색:** 문자 bigram TF-IDF와 코사인 유사도, 규칙 기반 재정렬을 사용합니다. 별도 임베딩 서버나 벡터 DB는 필요하지 않습니다.

## 2. 처음 실행하기

### ① 프로젝트 이동 및 설치

저장소 루트에서 실행합니다. 이미 `rag-explorer-local` 폴더라면 `cd`는 생략하세요.

```sh
cd RAG_SYSTEM_PROJECT/rag-explorer-local
node --version  # 22.13.0 이상
npm ci
```

### ② API 키 발급 및 `.env` 생성

1. [Google AI Studio](https://aistudio.google.com/apikey)에 로그인합니다.
2. **Create API key**를 눌러 안내에 따라 프로젝트를 선택하거나 생성하고, 발급된 키를 복사합니다. ([공식 안내](https://ai.google.dev/gemini-api/docs/api-key))
3. 프로젝트 폴더에서 `.env` 파일을 만들거나 엽니다.

**Windows PowerShell**

```powershell
if (!(Test-Path .env)) { New-Item .env -ItemType File }
notepad .env
```

**WSL**

```sh
touch .env
nano .env
```

`.env`에 아래 값을 입력하고 저장하세요. 이미 항목이 있다면 값만 수정합니다.

```dotenv
GOOGLE_API_KEY=발급받은_API_키
```

`.env`는 `package.json`과 같은 위치에 저장하세요. 파일명이 `.env.txt`가 되지 않도록 하고, 키는 Git에 올리지 마세요.

### ③ 서버 실행

```sh
npm run dev
```

**http://127.0.0.1:3000** 접속 → **모델 연결** → **Google 연결 확인 · 추론 없음** 클릭.

- 다음 실행부터는 `npm run dev`만 실행합니다.
- 종료는 **Ctrl+C**, `.env` 수정 후에는 서버를 다시 실행합니다.
- PowerShell 실행 정책 오류가 나면 `npm` 대신 `npm.cmd`를 사용하세요.

## 3. 화면 사용 순서

| 순서 | 화면 | 할 일 |
|---|---|---|
| 1 | [모델 연결](http://127.0.0.1:3000/connection) | 키 인식 상태를 확인하고 **Google 연결 확인 · 추론 없음** 클릭 |
| 2 | [파이프라인](http://127.0.0.1:3000) | 질문과 원문 입력. 노드에 마우스를 올리거나 클릭해 청크·검색 결과·프롬프트 확인 |
| 3 | [A/B 비교](http://127.0.0.1:3000/compare) | **현재 B를 A로 고정**한 뒤 B의 청크 크기, overlap, top-K, 컨텍스트 예산 등 변경 |
| 4 | A/B 비교 | 예상 비용 확인 후 **A/B 답변 생성 · 최대 2회 호출** 클릭 |
| 5 | [실험 기록](http://127.0.0.1:3000/history) | 설정, 토큰 사용량, 비용 추정치 확인. 기록을 A 또는 B로 불러와 비교 |
| 참고 | [가이드](http://127.0.0.1:3000/guide) | 개념과 사용 안내 확인 |

**처음에는 예제 원문과 질문으로 흐름을 확인한 뒤 설정을 하나씩 바꾸면 비교하기 쉽습니다.**

- 청킹·검색·예상 비용 계산은 로컬에서 처리합니다. 설정 변경만으로 Google API를 호출하지 않습니다.
- 연결 확인은 모델 정보 조회이며 답변 생성은 수행하지 않습니다.
- 생성 버튼은 A와 B를 순서대로 처리하므로 **한 번 클릭해도 최대 2회** 모델을 호출합니다. 질문·시스템 지시·검색된 근거가 Google로 전송됩니다.
- 완전히 같은 입력과 생성 설정의 성공 결과는 재사용합니다.
- **서버 API 키 비우기**는 현재 서버 프로세스의 키와 검증 상태만 지웁니다. `.env` 파일은 유지되므로 서버를 재시작하면 다시 읽습니다.

## 4. 빌드한 앱으로 실행하기

개발 모드 대신 빌드 결과로 로컬 실행하려면, 의존성 설치와 `.env` 설정을 먼저 마친 뒤 다음 순서로 실행합니다. 개발 서버가 켜져 있으면 먼저 Ctrl+C로 종료하세요.

```sh
npm run build
npm start
```

접속 주소는 동일하게 **http://127.0.0.1:3000** 입니다. `build`가 성공한 뒤 `start`를 실행해야 합니다. 소스를 수정했다면 다시 빌드하세요.

### 명령어 요약

| 명령 | 사용 시점 |
|---|---|
| `npm ci` | 최초 설치 또는 잠금 파일 기준 의존성 재설치 |
| `npm run dev` | 개발 모드 실행 |
| `npm run build` | 실행할 프로덕션 빌드 생성 |
| `npm start` | 만들어진 빌드로 서버 실행 |
| `npm run typecheck` | TypeScript 타입 검사 |
| `npm test` | 로컬 SQLite 테스트 실행 |

`dev`와 `build`는 프로젝트 스크립트에 따라 Webpack을 사용합니다. `npm test`는 전체 테스트를 실행하는 명령이 아니며, `lint` 스크립트는 등록되어 있지 않습니다.

## 5. 데이터 저장과 비용

### 저장 위치

- `data/rag-explorer.sqlite`: 설정, 예상 비용, 생성 결과와 토큰 통계. 필요할 때 자동 생성되며 서버 재시작 후에도 유지됩니다.
- 브라우저 탭의 `sessionStorage`: 페이지 이동 시 미저장 입력과 기준 A 복원에 사용합니다. 최대 24시간 임시 보관하며 API 키는 포함하지 않습니다.
- 백업: **서버 종료 후 `data` 폴더 전체**를 복사하세요.
- `data` 없이 새 폴더에서 실행하면 새 기록으로 시작합니다. 기존 Sites 기록은 포함되어 있지 않습니다.

### 모델 호출과 비용 해석

- 코드에 설정된 모델은 `gemini-3.5-flash-lite`입니다 (`lib/generation.ts`). 계정에서 해당 모델을 사용할 수 있는지는 연결 확인으로 검증하세요.
- 예상 토큰 수는 문자 기반 근사치이며 비용은 코드에 고정된 참고용 단가로 계산합니다. 실시간 가격이나 청구 금액이 아닙니다.
- 실제 호출 후 Google 응답의 토큰 사용량을 기록합니다. 예상 비용이 청구 상한을 보장하지는 않습니다.
- 최근 24시간 기준 100회 새 생성 호출 제한이 있으며 중복 호출을 제어합니다.
- 응답이 불확실하면 `unknown`으로 기록하고 자동 재시도하지 않습니다. 화면의 재시도 안내에 따라 Google 사용 내역을 먼저 확인하세요.

## 6. 문제 해결

| 증상 | 확인 / 해결 |
|---|---|
| `node` 또는 `npm`을 찾지 못함 | Node.js 설치 후 터미널을 다시 열고 버전 확인 |
| PowerShell에서 `npm.ps1` 실행 차단 | `npm.cmd ci` 또는 `npm.cmd run dev`처럼 실행 |
| `npm ci` 실패 | Node.js 버전, npm 레지스트리 연결, `package.json`과 `package-lock.json`의 일치 여부 확인 |
| `.env.example`을 찾지 못함 | 이 문서의 ② 단계처럼 `.env` 직접 생성 |
| 키가 없다고 표시 | `.env` 위치와 확장자 → `GOOGLE_API_KEY` 철자 → 다른 환경변수 설정 → 서버 재시작 |
| Google HTTP 400/401/403 | 키 오타, API 권한과 키 제한 확인 |
| Google HTTP 404 | 코드에 지정된 모델의 계정 접근 가능 여부 확인 |
| Google HTTP 429 | 계정의 할당량과 결제 상태 확인 |
| `node:sqlite` 오류 | Node.js 22.13.0 이상인지 확인하고 지원 버전에서 의존성 재설치 |
| 포트 3000 사용 중 | 기존 실행 터미널에서 Ctrl+C 후 재실행 |
| `npm start`에서 빌드를 찾지 못함 | `npm run build` 성공 후 다시 실행 |
| 같은 설정의 재호출 차단 | 이전 요청의 처리 상태와 Google 사용 내역 확인 후 화면 안내 따르기 |

연결 오류를 문의할 때는 **HTTP 상태 코드와 키를 제외한 오류 메시지**를 사용하세요.

## 7. 개발자 참고

### 검사 명령

일반 사용을 위해 매번 실행할 필요는 없습니다. 코드를 변경했을 때 필요한 검사를 실행하세요.

```sh
npm run typecheck
npm test
node --experimental-strip-types tests/rag-engine.test.mjs
node --experimental-strip-types tests/cost.test.mjs
node --experimental-strip-types tests/workspace-draft.test.mjs
node --experimental-strip-types tests/generation.test.mjs
npm run build
```

생성 테스트는 모의 Google 응답을 사용합니다. 테스트 통과만으로 실제 API 키나 모델 접근이 검증되지는 않습니다. 실제 연결은 모델 연결 화면에서 확인하고, 답변 생성 검증에는 위의 A/B 호출 횟수를 고려하세요.

### 소스 구조

| 경로 | 역할 |
|---|---|
| `app/` | 페이지와 서버 API |
| `components/` | 파이프라인 시각화와 UI |
| `lib/rag-engine.ts` | 청킹·검색·프롬프트 구성 |
| `lib/generation.ts` | 모델 지정과 Google 답변 생성 |
| `lib/local-db.ts` | SQLite 초기화와 접근 |
| `lib/experiment-store.ts` | 실험 기록과 생성 상태 관리 |
| `lib/cost.ts` | 토큰·비용 추정 |
| `tests/` | 로컬 저장, 검색, 비용, 입력 복원, 생성 테스트 |

