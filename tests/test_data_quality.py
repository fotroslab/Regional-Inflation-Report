# -*- coding: utf-8 -*-
"""کنترل کیفیت داده‌های پروژه — نرخ تورم استان‌های ایران.
اجرا: python3 -m unittest discover -s tests -v
"""
import csv
import json
import math
import unittest
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
GEOJSON = DATA / "iran_provinces.geojson"
GEOJSON_RAW = DATA / "iran_provinces_raw.geojson"

JALALI_MONTH_NAMES = {1:"فروردین",2:"اردیبهشت",3:"خرداد",4:"تیر",5:"مرداد",6:"شهریور",
                      7:"مهر",8:"آبان",9:"آذر",10:"دی",11:"بهمن",12:"اسفند"}

class TestGeoJSON(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gj = json.loads(GEOJSON.read_text(encoding="utf-8"))

    def test_feature_count_31(self):
        self.assertEqual(len(self.gj["features"]), 31)

    def test_all_multipolygon(self):
        for f in self.gj["features"]:
            self.assertEqual(f["geometry"]["type"], "MultiPolygon")

    def test_properties_complete(self):
        for f in self.gj["features"]:
            self.assertIn("name", f["properties"])
            self.assertIn("name_persian", f["properties"])

    def test_keys_unique(self):
        names = [f["properties"]["name"] for f in self.gj["features"]]
        self.assertEqual(len(names), len(set(names)))

    def test_coordinates_in_iran_bounds_and_rounded(self):
        for f in self.gj["features"]:
            for poly in f["geometry"]["coordinates"]:
                for ring in poly:
                    for pt in ring:
                        lon, lat = pt[0], pt[1]
                        self.assertTrue(43.5 <= lon <= 64.0, (f["properties"]["name"], lon))
                        self.assertTrue(24.5 <= lat <= 40.0, (f["properties"]["name"], lat))
                        self.assertEqual(round(lon, 3), lon)
                        self.assertEqual(round(lat, 3), lat)

    def test_raw_copy_exists_and_is_multipolygon(self):
        raw = json.loads(GEOJSON_RAW.read_text(encoding="utf-8"))
        self.assertEqual(len(raw["features"]), 31)

class TestFactInflationProvince(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.read_csv(DATA / "fact_inflation_province.csv")

    def test_row_count_310(self):  # 31 استان × 10 دوره
        self.assertEqual(len(self.df), 310)

    def test_31_provinces_10_periods(self):
        self.assertEqual(self.df.province.nunique(), 31)
        self.assertEqual(self.df.period_key.nunique(), 10)
        counts = self.df.groupby("province").size()
        self.assertTrue((counts == 10).all())

    def test_uniqueness_province_period(self):
        self.assertFalse(self.df.duplicated(subset=["province", "period_key"]).any())

    def test_period_types_and_months(self):
        for _, r in self.df.iterrows():
            if r.period_type == "سالانه":
                self.assertTrue(pd.isna(r.jalali_month) or r.jalali_month == "")
                self.assertEqual(r.months_in_period, 12)
                self.assertIn(str(r.jalali_year).translate(str.maketrans("0123456789","۰۱۲۳۴۵۶۷۸۹")), r.period_label)
            else:
                self.assertEqual(r.period_type, "ماهانه")
                self.assertIn(int(r.jalali_month), (3, 4))
                self.assertEqual(r.months_in_period, 1)
                self.assertIn(JALALI_MONTH_NAMES[int(r.jalali_month)], r.period_label)

    def test_jalali_year_range_and_month_domain(self):
        self.assertTrue(self.df.jalali_year.between(1397, 1405).all())
        months = self.df.jalali_month.dropna().astype(int)
        self.assertTrue(months.between(1, 12).all())

    def test_values_positive_finite_and_below_100(self):
        v = self.df.inflation_annual_pct
        self.assertTrue(v.notna().all())
        self.assertTrue((v > 0).all() and (v < 100).all())

    def test_labels_month_names(self):
        m = self.df[self.df.period_type == "ماهانه"]
        for _, r in m.iterrows():
            self.assertIn(JALALI_MONTH_NAMES[int(r.jalali_month)], r.period_label)

    def test_province_keys_match_geojson(self):
        gj_keys = {f["properties"]["name"] for f in json.loads(GEOJSON.read_text(encoding="utf-8"))["features"]}
        self.assertEqual(set(self.df.province.unique()), gj_keys)

    def test_persian_names_match_dim(self):
        dim = pd.read_csv(DATA / "dim_province.csv")
        dim_map = dict(zip(dim.province, dim.name_persian))
        for _, r in self.df.iterrows():
            self.assertEqual(dim_map[r.province], r.province_fa)

class TestUrbanTir1404(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.read_csv(DATA / "fact_inflation_urban_tir1404.csv")

    def test_row_count_and_unique(self):
        self.assertEqual(len(self.df), 31)
        self.assertFalse(self.df.duplicated(subset=["province"]).any())

    def test_values_in_sane_ranges(self):
        self.assertTrue(self.df.cpi_index.between(200, 600).all())
        for col in ["inflation_monthly_pct", "inflation_yoy_pct", "inflation_annual_pct"]:
            self.assertTrue(self.df[col].gt(0).all() and self.df[col].lt(150).all())

    def test_keys_match_geojson(self):
        gj_keys = {f["properties"]["name"] for f in json.loads(GEOJSON.read_text(encoding="utf-8"))["features"]}
        self.assertEqual(set(self.df.province.unique()), gj_keys)

class TestNationalReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nat = pd.read_csv(DATA / "national_inflation.csv")
        cls.fact = pd.read_csv(DATA / "fact_inflation_province.csv")
        cls.nat_u = pd.read_csv(DATA / "national_urban_tir1404.csv")
        cls.urban = pd.read_csv(DATA / "fact_inflation_urban_tir1404.csv")

    def test_national_periods(self):
        self.assertEqual(len(self.nat), 10)
        self.assertEqual(set(self.nat.period_key), set(self.fact.period_key))

    def test_national_within_province_range(self):
        for p, g in self.fact.groupby("period_key"):
            nat = float(self.nat.loc[self.nat.period_key == p, "inflation_annual_pct"].iloc[0])
            self.assertGreaterEqual(nat, g.inflation_annual_pct.min() - 1e-9, p)
            self.assertLessEqual(nat, g.inflation_annual_pct.max() + 1e-9, p)

    def test_national_urban_within_range(self):
        u = self.nat_u.iloc[0]
        for col, col_u in [("cpi_index","cpi_index"),("inflation_monthly_pct","inflation_monthly_pct"),
                           ("inflation_yoy_pct","inflation_yoy_pct"),("inflation_annual_pct","inflation_annual_pct")]:
            self.assertGreaterEqual(float(u[col]), self.urban[col_u].min() - 1e-9)
            self.assertLessEqual(float(u[col]), self.urban[col_u].max() + 1e-9)

class TestDims(unittest.TestCase):
    def test_dim_province(self):
        dim = pd.read_csv(DATA / "dim_province.csv")
        self.assertEqual(len(dim), 31)
        self.assertTrue(dim.province.is_unique)
        self.assertTrue(dim.region_fa.isin(["شمال","جنوب","شرق","غرب","مرکز"]).all())
        self.assertTrue((dim.groupby("region_fa").size() >= 3).all())

    def test_dim_period_sort(self):
        dp = pd.read_csv(DATA / "dim_period.csv")
        self.assertEqual(len(dp), 10)
        self.assertEqual(dp.period_key.nunique(), 10)
        self.assertTrue(dp.sort_order.is_unique)
        self.assertEqual(dp.sort_order.tolist(), list(range(1, 11)))

if __name__ == "__main__":
    unittest.main()
