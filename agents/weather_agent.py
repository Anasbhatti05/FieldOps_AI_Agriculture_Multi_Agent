from agents.models import AgentFinding, FieldAssessment


def analyze_weather(field: FieldAssessment) -> AgentFinding:
    evidence = [
        f"Entered rain forecast: {field.forecast_rain_mm:.1f} mm",
        f"Entered temperature: {field.temperature_c:.1f} C",
        f"Entered wind: {field.wind_kph:.1f} km/h",
        f"Recent rainfall: {field.recent_rain_mm:.1f} mm",
    ]
    notes = []
    actions = []
    if field.forecast_rain_mm >= 10:
        notes.append("Rain may reduce the need for planned irrigation.")
        actions.append("Check the local forecast before irrigation.")
    if field.temperature_c >= 38:
        notes.append("High temperature entered; inspect the crop during cooler hours.")
        actions.append("Check for heat stress early in the morning or late afternoon.")
    if field.wind_kph >= 25:
        notes.append("Strong wind entered; conditions may affect field work and spraying.")
        actions.append("Avoid spraying in windy conditions; follow the product label.")
    if not notes:
        notes.append("No demo weather alert was triggered by the entered values.")

    return AgentFinding(
        agent="Weather agent",
        finding=" ".join(notes),
        evidence=evidence,
        confidence="low",
        limitations=["Weather values are entered by the user; no live weather service is connected."],
        recommended_action=" ".join(actions) or "Use a trusted local forecast before time-sensitive field work.",
    )