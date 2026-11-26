<div dir="rtl">
<style>pre,code,kbd,samp{direction:ltr;text-align:left;unicode-bidi:embed}</style>

# فرهنگ داده (DATA_DICTIONARY) — پروژهٔ ۴

> واحد نرخ‌های تورم: **درصد (٪)** | واحد شاخص قیمت: عدد (سال پایه ۱۴۰۰=۱۰۰) | رمزینگ `province` همیشه انگلیسی (کلید Join با GeoJSON).

## ۱) `fact_inflation_province.csv` — واقعیت اصلی (خانوارهای کشور)
| ستون | نوع | توضیح |
| --- | --- | --- |
| province | string (key) | کلید انگلیسی استان مطابق GeoJSON (مثلاً `Tehran`) |
| province_fa | string | نام فارسی استان (مطابق منبع) |
| period_key | string | کلید دوره: `۱۳۹۷`…`۱۴۰۴` (سالانه) یا `1405-03`/`1405-04` (ماهانه) — ASCII |
| period_label | string | برچسب فارسی نمایشی (مثلاً «تیر ۱۴۰۵») |
| period_type | string | `سالانه` یا `ماهانه` |
| jalali_year | int | سال شمسی (۱۳۹۷–۱۴۰۵) |
| jalali_month | int یا خالی | فقط برای دوره‌های ماهانه: ۳ خرداد، ۴ تیر (خالی برای سالانه) |
| months_in_period | int | ۱۲ برای سالانه، ۱ برای ماهانه |
| inflation_annual_pct | float | **نرخ تورم سالانهٔ استان (٪)** — تغییر میانگین ۱۲ ماه منتهی به دوره نسبت به دورهٔ مشابه قبل |

Grain: یک ردیف به‌ازای (استان × دوره). ۳۱۰ ردیف.

## ۲) `fact_inflation_urban_tir1404.csv` — جدول مکمل (خانوارهای شهری، تیر ۱۴۰۴)
| ستون | نوع | توضیح |
| --- | --- | --- |
| province | string (key) | مطابق GeoJSON |
| province_fa | string | نام فارسی |
| period_key | string | `1404-04` |
| period_label | string | «تیر ۱۴۰۴ (شهری)» |
| period_type | string | `ماهانه` |
| cpi_index | float | شاخص قیمت مصرف‌کننده (پایه ۱۴۰۰) |
| inflation_monthly_pct | float | تورم ماهانه (تیر ۱۴۰۴ نسبت به خرداد ۱۴۰۴) |
| inflation_yoy_pct | float | تورم نقطه‌به‌نقطه (تیر ۱۴۰۴ نسبت به تیر ۱۴۰۳) |
| inflation_annual_pct | float | تورم سالانهٔ منتهی به تیر ۱۴۰۴ |

Grain: استان. ۳۱ ردیف. **دامنه: خانوارهای شهری — با جدول ۱ هم‌جنس نیست.**

## ۳) `national_inflation.csv` — مرجع کل کشور (هم‌راستا با جدول ۱)
`period_key, period_label, period_type, jalali_year, jalali_month, inflation_annual_pct` — ۱۰ ردیف.

## ۴) `national_urban_tir1404.csv` — مرجع کل کشور (هم‌راستا با جدول ۲)
`period_key, period_label, cpi_index, inflation_monthly_pct, inflation_yoy_pct, inflation_annual_pct` — ۱ ردیف (کل کشور: ۳۵۸٫۰۲ | ۳٫۴۲ | ۴۰٫۷۱ | ۳۵٫۳۲).

## ۵) `dim_province.csv` — بعد استان
`province (PK), name_persian, region_fa, region_en` — تقسیم‌بندی منطقه‌ای **نمایشی** (شمال/جنوب/شرق/غرب/مرکز)، نه جغرافیای رسمی. ۳۱ ردیف.

## ۶) `dim_period.csv` — بعد دوره
`period_key (PK), period_label, period_type, jalali_year, jalali_month, months_in_period, sort_order` — ترتیب زمانی ۱..۱۰ (۸ سالانه سپس خرداد و تیر ۱۴۰۵).

## ۷) `iran_provinces.geojson` / `iran_provinces_raw.geojson`
۳۱ Feature MultiPolygon؛ خواص: `name` (کلید) و `name_persian`. نسخهٔ ساده‌شده مختصات را به ۳ رقم گرد کرده است. انتساب اجباری: click_that_hood (MIT) + احتمال ODbL © OpenStreetMap.

## ۸) قواعد پیوند (Join)
- `fact.province = dim_province.province = GeoJSON.properties.name` (حتماً انگلیسی).
- `fact.period_key = dim_period.period_key`؛ `national_inflation.period_key = dim_period.period_key`.
- فارسی: `fact.province_fa ≡ dim_province.name_persian` (با املای کردستان/کردستان یکسان‌سازی شده).

## ۹) نکات تفسیری
- خالی‌بودن `jalali_month` برای سالانه‌ها عمدی است؛ در pandas به‌صورت NaN دیده می‌شود.
- ۱۴۰۵: نرخ «سالانه» منتهی به آن ماه است؛ نه میانگین سال ۱۴۰۵.
- میانگین سادهٔ استانی ≠ نرخ کشور؛ برای خط مرجع کشور از `national_inflation` استفاده کنید.

</div>
