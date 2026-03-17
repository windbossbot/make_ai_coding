from app.prompt_generator import build_prompt_package, infer_task_profile


def test_infer_frontend_landing_profile() -> None:
    profile = infer_task_profile("웹사이트 대문 만들기")

    assert profile.task_type == "frontend_landing"
    assert "playwright" in profile.suggested_skills
    assert any("반응형" in item for item in profile.quality_rules)


def test_infer_openai_profile_uses_openai_docs_skill() -> None:
    profile = infer_task_profile("OpenAI API 연동 기능 만들기")

    assert profile.task_type == "openai_integration"
    assert "openai-docs" in profile.suggested_skills


def test_build_prompt_package_contains_codex_request_sections() -> None:
    prompt = build_prompt_package("웹사이트 대문 만들기")

    assert "작업 해석" in prompt
    assert "추천 스킬/도구" in prompt
    assert "Codex 요청문" in prompt
    assert "현재 작업은 `웹사이트 대문 만들기` 입니다." in prompt
