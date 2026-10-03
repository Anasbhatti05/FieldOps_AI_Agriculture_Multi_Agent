from agents.models import AgentFinding, FieldAssessment
from agents.crop_health_agent import analyze_crop_health
from agents.irrigation_agent import analyze_irrigation
from agents.knowledge_agent import retrieve_guidance
from agents.pest_agent import screen_pests
from agents.soil_agent import analyze_soil
from agents.weather_agent import analyze_weather


def run_specialists(field: FieldAssessment) -> list[AgentFinding]:
    return [
        analyze_crop_health(field),
        screen_pests(field),
        analyze_soil(field),
        analyze_weather(field),
        analyze_irrigation(field),
        retrieve_guidance(field),
    ]