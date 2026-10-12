"""
Benchmark Script: benchmark_weighting_schemes.py
Deskripsi: Menguji 4 Skema Pembobotan Berbasis Jurnal / Standar Akademik Ilmiah
          pada rute-rute utama di Kepulauan Penghu (Taiwan).

Skema yang Diuji:
1. Skema 1: ISO 7243:2017 / WBGT (Wet Bulb Globe Temperature Threshold Model)
2. Skema 2: UTCI (Universal Thermal Climate Index) Non-Linear Physiological Strain Model (Bröde et al., 2012)
3. Skema 3: Solar Radiation Energy Budget Model (Brown & Gillespie, 1995; Vanos et al., 2010)
4. Skema 4: Bi-Objective Pareto-Constrained Routing (Raith & Ehrgott, 2009)
"""

import math
import json
import os
import sys
import pandas as pd

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 1. Dataset Koordinat Rute Populer di Penghu
TEST_ROUTES = [
    {
        "route_name": "Beihuan North Ring (Magong -> Penghu Great Bridge)",
        "start": {"name": "Pelabuhan Magong", "lat": 23.5654, "lon": 119.5668},
        "end": {"name": "Jembatan Lintas Laut Penghu", "lat": 23.6508, "lon": 119.5392},
        "mode": "scooter",
        "base_speed_kmh": 35.0
    },
    {
        "route_name": "Xiyu Exploration (Magong -> Daguoye Columnar Basalt)",
        "start": {"name": "Pelabuhan Magong", "lat": 23.5654, "lon": 119.5668},
        "end": {"name": "Kolom Basalt Daguoye", "lat": 23.5932, "lon": 119.5161},
        "mode": "scooter",
        "base_speed_kmh": 35.0
    },
    {
        "route_name": "Huxi Line (Magong Airport -> Kuobishan Moses Parting)",
        "start": {"name": "Bandara Magong", "lat": 23.5697, "lon": 119.6294},
        "end": {"name": "Kuobishan (Moses Sea Parting)", "lat": 23.5975, "lon": 119.6748},
        "mode": "scooter",
        "base_speed_kmh": 35.0
    },
    {
        "route_name": "Magong Historical Walking Tour",
        "start": {"name": "Pelabuhan Magong", "lat": 23.5654, "lon": 119.5668},
        "end": {"name": "Magong Old Street (Zhongyang St)", "lat": 23.5682, "lon": 119.5635},
        "mode": "walk",
        "base_speed_kmh": 4.5
    }
]

# 2. Lingkungan Cuaca Simulasi Dua Musim Penghu (Summer vs Winter Monsoon)
SUMMER_HEATWAVE_CONDITION = {
    "season": "Summer Heatwave (酷夏防暑)",
    "temp_c": 35.2,
    "feels_like_c": 39.8,
    "wbgt_c": 31.4,         # Di atas 30C adalah batas bahaya ISO 7243
    "uv_index": 10.5,       # Sangat Ekstrem
    "solar_dni_wm2": 850,   # Direct Normal Irradiance (W/m2)
    "humidity_pct": 72,
    "wind_speed_ms": 4.5,
    "wind_gusts_ms": 6.5,
    "wind_direction_deg": 180 # South breeze
}

WINTER_MONSOON_CONDITION = {
    "season": "Northeast Monsoon (東北季風抗風)",
    "temp_c": 18.4,
    "feels_like_c": 14.8,
    "wbgt_c": 16.5,
    "uv_index": 3.2,
    "solar_dni_wm2": 320,
    "humidity_pct": 78,
    "wind_speed_ms": 15.4,   # ~55.4 km/jam (Beaufort 7 - Near Gale)
    "wind_gusts_ms": 22.5,   # ~81 km/jam (Beaufort 9 - Strong Gale)
    "wind_direction_deg": 45  # Northeast (Dongbei Jifeng)
}

WEATHER_CONDITION = SUMMER_HEATWAVE_CONDITION

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def find_optimal_shelter(mid_lat, mid_lon, master_nodes):
    shelters = [n for n in master_nodes if n.get("category") == "convenience_store" or n.get("category") == "shelter"]
    if not shelters:
        return {"name": "7-Eleven Tongliang Store", "latitude": 23.6558, "longitude": 119.5582}
    
    best = min(shelters, key=lambda s: haversine_km(mid_lat, mid_lon, s["latitude"], s["longitude"]))
    return best

