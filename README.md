# FieldOps AI

**Agriculture decision intelligence for farmers and field teams.** A farmer enters a few field readings and may add a crop photo. Six specialist agents review the information, a deterministic tool estimates irrigation, a local knowledge base retrieves safety guidance, and a coordinator produces an evidence-backed action checklist and downloadable report.

The interface opens in Urdu and is designed for mobile screens. English is available from the language switch. The demo does not need an API key, internet weather feed, sensor, or irrigation hardware.

## Start on Windows

Install Python 3.11 or newer. Python 3.13 is supported.

1. Open this project folder in VS Code.
2. Open the terminal in VS Code (`Terminal` > `New Terminal`).
3. Run the setup script once:

   ```powershell
   .\setup.ps1
   ```

4. Start FieldOps AI:

   ```powershell
   .\start.ps1
   ```

5. Open the local address printed by Streamlit (normally `http://localhost:8501`). On a phone connected to the same Wi-Fi, use the computer's local network address and allow the connection through Windows Firewall if prompted.

If PowerShell blocks scripts, run these commands instead:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Stop the app with `Ctrl+C` in the terminal.

## Five-Minute Demo

1. Open the app and keep the default Urdu language, or select English.
2. Select **Load wheat demo**. The form fills with the controlled Multan wheat scenario from `data/sample_sensor_data/wheat_demo.json`.
3. Select **Check this field** (Urdu: **کھیت کی جانچ کریں**). No photo is required for the agent workflow to run.
4. Walk through the six specialist findings: crop image, pest screening, soil, weather, irrigation, and retrieved field guidance.
5. Point out the estimated water amount, its assumptions, the validator's review flags, and the human-review warning.
6. Download the farmer-readable Markdown report and the complete JSON trace.
7. To show the rain/conflict case, change expected rain to `40 mm`, submit again, and show that the estimate changes and asks for an in-field recheck.

## Test with Excel and Pictures

1. In the app, download **Excel field sheet**. It includes a yellow blank row, four ready-made cases, and a **Sample Photos** sheet with wheat, cotton, and rice pictures.
2. In Excel, fill the yellow row. Choose the crop and growth stage from their Urdu drop-downs. Enter a number in every measurement field; enter `0` when there was no rain or wind.
3. Save the workbook as `.xlsx`, upload it into the app, choose your row, and select **Check selected Excel row**. The same six agents run and the report appears below.
4. Try **Dry wheat** (17% moisture, no forecast rain) and **Rain offset** (17% moisture, 40 mm forecast rain). The first estimates a water gap; the second estimates zero after rain and asks you to check the field again.
5. Download one of the sample pictures from **Sample pictures for upload testing**, or save an image from the workbook's **Sample Photos** sheet, then upload it with the Excel row or manual form to check the photo upload workflow.

The supplied pictures are computer-generated illustrations because the environment had no access to an open image source. They test image upload only; they are not real crop photos and must not be used to assess vision accuracy. Use your own clear crop photo for a meaningful optional Groq image-screening demo.

For a photo demo, use a crop photo you have permission to share. Without a Groq key the app accepts the photo but does not pretend to diagnose it. With a key, the photo is sent to Groq for preliminary screening; a human must still verify it.

## Optional Groq Vision

AI image screening is off by default. For a **private demo only**, create a local `.env` from `.env.example`, add a Groq API key, then set `GROQ_VISION_ENABLED=true`. Keep `.env` private; it is ignored by Git. When enabled, uploaded crop photos are sent to Groq and may incur API charges. Do not enable this on an unauthenticated public deployment: visitors could consume your key. All other agents, retrieval, reports, and tests run without Groq.

Set `GROQ_VISION_MODEL` in `.env` if your Groq account uses a different vision model. Model availability depends on the account and provider and is not verified at setup time.

## Publish Online

The app includes a Dockerfile, a Render Blueprint, and a GitHub Actions test workflow. Public vision is disabled in the deployment configuration by default.

1. Create an **empty** GitHub repository (do not add another README or license). This project already has a local `main` branch and initial commit. `.gitignore` excludes `.env`, `.venv`, and local secrets; review the staged files before sharing.
2. Add your new repository as the remote and push the project:

   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/fieldops-ai-agriculture.git
   git push -u origin main
   ```

   Replace `YOUR_USERNAME` with your GitHub username and use the repository name you created.
3. In Render, choose **New +** > **Blueprint**, connect that GitHub repository, and deploy the included `render.yaml`. Render builds the Docker image and uses its Streamlit health endpoint.
4. Wait for the deployment to become healthy, then open the Render URL. The free service may sleep between visits. No Groq key is needed for the public demo.
5. GitHub Actions runs tests automatically on pushes and pull requests for Python 3.11 and 3.13.

The app currently has **no login, rate limiting, or persistent database**. Do not put private farmer data or Groq secrets in this public deployment. Read [SECURITY.md](SECURITY.md) before sharing it. A production launch needs authentication, abuse controls, privacy/consent handling, and agronomist validation.

## Run Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The tests cover irrigation arithmetic, rain offsets, structured specialist outputs, report exports, Excel template parsing, Urdu crop/stage values and numerals, and safety flags.

## What Is Included

- `app.py`: responsive Streamlit farmer dashboard, Urdu/English UI, uploads, trace, and exports.
- `agents/`: structured contracts, six specialists, coordinator, router, and validator.
- `tools/calculators.py`: deterministic water estimate with documented assumptions and input checks.
- `rag/`: small bilingual local guidance library and transparent lexical retrieval.
- `vision/`: optional Groq image-screening adapter with cautious prompt.
- `data/sample_sensor_data/`: repeatable hackathon demo scenario.
- `data/fieldops_test_workbook.xlsx`: fill-in Excel form and four test rows.
- `data/sample_images/`: synthetic images for checking the upload control only.
- `tools/spreadsheet.py`: Urdu/English Excel generation, parsing, and validation.
- `tests/`: focused unit and workflow checks.
- `setup.ps1`, `start.ps1`: Windows setup and launch helpers.
- `Dockerfile`, `render.yaml`: container and Render deployment configuration.
- `.github/workflows/tests.yml`: automated checks on GitHub.
- `SECURITY.md`: public-demo privacy and API-key guidance.

## Safety and Prototype Limits

- This is a hackathon prototype, not agronomic advice or a validated crop diagnostic product.
- Moisture thresholds, target moisture, root depth, and effective-rain assumptions are demonstration defaults. They are not calibrated to crop variety, soil texture, irrigation method, or district.
- Weather is typed by the user; no live forecast is connected.
- The small RAG library is general safety guidance, not district-specific treatment guidance.
- Image and pest screening are preliminary. Never apply pesticide based only on this output; consult local agriculture extension and follow product labels and local rules.
- The app does not control pumps, valves, machinery, or spraying equipment. A person reviews every action.

## Suggested Git Workflow

Create a private GitHub repository if you will add API credentials or farmer data. Commit `.env.example`, never `.env`, photos of people, or real farmer records. Review `.gitignore` before pushing.
