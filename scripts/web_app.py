"""Streamlit web app for generating Codex-ready prompts."""

from __future__ import annotations

import streamlit as st

from app.prompt_generator import build_prompt_package, infer_task_profile

EXAMPLES = [
    "웹사이트 대문 만들기",
    "OpenAI API 연동 기능 만들기",
    "크롤러 만들기",
    "백테스트 시스템 초안 만들기",
    "관리자용 대시보드 화면 만들기",
]


def inject_styles() -> None:
    """Apply a small custom visual layer on top of Streamlit defaults."""

    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(0, 255, 163, 0.12), transparent 28%),
                radial-gradient(circle at top right, rgba(255, 184, 0, 0.10), transparent 22%),
                linear-gradient(180deg, #07111a 0%, #0c1722 45%, #111a22 100%);
            color: #f4f7fb;
        }
        .block-container {
            max-width: 1120px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        .hero-card, .panel-card {
            border: 1px solid rgba(255, 255, 255, 0.10);
            background: rgba(7, 13, 18, 0.72);
            backdrop-filter: blur(10px);
            border-radius: 22px;
            padding: 1.2rem 1.2rem 1rem 1.2rem;
            box-shadow: 0 18px 60px rgba(0, 0, 0, 0.28);
        }
        .eyebrow {
            display: inline-block;
            font-size: 0.8rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #9cd4c2;
            margin-bottom: 0.6rem;
        }
        .hero-title {
            font-size: 2.6rem;
            line-height: 1.05;
            font-weight: 800;
            margin-bottom: 0.6rem;
            color: #f8fafc;
        }
        .hero-copy {
            font-size: 1.02rem;
            color: #c8d4df;
            max-width: 48rem;
            margin-bottom: 0;
        }
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.8rem;
            margin-top: 1rem;
        }
        .stat-card {
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            background: rgba(255, 255, 255, 0.04);
        }
        .stat-kicker {
            color: #8cb3a6;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .stat-value {
            font-size: 1.05rem;
            font-weight: 700;
            color: #ffffff;
            margin-top: 0.25rem;
        }
        .section-label {
            font-size: 0.84rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #9eb2c6;
            margin-bottom: 0.45rem;
        }
        .stTextArea textarea {
            border-radius: 16px;
        }
        @media (max-width: 900px) {
            .hero-title {
                font-size: 2rem;
            }
            .stat-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    """Render the app header."""

    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">Prompt Engine</div>
            <div class="hero-title">짧게 쓰면, Codex용 요청문으로 확장합니다.</div>
            <p class="hero-copy">
                작업 설명 한 줄만 입력하면 작업 유형, 추천 스킬, 보안 규칙, 품질 기준,
                검증 포인트까지 묶어서 바로 붙여넣을 수 있는 요청문을 생성합니다.
            </p>
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-kicker">Focus</div>
                    <div class="stat-value">스킬 추천 + 안전한 코딩 기준</div>
                </div>
                <div class="stat-card">
                    <div class="stat-kicker">Use Case</div>
                    <div class="stat-value">랜딩 페이지, 자동화, API, OpenAI 연동</div>
                </div>
                <div class="stat-card">
                    <div class="stat-kicker">Output</div>
                    <div class="stat-value">바로 실행 가능한 Codex 요청문</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    """Render example shortcuts and return the selected prompt seed."""

    st.sidebar.title("Prompt Seeds")
    st.sidebar.write("예시를 눌러 시작한 뒤 바로 수정해도 됩니다.")
    selected = st.sidebar.radio("빠른 시작", EXAMPLES, index=0)
    st.sidebar.markdown("---")
    st.sidebar.write("추천 흐름")
    st.sidebar.write("1. 작업 한 줄 입력")
    st.sidebar.write("2. 생성 버튼 클릭")
    st.sidebar.write("3. 결과를 복사해 Codex에 붙여넣기")
    return selected


def main() -> None:
    """Run the Streamlit app."""

    st.set_page_config(
        page_title="Make AI Coding",
        page_icon=":material/bolt:",
        layout="wide",
    )
    inject_styles()
    selected_example = render_sidebar()
    render_hero()

    if "task_input" not in st.session_state:
        st.session_state.task_input = selected_example
    elif st.session_state.task_input in EXAMPLES:
        st.session_state.task_input = selected_example

    st.markdown("")
    left, right = st.columns([1.1, 0.9], gap="large")

    with left:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Task Input</div>', unsafe_allow_html=True)
        task_summary = st.text_area(
            "작업 설명",
            key="task_input",
            height=180,
            placeholder="예: 웹사이트 대문 만들기",
            label_visibility="collapsed",
        )
        generate_clicked = st.button("요청문 생성", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">What This Adds</div>', unsafe_allow_html=True)
        st.write("- 작업 유형 자동 분류")
        st.write("- 필요한 스킬과 도구 추천")
        st.write("- 보안, 품질, 운영 규칙 자동 결합")
        st.write("- 최종 Codex 요청문까지 한 번에 출력")
        st.markdown("</div>", unsafe_allow_html=True)

    if not task_summary.strip():
        st.info("작업 설명을 한 줄 입력하면 바로 요청문을 생성할 수 있습니다.")
        return

    if generate_clicked or task_summary.strip():
        profile = infer_task_profile(task_summary)
        prompt_package = build_prompt_package(task_summary)

        st.markdown("")
        meta_col, skills_col, type_col = st.columns(3, gap="medium")
        meta_col.metric("Task Type", profile.task_type)
        skills_col.metric("Suggested Skills", str(len(profile.suggested_skills)))
        type_col.metric("Deliverables", str(len(profile.deliverables)))

        section_left, section_right = st.columns([1, 1], gap="large")

        with section_left:
            st.subheader("추천 스킬")
            if profile.suggested_skills:
                for skill in profile.suggested_skills:
                    st.write(f"- {skill}")
            else:
                st.write("- 특정 스킬 없이 기본 코딩 워크플로우 사용")

            st.subheader("핵심 초점")
            for area in profile.focus_areas:
                st.write(f"- {area}")

        with section_right:
            st.subheader("보안 및 품질 기준")
            for rule in profile.security_rules[:4]:
                st.write(f"- {rule}")
            for rule in profile.quality_rules[:4]:
                st.write(f"- {rule}")

        st.subheader("Codex 요청문 패키지")
        st.code(prompt_package, language="markdown")
        st.download_button(
            "요청문 다운로드",
            data=prompt_package,
            file_name="codex_prompt.txt",
            mime="text/plain",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
