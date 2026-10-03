from agents.models import AgentFinding, FieldAssessment


def validate_findings(field: FieldAssessment, findings: list[AgentFinding]) -> list[str]:
    flags = [
        "Confirm measurements in the field; the demo moisture target is not calibrated.",
        "Weather values are manual inputs, not a live forecast.",
        "Image and pest screening are preliminary; confirm with a local agriculture adviser.",
    ]
    irrigation = next((item for item in findings if item.agent == "Irrigation agent"), None)
    if field.soil_moisture_pct < 20 and irrigation and not irrigation.calculation.get("estimated_net_water_m3"):
        flags.append("Soil reading is in the dry demo band, but forecast rain offsets the demo estimate; verify soil after rain.")
    if any(item.confidence == "low" for item in findings):
        flags.append("At least one finding has low confidence; treat this plan as a checklist, not a diagnosis.")
    return flags