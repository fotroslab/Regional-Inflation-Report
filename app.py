# -*- coding: utf-8 -*-
"""
گزارش منطقه‌ای ایران — نرخ تورم به تفکیک استان (کاملاً آفلاین)
منبع هندسه: click_that_hood (MIT) | اعداد: مرکز آمار ایران (از طریق irangaah.ir / data.gov.ir و پیش‌نمایش iranstatis.com)
هیچ درخواست شبکه‌ای در زمان اجرا انجام نمی‌شود.
"""
import base64, html, json, math, re
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

BASE = Path(__file__).parent
DATA = BASE / "data"
ASSETS = BASE / "assets"

st.set_page_config(page_title="تورم استان‌های ایران | گزارش آفلاین", page_icon="🗺️",
                   layout="wide", initial_sidebar_state="expanded")

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
def fa_num(x, digits=1, suffix=""):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    s = f"{x:,.{digits}f}" if digits else f"{int(round(x)):,}"
    return s.translate(FA_DIGITS) + suffix

def load_css():
    css_fonts = ""
    for name, weight_range in [("Vazirmatn-latin", None), ("Vazirmatn-arabic", None)]:
        p = ASSETS / "fonts" / f"{name}.woff2"
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode()
            css_fonts += (f"@font-face{{font-family:'Vazirmatn';font-style:normal;font-weight:100 900;"
                          f"font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2');}}\n")
    css_fonts += "body, .stApp { font-family: 'Vazirmatn', Tahoma, sans-serif !important; }"
    st.markdown(f"""<style>
{css_fonts}
.stApp {{ background: #f7fafa; }}
.block-container {{ padding-top: 1.2rem; max-width: 1500px; }}
.rtl {{ direction: rtl; text-align: right; }}
.js-plotly-plot, .js-plotly-plot * {{ direction: ltr; }}
.kpi {{
  background:#ffffff; border:1px solid #dfe9e9; border-radius:14px;
  padding:14px 16px; box-shadow:0 1px 3px rgba(15,76,92,.08);
  direction:rtl; text-align:right; height:100%;
}}
.kpi .lbl {{ font-size:.78rem; color:#3d5a63; font-weight:600; }}
.kpi .val {{ font-size:1.55rem; font-weight:800; color:#0f4c5c; line-height:1.35; }}
.kpi .sub {{ font-size:.72rem; color:#6b8288; margin-top:2px; }}
.kpi.accent .val {{ color:#e3645f; }}
.card {{ background:#fff; border:1px solid #dfe9e9; border-radius:14px; padding:16px 18px;
        box-shadow:0 1px 3px rgba(15,76,92,.08); direction:rtl; text-align:right; }}
h1,h2,h3 {{ color:#0f4c5c !important; }}
.src-note {{ font-size:.72rem; color:#5b7178; direction:rtl; text-align:right; }}
.legend-wrap {{ direction:rtl; text-align:right; }}
.legend-bar {{ height:14px; border-radius:7px; border:1px solid #cfdcdc;
  background: linear-gradient(to right, #0f4c5c, #2e6b7e, #5b8f9c, #8db4bb, #bcd4d6, #e8f1f1); }}
.legend-labels {{ display:flex; justify-content:space-between; font-size:.75rem; color:#3d5a63; margin-top:3px; }}
.stTabs [data-baseweb="tab-list"] {{ direction: rtl; }}
[data-testid="stSidebar"] {{ background: #0f4c5c; }}
[data-testid="stSidebar"] * {{ color: #f7fafa !important; }}
[data-testid="stSidebar"] .stRadio label {{ font-size:.95rem; }}
.small-cap {{ font-size:.72rem; letter-spacing:.02em; color:#48666f; }}
</style>""", unsafe_allow_html=True)

# ----------------- داده -----------------
@st.cache_data
def load_data():
    fact = pd.read_csv(DATA / "fact_inflation_province.csv")
    urban = pd.read_csv(DATA / "fact_inflation_urban_tir1404.csv")
    national = pd.read_csv(DATA / "national_inflation.csv")
    national_u = pd.read_csv(DATA / "national_urban_tir1404.csv").iloc[0]
    dim_p = pd.read_csv(DATA / "dim_province.csv")
    dim_period = pd.read_csv(DATA / "dim_period.csv")
    geojson = json.loads((DATA / "iran_provinces.geojson").read_text())
    return fact, urban, national, national_u, dim_p, dim_period, geojson

