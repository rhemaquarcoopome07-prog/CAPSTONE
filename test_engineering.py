"""
test_engineering.py
====================
Unit tests verifying engineering.py calculations against hand-calculated
examples. Run with: python -m pytest test_engineering.py -v
(or just `python test_engineering.py` for a plain script run).
"""

import math

from engineering import CoolingBody, FlatWall, Fluid, Pipe


def test_pipe_flow_turbulent():
    """Water through a 50mm pipe at 5 L/s — turbulent regime, cross-checked
    against a manually-evaluated Swamee-Jain friction factor."""
    water = Fluid.from_library("Water (20 C)")
    pipe = Pipe(diameter=0.05, length=100, roughness=0.000045, fluid=water)
    q = 0.005  # m^3/s

    v = pipe.velocity(q)
    re = pipe.reynolds_number(q)
    f = pipe.friction_factor(q)
    dp = pipe.pressure_drop(q)

    assert math.isclose(v, q / (math.pi * 0.05**2 / 4), rel_tol=1e-9)
    assert re > 2300  # confirms turbulent

    eps_over_d = 0.000045 / 0.05
    term = eps_over_d / 3.7 + 5.74 / re**0.9
    f_expected = 0.25 / (math.log10(term) ** 2)
    assert math.isclose(f, f_expected, rel_tol=1e-9)

    dp_expected = f * (100 / 0.05) * (water.density * v**2 / 2)
    assert math.isclose(dp, dp_expected, rel_tol=1e-9)


def test_pipe_flow_laminar():
    """Low flow rate should trigger the laminar branch, f = 64/Re."""
    water = Fluid.from_library("Water (20 C)")
    pipe = Pipe(diameter=0.05, length=10, roughness=0.0, fluid=water)
    q = 0.00001  # tiny flow -> laminar
    re = pipe.reynolds_number(q)
    assert re < 2300
    f = pipe.friction_factor(q)
    assert math.isclose(f, 64.0 / re, rel_tol=1e-9)


def test_flat_wall_conduction():
    """Brick wall hand calc: k=0.7, dT=20C, L=0.2m -> q=70 W/m2, Q=700W over 10m2."""
    wall = FlatWall(thickness=0.2, thermal_conductivity=0.7, area=10)
    assert math.isclose(wall.heat_flux(25, 5), 70.0, rel_tol=1e-9)
    assert math.isclose(wall.heat_rate(25, 5), 700.0, rel_tol=1e-9)


def test_newtons_cooling_roundtrip():
    """Coffee cooling: compute time to reach 40C, then verify temperature_at
    that time returns exactly 40C (round-trip consistency check)."""
    body = CoolingBody(h=10, area=0.05, mass=0.3, specific_heat=4186)
    t0, t_inf, target = 90.0, 20.0, 40.0
    t = body.time_to_reach(t0, t_inf, target)
    t_check = body.temperature_at(t0, t_inf, t)
    assert math.isclose(t_check, target, abs_tol=1e-6)


def test_error_handling_no_crash():
    """Invalid inputs should raise ValueError, not crash with an unhandled exception."""
    bad_inputs = [
        lambda: Fluid("bad", -1, 1e-3),
        lambda: Pipe(0, 10, 0.001, Fluid.from_library("Water (20 C)")),
        lambda: FlatWall(-1, 0.5, 10),
        lambda: CoolingBody(-1, 1, 1, 1000),
        lambda: CoolingBody(10, 1, 1, 1000).time_to_reach(20, 20, 15),
    ]
    for fn in bad_inputs:
        try:
            fn()
            assert False, "Expected a ValueError but none was raised"
        except ValueError:
            pass


if __name__ == "__main__":
    tests = [
        test_pipe_flow_turbulent,
        test_pipe_flow_laminar,
        test_flat_wall_conduction,
        test_newtons_cooling_roundtrip,
        test_error_handling_no_crash,
    ]
    for t in tests:
        t()
        print(f"PASS: {t.__name__}")
    print("\nAll tests passed.")
