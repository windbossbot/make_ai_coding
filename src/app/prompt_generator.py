"""Prompt generation utilities for Codex-style coding requests."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TaskProfile:
    """Represents the inferred shape of a user task."""

    task_summary: str
    task_type: str
    focus_areas: list[str]
    suggested_skills: list[str]
    recommended_tools: list[str]
    deliverables: list[str]
    security_rules: list[str]
    quality_rules: list[str]
    workflow_rules: list[str]


COMMON_SECURITY_RULES = [
    "민감정보, API 키, 토큰, 비밀번호는 하드코딩하지 말고 `.env`와 `.env.example`로 관리한다.",
    "프로젝트 폴더 밖 파일이나 시스템 설정은 건드리지 않는다.",
    "파괴적 작업은 가능하면 `dry_run` 또는 명시적 승인 절차를 둔다.",
    "외부 입력값과 사용자 입력값은 검증하고, 비정상 값은 즉시 중단한다.",
]

COMMON_QUALITY_RULES = [
    "먼저 현재 프로젝트 구조와 사용 기술을 확인한 뒤 그 스타일에 맞춰 수정한다.",
    "전체 재작성보다 증분 수정 우선으로 작업한다.",
    "가능하면 테스트, lint, 또는 최소 실행 검증을 수행한다.",
    "변경 파일과 이유를 마지막에 간단히 요약한다.",
]

COMMON_WORKFLOW_RULES = [
    "Git 저장소라면 기존 변경 사항을 존중하고 unrelated 파일은 수정하지 않는다.",
    "명확한 산출물과 검증 결과를 함께 남긴다.",
    "필요한 도구와 스킬만 최소한으로 사용한다.",
]


def infer_task_profile(task_summary: str) -> TaskProfile:
    """Infer task type and prompt-building rules from a short task description."""

    normalized = task_summary.strip().lower()

    task_type = "general"
    focus_areas = ["구조 파악", "안전한 증분 수정", "검증"]
    suggested_skills: list[str] = []
    recommended_tools = ["git status", "pytest or equivalent", "lint or format checks"]
    deliverables = ["구현 코드", "변경 요약", "검증 결과", "남은 리스크"]
    security_rules = list(COMMON_SECURITY_RULES)
    quality_rules = list(COMMON_QUALITY_RULES)
    workflow_rules = list(COMMON_WORKFLOW_RULES)

    frontend_keywords = ("웹사이트", "랜딩", "대문", "홈페이지", "hero", "ui")
    automation_keywords = ("크롤링", "스크래핑", "수집", "자동화", "봇")
    trading_keywords = ("백테스트", "트레이딩", "주문", "매수", "매도")
    backend_keywords = ("api", "백엔드", "서버", "웹훅", "endpoint")
    security_keywords = ("보안", "security", "취약점", "cve")
    openai_keywords = ("openai", "codex", "gpt", "responses api")

    if any(keyword in normalized for keyword in frontend_keywords):
        task_type = "frontend_landing"
        focus_areas = [
            "프론트엔드 구조 파악",
            "인상적인 첫 화면 구현",
            "반응형 디자인",
            "접근성과 기본 상호작용",
        ]
        suggested_skills.append("playwright")
        recommended_tools = [
            "browser/dev server",
            "playwright for visual smoke checks",
            "lint or build check",
        ]
        quality_rules.extend(
            [
                "디자인은 평범한 템플릿처럼 보이지 않도록 명확한 콘셉트와 위계를 가진다.",
                "데스크톱과 모바일 모두 자연스럽게 보이도록 반응형으로 구현한다.",
                "폼이나 입력 요소가 있다면 기본 접근성과 입력 검증을 포함한다.",
            ]
        )
    elif any(keyword in normalized for keyword in openai_keywords):
        task_type = "openai_integration"
        focus_areas = [
            "공식 문서 기준 구현",
            "최신 API 사용",
            "환경변수 기반 설정",
            "샘플과 검증",
        ]
        suggested_skills.append("openai-docs")
        recommended_tools = [
            "official docs",
            "environment variables",
            "integration smoke test",
        ]
        quality_rules.append("OpenAI 관련 내용은 가능하면 공식 문서를 기준으로 구현하고 설명한다.")
    elif any(keyword in normalized for keyword in automation_keywords):
        task_type = "automation"
        focus_areas = [
            "작업 흐름 자동화",
            "로그와 오류 복구",
            "타임아웃과 재시도",
            "리소스 정리",
        ]
        recommended_tools = [
            "structured logging",
            "timeout and retry policy",
            "CLI entrypoint",
        ]
        quality_rules.extend(
            [
                "장기 실행 또는 반복 작업에는 timeout, heartbeat, 종료 신호 처리를 포함한다.",
                "시작/종료/오류 흐름을 로그로 남긴다.",
            ]
        )
    elif any(keyword in normalized for keyword in trading_keywords):
        task_type = "trading_or_backtest"
        focus_areas = [
            "계산 정확성",
            "데이터 검증",
            "주문 안전장치",
            "감사 가능한 로그",
        ]
        recommended_tools = [
            "unit tests for financial logic",
            "dry-run support",
            "structured logging",
        ]
        security_rules.extend(
            [
                (
                    "매수, 매도, 출금, DB 쓰기 같은 파괴적 작업은 "
                    "기본적으로 `dry_run=True`로 설계한다."
                ),
                "실행 전 잔고, 가격, 주문 수량 등 핵심 입력은 음수, null, 비정상 범위를 검증한다.",
                "규제 또는 윤리 리스크가 있으면 코드 주석이나 문서에 명시한다.",
            ]
        )
    elif any(keyword in normalized for keyword in backend_keywords):
        task_type = "backend_service"
        focus_areas = [
            "API 구조",
            "입력 검증",
            "에러 처리",
            "운영 가능성",
        ]
        recommended_tools = [
            "API tests",
            "input validation",
            "structured logs",
        ]
        quality_rules.extend(
            [
                "에러 메시지는 사용자 친화적으로 작성하고 해결 방향을 포함한다.",
                "장기 실행 서비스라면 health/heartbeat/timeout 전략을 고려한다.",
            ]
        )
    elif any(keyword in normalized for keyword in security_keywords):
        task_type = "security_review"
        focus_areas = [
            "위협 식별",
            "민감정보 보호",
            "취약점 완화",
            "검증 가능한 수정안",
        ]
        suggested_skills.append("security-best-practices")
        recommended_tools = [
            "dependency audit",
            "input validation review",
            "secret handling review",
        ]
        deliverables = ["보안 리스크 목록", "수정 코드", "검증 결과", "추가 권장 사항"]

    return TaskProfile(
        task_summary=task_summary,
        task_type=task_type,
        focus_areas=dedupe(focus_areas),
        suggested_skills=dedupe(suggested_skills),
        recommended_tools=dedupe(recommended_tools),
        deliverables=dedupe(deliverables),
        security_rules=dedupe(security_rules),
        quality_rules=dedupe(quality_rules),
        workflow_rules=dedupe(workflow_rules),
    )


def build_prompt_package(task_summary: str, output_language: str = "ko") -> str:
    """Build a full request package from a short task description."""

    profile = infer_task_profile(task_summary)
    language = normalize_language(output_language)
    if language == "en":
        return build_prompt_package_en(profile)

    lines: list[str] = []
    lines.append("작업 해석")
    lines.append(f"- 요청 요약: {profile.task_summary}")
    lines.append(f"- 추론된 작업 유형: {profile.task_type}")
    lines.append(f"- 핵심 초점: {', '.join(profile.focus_areas)}")
    lines.append("")
    lines.append("추천 스킬/도구")
    skills_label = ", ".join(profile.suggested_skills)
    if not skills_label:
        skills_label = "특정 스킬 없이 기본 코딩 워크플로우 사용"
    lines.append(
        f"- 스킬: {skills_label}"
    )
    lines.append(f"- 도구: {', '.join(profile.recommended_tools)}")
    lines.append("")
    lines.append("주의사항")
    for rule in profile.security_rules:
        lines.append(f"- {rule}")
    for rule in profile.quality_rules:
        lines.append(f"- {rule}")
    lines.append("")
    lines.append("Codex 요청문")
    lines.append(build_codex_request(profile))
    return "\n".join(lines)


def build_prompt_package_en(profile: TaskProfile) -> str:
    """Build an English request package while preserving the user's task summary."""

    translated_summary = translate_task_summary(profile.task_summary)
    lines: list[str] = []
    lines.append("Task Interpretation")
    lines.append(f"- Request summary: {translated_summary}")
    lines.append(f"- Inferred task type: {profile.task_type}")
    lines.append(f"- Core focus: {', '.join(to_english_focus(profile.focus_areas))}")
    lines.append("")
    lines.append("Suggested Skills/Tools")
    skills_label = ", ".join(profile.suggested_skills) or "Use the base coding workflow"
    lines.append(f"- Skills: {skills_label}")
    lines.append(f"- Tools: {', '.join(to_english_tools(profile.recommended_tools))}")
    lines.append("")
    lines.append("Important Notes")
    for rule in to_english_rules(profile.security_rules):
        lines.append(f"- {rule}")
    for rule in to_english_rules(profile.quality_rules):
        lines.append(f"- {rule}")
    lines.append("")
    lines.append("Codex Request")
    lines.append(build_codex_request_en(profile))
    return "\n".join(lines)


