from pathlib import Path

def build_prompt(resume_text: str, job_offer_text: str) -> str:
    base_dir = Path(__file__).resolve().parent
    template_file = base_dir / "prompts" / "GetReplacementsPrompt.txt"

    if not template_file.exists():
        raise FileNotFoundError(f"Base prompt not found: {template_file}")

    template = template_file.read_text(encoding="utf-8")

    return (
        template
        .replace("<<<RESUME>>>", resume_text.strip())
        .replace("<<<JOBOFFER>>>", job_offer_text.strip())
    )