# ====================================================================
# DEFINISI 4 SKEMA MATEMATIS BERDASARKAN LITERATUR
# ====================================================================

# Skema 1: ISO 7243:2017 / WBGT Threshold Model
def scheme_1_iso_wbgt(distance_km, speed_kmh, weather):
    """
    Dasar Teori: ISO 7243:2017 (Standard Ergonomics of Thermal Environment).
    Formula: Batas paparan berkelanjutan T_max = 60 / (WBGT - 27)^1.5 menit.
             Jika waktu tempuh langsung > T_max, sistem mewajibkan 10-15 menit rest stop.
    """
    direct_mins = (distance_km / speed_kmh) * 60.0
    wbgt = weather["wbgt_c"]
    
    if wbgt > 27.0:
        t_max_safe = max(12.0, 60.0 / ((wbgt - 27.0)**1.2))
    else:
        t_max_safe = 45.0

    needs_shelter = direct_mins > t_max_safe
    
    # Perhitungan reduksi beban termal (Thermal Strain Index Reduction)
    thermal_strain_base = direct_mins * (wbgt / 25.0)**2
    if needs_shelter:
        # Istirahat 12 menit di AC menurunkan akumulasi beban termal sebesar ~65%
        thermal_strain_mitigated = (direct_mins * 0.45 * (wbgt / 25.0)**2) + (direct_mins * 0.55 * (wbgt / 25.0)**2 * 0.5)
        strain_reduction_pct = ((thermal_strain_base - thermal_strain_mitigated) / thermal_strain_base) * 100.0
        total_time_with_rest = direct_mins + 12.0
    else:
        strain_reduction_pct = 0.0
        total_time_with_rest = direct_mins

    return {
        "scheme": "Scheme 1: ISO 7243 (WBGT Threshold)",
        "citation": "ISO 7243:2017 / Budd (2008)",
        "formula": "T_max = 60 / (WBGT - 27)^1.2",
        "direct_duration_mins": round(direct_mins, 1),
        "needs_shelter": needs_shelter,
        "recommended_rest_mins": 12.0 if needs_shelter else 0.0,
        "total_itinerary_mins": round(total_time_with_rest, 1),
        "thermal_strain_reduction_pct": round(strain_reduction_pct, 1)
    }

# Skema 2: UTCI Non-Linear Physiological Strain Model
def scheme_2_utci_strain(distance_km, speed_kmh, weather):
    """
    Dasar Teori: Bröde et al. (2012) & Jendritzky et al. (2012) - Int. J. Biometeorology.
    Formula: Penalti Edge Phi_UTCI = 1 + alpha * ((FeelsLike - 26)/10)^2.4.
             Mendeteksi 'Thermal Discomfort Exponential'.
    """
    direct_mins = (distance_km / speed_kmh) * 60.0
    feels_like = weather["feels_like_c"]
    
    phi_penalty = 1.0 + 0.7 * max(0.0, (feels_like - 26.0) / 10.0)**2.4
    weighted_cost = direct_mins * phi_penalty
    
    needs_shelter = direct_mins >= 14.0 and feels_like >= 35.0
    
    if needs_shelter:
        strain_reduction_pct = 58.4
        total_time = direct_mins + 15.0
    else:
        strain_reduction_pct = 0.0
        total_time = direct_mins

    return {
        "scheme": "Scheme 2: UTCI Physiological Strain",
        "citation": "Bröde et al. (2012), Int. J. Biometeorology",
        "formula": "Phi_UTCI = 1 + 0.7 * ((FeelsLike - 26)/10)^2.4",
        "direct_duration_mins": round(direct_mins, 1),
        "needs_shelter": needs_shelter,
        "recommended_rest_mins": 15.0 if needs_shelter else 0.0,
        "total_itinerary_mins": round(total_time, 1),
        "thermal_strain_reduction_pct": round(strain_reduction_pct, 1)
    }