def build_codex_request(profile: TaskProfile) -> str:
    """Render the final Codex-ready request body."""

    lines: list[str] = []
    lines.append(f"현재 작업은 `{profile.task_summary}` 입니다.")
    lines.append("")
    lines.append("목표:")
    for item in profile.focus_areas:
        lines.append(f"- {item} 관점에서 구현 또는 개선하세요.")
    lines.append("")
    lines.append("작업 방식:")
    for rule in profile.workflow_rules:
        lines.append(f"- {rule}")
    lines.append("")
    lines.append("보안/안전:")
    for rule in profile.security_rules:
        lines.append(f"- {rule}")
    lines.append("")
    lines.append("품질:")
    for rule in profile.quality_rules:
        lines.append(f"- {rule}")
    lines.append("")
    lines.append("권장 도구/스킬:")
    if profile.suggested_skills:
        lines.append(f"- 스킬: {', '.join(profile.suggested_skills)}")
    lines.append(f"- 도구: {', '.join(profile.recommended_tools)}")
    lines.append("")
    lines.append("최종 산출물:")
    for item in profile.deliverables:
        lines.append(f"- {item}")
    return "\n".join(lines)


def build_codex_request_en(profile: TaskProfile) -> str:
    """Render the final Codex-ready request in English."""

    translated_summary = translate_task_summary(profile.task_summary)
    lines: list[str] = []
    lines.append(f"The current task is `{translated_summary}`.")
    lines.append("")
    lines.append("Goals:")
    for item in to_english_focus(profile.focus_areas):
        lines.append(f"- Implement or improve the work from the perspective of {item}.")
    lines.append("")
    lines.append("Working Style:")
    for rule in to_english_rules(profile.workflow_rules):
        lines.append(f"- {rule}")
    lines.append("")
    lines.append("Security/Safety:")
    for rule in to_english_rules(profile.security_rules):
        lines.append(f"- {rule}")
    lines.append("")
    lines.append("Quality:")
    for rule in to_english_rules(profile.quality_rules):
        lines.append(f"- {rule}")
    lines.append("")
    lines.append("Recommended Tools/Skills:")
    if profile.suggested_skills:
        lines.append(f"- Skills: {', '.join(profile.suggested_skills)}")
    lines.append(f"- Tools: {', '.join(to_english_tools(profile.recommended_tools))}")
    lines.append("")
    lines.append("Final Deliverables:")
    for item in to_english_deliverables(profile.deliverables):
        lines.append(f"- {item}")
    return "\n".join(lines)


