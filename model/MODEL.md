# مدل داده (MODEL) — پروژهٔ ۴ | ستاره‌ای، با بعد دورهٔ غیرمعمول (سالانه + ماهانه)

> نکته: این مدل به‌جای fact ماهانهٔ یکنواخت، **ترکیب ۸ دورهٔ سالانه + ۲ ماهانه** را در یک fact واحد نگه می‌دارد؛ برای تحلیل در Power BI، اسلایسر `period_type` و مرتب‌سازی بر `sort_order` الزامی است.

## ۱) موجودیت‌ها

### dim_province (۱ ردیف به‌ازای استان؛ PK = province)
| ستون | نوع | توضیح |
| --- | --- | --- |
| province | text | کلید انگلیسی (مثلاً `Tehran`) — کلید Join با نقشه |
| name_persian | text | برچسب فارسی نمایشی |
| region_fa / region_en | text | تقسیم‌بندی نمایشی شمال/جنوب/شرق/غرب/مرکز (نه رسمی) |

### dim_period (PK = period_key)
| ستون | نوع | توضیح |
| --- | --- | --- |
| period_key | text | `1397`…`1404` یا `1405-03`/`1405-04` |
| period_label | text | برچسب فارسی (خرداد ۱۴۰۵ و …) |
| period_type | text | سالانه / ماهانه |
| jalali_year | int64 | ۱۳۹۷–۱۴۰۵ |
| jalali_month | int64 (nullable) | فقط دوره‌های ماهانه: ۳/۴ |
| months_in_period | int64 | ۱۲ سالانه / ۱ ماهانه |
| sort_order | int64 | ۱..۱۰ — مبنای Sort by Column برای period_label |

### fact_inflation_province (Grain: استان × دوره؛ FKها province و period_key)
`inflation_annual_pct` — نرخ تورم سالانه (٪).

### fact_inflation_urban_tir1404 (Grain: استان؛ FK province)
`cpi_index` (شاخص قیمت، پایه ۱۴۰۰)، `inflation_monthly_pct`، `inflation_yoy_pct`، `inflation_annual_pct` — **خانوارهای شهری، تیر ۱۴۰۴**.

### national_inflation (مرجع کل کشور؛ FK period_key → dim_period) — ۱۰ ردیف
### national_urban_tir1404 (مرجع کل کشور شهری) — ۱ ردیف؛ جدول کمکی، بدون رابطه یا با رابطه به dim_period روی period_key

## ۲) روابط (cardinality یک‌به‌چند، single-direction)

```
dim_province 1 ─── * fact_inflation_province * ─── 1 dim_period
dim_province 1 ─── * fact_inflation_urban_tir1404
dim_period   1 ─── * national_inflation
```

اصل فیلترینگ: فیلتر از dim_province/dim_period به factها. Cross-filter از fact به dim ممنوع (bidirectional استفاده نکنید).

## ۳) dim_month در Power Query (برای نسخهٔ ماهانهٔ آتی)
اگر بعداً بانک ماهانهٔ کامل (اشتراکی) تهیه شد، یک جدول `dim_month` با این ستون‌ها در PQ بسازید:
```
period_key = Text.From([jalali_year]) & "-" & Text.PadStart(Text.From([jalali_month]), 2, "0")
period_label = ماه شمسی + سال، is_month_end، فصل شمسی، sort_key = jalali_year*100 + jalali_month
```
سپس `Sort by Column: period_label` روی `sort_key`. تا آن زمان dim_period کافی است.

## ۴) نکات مدل‌سازی برای Power BI
- `national_inflation` به‌عنوان **جدول مرجع** (disconnected یا متصل به dim_period روی period_key) استفاده می‌شود تا measure «اختلاف با کشور» از طریق TREATAS یا رابطه ساده کار کند.
- برای نقشه (Shape Map) بعد استانِ fact لازم نیست؛ Shape خودش کلید `name` را می‌خواهد — `Dim Province[province]` را در Location بگذارید و `inflation_annual_pct` را در Color saturation.
- اندازه‌گیری «گسترهٔ استانی» = MAX − MIN در context دورهٔ انتخابی.
- Active relationships فقط همین موارد بالا؛ هیچ relationship غیرمستقیمی بین دو fact نسازید (factها روی dim_province/dim_period متحد می‌شوند).
- Aggregation modes: همه Import (داده کوچک ≤ ۳۵۰ ردیف؛ DirectQuery بی‌مورد است).

## ۵) صداقت داده در مدل
هیچ ستون فروش/سفارش/تیکت وجود ندارد؛ اگر کسی چنین ستون‌هایی اضافه کند، مدل سکوتاً معنای دیگری می‌گیرد. هر تغییر CSV باید با `tests/test_data_quality.py` دوباره چک شود و VALIDATION.md به‌روز شود.
