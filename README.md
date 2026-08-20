# 🛠️ Fluid Flow & Heat Transfer Engineering Suite

A multi-page Streamlit application built as the capstone project for **PE 262**.
It bundles three engineering calculators — pipe flow, heat transfer, and a
rock/fluid data dashboard — into one deployed tool, backed by an object-oriented
Python engineering core.

**Live app:** _[add your Streamlit Community Cloud URL here after deployment]_
**Repo:** _[add your GitHub repo URL here]_

## Modules

### 📐 Pipe Flow Analyser
Pick a fluid (water, air, crude oil, or a custom fluid), enter pipe geometry
(diameter, length, roughness) and a flow rate. Get velocity, Reynolds number,
Darcy friction factor (laminar `64/Re` or turbulent Swamee-Jain), and pressure
drop. Includes an interactive pressure-drop-vs-flow-rate plot and CSV export
of both the single result and the full curve.

### 🔥 Heat Transfer Calculator
Two calculators in tabs:
1. **Steady-state conduction** through a single-layer flat wall (Fourier's Law).
2. **Newton's Law of Cooling** — time to cool from an initial temperature to a
   target temperature in a given ambient, with a live cooling-curve plot that
   updates as you move the sliders.

### 🪨 Rock & Fluid Data Dashboard
Upload a CSV of rock/core or fluid sample data. View summary statistics,
filter by a porosity threshold, view a porosity histogram and a
porosity-permeability crossplot (with an optional log scale), and download
the filtered data as CSV. A synthetic demo CSV is provided if you don't have
your own data handy.

## Architecture

All the physics/engineering logic lives in **`engineering.py`**, fully
decoupled from the Streamlit UI:

- `Fluid` — fluid properties (density, viscosity), with a small preset
  library (`FLUID_LIBRARY`) plus support for custom fluids.
- `Pipe` — pipe geometry + a `Fluid`; computes velocity, Reynolds number,
  friction factor, and pressure drop.
- `FlatWall` — steady-state 1D conduction (Fourier's Law).
- `CoolingBody` — Newton's Law of Cooling (lumped-capacitance model), with
  both a forward solution (`temperature_at`) and an inverse solution
  (`time_to_reach`).

Every public method has a docstring, and every constructor validates its
inputs and raises a clear `ValueError` on bad input rather than crashing —
the Streamlit pages catch these and display a friendly error message.

`test_engineering.py` contains unit tests that verify the calculations
against hand-calculated examples (see "Verification" below).

## Running locally

```bash
pip install -r requirements.txt
streamlit run Home.py
```

## Running the tests

```bash
python test_engineering.py
```

## Verification against hand calculations

- **Pipe flow:** water, D=50mm, L=100m, ε=0.045mm, Q=5 L/s → V=2.546 m/s,
  Re≈126,800 (turbulent), friction factor cross-checked against a manually
  evaluated Swamee-Jain formula, pressure drop cross-checked against the
  Darcy-Weisbach equation evaluated by hand.
- **Conduction:** brick wall, k=0.7 W/m·K, thickness=0.2m, area=10 m²,
  ΔT=20°C → q = 0.7×20/0.2 = **70 W/m²**, Q = 70×10 = **700 W**. Matches.
- **Newton's cooling:** h=10, A=0.05 m², m=0.3 kg, c=4186 J/kg·K, cooling
  90°C → 40°C in a 20°C ambient → t ≈ 3146 s (52.4 min). Verified by
  plugging the computed time back into the forward solution and confirming
  it returns exactly 40°C.

## Deployment (Streamlit Community Cloud)

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in, and
   click "New app".
3. Point it at this repo, branch `main`, main file path `Home.py`.
4. Deploy. The `pages/` directory is auto-discovered for multipage navigation.

## AI usage documentation

AI assistance was used during development. Below are three representative
prompts, along with what was verified and what was corrected:

1. **Prompt:** "Give me the Swamee-Jain explicit approximation to the
   Colebrook equation for the Darcy friction factor."
   **Verified:** The formula was cross-checked against a standard fluid
   mechanics reference and hand-evaluated for the D=50mm/Q=5L/s example
   above (see `test_pipe_flow_turbulent`).
   **Corrected:** The initial AI-suggested version used `Re^0.9` inside the
   log term but with different implicit units; had to make sure Reynolds
   number was computed as a plain dimensionless float before passing it in,
   otherwise the formula silently returned nonsense — added an explicit
   Reynolds-number calculation step and unit test to lock this in.

2. **Prompt:** "How do I solve Newton's Law of Cooling for the time to reach
   a target temperature, not just the temperature at a given time?"
   **Verified:** Derived the inverse solution
   `t = -ln[(T_target - T_inf)/(T0 - T_inf)] / k` and checked it by plugging
   the resulting time back into the forward equation to confirm it returns
   the target temperature exactly (see `test_newtons_cooling_roundtrip`).
   **Corrected:** The first version didn't guard against `T_target` being
   outside the physically reachable range between `T0` and `T_inf`, which
   would silently produce a `math.log` domain error or a nonsensical
   negative time. Added explicit validation that raises a clear `ValueError`
   instead.

3. **Prompt:** "Suggest how to structure a multipage Streamlit app so the
   physics logic isn't duplicated across pages."
   **Verified:** Confirmed the suggested pattern (single `engineering.py`
   module imported by each page in `pages/`) actually works with
   Streamlit's file-based multipage routing, and that classes could be
   instantiated fresh per page run without state issues.
   **Corrected:** The initial suggestion put Streamlit `st.` calls directly
   inside the engineering classes (for displaying results), which would
   have made the classes untestable outside a running Streamlit app. Removed
   all UI code from `engineering.py` and kept it as pure Python, verified by
   running `test_engineering.py` completely independently of Streamlit.

## Course

PE 262 — Capstone Project. Built with Python, Streamlit, Pandas, NumPy,
and Matplotlib.