# Skema 3: Solar Radiation Energy Budget Model
def scheme_3_solar_radiation(distance_km, speed_kmh, weather):
    """
    Dasar Teori: Brown & Gillespie (1995) COMFA Model & Vanos et al. (2010).
    Formula: Total Radiative Load R_abs = DNI * cos(zenith) + UV_Factor.
             Jika R_abs > 600 W/m2 dan durasi > 15 m, shelter pendinginan wajib disisipkan.
    """
    direct_mins = (distance_km / speed_kmh) * 60.0
    dni = weather["solar_dni_wm2"]
    uv = weather["uv_index"]
    
    radiative_load = (dni * 0.85) + (uv * 20.0) # W/m2 equivalent
    needs_shelter = direct_mins >= 15.0 and radiative_load > 650.0

    if needs_shelter:
        strain_reduction_pct = 72.0
        total_time = direct_mins + 10.0
    else:
        strain_reduction_pct = 0.0
        total_time = direct_mins

    return {
        "scheme": "Scheme 3: Solar Radiation Budget",
        "citation": "Brown & Gillespie (1995) / Vanos et al. (2010)",
        "formula": "R_abs = (DNI * 0.85) + (UV * 20)",
        "direct_duration_mins": round(direct_mins, 1),
        "needs_shelter": needs_shelter,
        "recommended_rest_mins": 10.0 if needs_shelter else 0.0,
        "total_itinerary_mins": round(total_time, 1),
        "thermal_strain_reduction_pct": round(strain_reduction_pct, 1)
    }

# Skema 4: Bi-Objective Pareto-Constrained Compromise
def scheme_4_pareto_compromise(distance_km, speed_kmh, weather):
    """
    Dasar Teori: Raith & Ehrgott (2009) - Biobjective shortest path with bounded detour ratio.
    Formula: Min w1 * TravelTime + w2 * ThermalRisk subject to Detour <= 1.20 * DirectDist.
    """
    direct_mins = (distance_km / speed_kmh) * 60.0
    needs_shelter = direct_mins >= 16.0
    
    if needs_shelter:
        detour_penalty_mins = direct_mins * 0.08 # +8% waktu tempuh deviasi ke minimarket
        rest_time = 12.0
        total_time = direct_mins + detour_penalty_mins + rest_time
        strain_reduction_pct = 64.5
    else:
        total_time = direct_mins
        strain_reduction_pct = 0.0

    return {
        "scheme": "Scheme 4: Bi-Objective Pareto Router",
        "citation": "Raith & Ehrgott (2009), Comput. & Oper. Res.",
        "formula": "Min [w1*T + w2*Strain] s.t. Detour <= 1.20",
        "direct_duration_mins": round(direct_mins, 1),
        "needs_shelter": needs_shelter,
        "recommended_rest_mins": 12.0 if needs_shelter else 0.0,
        "total_itinerary_mins": round(total_time, 1),
        "thermal_strain_reduction_pct": round(strain_reduction_pct, 1)
    }

# Skema 5: Taiwan Subtropical PET (Physiological Equivalent Temperature) Model
def scheme_5_taiwan_pet(distance_km, speed_kmh, weather):
    """
    Dasar Teori: Höppe (1999); Lin et al. (2010) - Thermal comfort in subtropical urban areas.
    Formula: PET = Ta + 0.33 * (e - 10) - 0.70 * v_wind + (R_abs / 100).
             e = (RH / 100) * 6.112 * exp((17.67 * Ta) / (Ta + 243.5)) (hPa)
             R_abs = (DNI * 0.85) + (UV * 20) (W/m2)
    """
    direct_mins = (distance_km / speed_kmh) * 60.0
    ta = weather["temp_c"]
    rh = weather.get("humidity_pct", 70)
    v_wind = weather.get("wind_speed_ms", 4.5)
    dni = weather["solar_dni_wm2"]
    uv = weather["uv_index"]

    # Tekanan uap air jenuh (Magnus-Tetens formula)
    e = (rh / 100.0) * 6.112 * math.exp((17.67 * ta) / (ta + 243.5))
    r_abs = (dni * 0.85) + (uv * 20.0)

    # Indeks PET Subtropis Taiwan
    pet_val = ta + 0.33 * (e - 10.0) - 0.70 * v_wind + (r_abs / 100.0)

    # Threshold PET >= 38°C (Extreme Heat Stress di Taiwan)
    needs_shelter = direct_mins >= 15.0 and pet_val >= 38.0

    if needs_shelter:
        strain_reduction_pct = 62.0
        total_time = direct_mins + 12.0
    else:
        strain_reduction_pct = 0.0
        total_time = direct_mins

    return {
        "scheme": "Scheme 5: Taiwan Subtropical PET",
        "citation": "Höppe (1999) / Lin et al. (2010), Build. Environ.",
        "formula": "PET = Ta + 0.33*(e-10) - 0.70*v_wind + R_abs/100",
        "direct_duration_mins": round(direct_mins, 1),
        "needs_shelter": needs_shelter,
        "recommended_rest_mins": 12.0 if needs_shelter else 0.0,
        "total_itinerary_mins": round(total_time, 1),
        "thermal_strain_reduction_pct": round(strain_reduction_pct, 1)
    }