fact, urban, national, national_u, dim_p, dim_period, geojson = load_data()
NAT_ANNUAL = dict(zip(national.period_key, national.inflation_annual_pct))

# ----------------- نقشهٔ SVG -----------------
@st.cache_data
def build_map_svg(values_json: str, highlight: str | None = None) -> str:
    values = json.loads(values_json)
    feats = geojson["features"]
    lon_min, lat_min, lon_max, lat_max = 44.0, 24.8, 63.5, 39.9
    W, H, PAD = 720, 560, 8
    mean_lat = math.radians((lat_min + lat_max) / 2)
    kx = math.cos(mean_lat)
    def proj(lon, lat):
        x = (lon - lon_min) * kx
        y = (lat_max - lat)
        return x, y
    xs, ys = [], []
    for f in feats:
        for poly in f["geometry"]["coordinates"]:
            for ring in poly:
                for lon, lat, *_ in ring:
                    x, y = proj(lon, lat); xs.append(x); ys.append(y)
    sx = (W - 2*PAD) / (max(xs) - min(xs)); sy = (H - 2*PAD) / (max(ys) - min(ys))
    s = min(sx, sy)
    ox = PAD + (W - 2*PAD - (max(xs)-min(xs))*s)/2 - min(xs)*s
    oy = PAD + (H - 2*PAD - (max(ys)-min(ys))*s)/2 - min(ys)*s
    def P(lon, lat):
        x, y = proj(lon, lat)
        return ox + x*s, oy + y*s

    vmin, vmax = min(values.values()), max(values.values())
    if vmax - vmin < 1e-9: vmax = vmin + 1
    stops = ["#e8f1f1", "#bcd4d6", "#8db4bb", "#5b8f9c", "#2e6b7e", "#0f4c5c"]
    def hex2rgb(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))
    rgb = [hex2rgb(c) for c in stops]
    def color(v):
        t = (v - vmin)/(vmax - vmin)
        pos = t*(len(rgb)-1); i = min(int(pos), len(rgb)-2); f_ = pos - i
        c = tuple(round(rgb[i][j]*(1-f_) + rgb[i+1][j]*f_) for j in range(3))
        return '#%02x%02x%02x' % c

    parts = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="نقشهٔ تورم استان‌های ایران">']
    for f in feats:
        name = f["properties"]["name"]; fa = f["properties"]["name_persian"]
        v = values.get(name)
        fill = color(v) if v is not None else "#d9e2e2"
        d_parts = []
        for poly in f["geometry"]["coordinates"]:
            for ring in poly:
                if len(ring) < 3: continue
                pts = [P(lon, lat) for lon, lat, *_ in ring]
                d_parts.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
        d = "".join(d_parts)
        hl = ' stroke="#e3645f" stroke-width="2.4"' if highlight == name else ' stroke="#f7fafa" stroke-width="0.9"'
        tip = html.escape(f"{fa} — تورم سالانه: {v:.1f}٪" if v is not None else fa)
        parts.append(f'<path d="{d}" fill="{fill}"{hl} stroke-linejoin="round"><title>{tip}</title></path>')
    parts.append('</svg>')
    return "".join(parts)

def legend_html():
    return ('<div class="legend-wrap"><div class="legend-bar"></div>'
            '<div class="legend-labels"><span>کمتر</span><span>نرخ تورم سالانه</span><span>بیشتر</span></div></div>')

def kpi(label, value, sub="", accent=False):
    return (f'<div class="kpi{" accent" if accent else ""}"><div class="lbl">{label}</div>'
            f'<div class="val">{value}</div><div class="sub">{sub}</div></div>')

PLOT_FONT = dict(family="Vazirmatn, Tahoma, sans-serif", size=13, color="#12333d")
def style_fig(fig, height=430):
    fig.update_layout(height=height, font=PLOT_FONT, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=8, r=8, t=38, b=8),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=1, xanchor="right"),
                      hoverlabel=dict(font_family="Vazirmatn"))
    fig.update_xaxes(gridcolor="#e3ecec", zeroline=False)
    fig.update_yaxes(gridcolor="#e3ecec", zeroline=False)
    return fig

