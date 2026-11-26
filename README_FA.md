# پروژهٔ ۴ — گزارش آفلاین تورم استان‌های ایران 🗺️

> تاریخ: ۱۴۰۵/۰۹/۰۵ (۲۰۲۶-11-26) | پوشه: `project_04_regional_offline_map/` | اپ زندهٔ این محیط: **پورت ۸۵۰۵**
> این نسخه با **دادهٔ واقعی آمار تورم (مرکز آمار ایران)** ساخته شده است؛ نسخهٔ قبلی با دادهٔ فروش ساختگی کنار گذاشته شد.

## این پروژه چیست؟

نمونه‌کاری از یک **گزارش گرافیکی کاملاً آفلاین** برای Power BI / ارائهٔ رزومه: نقشهٔ Choropleth استان‌های ایران + رتبه‌بندی و روند نرخ تورم، با دادهٔ رسمی آمار تورم مرکز آمار ایران — بدون هیچ tile، CDN یا تماس شبکه در زمان اجرا.

- **هندسهٔ نقشه:** `click_that_hood` (MIT) — واقعی، ساده‌شده، انتساب اجباری همراه (رجوع کنید به SOURCES.md).
- **اعداد:** نرخ تورم سالانهٔ **خانوارهای کشور** به تفکیک ۳۱ استان، ۱۳۹۷ تا تیر ۱۴۰۵ (۱۰ دوره) — مأخذ: مرکز آمار ایران (بازنشر irangaah.ir مستند به data.gov.ir)؛ به‌همراه جدول مکمل تیر ۱۴۰۴ **خانوارهای شهری** (شاخص قیمت، ماهانه، نقطه‌ای، سالانه) — مأخذ: مرکز آمار ایران (پیش‌نمایش iranstatis.com؛ آینهٔ غیررسمی مورد تأیید شما).
- **فارسی/RTL**، فونت Vazirmatn جاسازی‌شده (OFL)، اعداد فارسی، تم «Regional Offline Fa» (`#0f4c5c` غالب + `#e3645f` تأکید روی `#f7fafa`).

## اجرا (اپ پیش‌نمایش)

```bash
cd project_04_regional_offline_map
pip install -r requirements.txt
streamlit run app.py --server.port 8505
```

صفحات: **۱) نمای کلی منطقه‌ای** (نقشه + KPI) • **۲) رتبه‌بندی استان‌ها** • **۳) روند تاریخی (۱۳۹۷–تیر ۱۴۰۵)** • **۴) دربارهٔ داده و نقشه**. فیلتر دامنه: «خانوارهای کشور» یا «شهری تیر ۱۴۰۴». هیچ درخواست شبکه‌ای انجام نمی‌شود.

## تست‌ها

```bash
python3 -m unittest discover -s tests -v   # ۲۳ تست — همه سبز
python3 -m json.tool report/theme.json > /dev/null   # اعتبار JSON تم
```

جزئیات: `VALIDATION.md` (شامل موارد تست‌نشده) و `report/OFFLINE_TEST.md`.

## ساختار پروژه

```
project_04_regional_offline_map/
├── app.py                     # اپ Streamlit (۴ صفحه، FA/RTL، نقشهٔ SVG داخلی)
├── requirements.txt
├── README_FA.md               # همین فایل
├── PORTFOLIO_CASE_STUDY_EN.md # مطالعهٔ موردی انگلیسی
├── VALIDATION.md / LIMITATIONS.md / SOURCES.md
├── data/
│   ├── iran_provinces.geojson          # ۳۱ Feature، ساده‌شده (۳رقم اعشار)
│   ├── iran_provinces_raw.geojson      # بدون ساده‌سازی
│   ├── fact_inflation_province.csv     # ۳۱۰ ردیف: ۳۱×۱۰ دوره (خانوارهای کشور)
│   ├── fact_inflation_urban_tir1404.csv# ۳۱ ردیف (خانوارهای شهری، تیر ۱۴۰۴)
│   ├── national_inflation.csv          # مرجع کل کشور (۱۰ دوره)
│   ├── national_urban_tir1404.csv      # مرجع کل کشور (شهری)
│   ├── dim_province.csv / dim_period.csv
│   ├── DATA_DICTIONARY.md / QUALITY_REPORT.md
├── model/
│   ├── MODEL.md               # مدل ستاره‌ای + روابط + dim_month در PQ
│   ├── measures.dax           # معیارهای DAX (بازبینی‌شده، اجرا نشده)
│   └── model_diagram.svg
├── report/
│   ├── POWER_BI_BUILD_GUIDE.md# ساخت Shape Map در Desktop گام‌به‌گام
│   ├── OFFLINE_TEST.md        # چک‌لیست آفلاین‌بودن
│   └── theme.json             # «Regional Offline Fa»
├── tests/test_data_quality.py # ۲۳ کنترل
└── assets/
    ├── preview.png            # اسکرین‌شات واقعی — نمای کلی (اپ زنده، پورت ۸۵۰۵)
    ├── preview_ranking.png    # اسکرین‌شات — رتبه‌بندی استان‌ها
    ├── preview_trend.png      # اسکرین‌شات — روند تاریخی
    └── fonts/Vazirmatn-*.woff2
```

## داده — صادقانه

| سؤال | پاسخ |
| --- | --- |
| آیا اعداد «واقعی» هستند؟ | **آمار رسمی تورم مرکز آمار ایران‌اند** ولی با رونویسی دستی از آینه‌های غیررسمی وارد شده‌اند؛ تطبیق با فایل اصلی data.gov.ir انجام نشده (رجوع کنید به VALIDATION.md). |
| چرا دوره‌ها نامنظم‌اند؟ | سری ماهانهٔ استانی فقط با اشتراک پولی iranstatis در دسترس است؛ سری رایگان: ۸ سالانه + ۲ ماهانه (خرداد/تیر ۱۴۰۵). |
| فروش/سفارش/تیکت کجاست؟ | **حذف شد.** نسخهٔ قدیمی با آن ساختگی بود و نباید به آن استناد کرد. |
| مجوز نقشه؟ | click_that_hood — MIT؛ هندسهٔ زیرین ممکن است ODbL © OSM. انتساب حذف نشود. |
| کاربرد حقوقی؟ | خیر؛ نقشه و داده صرفاً آماری/تحلیلی‌اند. |

## مسیر تکمیل (Roadmap)

1. **تطبیق ارقام با فایل اصلی data.gov.ir یا PDF رسمی مرکز آمار** (الزامی برای انتشار).
2. در صورت دسترسی به amar.org.ir از شبکهٔ داخلی: جایگزینی منبع به مرجع رسمی.
3. ساخت فایل `.pbix` طبق `report/POWER_BI_BUILD_GUIDE.md` و تست Shape Map در Power BI Desktop (نیازمند ویندوز).
4. افزودن سری ماهانهٔ کامل در صورت تهیهٔ اشتراک iranstatis (اختیاری).

## مجوز و انتساب

- کد این پروژه: MIT (آزاد برای استفادهٔ نمونه‌کار/آموزشی).
- نقشه: Boundaries: click_that_hood (MIT License) — simplified; © OpenStreetMap contributors may apply (ODbL) for underlying boundaries.
- داده: مرکز آمار ایران؛ بازنشر: irangaah.ir (مستند به data.gov.ir) و پیش‌نمایش iranstatis.com — ببینید SOURCES.md. ارقام متعلق به مرکز آمار ایران است.
- فونت Vazirmatn: SIL OFL 1.1.
