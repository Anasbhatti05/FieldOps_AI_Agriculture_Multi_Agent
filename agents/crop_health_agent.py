from agents.models import AgentFinding, FieldAssessment
from vision.inference import inspect_crop_image


def analyze_crop_health(field: FieldAssessment) -> AgentFinding:
    try:
        result = inspect_crop_image(field.image_bytes)
    except Exception as error:
        result = {
            "status": "needs_review",
            "finding": f"Image screening could not run ({type(error).__name__}); please ask a field adviser to inspect the crop.",
            "confidence": "low",
        }

    evidence = [f"Selected crop: {field.crop}", f"Growth stage: {field.crop_stage}"]
    if field.image_bytes:
        evidence.append(f"Photo received: {len(field.image_bytes) // 1024} KB")
    return AgentFinding(
        agent="Crop health / vision agent",
        status=result.get("status", "needs_review"),
        finding=result["finding"],
        evidence=evidence,
        confidence="low",
        limitations=["Image screening is preliminary; a photo cannot confirm a diagnosis."],
        recommended_action=result.get("next_check", "Show the crop to a local agriculture extension worker."),
    )