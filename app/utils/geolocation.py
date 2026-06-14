import math
from typing import List, Tuple

EARTH_RADIUS_KM = 6371.0

# KES pricing tiers for distance-based surcharge
_TIER1_KM = 5.0
_TIER1_RATE = 0.0    # free within 5 km
_TIER2_KM = 20.0
_TIER2_RATE = 10.0   # KES 10/km from 5–20 km
_TIER3_RATE = 15.0   # KES 15/km beyond 20 km


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in km between two GPS coordinates."""
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def bounding_box(lat: float, lon: float, radius_km: float) -> Tuple[float, float, float, float]:
    """Return (min_lat, max_lat, min_lon, max_lon) for a rough bounding box."""
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)))
    return lat - lat_delta, lat + lat_delta, lon - lon_delta, lon + lon_delta


def distance_surcharge(distance_km: float) -> float:
    """Calculate KES surcharge for a given pickup distance."""
    if distance_km <= _TIER1_KM:
        return 0.0
    elif distance_km <= _TIER2_KM:
        return (_TIER2_KM - _TIER1_KM) * _TIER2_RATE if distance_km >= _TIER2_KM else (distance_km - _TIER1_KM) * _TIER2_RATE
    else:
        tier2_charge = (_TIER2_KM - _TIER1_KM) * _TIER2_RATE
        tier3_charge = (distance_km - _TIER2_KM) * _TIER3_RATE
        return tier2_charge + tier3_charge


def adjusted_price(base_price: float, distance_km: float) -> float:
    return base_price + distance_surcharge(distance_km)
