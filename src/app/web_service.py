"""FastAPI web service for the prompt generator."""

from __future__ import annotations

from html import escape

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .prompt_generator import build_prompt_package, infer_task_profile

app = FastAPI(title="Make AI Coding", version="0.2.0")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    """Render the main prompt generator page."""

    return render_page(task_summary="", prompt_package="", task_type="", skills=[])


@app.get("/generate", response_class=HTMLResponse)
def generate(task: str = "") -> str:
    """Generate a prompt package from form input."""

    cleaned_task = task.strip()
    if not cleaned_task:
        return render_page(
            task_summary="",
            prompt_package="작업 설명을 입력해 주세요.",
            task_type="general",
            skills=[],
        )

    profile = infer_task_profile(cleaned_task)
    prompt_package = build_prompt_package(cleaned_task)
    return render_page(
        task_summary=cleaned_task,
        prompt_package=prompt_package,
        task_type=profile.task_type,
        skills=profile.suggested_skills,
    )


def render_page(
    *,
    task_summary: str,
    prompt_package: str,
    task_type: str,
    skills: list[str],
) -> str:
    """Build the HTML page for the prompt generator."""

    safe_task = escape(task_summary)
    safe_prompt = escape(prompt_package)
    safe_task_type = escape(task_type or "ready")
    skill_badges = "".join(
        f'<span class="badge">{escape(skill)}</span>' for skill in skills
    ) or '<span class="badge muted">base workflow</span>'
    empty_state = '<div class="empty">작업 설명을 입력하면 결과가 여기에 표시됩니다.</div>'
    prompt_block = f"<pre>{safe_prompt}</pre>" if prompt_package else empty_state

    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Make AI Coding</title>
      <style>
        :root {{
          --bg: #09111a;
          --bg2: #111d27;
          --panel: rgba(10, 17, 24, 0.76);
          --line: rgba(255, 255, 255, 0.10);
          --text: #f6f7fb;
          --muted: #b9c6d3;
          --accent: #2ee6a6;
          --accent2: #ffbf47;
        }}
        * {{ box-sizing: border-box; }}
        body {{
          margin: 0;
          font-family: "Segoe UI", "Noto Sans KR", sans-serif;
          color: var(--text);
          background:
            radial-gradient(circle at top left, rgba(46, 230, 166, 0.14), transparent 28%),
            radial-gradient(circle at top right, rgba(255, 191, 71, 0.14), transparent 22%),
            linear-gradient(180deg, var(--bg) 0%, var(--bg2) 100%);
        }}
        .shell {{
          max-width: 1140px;
          margin: 0 auto;
          padding: 28px 20px 56px;
        }}
        .hero, .panel {{
          background: var(--panel);
          border: 1px solid var(--line);
          border-radius: 24px;
          box-shadow: 0 18px 70px rgba(0, 0, 0, 0.28);
          backdrop-filter: blur(10px);
        }}
        .hero {{
          padding: 28px;
          margin-bottom: 22px;
        }}
        .eyebrow {{
          display: inline-block;
          color: #99d2bf;
          text-transform: uppercase;
          letter-spacing: 0.12em;
          font-size: 12px;
          margin-bottom: 12px;
        }}
        h1 {{
          margin: 0 0 12px;
          font-size: clamp(2rem, 4.4vw, 4rem);
          line-height: 0.98;
        }}
        .lede {{
          max-width: 760px;
          color: var(--muted);
          font-size: 1.05rem;
          line-height: 1.7;
          margin: 0;
        }}
        .grid {{
          display: grid;
          grid-template-columns: 1.05fr 0.95fr;
          gap: 20px;
        }}
        .panel {{
          padding: 22px;
        }}
        .section {{
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: #9db0c2;
          margin-bottom: 10px;
        }}
        textarea {{
          width: 100%;
          min-height: 180px;
          border-radius: 18px;
          border: 1px solid var(--line);
          background: rgba(255, 255, 255, 0.03);
          color: var(--text);
          padding: 16px;
          font-size: 16px;
          resize: vertical;
        }}
        button {{
          width: 100%;
          margin-top: 14px;
          padding: 14px 18px;
          border: 0;
          border-radius: 999px;
          background: linear-gradient(90deg, var(--accent), #64f4d0);
          color: #071019;
          font-size: 15px;
          font-weight: 800;
          cursor: pointer;
        }}
        .meta {{
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          margin-top: 4px;
          margin-bottom: 18px;
        }}
        .badge {{
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 8px 12px;
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.06);
          border: 1px solid var(--line);
          color: var(--text);
          font-size: 13px;
        }}
        .badge.muted {{
          color: var(--muted);
        }}
        .helper-list {{
          margin: 0;
          padding-left: 18px;
          color: var(--muted);
          line-height: 1.9;
        }}
        pre {{
          margin: 0;
          padding: 18px;
          overflow-x: auto;
          white-space: pre-wrap;
          border-radius: 18px;
          border: 1px solid var(--line);
          background: rgba(0, 0, 0, 0.28);
          color: #eff4fa;
          line-height: 1.65;
          font-size: 14px;
        }}
        .empty {{
          color: var(--muted);
          padding: 18px;
          border-radius: 18px;
          border: 1px dashed rgba(255, 255, 255, 0.16);
        }}
        @media (max-width: 900px) {{
          .grid {{
            grid-template-columns: 1fr;
          }}
          .shell {{
            padding: 18px 14px 44px;
          }}
        }}
      </style>
    </head>
    <body>
      <main class="shell">
        <section class="hero">
          <div class="eyebrow">Prompt Engine</div>
          <h1>짧게 쓰면, Codex용 요청문으로 확장합니다.</h1>
          <p class="lede">
            작업 설명 한 줄만 입력하면 작업 유형, 추천 스킬, 보안 규칙, 품질 기준,
            검증 포인트까지 묶어서 바로 붙여넣을 수 있는 요청문을 생성합니다.
          </p>
        </section>

        <section class="grid">
          <div class="panel">
            <div class="section">Task Input</div>
            <form method="get" action="/generate">
              <textarea name="task" placeholder="예: 웹사이트 대문 만들기">{safe_task}</textarea>
              <button type="submit">요청문 생성</button>
            </form>
          </div>

          <div class="panel">
            <div class="section">What This Adds</div>
            <ul class="helper-list">
              <li>작업 유형 자동 분류</li>
              <li>필요한 스킬과 도구 추천</li>
              <li>보안, 품질, 운영 규칙 자동 결합</li>
              <li>바로 붙여넣을 수 있는 최종 Codex 요청문 출력</li>
            </ul>
          </div>
        </section>

        <section class="panel" style="margin-top: 20px;">
          <div class="section">Task Meta</div>
          <div class="meta">
            <span class="badge">task type: {safe_task_type}</span>
            {skill_badges}
          </div>
          {prompt_block}
        </section>
      </main>
    </body>
    </html>
    """
