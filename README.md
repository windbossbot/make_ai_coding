# Safe Automation Template

운영 자동화, 데이터 처리, 백테스트, 크롤링, 내부 도구를 위한 안전 기본값 템플릿이자,
짧은 작업 설명을 Codex용 정교한 요청문으로 바꿔주는 웹 서비스형 프롬프트 생성기입니다.

## 포함된 기본값
- 시작 시 PID, 실행 명령어, 로그 파일 경로 기록
- 포트 충돌과 기존 PID 파일 감지
- `dry_run=True` 기본 보호 장치
- `.env` 기반 설정 로드와 `.env.example` 제공
- JSON 구조 로그
- 종료 시 임시 디렉터리 자동 정리
- 입력 데이터 무결성 검증 유틸리티
- 작업 유형 분류 기반 Codex 요청문 생성기
- `pytest`, `ruff`, GitHub Actions, Docker 템플릿

## 권장 구조
```text
project/
├── src/
├── utils/
├── config/
├── tests/
├── scripts/
├── docs/
├── .env.example
└── README.md
```

## 빠른 시작
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
copy .env.example .env
python scripts/run_example.py --mode oneshot --dry-run
python scripts/generate_prompt.py "웹사이트 대문 만들기"
uvicorn app.web_service:app --reload
```

## 실행 예시
단발성 작업:
```bash
python scripts/run_example.py --mode oneshot --dry-run
```

프롬프트 생성:
```bash
python scripts/generate_prompt.py "웹사이트 대문 만들기"
```

웹 서비스 실행:
```bash
uvicorn app.web_service:app --reload
```

지속성 작업:
```bash
python scripts/run_example.py --mode service --port 8000 --timeout-seconds 600
```

강제 실행:
```bash
python scripts/run_example.py --mode oneshot --execute --force
```

## 종료 정리 명령어
- Windows: `taskkill /PID <PID> /F`
- Unix: `kill -9 <PID>` 또는 `pkill -f run_example.py`

## 품질 게이트
```bash
pytest
ruff check .
```

## 프롬프트 생성기 동작 방식
- 입력: 사용자의 짧은 작업 설명
- 분류: 웹, 백엔드, 자동화, 보안, OpenAI 연동, 트레이딩/백테스트 등
- 조합: 스킬 추천, 보안 규칙, 품질 규칙, 산출물 형식
- 출력: 바로 Codex에 붙여넣을 수 있는 요청문

## 배포 메모
- 웹 서비스 배포 시 `render.yaml`을 사용할 수 있습니다.
- 시작 명령은 `uvicorn app.web_service:app --host 0.0.0.0 --port $PORT` 입니다.
- 이전처럼 단발성 스크립트를 실행하면 배포 플랫폼에서 조기 종료로 실패할 수 있습니다.
- 루트 `/` 경로에서 바로 HTML 페이지가 열리도록 구성했습니다.

예시 입력:
```text
웹사이트 대문 만들기
```

예시 출력 항목:
- 작업 해석
- 추천 스킬/도구
- 주의사항
- Codex 요청문
