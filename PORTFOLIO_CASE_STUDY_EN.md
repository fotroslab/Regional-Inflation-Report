# Portfolio Case Study — Offline Regional Inflation Report for Iran (Project 04)

**Date:** 2026-11-26 · **Stack:** Python · Streamlit · pandas · plotly · Power BI (guide only, no .pbix) · Git
**Live demo:** Streamlit app on port 8505 · **License:** code MIT; map & data attributions below

## One-liner
A fully **offline**, Persian/RTL report that maps **official Iranian CPI inflation by province** — province-level annual CPI inflation for 2018–2025 plus two monthly snapshots (Jun & Jul 2026) — with internal GeoJSON, local fonts and zero runtime network calls.

## Why this project
Most "Iran map" dashboards lean on online basemap tiles (violating air-gap policies) or on made-up sales figures. Project 04 proves the opposite workflow: an offline-safe, honesty-first report built from **official statistics** (Statistical Center of Iran), rendered 100% locally, with every limitation written down.

## Data (honest sourcing)
- **Primary series — Annual CPI inflation by province (all households):** 31 provinces × 10 periods = 310 rows; 1397–1404 annual averages plus خرداد/تیر 1405 monthly-year rates. Source: Statistical Center of Iran (CPI, base year 1400=100), republished by irangaah.ir documented to data.gov.ir (Iran Open Data Portal). Transcribed manually → transcription risk documented, cross-check with the official file required before professional publication.
- **Supplementary table — July 2025 / Tir 1404 (urban households):** price index + monthly / YoY / annual inflation; shown with scope labeled "خانوارهای شهری" and never blended with the all-household series. Source: Statistical Center of Iran via the public preview preview table on iranstatis.com (user-approved unofficial mirror). The full monthly provincial archive is paywalled and was not used.
- **Boundaries:** click_that_hood `iran-provinces.geojson` — real geometry, MIT © Code for America; coordinates rounded to 3 decimals; underlying geometry may be ODbL © OpenStreetMap contributors. Mandatory attribution kept in every document.
- **Prior version** (synthetic sales/orders/tickets, seed=14030404) was retired entirely; no synthetic numbers remain anywhere in the project.

## What was built
1. **Streamlit app (4 pages, FA/RTL, Vazirmatn embedded as base64 WOFF2):**
   1. Regional overview — internal-projection SVG choropleth, KPI strip (national rate, top/bottom province, max–min spread), «کمتر…بیشتر» legend.
   2. Province ranking — all 31 provinces, national-average dashed line, coral = above national.
   3. Historical trend — 10-period line chart for selectable provinces vs the national dashed reference.
   4. About the data & map — full attribution, scope warnings, limitations.
2. **Star model for Power BI** (`model/MODEL.md`, `model/measures.dax`): `dim_period` + `dim_province` + fact tables; measures for national delta, rank, min/max, above-national flag. `report/POWER_BI_BUILD_GUIDE.md` walks through a Shape Map build with the internal GeoJSON.
3. **Quality gates:** 23 unittest controls (row counts, 31/31 key match CSV↔GeoJSON, MultiPolygon checks, national-inside-province-range for all 10 periods, period-type/month-domain checks), AppTest for all 4 pages × both data scopes, real screenshots via headless Chromium.
4. **Docs:** README_FA, VALIDATION (tested vs untested, explicitly honest), LIMITATIONS, SOURCES (attribution + mirror-access notes), data dictionary & auto-generated quality report.

## Engineering notes
- **Zero external requests at runtime** — map is projected in-process (equirectangular + cos(φ) latitude correction) from local GeoJSON; fonts local; Plotly figures configured with `.js-plotly-plot{direction:ltr}` while the page stays RTL.
- **Honest scoping:** annual vs monthly cadence is labeled on axes; national pace is shown as a reference line, not merged into provincial averages; mean-of-provinces ≠ national rate (basket weights) — documented.
- **Key discipline:** the join key is GeoJSON `name` (English) everywhere; a rename breaks the map visibly (tested 31/31).

## Screenshots
`assets/preview.png` (overview) · `assets/preview_ranking.png` (ranking) — captured from the live app (port 8505, 1760×1100).

## Limitations (explicit)
- Figures were transcribed manually from mirrors of official tables — **independent cross-check against the canonical data.gov.ir file is pending** (see VALIDATION.md). amar.org.ir is unreachable from this environment.
- No uniform monthly provincial series (needs paid iranstatis subscription); trend chart mixes 8 annual points + 2 monthly snapshots (irregular spacing, categorical axis).
- No physical internet-cut test; Shape Map rendering in Power BI Desktop not tested; DAX measures not executed in a real engine; no `.pbix` delivered.
- Boundaries are approximate (3-decimal rounding); not legal/cadastral; islands not rendered.
- Illustrative 5-region grouping — not official administrative geography.

## Impact / takeaways
- Demonstrates the full "offline-first + honesty-first" BI workflow: real official data, offline rendering, custom GeoJSON pipeline, automated quality gates, and docs that say what was *not* tested.
- Reusable template for air-gapped BI portfolios: local fonts, local GeoJSON, embedded theme, AppTest + screenshot gates.

## Attribution (mandatory)
Boundaries: click_that_hood (MIT License) — simplified; © OpenStreetMap contributors may apply (ODbL) for underlying boundaries. Data: Statistical Center of Iran (via irangaah.ir documented to data.gov.ir, and the Tir 1404 urban preview on iranstatis.com). Font: Vazirmatn (SIL OFL 1.1).
