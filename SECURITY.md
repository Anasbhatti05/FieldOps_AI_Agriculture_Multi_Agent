# Security and Privacy

- Never commit `.env`, API keys, private farmer records, or images that contain a person's face or identifying details.
- If an API key is pasted into a chat, issue tracker, screenshot, or public repository, revoke it immediately and create a replacement. Do not reuse the exposed key.
- Public deployment keeps `GROQ_VISION_ENABLED=false` and does not need `GROQ_API_KEY`.
- `OPENAI_API_KEY` is not used by this prototype. Do not configure it.
- Streamlit Community Cloud secrets may be used for a private demo. Enabling Groq vision sends uploaded crop images to Groq and may incur provider charges. Only enable it after reviewing provider terms and API limits; do not enable it on the unauthenticated public demo.
- The prototype has no login, rate limiting, database, or access control. Do not upload confidential farm records or use it as a public production service.
- Results are decision support only. A qualified local adviser must verify consequential farm actions.
