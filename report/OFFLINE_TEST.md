<div dir="rtl">
<style>pre,code,kbd,samp{direction:ltr;text-align:left;unicode-bidi:embed}</style>

# چک‌لیست تست آفلاین (OFFLINE_TEST) — پروژهٔ ۴

> هدف: اطمینان از اینکه بازکردن/رندر گزارش **هیچ درخواست شبکه‌ای** نمی‌سازد.
> اجرا در: ویندوز (برای .pbix/Desktop) و لینوکس/مک (برای اپ Streamlit).

## الف) اپ Streamlit (این پروژه)
1. تله‌متری خاموش است: `.streamlit/config.toml` شامل `gatherUsageStats = false` است؛ در لاگ راه‌اندازی نباید خط «Collecting usage statistics» دیده شود و نباید هیچ درخواستی به `data.streamlit.io` برود. به‌علاوه `.gitignore` فایل `.streamlit/machine_id_v4` را نادیده می‌گیرد.
2. اپ را اجرا کنید: `streamlit run app.py --server.port 8505`
2. همهٔ منابع خارجی را قطع کنید: Wi-Fi off / airplane mode / قطع کابل.
3. صفحه را Hard Reload کنید (Ctrl+Shift+R): باید کامل و بدون جای‌خالی رندر شود.
4. DevTools → Network: پس از reload اول، **هیچ درخواستی** به میزبان‌های خارجی (tile, CDN, fonts.googleapis…) نباید باشد. تنها درخواست‌ها: خودِ `localhost:8505` (JS/CSS داخلی Streamlit).
5. هر ۴ صفحه و هر دو دامنهٔ آمار را بازدید کنید — بدون خطا/اسپینر بی‌پایان.
6. نقشه را Zoom/Hover کنید — باید بدون شبکه کار کند (SVG داخلی).
7. فونت فارسی باید رندر شود (Vazirmatn جاسازی‌شده)؛ اگر سیستم فونت نداشت، Tahoma fallback است — ظاهر فرق می‌کند ولی کار می‌کند.
8. اسکرین‌شات بگیرید و با `assets/preview.png` مقایسه کنید (رندر باید یکسان باشد).

## ب) Power BI Desktop (پس از ساخت .pbix طبق POWER_BI_BUILD_GUIDE.md)
1. فایل .pbix را بسازید و ببندید.
2. Wi-Fi off / airplane mode.
3. Desktop را باز کنید → فایل را Open کنید:
   - [ ] نقشهٔ Shape Map بدون پیام خطا رندر می‌شود (tile-based maps ممنوع‌اند).
   - [ ] هیچ visual ارور «Couldn't retrieve map tiles» نمی‌دهد.
   - [ ] فونت‌ها (Vazirmatn/Tahoma) درست‌اند.
   - [ ] اسلایسر دوره کار می‌کند.
4. Export → PDF (آفلاین) انجام می‌شود.
5. (اختیاری ولی توصیه‌شده) با Resource Monitor/Process Explorer تأیید کنید Desktop در زمان بازکردن فایل به شبکه وصل نشده.

## ج) چیزهایی که آفلاین **نیستند** و نباید اضافه شوند
- Bing/Azure/OSM/Mapbox tiles، Google Fonts <link>، CDNهای JS، هر `http(s)://` داخل کد/HTML/تم.
- فراخوانی API (مثلاً amar.org.ir) از داخل اپ/گزارش — این پروژه عمداً داده را **داخل فایل** نگه می‌دارد.

## د) اگر چیزی خراب شد
- نقشه خالی → کلید `province` با `name` داخل GeoJSON یکی نیست (املا!). جدول tests را اجرا کنید.
- فونت fallback → فونت روی سیستم نصب نیست؛ در Streamlit مشکلی نیست (base64) ولی در PDF/چاپ Desktop نصب لازم است.
- اعداد NaN → `jalali_month` خالیِ سالانه‌ها را به null واقعی تبدیل کنید (PQ: Replace Values).

## ه) وضعیت فعلی این پروژه (صادقانه)
اتصال فیزیکی اینترنت در این محیط قطع **نشده**؛ آفلاین‌بودن «با طراحی + بررسی استاتیک» تأیید شده و تست گام‌به‌گام الف/ب برای Desktop نیازمند اجرای شماست.

</div>
