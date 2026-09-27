"""
backend/routes/simulation.py
Atmospheric AI Twin & Microclimate Simulation Endpoint ("What-If Engine").
"""
from fastapi import APIRouter, HTTPException
from backend.models import SimulationRequest, SimulationResponse, SectorImpact
from backend.services.weather_service import fetch_weather
from backend.services.llm_service import generate_simulation_analysis

router = APIRouter(prefix="/simulate", tags=["Atmospheric AI Twin — Microclimate Sandbox"])


def _calculate_sector_impacts(sim: dict) -> tuple[dict[str, SectorImpact], int, str]:
    temp = float(sim.get("temp", 25.0))
    humidity = float(sim.get("humidity", 50.0))
    wind = float(sim.get("wind_speed", 10.0))
    rain = float(sim.get("rain_rate", 0.0))

    # 1. Agriculture Risk
    agri_heat = max(0.0, (temp - 28.0) * 3.2) if temp > 28.0 else 0.0
    agri_frost = max(0.0, (18.0 - temp) * 4.0) if temp < 18.0 else 0.0
    agri_rain = min(40.0, rain * 0.45)
    agri_wind = min(25.0, max(0.0, wind - 20.0) * 0.4)
    agri_hum = max(0.0, (humidity - 80.0) * 0.5) if humidity > 80.0 else (max(0.0, (35.0 - humidity) * 0.4) if humidity < 35.0 else 0.0)
    agri_score = min(100, max(0, int(agri_heat + agri_frost + agri_rain + agri_wind + agri_hum)))
    agri_level = "Critical" if agri_score >= 75 else "Severe" if agri_score >= 50 else "Moderate" if agri_score >= 25 else "Low"

    drivers_agri = [("Heat Stress", agri_heat), ("Cold Frost", agri_frost), ("Rain Inundation", agri_rain), ("Wind Lodging", agri_wind), ("Humidity Anomaly", agri_hum)]
    agri_factor = max(drivers_agri, key=lambda x: x[1])[0] if max(drivers_agri, key=lambda x: x[1])[1] > 5 else "Nominal Conditions"
    agri_adv = "Suspend crop spraying & inspect irrigation channels." if agri_score >= 50 else ("Protect sensitive crops from thermal/moisture stress." if agri_score >= 25 else "Crop environmental conditions are optimal.")

    # 2. Aviation Risk
    vis_est = max(0.2, 10.0 - (rain * 0.08 + max(0.0, humidity - 75.0) * 0.12 + (wind / 25.0)))
    av_wind = min(45.0, wind * 0.55)
    av_rain = min(35.0, rain * 0.4)
    av_vis = max(0.0, (5.0 - vis_est) * 12.0)
    av_temp = max(0.0, (temp - 36.0) * 2.5)
    av_score = min(100, max(0, int(av_wind + av_rain + av_vis + av_temp)))
    av_level = "Critical" if av_score >= 75 else "Severe" if av_score >= 50 else "Moderate" if av_score >= 25 else "Low"

    drivers_av = [("Crosswind & Turbulence", av_wind), ("Precipitation Rate", av_rain), ("Low Visibility", av_vis), ("High Density Altitude", av_temp)]
    av_factor = max(drivers_av, key=lambda x: x[1])[0] if max(drivers_av, key=lambda x: x[1])[1] > 5 else "VFR Clear"
    av_adv = "VFR restricted; expect hold patterns & wind shear alerts." if av_score >= 50 else ("Approach caution due to micro-turbulence." if av_score >= 25 else "Flight operations nominal; clear corridors.")

    # 3. Smart City Infrastructure
    city_rain = min(60.0, rain * 0.55)
    city_wind = min(35.0, max(0.0, wind - 25.0) * 0.5)
    city_heat = max(0.0, (temp - 34.0) * 3.0)
    city_score = min(100, max(0, int(city_rain + city_wind + city_heat)))
    city_level = "Critical" if city_score >= 75 else "Severe" if city_score >= 50 else "Moderate" if city_score >= 25 else "Low"

    drivers_city = [("Stormwater Drainage Cap", city_rain), ("Structural Wind Load", city_wind), ("Urban Heat Island", city_heat)]
    city_factor = max(drivers_city, key=lambda x: x[1])[0] if max(drivers_city, key=lambda x: x[1])[1] > 5 else "Nominal Urban Flow"
    city_adv = "Deploy municipal drainage pumps & divert low-lying traffic." if city_score >= 50 else ("Monitor drainage checkpoints in vulnerable sectors." if city_score >= 25 else "Urban infrastructure functioning normally.")

    # 4. Energy Grid Stress
    grid_ac = max(0.0, (temp - 28.0) * 3.8) if temp > 28.0 else 0.0
    grid_heat_loss = max(0.0, (12.0 - temp) * 3.2) if temp < 12.0 else 0.0
    grid_wind = min(30.0, max(0.0, wind - 35.0) * 0.5)
    grid_hum = max(0.0, (humidity - 85.0) * 0.5)
    grid_score = min(100, max(0, int(grid_ac + grid_heat_loss + grid_wind + grid_hum)))
    grid_level = "Critical" if grid_score >= 75 else "Severe" if grid_score >= 50 else "Moderate" if grid_score >= 25 else "Low"

    drivers_grid = [("Peak AC Cooling Demand", grid_ac), ("Heating Grid Surge", grid_heat_loss), ("Feeder Line Wind Stress", grid_wind), ("Substation Humidity Risk", grid_hum)]
    grid_factor = max(drivers_grid, key=lambda x: x[1])[0] if max(drivers_grid, key=lambda x: x[1])[1] > 5 else "Stable Grid Load"
    grid_adv = "Stage substation cooling & bring spinning reserves online." if grid_score >= 50 else ("Monitor feeder transformer thermal loads." if grid_score >= 25 else "Grid power distribution within safe margins.")

    # 5. Public Health Risk
    heat_index = temp + 0.55 * (humidity / 100.0) * (temp - 14.5)
    health_heat = max(0.0, (heat_index - 30.0) * 3.5) if heat_index > 30.0 else 0.0
    health_cold = max(0.0, (10.0 - temp) * 4.0) if temp < 10.0 else 0.0
    health_rain = min(25.0, rain * 0.3)
    health_score = min(100, max(0, int(health_heat + health_cold + health_rain)))
    health_level = "Critical" if health_score >= 75 else "Severe" if health_score >= 50 else "Moderate" if health_score >= 25 else "Low"

    drivers_health = [("Thermal Heat Stress", health_heat), ("Hypothermia Exposure", health_cold), ("Vector / Flood Risk", health_rain)]
    health_factor = max(drivers_health, key=lambda x: x[1])[0] if max(drivers_health, key=lambda x: x[1])[1] > 5 else "Low Environmental Threat"
    health_adv = "Activate cooling centers & issue heat / hydration advisories." if health_score >= 50 else ("Advise vulnerable populations to limit peak exposure." if health_score >= 25 else "Environmental health threat is minimal.")

    matrix = {
        "Agriculture": SectorImpact(score=agri_score, risk_level=agri_level, key_factor=agri_factor, advisory=agri_adv),
        "Aviation": SectorImpact(score=av_score, risk_level=av_level, key_factor=av_factor, advisory=av_adv),
        "Smart City": SectorImpact(score=city_score, risk_level=city_level, key_factor=city_factor, advisory=city_adv),
        "Energy Grid": SectorImpact(score=grid_score, risk_level=grid_level, key_factor=grid_factor, advisory=grid_adv),
        "Public Health": SectorImpact(score=health_score, risk_level=health_level, key_factor=health_factor, advisory=health_adv),
    }

    avg_score = int(sum(s.score for s in matrix.values()) / len(matrix))
    overall_level = "Critical Hazard" if avg_score >= 75 else "Severe Advisory" if avg_score >= 50 else "Moderate Watch" if avg_score >= 25 else "Nominal"

    return matrix, avg_score, overall_level