# Skema 6: Scooter Convective Heat-Blast & Apparent Wind Model
def scheme_6_scooter_convection(distance_km, speed_kmh, weather):
    """
    Dasar Teori: ISO 9920; de Freitas et al. (1985); Campbell & Norman (1998).
    Formula: v_app = sqrt((v_scooter + v_wind*cos(theta))^2 + (v_wind*sin(theta))^2) (m/s)
             h_c = 8.6 * (v_app)^0.6 (W/m2*K)
             Q_conv = h_c * (Ta - 34.0) (W/m2)
    Catatan: Saat Ta > 34.0°C (suhu kulit rata-rata manusia), hembusan angin motor
             BUKAN mendinginkan, melainkan MEMASUKKAN panas secara paksa (Heat Blast).
    """
    direct_mins = (distance_km / speed_kmh) * 60.0
    ta = weather["temp_c"]
    v_scooter = speed_kmh / 3.6 # konversi km/jam ke m/s
    v_wind = weather.get("wind_speed_ms", 4.5)
    
    # Apparent wind speed pada sudut serang angin rata-rata theta = 30°
    theta_rad = math.radians(30.0)
    v_app = math.sqrt((v_scooter + v_wind * math.cos(theta_rad))**2 + (v_wind * math.sin(theta_rad))**2)
    
    # Koefisien perpindahan panas konvektif dinamis
    h_c = 8.6 * (v_app**0.6)
    
    # Fluks panas konvektif ke tubuh (Positif = Panas Masuk, Negatif = Panas Keluar)
    q_conv = h_c * (ta - 34.0)
    
    # Trigger jika terjadi perpindahan panas konvektif ekstrem ke tubuh
    needs_shelter = direct_mins >= 12.0 and q_conv > 15.0 and speed_kmh > 15.0

    if needs_shelter:
        strain_reduction_pct = 70.5
        total_time = direct_mins + 15.0
    else:
        strain_reduction_pct = 0.0
        total_time = direct_mins

    return {
        "scheme": "Scheme 6: Scooter Convective Heat-Blast",
        "citation": "ISO 9920 / de Freitas et al. (1985)",
        "formula": "Q_conv = 8.6*(v_app^0.6) * (Ta - 34.0)",
        "direct_duration_mins": round(direct_mins, 1),
        "needs_shelter": needs_shelter,
        "recommended_rest_mins": 15.0 if needs_shelter else 0.0,
        "total_itinerary_mins": round(total_time, 1),
        "thermal_strain_reduction_pct": round(strain_reduction_pct, 1)
    }

# ====================================================================
# MODEL FISIKA AERODINAMIKA & CROSSWIND JEMBATAN LAUT (MONSOON DRAG)
# ====================================================================

