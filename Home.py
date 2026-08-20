"""
Home.py
=======
Landing page for the Fluid Flow & Heat Transfer Engineering Suite.

This is the entry point for the multi-page Streamlit app. The three
engineering modules live in the pages/ directory and are auto-discovered
by Streamlit's multipage navigation.
"""

import streamlit as st

st.set_page_config(
    page_title="Fluid Flow & Heat Transfer Suite",
    page_icon="🛠️",
    layout="wide",
)

st.title("🛠️ Fluid Flow & Heat Transfer Engineering Suite")

st.markdown(
    """
Welcome! This suite bundles three engineering calculators into one app,
built as the capstone project for **PE 262**.

Use the sidebar to navigate between modules:

- **📐 Pipe Flow Analyser** — velocity, Reynolds number, friction factor,
  and pressure drop for flow through a circular pipe, with an interactive
  pressure-drop-vs-flow-rate plot and CSV export.
- **🔥 Heat Transfer Calculator** — steady-state conduction through a flat
  wall (Fourier's Law) and transient cooling via Newton's Law of Cooling,
  with a live cooling curve.
- **🪨 Rock & Fluid Data Dashboard** — upload your own rock/fluid property
  CSV, filter it, and generate porosity/permeability crossplots.

All calculations are implemented in `engineering.py` as reusable,
documented, unit-verified classes (`Fluid`, `Pipe`, `FlatWall`,
`CoolingBody`) — see the GitHub repo for details and the developer report.
"""
)

st.info(
    "👈 Pick a module from the sidebar to get started.",
    icon="👈",
)

with st.expander("About this project"):
    st.markdown(
        """
        **Course:** PE 262 — Capstone Project
        **Stack:** Python, Streamlit, Pandas, Matplotlib
        **Architecture:** OOP engineering core (`engineering.py`) fully
        decoupled from the Streamlit UI pages, so the physics can be
        unit-tested independently of the app (see `test_engineering.py`).
        """
    )

with st.expander("Quick calculation sanity check"):
    st.markdown(
        "A live import check confirms the core engineering module loads "
        "correctly and produces the expected result for a textbook example "
        "(brick wall conduction: k=0.7 W/m·K, 200 mm thick, ΔT=20°C)."
    )
    try:
        from engineering import FlatWall

        wall = FlatWall(thickness=0.2, thermal_conductivity=0.7, area=10)
        q = wall.heat_flux(25, 5)
        st.success(f"engineering.py loaded OK — sample heat flux q = {q:.1f} W/m² (expected 70.0 W/m²)")
    except Exception as e:
        st.error(f"engineering.py failed to load or compute: {e}")
