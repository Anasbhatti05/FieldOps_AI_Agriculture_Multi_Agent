from agents.models import AgentFinding, FieldAssessment


def screen_pests(field: FieldAssessment) -> AgentFinding:
    if not field.image_bytes:
        return AgentFinding(
            agent="Pest screening agent",
            status="needs_review",
            finding="No photo supplied; pests and leaf symptoms were not screened.",
            evidence=[f"Selected crop: {field.crop}"],
            confidence="low",
            limitations=["This demo cannot diagnose pests without a validated crop-specific model."],
            recommended_action="Check both sides of several leaves and ask a local adviser if damage is visible.",
        )

    return AgentFinding(
        agent="Pest screening agent",
        status="needs_review",
        finding="A photo is available, but this MVP does not confirm pest or disease identity.",
        evidence=["Photo screening is preliminary and not a verified pest classifier."],
        confidence="low",
        limitations=["Do not spray or apply treatment based only on this screening."],
        recommended_action="Inspect affected and healthy plants side by side; seek local expert confirmation before treatment.",
    )