@router.post("", response_model=SimulationResponse, include_in_schema=False)
@router.post("/", response_model=SimulationResponse, summary="Run Atmospheric AI Twin Microclimate Simulation")
async def run_simulation(request: SimulationRequest):
    """
    Simulate what-if microclimate shifts on top of live location telemetry.
    Calculates multi-sector impact matrices and generates a Gemini AI Emergency Playbook.
    """
    try:
        baseline = fetch_weather(request.location)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch baseline telemetry: {e}")

    sim_temp = round(float(baseline.get("temp", 28.0)) + request.temp_delta, 1)
    sim_humidity = min(100, max(10, int(baseline.get("humidity", 65) + request.humidity_delta)))
    sim_wind = round(max(0.0, float(baseline.get("wind_speed", 12.0)) + request.wind_gust_kmh), 1)
    sim_rain = round(max(0.0, float(request.rain_rate_mm_hr)), 1)
    sim_feels = round(sim_temp + (0.4 * (sim_humidity / 100) * sim_temp), 1)

    simulated_weather = {
        "temp": sim_temp,
        "feels_like": sim_feels,
        "humidity": sim_humidity,
        "wind_speed": sim_wind,
        "rain_rate": sim_rain,
        "condition": "Simulated Extremes" if (sim_rain > 30 or sim_temp > 40 or sim_wind > 60) else baseline.get("condition", "Clear"),
    }

    impact_matrix, overall_index, hazard_level = _calculate_sector_impacts(simulated_weather)

    ai_playbook = generate_simulation_analysis(
        location=request.location,
        baseline=baseline,
        simulated=simulated_weather,
        preset_name=request.preset_name,
        domain=request.domain,
        language_code=request.language_code,
    )

    return SimulationResponse(
        location=request.location,
        preset_name=request.preset_name,
        baseline_weather=baseline,
        simulated_weather=simulated_weather,
        impact_matrix=impact_matrix,
        overall_hazard_index=overall_index,
        hazard_level=hazard_level,
        ai_playbook=ai_playbook,
    )