load_css()

# ----------------- سایدبار -----------------
with st.sidebar:
    st.markdown("## 🗺️ تورم استان‌های ایران")
    st.markdown('<div class="small-cap">گزارش کاملاً آفلاین — بدون tile و بدون CDN</div>', unsafe_allow_html=True)
    page = st.radio("صفحه", ["۱) نمای کلی منطقه‌ای", "۲) رتبه‌بندی استان‌ها", "۳) روند تاریخی", "۴) دربارهٔ داده و نقشه"], label_visibility="collapsed")
    st.markdown("---")
    scope = st.radio("دامنهٔ آمار", ["خانوارهای کشور — نرخ تورم سالانه (۱۳۹۷ تا تیر ۱۴۰۵)",
                                    "خانوارهای شهری — تیر ۱۴۰۴ (ماهانه/نقطه‌ای/سالانه)"])
    is_urban = scope.startswith("خانوارهای شهری")
    st.markdown("---")
    st.caption("مأخذ: مرکز آمار ایران | بازنشر: irangaah.ir مستند به data.gov.ir و پیش‌نمایش iranstatis.com")
    st.caption("هندسه: click_that_hood (MIT) — ساده‌شده؛ ممکن است شامل © OSM (ODbL) باشد")

is_main = not is_urban
NAT = fact  # main national-scope fact

def main_selection(period_key):
    d = NAT[NAT.period_key == period_key][["province", "inflation_annual_pct"]]
    return dict(zip(d.province, d.inflation_annual_pct))

period_options = list(dim_period.sort_values("sort_order").set_index("period_key").period_label)
period_keys = list(dim_period.sort_values("sort_order").period_key)

if page.startswith("۱"):
    st.markdown('<div class="rtl"><h1>نمای کلی منطقه‌ای — نرخ تورم سالانه استان‌ها</h1></div>', unsafe_allow_html=True)
    if is_main:
        sel = st.selectbox("دورهٔ آماری", range(len(period_keys)), format_func=lambda i: period_options[i], index=len(period_keys)-1)
        pkey = period_keys[sel]
        values = main_selection(pkey)
        plabel = period_options[sel]
        nat = NAT_ANNUAL[pkey]
        unit_txt = "٪"
    else:
        pkey = "1404-04"; plabel = "تیر ۱۴۰۴ (خانوارهای شهری)"
        values = dict(zip(urban.province, urban.inflation_annual_pct))
        nat = float(national_u.inflation_annual_pct); unit_txt = "٪"
    vals = list(values.values())
    pmax, pmin = max(vals), min(vals)
    name_max = [p for p, v in values.items() if v == pmax][0]
    name_min = [p for p, v in values.items() if v == pmin][0]
    fa_of = dict(zip(dim_p.province, dim_p.name_persian))
    st.markdown(f'<div class="rtl src-note">دوره: <b>{plabel}</b> — مأخذ: مرکز آمار ایران</div>', unsafe_allow_html=True)
    c = st.columns(4)
    c[0].markdown(kpi("نرخ تورم سالانه — کل کشور", fa_num(nat, 1, "٪"), "میانگین ۱۲ ماه منتهی به دوره"), unsafe_allow_html=True)
    c[1].markdown(kpi("بالاترین استان", fa_num(pmax, 1, "٪"), fa_of[name_max], accent=True), unsafe_allow_html=True)
    c[2].markdown(kpi("پایین‌ترین استان", fa_num(pmin, 1, "٪"), fa_of[name_min]), unsafe_allow_html=True)
    c[3].markdown(kpi("اختلاف بیشترین−کمترین", fa_num(pmax - pmin, 1, " واحد درصد"), "گسترهٔ استانی تورم"), unsafe_allow_html=True)
    st.markdown("")
    left, right = st.columns([3, 2])
    with left:
        svg = build_map_svg(json.dumps(values), None)
        st.markdown(f'<div class="card">{svg}</div>', unsafe_allow_html=True)
        st.markdown(legend_html(), unsafe_allow_html=True)
    with right:
        st.markdown('<div class="rtl"><h3>پنج استان پرتورم این دوره</h3></div>', unsafe_allow_html=True)
        top5 = sorted(values.items(), key=lambda kv: -kv[1])[:5]
        fig = go.Figure(go.Bar(x=[v for _, v in top5][::-1], y=[fa_of[k] for k, _ in top5][::-1],
                               orientation="h", marker_color="#0f4c5c",
                               text=[f"{v:.1f}٪" for _, v in top5][::-1], textposition="outside"))
        fig.add_vline(x=nat, line_dash="dash", line_color="#e3645f", annotation_text="کشور", annotation_font_color="#e3645f")
        fig.update_layout(title="بالاترین نرخ‌ها نسبت به متوسط کشوری (خط مرجانی)")
        st.plotly_chart(style_fig(fig, 300), width="stretch")
        st.markdown('<div class="rtl src-note">نقشه از فایل GeoJSON داخلی رندر می‌شود؛ هیچ کاشی/نقشهٔ آنلاین دریافت نمی‌شود. مرزها تقریبی و فاقد ارزش ثبتی هستند.</div>', unsafe_allow_html=True)