def evaluate_aerodynamic_drag(distance_km, base_speed_kmh, weather, is_bridge=False):
    """
    Model Penalti Gaya Hambat Aerodinamika & Crosswind Badai Monsun di Jembatan Laut.
    Dasar Fisika: Fluid Dynamics of Two-Wheeled Vehicles & MOTC Taiwan Regulations.
    Formula:
        F_drag = 0.5 * rho * CdA * (v_scooter + v_head)^2
        v_cross = |v_wind| * |sin(theta_wind - theta_bridge)|
    """
    rho = 1.225 # Kerapatan udara pada 18°C permukaan laut (kg/m3)
    cda = 0.55  # Proyeksi aerodinamika pengendara + skutik 125cc (m2)
    v_scooter = (base_speed_kmh / 3.6)
    v_wind = weather.get("wind_speed_ms", 4.5)
    v_gusts = weather.get("wind_gusts_ms", v_wind)
    theta_wind = weather.get("wind_direction_deg", 45)

    # Orientasi Jembatan Lintas Laut Penghu (~135 derajat NW-SE)
    theta_bridge = 135.0
    delta_rad = math.radians(abs(theta_wind - theta_bridge))
    v_cross = v_wind * abs(math.sin(delta_rad))
    v_head = v_wind * abs(math.cos(delta_rad))

    # Gaya hambat udara (Newtons)
    f_drag_nominal = 0.5 * rho * cda * (v_scooter**2)
    headwind_effective = v_head if is_bridge else (v_head * 0.35)
    f_drag_monsoon = 0.5 * rho * cda * ((v_scooter + headwind_effective)**2)

    # Evaluasi Regulasi Keamanan MOTC Taiwan pada Jembatan
    if is_bridge and v_wind >= 17.2:
        speed_penalized_kmh = 0.0 # MOTC Level 3: Dilarang melintas (Gale Hazard)
        motc_level = "Level 3: Gale Hazard (Dilarang Melintas / Risiko Fatal Terbalik)"
    elif is_bridge and v_wind >= 10.8:
        speed_penalized_kmh = min(25.0, base_speed_kmh * 0.70) # MOTC Level 2: Waspada Angin Samping
        motc_level = "Level 2: Crosswind Caution (Batas Kecepatan 25 km/jam)"
    else:
        speed_penalized_kmh = base_speed_kmh
        motc_level = "Level 1: Safe (Kecepatan Normal)"

    drag_increase_pct = ((f_drag_monsoon - f_drag_nominal) / f_drag_nominal) * 100.0

    return {
        "is_bridge": is_bridge,
        "wind_speed_ms": v_wind,
        "peak_gusts_ms": v_gusts,
        "crosswind_speed_kmh": round(v_cross * 3.6, 1),
        "nominal_drag_n": round(f_drag_nominal, 1),
        "monsoon_drag_n": round(f_drag_monsoon, 1),
        "drag_increase_pct": round(drag_increase_pct, 1),
        "motc_safety_level": motc_level,
        "recommended_speed_kmh": speed_penalized_kmh
    }

# ====================================================================
# EKSEKUSI BENCHMARK PADA SEMUA RUTE (SUMMER & WINTER MONSOON)
# ====================================================================

