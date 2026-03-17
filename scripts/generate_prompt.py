"""CLI to generate Codex-ready prompts from a short task description."""

from __future__ import annotations

import argparse

from app.prompt_generator import build_prompt_package


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""

    parser = argparse.ArgumentParser(
        description="Generate a Codex-ready request prompt from a short task description."
    )
    parser.add_argument("task", help="Short task description, for example: 웹사이트 대문 만들기")
    return parser


def main() -> int:
    """Generate and print the prompt package."""

    parser = build_parser()
    args = parser.parse_args()
    print(build_prompt_package(args.task))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
