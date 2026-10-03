from agents.models import AgentFinding, FieldAssessment


def analyze_soil(field: FieldAssessment) -> AgentFinding:
    moisture = field.soil_moisture_pct
    if moisture < 20:
        finding, confidence = "Soil moisture is low against the demo screening band.", "medium"
        action = "Check moisture in two spots near the crop roots before deciding on water."
    elif moisture < 26:
        finding, confidence = "Soil moisture is near the demo watch band.", "low"
        action = "Recheck soil moisture soon; avoid deciding from one reading alone."
    else:
        finding, confidence = "The reading is above the demo low-moisture band.", "low"
        action = "No low-moisture alert from this reading; keep monitoring the field."

    return AgentFinding(
        agent="Soil agent",
        finding=finding,
        evidence=[f"Entered soil moisture: {moisture:.1f}%"],
        confidence=confidence,
        limitations=["Screening bands are demo defaults, not calibrated to this field's soil."],
        recommended_action=action,
    )