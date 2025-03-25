# 도메인 상태 확인기

현재 PC 환경에서 도메인(URL 포함)에 접속 가능한지 확인하는 Node.js 코드입니다. 각 사이트에 대해 다음과 같은 정보를 확인하고 저장합니다:

- 접속한 사이트 주소 (URL 또는 도메인)
- IP 주소
- 접속 상태 (UP, ERROR, WARNING 등)
- 제공자 (클라우드/CDN 등)
- 확인 시간
- 고유 ID
- (옵션) 캡처 이미지 저장

---

## 💾 준비물

1. **Node.js 설치**  
   [https://nodejs.org](https://nodejs.org) 에서 설치해주세요.

2. **필수 패키지 설치**  
   터미널 또는 명령 프롬프트에서 아래 명령어로 Puppeteer 및 기타 의존성 설치:
   ```bash
   npm install puppeteer cli-progress sharp uuid
   ```

3. **도메인 목록**  
   프로젝트 루트 폴더에 `list.txt` 파일을 생성하고, 접속할 URL을 한 줄씩 입력해 주세요.  
   도메인 뿐만 아니라 전체 URL도 입력 가능합니다.

   ```
   https://www.naver.com
   youtube.com
   http://example.com/test
   ```

---

## ✅ 사용법

1. 다음 명령어로 스크립트 실행:
   ```bash
   node run.js
   ```

2. 실행 결과는 다음과 같이 저장됩니다:

   - **result.json**  
     각 URL의 상태를 포함하는 JSON 파일이 현재 디렉토리에 생성됩니다.

   - **캡처 이미지 (선택)**  
     설정에 따라 사이트 화면이 `./capture` 폴더에 저장됩니다. 각 파일은 `{id}.{확장자}` 형태입니다.

---

## 📝 출력 예시 (`result.json`)

```json
[
  {
    "id": "a7f1fcf3-21ee-4a66-86aa-fdb1cd7ea6cb",
    "domain": "www.naver.com",
    "ip": "223.130.200.107",
    "status": "UP",
    "provider": "AKAMAI",
    "timestamp": "2025-03-25 11:02:14.123"
  },
  ...
]
```

---

## 📸 캡처 기능

- 캡처 여부는 코드 내 `CAPTURE_ENABLED` 변수로 제어할 수 있습니다.
- 캡처는 전체 페이지를 고화질(`deviceScaleFactor: 2`)로 저장합니다.
- 저장 경로: `./capture/`
- 저장 포맷: png, webp 등 (`CAPTURE_FORMAT` 변수로 설정)
- 실패할 경우 최대 `CAPTURE_RETRY_COUNT` 횟수만큼 재시도 후, 실패 시 빈 흰색 이미지가 저장됩니다.

---

## ⚠️ 결과 코드 종류

| 코드       | 설명                                                                 |
|------------|----------------------------------------------------------------------|
| UP         | 정상적으로 접속됨                                                   |
| RESET      | 연결이 재설정됨 (`ERR_CONNECTION_RESET`) - 검열 등의 가능성 있음     |
| WARNING    | `warning.or.kr` 사이트로 리디렉션됨                                  |
| NODOMAIN   | 존재하지 않는 도메인 (`DNS_PROBE_FINISHED_NXDOMAIN`)                |
| ERROR      | 기타 오류                                                            |

---

## 📌 주의사항

- 인터넷 연결이 반드시 필요합니다.
- `list.txt`는 UTF-8 인코딩을 권장합니다.
- Puppeteer는 자체 Chromium을 사용하므로 크롬 설치가 필수는 아닙니다.
- DRM 또는 해상도 제한이 있는 사이트는 캡처가 실패할 수 있으며, 이 경우 빈 이미지가 저장됩니다.

---

## 🚀 속도 및 성능

- 동시 다중 탭 실행 (`MAX_CONCURRENT_TABS` 설정 가능)
- `cli-progress`를 사용한 실시간 진행률 표시
- 병렬 처리로 빠르게 많은 사이트를 검사할 수 있습니다

---

## 🛠 설정 예시 (코드 내 설정)

```js
const MAX_CONCURRENT_TABS = 5;          // 동시에 열 탭 수
const IS_HEAD_MODE = false;             // headless 모드 여부
const CAPTURE_ENABLED = true;           // 캡처 기능 사용 여부
const CAPTURE_RETRY_COUNT = 2;          // 캡처 실패 시 재시도 횟수
const CAPTURE_FORMAT = 'png';           // 캡처 저장 확장자
```

---

## 📁 디렉토리 구조

```
project-folder/
├── run.js
├── list.txt
├── result.json
└── capture/
    ├── {id}.png
    └── ...
```