def dedupe(values: list[str]) -> list[str]:
    """Remove duplicates while preserving order."""

    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def normalize_language(output_language: str) -> str:
    """Normalize the requested output language."""

    return "en" if output_language.lower().startswith("en") else "ko"


def translate_task_summary(task_summary: str) -> str:
    """Translate a short task summary into rough but usable English."""

    normalized = task_summary.strip()
    exact_mapping = {
        "웹사이트 대문 만들기": "create a website landing page",
        "랜딩 페이지 리디자인하기": "redesign a landing page",
        "관리자 대시보드 화면 만들기": "create an admin dashboard screen",
        "OpenAI API 연동 기능 만들기": "build an OpenAI API integration feature",
        "크롤러 만들기": "build a crawler",
        "백테스트 시스템 초안 만들기": "create a backtesting system draft",
        "FastAPI 서버 구조 잡기": "set up a FastAPI server structure",
        "보안 점검 체크리스트 만들기": "create a security review checklist",
    }
    if normalized in exact_mapping:
        return exact_mapping[normalized]

    translated = normalized
    replacements = [
        ("웹사이트", "website"),
        ("대문", "landing page"),
        ("랜딩 페이지", "landing page"),
        ("관리자", "admin"),
        ("대시보드", "dashboard"),
        ("화면", "screen"),
        ("연동 기능", "integration feature"),
        ("크롤러", "crawler"),
        ("백테스트", "backtesting"),
        ("시스템", "system"),
        ("초안", "draft"),
        ("서버 구조", "server structure"),
        ("보안 점검", "security review"),
        ("체크리스트", "checklist"),
        ("만들기", "build"),
        ("리디자인하기", "redesign"),
        ("구조 잡기", "set up the structure"),
    ]
    for old, new in replacements:
        translated = translated.replace(old, new)
    translated = " ".join(translated.split())
    return translated if translated != normalized else f"work on: {task_summary}"


