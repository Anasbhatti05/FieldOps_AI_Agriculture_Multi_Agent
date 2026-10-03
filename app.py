import io
import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageOps

from agents.coordinator import coordinate
from agents.models import FieldAssessment
from tools.spreadsheet import create_test_workbook, read_workbook
from ui.translations import AGENTS, crop_label, localized_actions, localized_finding, localized_summary, stage_label, text
from vision.inference import vision_enabled


load_dotenv()
st.set_page_config(page_title="FieldOps AI", page_icon="🌾", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&family=Noto+Sans+Arabic:wght@400;500;600;700;800&display=swap');
    :root {
        --field-ink: #203a2d;
        --field-green: #2f6147;
        --field-leaf: #7d9468;
        --field-gold: #d3a83d;
        --field-clay: #ba654e;
        --field-paper: #f4f6ef;
        --field-line: #dce4d5;
    }
    .stApp {
        color: var(--field-ink);
        background-color: var(--field-paper);
        background-image: repeating-linear-gradient(135deg, rgba(92, 120, 77, .035) 0, rgba(92, 120, 77, .035) 1px, transparent 1px, transparent 14px);
    }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 1180px; padding: 1.7rem 2rem 3.5rem; }
    h1, h2, h3, [data-testid="stWidgetLabel"] p { color: var(--field-ink); font-family: 'Noto Sans Arabic', 'Noto Nastaliq Urdu', sans-serif; }
    [data-testid="stMarkdownContainer"] p, [data-testid="stCaptionContainer"] p { font-family: 'Noto Sans Arabic', 'Noto Nastaliq Urdu', sans-serif; }
    [data-testid="stWidgetLabel"] p { font-size: 1.02rem; font-weight: 700; }
    [data-testid="stVerticalBlockBorderWrapper"] { background: rgba(255,255,255,.94); border-color: var(--field-line); border-radius: 8px; }
    div.stButton > button[kind="primary"], div.stFormSubmitButton > button { background: var(--field-green); border: 0; color: white; border-radius: 7px; min-height: 3rem; font-weight: 700; }
    div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button:hover { background: #234d38; border: 0; color: white; }
    div.stButton > button { border-radius: 7px; border-color: #b9c8b2; color: var(--field-ink); min-height: 2.7rem; }
    [data-testid="stMetric"] { background: #fff; border: 1px solid var(--field-line); border-radius: 7px; padding: .9rem 1rem; }
    [data-testid="stMetricLabel"] p { color: #5b6c5c; }
    .field-hero { background: linear-gradient(110deg, #234a36 0%, #356447 68%, #687b4d 100%); color: #fff; border-radius: 10px; padding: 1.55rem 1.8rem; margin: .5rem 0 1.2rem; border-bottom: 4px solid var(--field-gold); }
    .field-hero h1 { color: #fff; font-size: 2rem; margin: 0 0 .5rem; line-height: 1.65; }
    .field-hero p { color: #edf2e7; margin: 0; font-size: 1rem; line-height: 1.9; }
    .section-kicker { color: var(--field-green); font-size: .88rem; font-weight: 800; letter-spacing: .04em; text-transform: uppercase; }
    .priority-strip { border-right: 5px solid var(--field-gold); background: #fff; padding: .9rem 1.2rem; border-radius: 6px; margin: .6rem 0 1rem; }
    .safety-strip { border-right: 5px solid var(--field-clay); background: #fff5ee; padding: .9rem 1.1rem; border-radius: 6px; margin: .6rem 0; }
    .agent-name { color: var(--field-green); font-size: 1.08rem; font-weight: 800; }
    .urdu-copy { direction: rtl; text-align: right; line-height: 2.1; font-family: 'Noto Nastaliq Urdu', 'Noto Sans Arabic', sans-serif; }
    [data-testid="stFileUploader"] section { border-color: #aabca5; background: #fbfcf8; }
    @media (max-width: 700px) {
        .block-container { padding: .8rem .8rem 2rem; }
        .field-hero { padding: 1.15rem 1rem; }
        .field-hero h1 { font-size: 1.55rem; }
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def prepare_image(uploaded_file) -> tuple[bytes | None, str | None]:
    if uploaded_file is None:
        return None, None
    if uploaded_file.size > 8 * 1024 * 1024:
        return None, "Please use a photo smaller than 8 MB."
    with Image.open(io.BytesIO(uploaded_file.getvalue())) as image:
        normalized = ImageOps.exif_transpose(image).convert("RGB")
        normalized.thumbnail((1280, 1280))
        output = io.BytesIO()
        normalized.save(output, format="JPEG", quality=82, optimize=True)
        return output.getvalue(), None


def build_report(field: FieldAssessment, result, language: str) -> tuple[str, str]:
    irrigation = next(item for item in result.findings if item.agent == "Irrigation agent")
    water_m3 = float(irrigation.calculation.get("estimated_net_water_m3", 0))
    summary = localized_summary(language, field.soil_moisture_pct, field.forecast_rain_mm, water_m3)
    actions = localized_actions(language, field.forecast_rain_mm, field.temperature_c, field.wind_kph, water_m3)
    report_lines = [
        "# FieldOps AI - Field check" if language == "en" else "# FieldOps AI - کھیت کی جانچ",
        f"Generated: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}",
        "",
        f"- Crop: {crop_label(language, field.crop)}",
        f"- Stage: {stage_label(language, field.crop_stage)}",
        f"- Area: {field.field_area_acres:.2f} acres",
        f"- Soil moisture: {field.soil_moisture_pct:.1f}%",
        f"- Entered expected rain: {field.forecast_rain_mm:.1f} mm",
        f"- Temperature / wind: {field.temperature_c:.1f} C / {field.wind_kph:.1f} km/h",
        f"- Location: {field.location or 'Not entered'}",
        "",
        f"## {'Summary' if language == 'en' else 'خلاصہ'}",
        summary,
        "",
        f"## {'Next steps' if language == 'en' else 'اگلے قدم'}",
        *[f"{index}. {action}" for index, action in enumerate(actions, start=1)],
        "",
        f"## {'Specialist trace' if language == 'en' else 'ماہر ایجنٹس کی جانچ'}",
    ]
    for finding in result.findings:
        label = text(language, AGENTS[finding.agent])
        translated = localized_finding(language, finding.agent, field.soil_moisture_pct, field.forecast_rain_mm >= 10, water_m3)
        report_lines.extend([f"### {label}", translated])
        if finding.evidence:
            report_lines.extend([f"- {entry}" for entry in finding.evidence])
        if finding.sources:
            report_lines.append(f"Sources: {', '.join(finding.sources)}")
        report_lines.append("")
    report_lines.extend([
        f"## {'Calculation assumptions' if language == 'en' else 'حساب کی بنیاد'}",
        *[f"- {item}" for item in result.assumptions],
        "",
        f"## {'Review flags' if language == 'en' else 'دوبارہ جانچ'}",
        *[f"- {item}" for item in result.review_flags],
        "",
        text(language, "safety_note"),
    ])
    markdown_report = "\n".join(report_lines)
    json_report = json.dumps(
        {
            "generated_at": datetime.now().astimezone().isoformat(),
            "field": field.model_dump(mode="json", exclude={"image_bytes"}),
            "assessment": result.model_dump(mode="json"),
        },
        ensure_ascii=False,
        indent=2,
    )
    return markdown_report, json_report


def render_results(field: FieldAssessment, result, language: str) -> None:
    irrigation = next(item for item in result.findings if item.agent == "Irrigation agent")
    water_m3 = float(irrigation.calculation.get("estimated_net_water_m3", 0))
    summary = localized_summary(language, field.soil_moisture_pct, field.forecast_rain_mm, water_m3)
    actions = localized_actions(language, field.forecast_rain_mm, field.temperature_c, field.wind_kph, water_m3)
    priority_key = result.priority
    st.markdown(f"## {text(language, 'results')}")
    st.markdown(
        f"<div class='priority-strip'><b>{text(language, 'priority')}: {text(language, priority_key)}</b><br>{summary}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"### {text(language, 'actions')}")
    for number, action in enumerate(actions, start=1):
        st.markdown(f"**{number}.** {action}")
    if water_m3 > 0:
        st.metric(text(language, "estimated_water"), f"{water_m3:,.0f} m³", text(language, "water_unit"))

    st.markdown(f"### {text(language, 'agents')}")
    for row_start in range(0, len(result.findings), 2):
        columns = st.columns(2)
        for column, finding in zip(columns, result.findings[row_start:row_start + 2]):
            with column:
                with st.container(border=True):
                    label = text(language, AGENTS[finding.agent])
                    st.markdown(f"<div class='agent-name'>{label}</div>", unsafe_allow_html=True)
                    st.markdown(localized_finding(language, finding.agent, field.soil_moisture_pct, field.forecast_rain_mm >= 10, water_m3))
                    if finding.calculation:
                        with st.expander(text(language, "assumptions")):
                            for key, value in finding.calculation.items():
                                st.caption(f"{key.replace('_', ' ')}: {value}")
                    if finding.evidence or finding.limitations:
                        with st.expander(text(language, "evidence")):
                            for evidence in finding.evidence:
                                st.write(f"- {evidence}")
                            if finding.sources:
                                st.caption("Knowledge files: " + ", ".join(finding.sources))
                            for limitation in finding.limitations:
                                st.caption(limitation)

    st.markdown(f"### {text(language, 'safety')}")
    st.markdown(f"<div class='safety-strip'>{text(language, 'safety_note')}</div>", unsafe_allow_html=True)
    with st.expander(text(language, "assumptions")):
        for assumption in result.assumptions:
            st.write(f"- {assumption}")
        for flag in result.review_flags:
            st.write(f"- {flag}")
    report_markdown, report_json = build_report(field, result, language)
    left, right = st.columns(2)
    with left:
        st.download_button(
            text(language, "download_md"),
            data=report_markdown.encode("utf-8"),
            file_name="fieldops-field-report.md",
            mime="text/markdown; charset=utf-8",
            use_container_width=True,
        )
    with right:
        st.download_button(
            text(language, "download_json"),
            data=report_json.encode("utf-8"),
            file_name="fieldops-assessment.json",
            mime="application/json",
            use_container_width=True,
        )


def main() -> None:
    if "language" not in st.session_state:
        st.session_state.language = "ur"
    language = st.radio(
        text(st.session_state.language, "language"),
        options=["ur", "en"],
        format_func=lambda value: text(value, "urdu" if value == "ur" else "english"),
        horizontal=True,
        key="language",
    )

    st.markdown(
        f"<div class='field-hero'><h1>{text(language, 'title')}</h1><p>FIELDOPS AI &nbsp; | &nbsp; {text(language, 'subtitle')}</p></div>",
        unsafe_allow_html=True,
    )
    st.info(text(language, "local_note"))
    st.caption(text(language, "groq_note" if vision_enabled() else "no_groq_note"))

    if st.button(text(language, "demo"), type="primary", use_container_width=False):
        st.session_state.update(
            {
                "crop": "Wheat",
                "stage": "Flowering",
                "area": 5.0,
                "moisture": 17.0,
                "recent_rain": 1.0,
                "forecast_rain": 0.0,
                "temperature": 34.0,
                "wind": 8.0,
                "location": "Multan",
                "notes": "Some leaves look pale; check irrigation first.",
                "analysis": None,
            }
        )
        st.rerun()

    st.markdown(f"### {text(language, 'excel_title')}")
    st.caption(text(language, "excel_help"))
    st.download_button(
        text(language, "excel_download"),
        data=create_test_workbook(),
        file_name="fieldops_test_workbook.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    workbook_upload = st.file_uploader(
        text(language, "excel_upload"),
        type=["xlsx"],
        key="excel_upload",
    )

    if workbook_upload:
        try:
            scenarios = read_workbook(workbook_upload.getvalue())
        except Exception as error:
            scenarios = []
            st.error(f"{text(language, 'excel_error')}: {error}")
        if scenarios:
            selected_index = st.selectbox(
                text(language, "excel_row"),
                options=range(len(scenarios)),
                format_func=lambda index: (
                    f"{scenarios[index].name} | row {scenarios[index].row_number}"
                    + (f" | {text(language, 'excel_missing')}: {scenarios[index].error}" if scenarios[index].error else "")
                ),
                key="excel_scenario",
            )
            selected_scenario = scenarios[selected_index]
            excel_photo = st.file_uploader(
                text(language, "photo"),
                type=["jpg", "jpeg", "png", "webp"],
                help=text(language, "photo_hint"),
                key="excel_photo",
            )
            if selected_scenario.error:
                st.warning(f"{text(language, 'excel_missing')}: {selected_scenario.error}")
            if st.button(text(language, "excel_analyze"), type="primary", disabled=selected_scenario.field is None):
                image_bytes, image_error = prepare_image(excel_photo)
                if image_error:
                    st.error(image_error)
                else:
                    field = selected_scenario.field.model_copy(update={"image_bytes": image_bytes})
                    with st.spinner(text(language, "agents")):
                        result = coordinate(field)
                    st.session_state.analysis = (field, result)
                    st.success(text(language, "excel_done"))

    with st.expander(text(language, "sample_pictures")):
        st.caption(text(language, "synthetic_note"))
        sample_images = [
            ("synthetic_wheat_upload_test.jpg", "sample_wheat"),
            ("synthetic_cotton_upload_test.jpg", "sample_cotton"),
            ("synthetic_rice_upload_test.jpg", "sample_rice"),
        ]
        for filename, label_key in sample_images:
            image_path = Path(__file__).parent / "data" / "sample_images" / filename
            if image_path.exists():
                st.download_button(
                    text(language, label_key),
                    data=image_path.read_bytes(),
                    file_name=filename,
                    mime="image/jpeg",
                    key=f"download_{filename}",
                    use_container_width=True,
                )

    st.markdown(f"### {text(language, 'form_title')}")
    with st.form("field_assessment", clear_on_submit=False):
        first, second = st.columns(2)
        with first:
            crop = st.selectbox(
                text(language, "crop"),
                ["Wheat", "Cotton", "Rice", "Maize"],
                format_func=lambda value: crop_label(language, value),
                key="crop",
            )
            area = st.number_input(text(language, "area"), min_value=0.1, max_value=100000.0, step=0.5, key="area")
            recent_rain = st.number_input(text(language, "recent_rain"), min_value=0.0, max_value=500.0, step=1.0, key="recent_rain")
            temperature = st.number_input(text(language, "temperature"), min_value=-10.0, max_value=65.0, step=1.0, key="temperature")
            location = st.text_input(text(language, "location"), key="location")
        with second:
            stage = st.selectbox(
                text(language, "stage"),
                ["Seedling", "Vegetative", "Flowering", "Maturity"],
                format_func=lambda value: stage_label(language, value),
                key="stage",
            )
            moisture = st.number_input(text(language, "moisture"), min_value=0.0, max_value=100.0, step=1.0, key="moisture")
            forecast_rain = st.number_input(text(language, "forecast_rain"), min_value=0.0, max_value=500.0, step=1.0, key="forecast_rain")
            wind = st.number_input(text(language, "wind"), min_value=0.0, max_value=200.0, step=1.0, key="wind")
            notes = st.text_area(text(language, "notes"), height=90, key="notes")
            st.caption(text(language, "voice_hint"))
        uploaded_image = st.file_uploader(text(language, "photo"), type=["jpg", "jpeg", "png", "webp"], help=text(language, "photo_hint"))
        if uploaded_image:
            st.image(uploaded_image.getvalue(), caption=uploaded_image.name, width=260)
        submitted = st.form_submit_button(text(language, "analyze"), type="primary", use_container_width=True)

    if submitted:
        try:
            image_bytes, image_error = prepare_image(uploaded_image)
            if image_error:
                st.error(image_error)
            else:
                field = FieldAssessment(
                    crop=crop,
                    crop_stage=stage,
                    field_area_acres=area,
                    soil_moisture_pct=moisture,
                    recent_rain_mm=recent_rain,
                    forecast_rain_mm=forecast_rain,
                    temperature_c=temperature,
                    wind_kph=wind,
                    location=location,
                    image_bytes=image_bytes,
                    notes=notes,
                )
                with st.spinner(text(language, "agents")):
                    result = coordinate(field)
                st.session_state.analysis = (field, result)
        except Exception as error:
            st.error(f"Could not complete this field check: {error}")

    analysis = st.session_state.get("analysis")
    if analysis:
        field, result = analysis
        render_results(field, result, language)
    else:
        st.caption(text(language, "waiting"))


if __name__ == "__main__":
    main()