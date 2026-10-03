from agents.models import AssessmentResult, FieldAssessment
from agents.router import run_specialists
from agents.validator import validate_findings


def coordinate(field: FieldAssessment) -> AssessmentResult:
    findings = run_specialists(field)
    irrigation = next(item for item in findings if item.agent == "Irrigation agent")
    weather = next(item for item in findings if item.agent == "Weather agent")
    soil = next(item for item in findings if item.agent == "Soil agent")

    actions = [
        "Check soil moisture in two places near the crop roots.",
        irrigation.recommended_action,
        "Inspect several plants and show unusual symptoms to a local agriculture adviser before treatment.",
    ]
    if field.forecast_rain_mm >= 10:
        actions.insert(1, "Confirm the local rain forecast and recheck soil after rain.")
    if field.temperature_c >= 38:
        actions.append("Inspect the crop during cooler hours for signs of heat stress.")
    if field.wind_kph >= 25:
        actions.append("Avoid spraying in strong wind; follow local rules and the product label.")

    dry_band = field.soil_moisture_pct < 20
    estimated_volume = float(irrigation.calculation.get("estimated_net_water_m3", 0))
    priority = "soon" if dry_band or field.temperature_c >= 38 else "routine"
    if dry_band and estimated_volume == 0 and field.forecast_rain_mm >= 10:
        summary = "Soil reading is low, but entered forecast rain changes the demo estimate. Check the field again after rain before deciding."
    elif irrigation.calculation.get("estimated_net_water_m3", 0) > 0:
        summary = "The demo estimate shows a possible moisture gap. Verify the soil in the field before deciding on irrigation."
    else:
        summary = "No immediate irrigation flag from the demo estimate. Keep checking the field and local forecast."

    evidence = []
    for finding in findings:
        evidence.extend(f"{finding.agent}: {item}" for item in finding.evidence)
    assumptions = list(dict.fromkeys(
        limitation
        for finding in findings
        for limitation in finding.limitations
    ))
    limitations = [
        "This hackathon prototype is not a substitute for an agronomist or local extension advice.",
        "No hardware is controlled and no treatment is prescribed.",
    ]
    review_flags = validate_findings(field, findings)
    if soil.confidence == "low" or weather.confidence == "low":
        priority = "soon" if priority == "routine" else priority

    return AssessmentResult(
        findings=findings,
        priority=priority,
        summary=summary,
        actions=list(dict.fromkeys(actions)),
        evidence=evidence,
        assumptions=assumptions,
        limitations=limitations,
        review_flags=review_flags,
    )