elif page.startswith("۲"):
    st.markdown('<div class="rtl"><h1>رتبه‌بندی استان‌ها</h1></div>', unsafe_allow_html=True)
    if is_main:
        sel = st.selectbox("دورهٔ آماری", range(len(period_keys)), format_func=lambda i: period_options[i], index=len(period_keys)-1)
        pkey = period_keys[sel]; plabel = period_options[sel]
        d = NAT[NAT.period_key == pkey][["province","province_fa","inflation_annual_pct"]].rename(columns={"inflation_annual_pct":"val"})
        nat = NAT_ANNUAL[pkey]; metric_lbl = "نرخ تورم سالانه (٪)"
    else:
        metric = st.radio("شاخص", ["تورم سالانه", "تورم نقطه‌به‌نقطه", "تورم ماهانه"], horizontal=True)
        col = {"تورم سالانه": "inflation_annual_pct", "تورم نقطه‌به‌نقطه": "inflation_yoy_pct", "تورم ماهانه": "inflation_monthly_pct"}[metric]
        d = urban[["province","province_fa", col]].rename(columns={col: "val"})
        nat = {"تورم سالانه": float(national_u.inflation_annual_pct), "تورم نقطه‌به‌نقطه": float(national_u.inflation_yoy_pct), "تورم ماهانه": float(national_u.inflation_monthly_pct)}[metric]
        plabel = f"تیر ۱۴۰۴ (شهری) — {metric}"; metric_lbl = metric + " (٪)"
    d = d.sort_values("val", ascending=True)
    colors = ["#e3645f" if v > nat else "#0f4c5c" for v in d.val]
    fig = go.Figure(go.Bar(x=d.val, y=d.province_fa, orientation="h", marker_color=colors,
                           text=[f"{v:.1f}٪" for v in d.val], textposition="outside"))
    fig.add_vline(x=nat, line_dash="dash", line_color="#12333d", annotation_text="متوسط کشور", annotation_position="top")
    fig.update_layout(title=f"{metric_lbl} — {plabel} (قرمز = بالاتر از متوسط کشوری)")
    fig.update_xaxes(title=metric_lbl)
    st.plotly_chart(style_fig(fig, 780), width="stretch")
    st.markdown('<div class="rtl src-note">خط چین: متوسط کل کشور. رنگ مرجانی یعنی استان بالاتر از متوسط کشور است.</div>', unsafe_allow_html=True)

