from fastapi.testclient import TestClient

from app.web_service import app

client = TestClient(app)


def test_home_route_returns_page() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Make AI Coding" in response.text
    assert "8 presets" in response.text
    assert "결과 복사" in response.text
    assert "lang-en" in response.text


def test_generate_route_returns_prompt_content() -> None:
    response = client.get("/generate", params={"task": "웹사이트 대문 만들기"})

    assert response.status_code == 200
    assert "frontend_landing" in response.text
    assert "Codex 요청문" in response.text


def test_generate_route_can_render_english_output() -> None:
    response = client.get(
        "/generate",
        params={"task": "웹사이트 대문 만들기", "output_language": "en"},
    )

    assert response.status_code == 200
    assert "Task Interpretation" in response.text
    assert "Copy result" in response.text
    assert "create a website landing page" in response.text
