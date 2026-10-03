from dataclasses import dataclass


@dataclass(frozen=True)
class IrrigationEstimate:
    recommended: bool
    deficit_mm: float
    effective_rain_mm: float
    net_water_m3: float
    assumptions: tuple[str, ...]


def estimate_irrigation(
    soil_moisture_pct: float,
    area_hectares: float,
    forecast_rain_mm: float,
    *,
    target_moisture_pct: float = 26.0,
    root_zone_depth_m: float = 0.3,
    effective_rain_fraction: float = 0.8,
) -> IrrigationEstimate:
    """Return a transparent demonstration estimate, not an irrigation prescription."""
    if not 0 <= soil_moisture_pct <= 100:
        raise ValueError("Soil moisture must be between 0 and 100 percent.")
    if area_hectares <= 0:
        raise ValueError("Field area must be greater than zero.")
    if forecast_rain_mm < 0:
        raise ValueError("Forecast rainfall cannot be negative.")
    if not 0 < effective_rain_fraction <= 1:
        raise ValueError("Effective rainfall fraction must be greater than 0 and at most 1.")

    moisture_deficit_pct = max(0.0, target_moisture_pct - soil_moisture_pct)
    gross_deficit_mm = moisture_deficit_pct * root_zone_depth_m * 10
    effective_rain_mm = forecast_rain_mm * effective_rain_fraction
    deficit_mm = max(0.0, gross_deficit_mm - effective_rain_mm)

    return IrrigationEstimate(
        recommended=soil_moisture_pct < target_moisture_pct and deficit_mm > 0,
        deficit_mm=round(deficit_mm, 1),
        effective_rain_mm=round(effective_rain_mm, 1),
        net_water_m3=round(deficit_mm * area_hectares * 10, 1),
        assumptions=(
            f"Demo target moisture: {target_moisture_pct:.0f}% (not field-calibrated).",
            f"Demo effective root zone: {root_zone_depth_m:.1f} m.",
            f"Estimated effective rainfall: {effective_rain_fraction:.0%} of forecast rainfall.",
            "Confirm soil type, crop stage and local advice before irrigating.",
        ),
    )