elif page.startswith("۳"):
    st.markdown('<div class="rtl"><h1>روند تاریخی — نرخ تورم سالانه (۱۳۹۷ تا تیر ۱۴۰۵)</h1></div>', unsafe_allow_html=True)
    fa_of = dict(zip(dim_p.province, dim_p.name_persian))
    en_of = dict(zip(dim_p.name_persian, dim_p.province))
    default_sel = ["تهران", "ایلام", "کردستان", "سیستان و بلوچستان"]
    chosen = st.multiselect("استان‌ها (حداکثر ۶)", sorted(fa_of.values()), default=default_sel, max_selections=6)
    order = list(dim_period.sort_values("sort_order").period_key)
    label_of = dict(zip(dim_period.period_key, dim_period.period_label))
    fig = go.Figure()
    for fa in chosen:
        en = en_of[fa]
        s = NAT[NAT.province == en].set_index("period_key").inflation_annual_pct
        fig.add_trace(go.Scatter(x=order, y=[s[k] for k in order], mode="lines+markers", name=fa))
    fig.add_trace(go.Scatter(x=order, y=[NAT_ANNUAL[k] for k in order], mode="lines",
                             name="کل کشور", line=dict(dash="dash", color="#e3645f", width=3)))
    fig.update_xaxes(title="دوره (۸ سال سالانه + دو ماههٔ ۱۴۰۵)", ticktext=[label_of[k] for k in order], tickvals=order, type="category")
    fig.update_yaxes(title="نرخ تورم سالانه (٪)")
    fig.update_layout(title="روند نرخ تورم سالانهٔ استان‌های منتخب در برابر کل کشور")
    st.plotly_chart(style_fig(fig, 480), width="stretch")
    st.markdown('<div class="rtl src-note">توجه: هشت نقطهٔ نخست، میانگین سالانهٔ هر سال (خانوارهای کشور) است و دو نقطهٔ آخر، نرخ سالانه در ماه‌های خرداد و تیر ۱۴۰۵؛ فواصل زمانی یکنواخت نیستند و روی محور دسته‌ای نمایش داده شده‌اند. قلهٔ تیر ۱۴۰۴ در این سری دیده نمی‌شود چون دادهٔ ماهانهٔ استانی به‌صورت رایگان در دسترس نیست (به «دربارهٔ داده» مراجعه کنید).</div>', unsafe_allow_html=True)
    delta = NAT[NAT.period_key.isin(["1397","1404"])].pivot(index="province", columns="period_key", values="inflation_annual_pct")
    delta["change"] = delta["1404"] - delta["1397"]
    fig2 = go.Figure(go.Bar(x=[fa_of[p] for p in delta.sort_values("change").index],
                            y=delta.sort_values("change").change,
                            marker_color="#0f4c5c"))
    fig2.update_layout(title="تغییر نرخ تورم سالانه از ۱۳۹۷ تا ۱۴۰۴ (واحد درصد)")
    fig2.update_yaxes(title="تغییر (واحد درصد)")
    st.plotly_chart(style_fig(fig2, 360), width="stretch")