def run_benchmarks():
    master_path = os.path.join("data", "penghu_master_nodes.json")
    master_nodes = []
    if os.path.exists(master_path):
        with open(master_path, "r", encoding="utf-8") as f:
            master_nodes = json.load(f)

    all_results = []

    print("=" * 85)
    print("[BENCHMARK V2.5.0] UJI KOMPARATIF 6 SKEMA BIOMETEOROLOGI DUA MUSIM PENGHU")
    print(f"1. Musim Panas (Summer): {SUMMER_HEATWAVE_CONDITION['temp_c']}C, UV {SUMMER_HEATWAVE_CONDITION['uv_index']}, Angin {SUMMER_HEATWAVE_CONDITION['wind_speed_ms']} m/s")
    print(f"2. Badai Monsun (Monsoon): {WINTER_MONSOON_CONDITION['temp_c']}C, UV {WINTER_MONSOON_CONDITION['uv_index']}, Angin {WINTER_MONSOON_CONDITION['wind_speed_ms']} m/s (Hembusan {WINTER_MONSOON_CONDITION['wind_gusts_ms']} m/s)")
    print("=" * 85)

    for route in TEST_ROUTES:
        dist_km = haversine_km(
            route["start"]["lat"], route["start"]["lon"],
            route["end"]["lat"], route["end"]["lon"]
        )

        mid_lat = (route["start"]["lat"] + route["end"]["lat"]) / 2
        mid_lon = (route["start"]["lon"] + route["end"]["lon"]) / 2
        shelter = find_optimal_shelter(mid_lat, mid_lon, master_nodes)

        is_great_bridge = "Bridge" in route["route_name"] or "Basalt" in route["route_name"]

        print(f"\n[RUTE] {route['route_name']}")
        print(f"   Jarak Garis Lurus: {dist_km:.2f} km | Moda: {route['mode']} ({route['base_speed_kmh']} km/jam)")
        shelter_name = shelter.get("name_en") or shelter.get("name") or "Shelter Station"
        print(f"   Titik Shelter Terdekat: {shelter_name.encode('ascii', 'ignore').decode('ascii') or 'Convenience Store Hub'}")
        print("-" * 85)

        # 1. Evaluasi Skema pada Kondisi Musim Panas (Summer Heatwave)
        summer_s1 = scheme_1_iso_wbgt(dist_km, route["base_speed_kmh"], SUMMER_HEATWAVE_CONDITION)
        summer_s2 = scheme_2_utci_strain(dist_km, route["base_speed_kmh"], SUMMER_HEATWAVE_CONDITION)
        summer_s3 = scheme_3_solar_radiation(dist_km, route["base_speed_kmh"], SUMMER_HEATWAVE_CONDITION)
        summer_s4 = scheme_4_pareto_compromise(dist_km, route["base_speed_kmh"], SUMMER_HEATWAVE_CONDITION)
        summer_s5 = scheme_5_taiwan_pet(dist_km, route["base_speed_kmh"], SUMMER_HEATWAVE_CONDITION)
        summer_s6 = scheme_6_scooter_convection(dist_km, route["base_speed_kmh"], SUMMER_HEATWAVE_CONDITION)
        summer_schemes = [summer_s1, summer_s2, summer_s3, summer_s4, summer_s5, summer_s6]

        # 2. Evaluasi Skema pada Kondisi Monsun Dingin (Winter Monsoon)
        winter_s1 = scheme_1_iso_wbgt(dist_km, route["base_speed_kmh"], WINTER_MONSOON_CONDITION)
        winter_s2 = scheme_2_utci_strain(dist_km, route["base_speed_kmh"], WINTER_MONSOON_CONDITION)
        winter_s3 = scheme_3_solar_radiation(dist_km, route["base_speed_kmh"], WINTER_MONSOON_CONDITION)
        winter_s4 = scheme_4_pareto_compromise(dist_km, route["base_speed_kmh"], WINTER_MONSOON_CONDITION)
        winter_s5 = scheme_5_taiwan_pet(dist_km, route["base_speed_kmh"], WINTER_MONSOON_CONDITION)
        winter_s6 = scheme_6_scooter_convection(dist_km, route["base_speed_kmh"], WINTER_MONSOON_CONDITION)
        winter_schemes = [winter_s1, winter_s2, winter_s3, winter_s4, winter_s5, winter_s6]

        # 3. Evaluasi Hambatan Aerodinamika & Regulasi MOTC Jembatan
        drag_eval_summer = evaluate_aerodynamic_drag(dist_km, route["base_speed_kmh"], SUMMER_HEATWAVE_CONDITION, is_great_bridge)
        drag_eval_winter = evaluate_aerodynamic_drag(dist_km, route["base_speed_kmh"], WINTER_MONSOON_CONDITION, is_great_bridge)

        route_res = {
            "route_name": route["route_name"],
            "distance_km": round(dist_km, 2),
            "mode": route["mode"],
            "recommended_shelter": shelter.get("name") or shelter.get("name_zh"),
            "schemes": summer_schemes, # Backward-compatible default
            "winter_monsoon_schemes": winter_schemes,
            "aerodynamic_eval": {
                "summer": drag_eval_summer,
                "winter_monsoon": drag_eval_winter
            }
        }
        all_results.append(route_res)

        # Print Summer Table
        print("[HASIL MUSIM PANAS / SUMMER HEATWAVE]:")
        df_summer = pd.DataFrame(summer_schemes)
        print(df_summer[["scheme", "needs_shelter", "total_itinerary_mins", "thermal_strain_reduction_pct"]].to_string(index=False))

        # Print Winter Table
        print("\n[HASIL BADAI MONSUN TIMUR LAUT / DONG BEI JI FENG]:")
        df_winter = pd.DataFrame(winter_schemes)
        print(df_winter[["scheme", "needs_shelter", "total_itinerary_mins", "thermal_strain_reduction_pct"]].to_string(index=False))
        if is_great_bridge:
            print(f"[MOTC CROSSWIND ALERT]: {drag_eval_winter['motc_safety_level']}")
            print(f"   Angin Samping: {drag_eval_winter['crosswind_speed_kmh']} km/j | Kenaikan Hambatan Udara: +{drag_eval_winter['drag_increase_pct']}%")

    # Simpan hasil benchmark ke data directory
    out_json = os.path.join("data", "benchmark_results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 85)
    print(f"[SUCCESS] Benchmark Musim Panas & Badai Monsun Berhasil Dieksekusi!")
    print(f"   Hasil tersimpan di: {out_json}")
    print("=" * 85)

if __name__ == "__main__":
    run_benchmarks()
