# System Architecture

## Workflow

```text
Farmer form + optional crop photo
        |
        v
Input contract (Pydantic)
        |
        +--> Crop image screening (optional Groq; otherwise review required)
        +--> Pest screening (cautious, no diagnosis)
        +--> Soil screening
        +--> Weather screening (user-entered values)
        +--> Irrigation estimate (deterministic calculation)
        +--> Knowledge retrieval (local bilingual Markdown)
        |
        v
Coordinator combines findings and prioritizes checks
        |
        v
Validator adds uncertainty, conflicts, and human-review flags
        |
        v
Urdu/English action checklist + Markdown report + JSON trace
```

## Contracts

Each specialist returns `AgentFinding`: agent name, status, finding, evidence, optional calculation, confidence, limitations, next action, and source documents. `FieldAssessment` carries user inputs. `AssessmentResult` is the coordinator output. Reports omit photo bytes.

## Boundaries

Calculations are deterministic and isolated from language-model output. The vision model is optional and cannot authorize treatment. Weather, crop symptoms, and all actions require human review. No actuators are connected. The local retriever ranks paragraphs by token overlap; it is intentionally small and explainable, not a production vector database.

## Extension Points

- Replace user-entered weather with a sourced provider and timestamped forecast.
- Calibrate moisture thresholds and water estimates with local agronomists and soil data.
- Add a validated crop-specific image model and labeled evaluation set.
- Replace the demo retriever with a reviewed, versioned district knowledge collection.
- Add an audit store only after privacy, consent, retention, and access controls are defined.
