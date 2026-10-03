import unittest

from tools.calculators import estimate_irrigation


class IrrigationEstimateTests(unittest.TestCase):
    def test_dry_field_estimates_water_with_explicit_rainfall_adjustment(self):
        estimate = estimate_irrigation(soil_moisture_pct=20, area_hectares=1, forecast_rain_mm=0)

        self.assertTrue(estimate.recommended)
        self.assertEqual(estimate.deficit_mm, 18.0)
        self.assertEqual(estimate.net_water_m3, 180.0)
        self.assertEqual(estimate.effective_rain_mm, 0.0)
        self.assertTrue(estimate.assumptions)

    def test_forecast_rain_can_remove_estimated_deficit(self):
        estimate = estimate_irrigation(soil_moisture_pct=20, area_hectares=1, forecast_rain_mm=30)

        self.assertFalse(estimate.recommended)
        self.assertEqual(estimate.deficit_mm, 0.0)
        self.assertEqual(estimate.net_water_m3, 0.0)

    def test_rejects_invalid_field_area(self):
        with self.assertRaises(ValueError):
            estimate_irrigation(soil_moisture_pct=20, area_hectares=0, forecast_rain_mm=0)


if __name__ == "__main__":
    unittest.main()