def to_english_focus(values: list[str]) -> list[str]:
    """Translate common focus labels into English."""

    mapping = {
        "구조 파악": "understanding the existing structure",
        "안전한 증분 수정": "safe incremental changes",
        "검증": "verification",
        "프론트엔드 구조 파악": "understanding the frontend structure",
        "인상적인 첫 화면 구현": "building a strong first-screen experience",
        "반응형 디자인": "responsive design",
        "접근성과 기본 상호작용": "accessibility and basic interactions",
        "공식 문서 기준 구현": "implementation based on official documentation",
        "최신 API 사용": "using the latest API patterns",
        "환경변수 기반 설정": "environment-variable based configuration",
        "샘플과 검증": "samples and validation",
        "작업 흐름 자동화": "workflow automation",
        "로그와 오류 복구": "logging and recovery from errors",
        "타임아웃과 재시도": "timeouts and retries",
        "리소스 정리": "resource cleanup",
        "계산 정확성": "calculation accuracy",
        "데이터 검증": "data validation",
        "주문 안전장치": "order safety guards",
        "감사 가능한 로그": "auditable logging",
        "API 구조": "API structure",
        "입력 검증": "input validation",
        "에러 처리": "error handling",
        "운영 가능성": "operability",
        "위협 식별": "threat identification",
        "민감정보 보호": "sensitive data protection",
        "취약점 완화": "vulnerability mitigation",
        "검증 가능한 수정안": "verifiable fixes",
    }
    return [mapping.get(value, value) for value in values]


