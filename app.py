import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))  # so `from agent import analyze` works

from agent import analyze  # noqa: E402

st.set_page_config(page_title="JD Analyzer", page_icon="📄", layout="centered")
st.title("JD Analyzer Agent")
st.caption("Paste a job description to see how well it matches your skills.")

jd = st.text_area(
    "Job description",
    height=300,
    placeholder="Paste the full job description here...",
)

if st.button("Analyze", type="primary"):
    if len(jd.strip()) < 200:
        st.warning("Please paste a full job description (at least 200 characters).")
        st.stop()

    with st.spinner("Analyzing... this can take a few seconds"):
        result = analyze(jd)

    if result is None:
        st.error(
            "The agent could not return a valid result. This is usually a quota "
            "limit or a model error. Check the terminal for details and try again."
        )
        st.stop()

    st.subheader(result.get("role_type", "Result"))
    st.metric("Fit score (rough signal)", f"{result.get('fit_score', '?')} / 10")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Matching skills**")
        for s in result.get("matching_skills", []):
            st.success(s)
    with col2:
        st.markdown("**Missing skills**")
        for s in result.get("missing_skills", []):
            st.error(s)

    with st.expander("Required skills"):
        st.write(result.get("required_skills", []))
    