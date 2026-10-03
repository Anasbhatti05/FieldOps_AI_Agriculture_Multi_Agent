$ErrorActionPreference = "Stop"
$python = ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Project environment not found. Run .\setup.ps1 first."
}

& $python -m streamlit run app.py