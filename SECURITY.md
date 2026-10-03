# Security and Privacy

- Never commit `.env`, API keys, private farmer records, or images that contain a person's face or identifying details.
- Public deployment keeps `GROQ_VISION_ENABLED=false` and does not need `GROQ_API_KEY`.
- Enabling Groq vision sends uploaded crop images to Groq and may incur provider charges. Only enable it for a private, controlled demo after reviewing provider terms and API limits.
- The prototype has no login, rate limiting, database, or access control. Do not upload confidential farm records or use it as a public production service.
- Results are decision support only. A qualified local adviser must verify consequential farm actions.
