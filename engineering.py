"""
engineering.py
==============
Core engineering classes for the Fluid Flow & Heat Transfer Engineering Suite.

This module contains all physics/OOP logic, kept separate from the Streamlit
UI code so the calculations can be unit-tested and reused across pages.

Classes
-------
Fluid           - holds fluid properties (density, viscosity, etc.)
Pipe            - pipe geometry + flow calculations (Reynolds no., friction
                  factor, pressure drop) for a given Fluid
FlatWall        - steady-state 1D conduction through a single-layer wall
CoolingBody     - Newton's Law of Cooling (lumped capacitance) calculations

All numeric inputs are validated; invalid input raises a ValueError with a
clear message so the calling Streamlit page can catch it and show a
friendly error instead of crashing.
"""

import math


# ---------------------------------------------------------------------------
# Preset fluid property library (SI units, at roughly room temperature/20 C)
# density in kg/m^3, dynamic viscosity in Pa.s (= kg/(m.s))
# ---------------------------------------------------------------------------
FLUID_LIBRARY = {
    "Water (20 C)":      {"density": 998.0,  "viscosity": 1.002e-3},
    "Air (20 C, 1 atm)": {"density": 1.204,  "viscosity": 1.825e-5},
    "Crude Oil (medium)": {"density": 870.0, "viscosity": 1.0e-2},
}


class Fluid:
    """
    Represents a fluid with the properties needed for pipe-flow analysis.

    Parameters
    ----------
    name : str
        Display name of the fluid.
    density : float
        Fluid density in kg/m^3. Must be > 0.
    viscosity : float
        Dynamic viscosity in Pa.s (kg/(m.s)). Must be > 0.
    """

    def __init__(self, name: str, density: float, viscosity: float):
        if density <= 0:
            raise ValueError("Fluid density must be a positive number (kg/m^3).")
        if viscosity <= 0:
            raise ValueError("Fluid viscosity must be a positive number (Pa.s).")
        self.name = name
        self.density = density
        self.viscosity = viscosity

    @classmethod
    def from_library(cls, fluid_name: str) -> "Fluid":
        """Build a Fluid from the built-in FLUID_LIBRARY preset dictionary."""
        if fluid_name not in FLUID_LIBRARY:
            raise ValueError(f"Unknown fluid preset: {fluid_name}")
        props = FLUID_LIBRARY[fluid_name]
        return cls(fluid_name, props["density"], props["viscosity"])

    def __repr__(self):
        return f"Fluid({self.name}, rho={self.density} kg/m3, mu={self.viscosity} Pa.s)"


class Pipe:
    """
    Represents a circular pipe carrying a given Fluid, and provides
    the standard incompressible internal-flow calculations:
    velocity, Reynolds number, Darcy friction factor, and pressure drop.

    Parameters
    ----------
    diameter : float
        Internal pipe diameter in metres. Must be > 0.
    length : float
        Pipe length in metres. Must be > 0.
    roughness : float
        Absolute internal roughness in metres (e.g. 4.5e-5 for commercial
        steel). Must be >= 0.
    fluid : Fluid
        The Fluid object flowing through the pipe.
    """

    def __init__(self, diameter: float, length: float, roughness: float, fluid: Fluid):
        if diameter <= 0:
            raise ValueError("Pipe diameter must be a positive number (m).")
        if length <= 0:
            raise ValueError("Pipe length must be a positive number (m).")
        if roughness < 0:
            raise ValueError("Roughness cannot be negative (m).")
        if not isinstance(fluid, Fluid):
            raise ValueError("fluid must be a Fluid instance.")
        self.diameter = diameter
        self.length = length
        self.roughness = roughness
        self.fluid = fluid

    def area(self) -> float:
        """Return the pipe's internal cross-sectional area in m^2."""
        return math.pi * (self.diameter ** 2) / 4.0

    def velocity(self, flow_rate: float) -> float:
        """
        Return mean flow velocity (m/s) for a given volumetric flow rate.

        Parameters
        ----------
        flow_rate : float
            Volumetric flow rate in m^3/s. Must be > 0.
        """
        if flow_rate <= 0:
            raise ValueError("Flow rate must be a positive number (m^3/s).")
        return flow_rate / self.area()

    def reynolds_number(self, flow_rate: float) -> float:
        """Return the Reynolds number Re = rho*V*D/mu for a given flow rate (m^3/s)."""
        v = self.velocity(flow_rate)
        return (self.fluid.density * v * self.diameter) / self.fluid.viscosity

    def friction_factor(self, flow_rate: float) -> float:
        """
        Return the Darcy-Weisbach friction factor.

        Uses the laminar solution f = 64/Re for Re < 2300, and the
        Swamee-Jain explicit approximation to the Colebrook equation for
        turbulent flow (Re >= 2300):

            f = 0.25 / [log10(eps/(3.7*D) + 5.74/Re^0.9)]^2
        """
        re = self.reynolds_number(flow_rate)
        if re < 2300:
            return 64.0 / re
        term = (self.roughness / (3.7 * self.diameter)) + (5.74 / (re ** 0.9))
        return 0.25 / (math.log10(term) ** 2)

    def pressure_drop(self, flow_rate: float) -> float:
        """
        Return the Darcy-Weisbach pressure drop (Pa) for a given flow rate (m^3/s):

            dP = f * (L/D) * (rho * V^2 / 2)
        """
        f = self.friction_factor(flow_rate)
        v = self.velocity(flow_rate)
        return f * (self.length / self.diameter) * (self.fluid.density * v ** 2 / 2.0)

    def summary(self, flow_rate: float) -> dict:
        """Return a dict of all key results for a given flow rate (m^3/s)."""
        return {
            "velocity_m_s": self.velocity(flow_rate),
            "reynolds_number": self.reynolds_number(flow_rate),
            "friction_factor": self.friction_factor(flow_rate),
            "pressure_drop_Pa": self.pressure_drop(flow_rate),
        }


