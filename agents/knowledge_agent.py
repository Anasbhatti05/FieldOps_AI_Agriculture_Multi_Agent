from agents.models import AgentFinding, FieldAssessment
from rag.retriever import retrieve


def retrieve_guidance(field: FieldAssessment) -> AgentFinding:
    query = f"{field.crop} {field.crop_stage} soil moisture irrigation rainfall pest photo {field.notes}"
    passages = retrieve(query)
    return AgentFinding(
        agent="Knowledge / RAG agent",
        finding=f"Found {len(passages)} relevant demo guidance passage(s).",
        evidence=[passage.text for passage in passages],
        confidence="low" if passages else "low",
        limitations=["Local knowledge is a small demo set and has not been calibrated for your district."],
        recommended_action="Use the passages as prompts for a local field check, not as a treatment prescription.",
        sources=[passage.source for passage in passages],
    )