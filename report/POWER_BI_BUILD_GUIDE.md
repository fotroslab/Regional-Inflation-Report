# راهنمای ساخت گزارش در Power BI Desktop — گام‌به‌گام (فارسی)

> نیازمند: **Power BI Desktop (ویندوز)**. خروجی این پروژه شامل `.pbix` نیست؛ این راهنما تنها سند اجرایی ساخت آن است.
> زمان تقریبی: ۳۰–۴۵ دقیقه. توصیه: قبل از انتشار، ارقام را با فایل اصلی data.gov.ir تطبیق دهید (VALIDATION.md).

## ۱) دریافت و آماده‌سازی داده
1. `Get Data → Text/CSV` و هر ۵ CSV پوشهٔ `data/` را وارد کنید:
   `fact_inflation_province`, `fact_inflation_urban_tir1404`, `national_inflation`, `national_urban_tir1404`, `dim_province`, `dim_period`.
2. در Power Query:
   - `dim_period`: نوع `jalali_year`/`jalali_month`/`months_in_period`/`sort_order` → عددی؛ `period_key` → متن؛ **Sort by Column**: `period_label` بر اساس `sort_order`.
   - `jalali_month` خالیِ سالانه‌ها را همان خالی بگذارید (null).
   - در `fact_inflation_province` ستون‌های عددی نوعِ Decimal بگذارید.
   - (اختیاری) برای نسخهٔ ماهانهٔ آتی: جدول `dim_month` را طبق «model/MODEL.md §۳» بسازید.
3. Encoding: UTF-8 (دارای فارسی) — در Import پیش‌نمایش، اگر فارسی خرابه بود، File Origin = 65001 انتخاب کنید.

## ۲) مدل و روابط
- روابط (یک‌به‌چند، single direction):
  `dim_province[province] → fact_inflation_province[province]`
  `dim_period[period_key] → fact_inflation_province[period_key]`
  `dim_province[province] → fact_inflation_urban_tir1404[province]`
  `dim_period[period_key] → national_inflation[period_key]`
- دو fact را مستقیماً به هم وصل **نکنید**.
- `national_urban_tir1404` را disconnected نگه دارید یا با `period_key = "1404-04"` به dim_period وصل کنید.
- View → Model view: چیدمان ستاره‌ای؛ dimها اطراف، factها وسط.

## ۳) معیارها (measure)
محتوای `model/measures.dax` را کپی کنید. حداقل‌ها:
`نرخ تورم سالانه`، `نرخ کشور`، `اختلاف با کشور`، `بیشترین/کمترین تورم استان`، `گسترهٔ استانی`، `رتبهٔ تورم استان`.
⚠️ این معیارها در موتور واقعی اجرا نشده‌اند؛ پس از Paste در Desktop خطاهای locale/نقطه‌ویرگول را اصلاح کنید (مثلاً اگر جداکنندهٔ آرگومانت سیستم شما `;` است).

## ۴) تم
`View → Themes → Browse for themes → report/theme.json`
تم «Regional Offline Fa»: پس‌زمینهٔ `#f7fafa`، سری‌ها teal/coral، فونت Vazirmatn (اگر سیستم فونت را نشناخت، Tahoma).

## ۵) نقشهٔ Shape Map (کمربند آفلاین — بدون tile)
1. `Insert → Visuals → Shape Map` (اگر در نسخهٔ شما Shape Map دیده نشد، از Visual Marketplace آفلاین یا filled map با GeoJSON استفاده کنید — ببینید §۷).
2. در Format → **Shape → + Add map** → فایل `data/iran_provinces.geojson` را انتخاب کنید. نقشهٔ استان‌های ایران بارگذاری می‌شود.
3. Fields:
   - **Location** = `dim_province[province]` (کلید انگلیسی) — باید با فیلد `name` داخل GeoJSON دقیقاً یکی باشد.
   - **Color saturation** = `[نرخ تورم سالانه]`
4. Format → Colors: گرادیان از `#e8f1f1` تا `#0f4c5c`؛ **Diverging** نکنید مگر اینکه بخواهید اختلاف با کشور را نشان دهید (آن‌وقت `#e3645f` برای بالاتر از کشور).
5. Format → Legend: عنوان «نرخ تورم سالانه»؛ متن «کمتر … بیشتر» راست‌چین.
6. Tooltip: `dim_province[name_persian]` + `[نرخ تورم سالانه]` + `dim_period[period_label]`.
7. مهم: هیچ Map tile/Azure Maps/Bing را فعال نکنید؛ Shape Map با GeoJSON داخلی کاملاً آفلاین رندر می‌شود.

## ۶) صفحات
1. **نمای کلی منطقه‌ای**: Shape Map + کارت‌های KPI (کشور / بالاترین / پایین‌ترین / گستره) + اسلایسر `dim_period[period_label]` (مرتب بر sort_order).
2. **رتبه‌بندی**: نمودار میله‌ای افقی ۳۱ استان، مرتب نزولی، خط مرجع کشور (dashed).
3. **روند**: خطی روی `dim_period[period_label]` (sort_order)؛ Legend → province؛ خط کشور dashed `#e3645f`. توجه: محور دسته‌ای است (۸ سالانه + ۲ ماهانه، فواصل نامنظم).
4. **دربارهٔ داده**: Text box با مأخذها/انتساب اجباری (SOURCES.md §۱) و هشدار دامنه (شهری در برابر کشور).

## ۷) اگر Shape Map در نسخهٔ Desktop شما نبود
- گزینهٔ جایگزین کاملاً آفلاین: **Filled Map با GeoJSON** هم نیازمند tile است → **استفاده نکنید**.
- بهترین جایگزین آفلاین: نمودار میله‌ای/TreeMap رتبه‌بندی (بدون نقشه) یا Import تصویر SVG استاتیک نقشه (از اپ این پروژه: `assets/preview.png`) با Bookmark/زر.
- Shape Map در نسخه‌های اخیر Power BI Desktop همچنان موجود است ولی گاهی زیر «More visuals» پنهان است — جستجو کنید.

## ۸) انتشار
- ذخیره به‌صورت `.pbix` در پوشهٔ پروژه (توسط شما؛ در این گزارش تولید نشد).
- اگر به Power BI Service می‌فرستید: Shape Map ممکن است در Service رندر متفاوت داشته باشد — قبل از تحویل تست کنید.
- چاپ/PDF: `File → Export → PDF` (فونت Vazirmatn باید روی سیستم مقصد نصب باشد، وگرنه Tahoma).

## ۹) چک آفلاین پس از ساخت
`report/OFFLINE_TEST.md` را مرحله‌به‌مرحله اجرا کنید (airplane mode + بازکردن Desktop + رندر هر ۴ صفحه).

## ۱۰) صداقت محتوا
- هیچ عددی از فروش/سفارش/تیکت در مدل نیست؛ اگر اضافه شد، گزارش معنای دیگری می‌گیرد و باید VALIDATION/README بازنوشت شود.
- انتساب نقشه (click_that_hood MIT + ODbL احتمالی OSM) در صفحهٔ «دربارهٔ داده» **الزامی** است.