class FlatWall:
    """
    Steady-state 1D conduction through a single-layer flat wall
    (Fourier's Law).

    Parameters
    ----------
    thickness : float
        Wall thickness in metres. Must be > 0.
    thermal_conductivity : float
        Material thermal conductivity k, in W/(m.K). Must be > 0.
    area : float
        Cross-sectional area normal to heat flow, in m^2. Must be > 0.
    """

    def __init__(self, thickness: float, thermal_conductivity: float, area: float):
        if thickness <= 0:
            raise ValueError("Wall thickness must be a positive number (m).")
        if thermal_conductivity <= 0:
            raise ValueError("Thermal conductivity must be a positive number (W/m.K).")
        if area <= 0:
            raise ValueError("Area must be a positive number (m^2).")
        self.thickness = thickness
        self.k = thermal_conductivity
        self.area = area

    def heat_flux(self, t_hot: float, t_cold: float) -> float:
        """Return heat flux q (W/m^2): q = k * (T_hot - T_cold) / thickness."""
        return self.k * (t_hot - t_cold) / self.thickness

    def heat_rate(self, t_hot: float, t_cold: float) -> float:
        """Return total heat transfer rate Q (W): Q = q * area."""
        return self.heat_flux(t_hot, t_cold) * self.area


class CoolingBody:
    """
    Newton's Law of Cooling (lumped-capacitance model).

    dT/dt = -h*A/(m*c) * (T - T_inf)  =>  T(t) = T_inf + (T0 - T_inf)*exp(-k*t)

    where k = h*A / (m*c) is the cooling-rate constant (1/s).

    Parameters
    ----------
    h : float
        Convective heat transfer coefficient, W/(m^2.K). Must be > 0.
    area : float
        Surface area exposed to the ambient fluid, m^2. Must be > 0.
    mass : float
        Mass of the body, kg. Must be > 0.
    specific_heat : float
        Specific heat capacity of the body, J/(kg.K). Must be > 0.
    """

    def __init__(self, h: float, area: float, mass: float, specific_heat: float):
        if h <= 0:
            raise ValueError("Heat transfer coefficient h must be positive (W/m^2.K).")
        if area <= 0:
            raise ValueError("Area must be positive (m^2).")
        if mass <= 0:
            raise ValueError("Mass must be positive (kg).")
        if specific_heat <= 0:
            raise ValueError("Specific heat must be positive (J/kg.K).")
        self.h = h
        self.area = area
        self.mass = mass
        self.c = specific_heat

    def rate_constant(self) -> float:
        """Return the cooling-rate constant k = h*A/(m*c), in 1/s."""
        return (self.h * self.area) / (self.mass * self.c)

    def temperature_at(self, t0: float, t_inf: float, time: float) -> float:
        """
        Return body temperature at a given time (s) using the analytical
        solution T(t) = T_inf + (T0 - T_inf) * exp(-k*t).
        """
        if time < 0:
            raise ValueError("Time cannot be negative (s).")
        k = self.rate_constant()
        return t_inf + (t0 - t_inf) * math.exp(-k * time)

    def time_to_reach(self, t0: float, t_inf: float, t_target: float) -> float:
        """
        Return the time (s) required to cool from T0 to T_target in an
        ambient of T_inf, solved analytically:

            t = -ln[(T_target - T_inf) / (T0 - T_inf)] / k

        Raises ValueError if T_target is not strictly between T0 and T_inf
        (physically unreachable / already reached).
        """
        if t0 == t_inf:
            raise ValueError("Initial temperature equals ambient temperature; body will not cool.")
        # Check target lies strictly between T0 and T_inf (on the cooling/heating path)
        lo, hi = sorted([t_inf, t0])
        if not (lo < t_target < hi):
            raise ValueError(
                "Target temperature must lie strictly between the initial "
                "temperature and the ambient temperature."
            )
        k = self.rate_constant()
        ratio = (t_target - t_inf) / (t0 - t_inf)
        return -math.log(ratio) / k