def to_english_rules(values: list[str]) -> list[str]:
    """Translate known rules into English with a sensible fallback."""

    mapping = {
        (
            "민감정보, API 키, 토큰, 비밀번호는 하드코딩하지 말고 "
            "`.env`와 `.env.example`로 관리한다."
        ): (
            "Do not hardcode secrets, API keys, tokens, or passwords. "
            "Manage them with `.env` and `.env.example`."
        ),
        "프로젝트 폴더 밖 파일이나 시스템 설정은 건드리지 않는다.": (
            "Do not modify files outside the project folder or change system settings."
        ),
        "파괴적 작업은 가능하면 `dry_run` 또는 명시적 승인 절차를 둔다.": (
            "For destructive actions, prefer a `dry_run` mode or an explicit approval step."
        ),
        "외부 입력값과 사용자 입력값은 검증하고, 비정상 값은 즉시 중단한다.": (
            "Validate external and user-provided input, and stop immediately on abnormal values."
        ),
        "먼저 현재 프로젝트 구조와 사용 기술을 확인한 뒤 그 스타일에 맞춰 수정한다.": (
            "Inspect the current project structure and tech stack first, "
            "then match the existing style."
        ),
        "전체 재작성보다 증분 수정 우선으로 작업한다.": (
            "Prefer incremental changes over a full rewrite."
        ),
        "가능하면 테스트, lint, 또는 최소 실행 검증을 수행한다.": (
            "Run tests, lint, or at least a minimal execution check whenever possible."
        ),
        "변경 파일과 이유를 마지막에 간단히 요약한다.": (
            "Briefly summarize the changed files and the reason for each change at the end."
        ),
        "Git 저장소라면 기존 변경 사항을 존중하고 unrelated 파일은 수정하지 않는다.": (
            "If this is a Git repository, respect existing changes "
            "and do not modify unrelated files."
        ),
        "명확한 산출물과 검증 결과를 함께 남긴다.": (
            "Leave behind clear deliverables and verification results."
        ),
        "필요한 도구와 스킬만 최소한으로 사용한다.": (
            "Use only the minimum tools and skills needed for the task."
        ),
        "디자인은 평범한 템플릿처럼 보이지 않도록 명확한 콘셉트와 위계를 가진다.": (
            "Give the design a clear concept and visual hierarchy "
            "so it does not feel like a generic template."
        ),
        "데스크톱과 모바일 모두 자연스럽게 보이도록 반응형으로 구현한다.": (
            "Make the result responsive so it feels natural on both desktop and mobile."
        ),
        "폼이나 입력 요소가 있다면 기본 접근성과 입력 검증을 포함한다.": (
            "If there are forms or inputs, include basic accessibility and input validation."
        ),
        "OpenAI 관련 내용은 가능하면 공식 문서를 기준으로 구현하고 설명한다.": (
            "For OpenAI-related work, implement and explain the solution "
            "using official documentation whenever possible."
        ),
        "장기 실행 또는 반복 작업에는 timeout, heartbeat, 종료 신호 처리를 포함한다.": (
            "For long-running or repeated jobs, include timeout, heartbeat, "
            "and shutdown-signal handling."
        ),
        "시작/종료/오류 흐름을 로그로 남긴다.": "Log startup, shutdown, and error flows.",
        "매수, 매도, 출금, DB 쓰기 같은 파괴적 작업은 기본적으로 `dry_run=True`로 설계한다.": (
            "Design destructive actions such as buy, sell, withdrawal, "
            "or DB writes with `dry_run=True` by default."
        ),
        "실행 전 잔고, 가격, 주문 수량 등 핵심 입력은 음수, null, 비정상 범위를 검증한다.": (
            "Before execution, validate balances, prices, order sizes, "
            "and other core inputs against negatives, nulls, and abnormal ranges."
        ),
        "규제 또는 윤리 리스크가 있으면 코드 주석이나 문서에 명시한다.": (
            "If there are regulatory or ethical risks, document them "
            "in code comments or supporting docs."
        ),
        "에러 메시지는 사용자 친화적으로 작성하고 해결 방향을 포함한다.": (
            "Write user-friendly error messages and include guidance on how to resolve the issue."
        ),
        "장기 실행 서비스라면 health/heartbeat/timeout 전략을 고려한다.": (
            "For long-running services, consider a health, heartbeat, and timeout strategy."
        ),
    }
    return [mapping.get(value, value) for value in values]


def to_english_tools(values: list[str]) -> list[str]:
    """Translate tool hints into English."""

    mapping = {
        "git status": "git status",
        "pytest or equivalent": "pytest or an equivalent test runner",
        "lint or format checks": "lint or formatting checks",
        "browser/dev server": "browser or local dev server",
        "playwright for visual smoke checks": "Playwright for visual smoke checks",
        "lint or build check": "lint or build check",
        "official docs": "official docs",
        "environment variables": "environment variables",
        "integration smoke test": "integration smoke test",
        "structured logging": "structured logging",
        "timeout and retry policy": "timeout and retry policy",
        "CLI entrypoint": "CLI entrypoint",
        "unit tests for financial logic": "unit tests for financial logic",
        "dry-run support": "dry-run support",
        "API tests": "API tests",
        "input validation": "input validation",
        "structured logs": "structured logs",
        "dependency audit": "dependency audit",
        "input validation review": "input validation review",
        "secret handling review": "secret handling review",
    }
    return [mapping.get(value, value) for value in values]


def to_english_deliverables(values: list[str]) -> list[str]:
    """Translate deliverable labels into English."""

    mapping = {
        "구현 코드": "implemented code",
        "변경 요약": "change summary",
        "검증 결과": "verification results",
        "남은 리스크": "remaining risks",
        "보안 리스크 목록": "security risk list",
        "수정 코드": "fixes",
        "추가 권장 사항": "additional recommendations",
    }
    return [mapping.get(value, value) for value in values]