else:  # دربارهٔ داده و نقشه
    st.markdown('<div class="rtl"><h1>دربارهٔ داده و نقشه</h1></div>', unsafe_allow_html=True)
    st.markdown("""<div class="card rtl">
<h3>این گزارش چیست؟</h3>
<p>گزارش گرافیکی <b>کاملاً آفلاین</b> از <b>نرخ تورم به تفکیک ۳۱ استان ایران</b> برای استفادهٔ آموزشی/آزمایشی در Power BI و ارائهٔ نمونه‌کار. بدون هیچ tile، CDN یا فراخوانی شبکه در زمان اجرا. اعداد، آمار رسمی تورم هستند (نه فروش/سفارش/تیکت و نه دادهٔ بازار).</p>

<h3>دادهٔ اصلی — نرخ تورم سالانهٔ خانوارهای کشور</h3>
<ul>
<li><b>مأخذ:</b> مرکز آمار ایران (سری شاخص قیمت مصرف‌کننده، سال پایه ۱۴۰۰).</li>
<li><b>بازنشر:</b> جدول «درصد تغییرات شاخص قیمت مصرف‌کننده خانوارهای کشور به تفکیک استان (نرخ تورم سالانه)» در <b>irangaah.ir</b>، مستند به <b>data.gov.ir</b> (درگاه ملی داده‌های باز ایران) — داده‌ها بدون تغییر در ارقام و پس از یکدست‌سازی حروف منتشر شده‌اند.</li>
<li><b>پوشش:</b> ۳۱ استان × ۱۰ دوره = ۳۱۰ ردیف: سال‌های ۱۳۹۷ تا ۱۴۰۴ (سالانه) + خرداد ۱۴۰۵ و تیر ۱۴۰۵ (نرخ سالانهٔ ماهانه). کل کشور: ۱۰ مقدار مرجع در <code>data/national_inflation.csv</code>.</li>
<li><b>خطر ترنسکریپشن:</b> مقادیر با دست از جدول وب بازنویسی شده‌اند؛ پیش از هر انتشار حرفه‌ای با فایل اصلی data.gov.ir تطبیق دهید (رجوع کنید به VALIDATION.md).</li>
</ul>

<h3>دادهٔ مکمل — تیر ۱۴۰۴ (خانوارهای شهری)</h3>
<ul>
<li><b>مأخذ:</b> مرکز آمار ایران — <b>پیش‌نمایش جزئی</b> جدول «نرخ تورم استان‌ها» در iranstatis.com (شاخص قیمت، تورم ماهانه، نقطه‌به‌نقطه و سالانه؛ ۳۱ استان).</li>
<li>iranstatis.com یک <b>آینهٔ غیررسمی</b> است؛ کاربر صریحاً استفاده از آن را تأیید کرده است. بانک کامل ماهانهٔ استانی اشتراکی است و در این پروژه استفاده نشده.</li>
<li>دامنهٔ این جدول <b>خانوارهای شهری</b> است و با سری «خانوارهای کشور» هم‌تعریف نیست؛ با هم برش نمی‌خورند.</li>
</ul>

<h3>هندسهٔ نقشه</h3>
<ul>
<li>فایل GeoJSON از مخزن <b>codeforamerica/click_that_hood</b> (فایل iran-provinces.geojson) — مجوز <b>MIT © Code for America</b>؛ مختصات به ۳ رقم اعشار ساده‌سازی شده‌اند (≈۲٫۲ مگابایت).</li>
<li>هندسهٔ زیرین ممکن است <b>ODbL © OpenStreetMap contributors</b> باشد. <b>انتساب اجباری:</b> «Boundaries: click_that_hood (MIT License) — simplified; © OpenStreetMap contributors may apply (ODbL) for underlying boundaries»</li>
<li>مرزها تقریبی‌اند؛ کاربرد حقوقی/ثبتی ندارند؛ جزایر نمایش داده نمی‌شوند؛ مرزهای بین‌المللی محل مناقشه‌اند و این نقشه سند ارضی نیست.</li>
</ul>

<h3>تقسیم‌بندی منطقه‌ای</h3>
<p>گروه‌بندی «شمال/جنوب/شرق/غرب/مرکز» در <code>dim_province.csv</code> صرفاً نمایشی است و جغرافیای رسمی ایران محسوب نمی‌شود.</p>

<h3>محدودیت‌های کلیدی</h3>
<ul>
<li>فاقد فایل .pbix — ساخت Shape Map باید در Power BI Desktop انجام شود (report/POWER_BI_BUILD_GUIDE.md).</li>
<li>سری زمانی استانی یکنواخت و <b>ماهانه</b> به‌صورت رایگان در دسترس نیست؛ ۱۰ دورهٔ موجود شامل ۸ سالانه + ۲ ماهانه است و فواصل نامنظم‌اند.</li>
<li>اعداد «فروش/سفارش/تیکت» نسخهٔ قبلی این پروژه کاملاً کنار گذاشته شد؛ گزارش اکنون آمار رسمی تورم را نشان می‌دهد.</li>
<li>تست فیزیکی قطع اینترنت و رندر Shape Map در Desktop انجام نشده (رجوع کنید به VALIDATION.md).</li>
</ul>

<h3>فونت</h3>
<p>Vazirmatn — مجوز SIL Open Font License 1.1 — به‌صورت محلی در assets/fonts جاسازی شده است (هیچ بارگذاری شبکه‌ای).</p>
</div>""", unsafe_allow_html=True)

st.caption("© ۱۴۰۵ — گزارش نمونه‌کار آفلاین | نقشه: click_that_hood (MIT) + داده‌های مرکز آمار ایران (از طریق بازنشرکنندگان ذکرشده)")
