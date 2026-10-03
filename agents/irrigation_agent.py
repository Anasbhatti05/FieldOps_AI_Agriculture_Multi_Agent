from agents.models import AgentFinding, FieldAssessment
from tools.calculators import estimate_irrigation


def analyze_irrigation(field: FieldAssessment) -> AgentFinding:
    area_hectares = field.field_area_acres * 0.404686
    estimate = estimate_irrigation(
        soil_moisture_pct=field.soil_moisture_pct,
        area_hectares=area_hectares,
        forecast_rain_mm=field.forecast_rain_mm,
    )
    if estimate.recommended:
        finding = "The demo estimate shows a moisture gap after the entered rain forecast. Verify before watering."
        action = f"Check soil near roots; if still dry, discuss about {estimate.net_water_m3:.0f} m3 net water with a local adviser."
    else:
        finding = "The demo estimate does not flag irrigation now after accounting for entered forecast rain."
        action = "Recheck soil after the forecast rain; do not irrigate from this estimate alone."

    return AgentFinding(
        agent="Irrigation agent",
        finding=finding,
        evidence=[
            f"Soil moisture: {field.soil_moisture_pct:.1f}%",
            f"Forecast rain: {field.forecast_rain_mm:.1f} mm",
            f"Field area: {field.field_area_acres:.2f} acres",
        ],
        calculation={
            "estimated_net_deficit_mm": estimate.deficit_mm,
            "effective_rain_mm": estimate.effective_rain_mm,
            "estimated_net_water_m3": estimate.net_water_m3,
        },
        confidence="low",
        limitations=list(estimate.assumptions),
        recommended_action=action,
    )