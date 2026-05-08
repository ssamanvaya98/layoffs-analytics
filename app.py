"""
app.py  –  Navigating the Shift:
           Global and India-Centric Visual Analytics of Tech Layoffs

Run:
    pip install streamlit plotly pandas numpy
    python generate_data.py        # first time only
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tech Layoffs Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stSidebar"] { background: #0f172a; }
  [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
  .metric-card {
      background: #1e293b; border-radius: 12px; padding: 18px 22px;
      border-left: 4px solid #6366f1; margin-bottom: 8px;
  }
  .metric-card h2 { color: #818cf8; font-size: 2rem; margin: 0; }
  .metric-card p  { color: #94a3b8; margin: 0; font-size: 0.85rem; }
  .section-title  { color: #6366f1; font-size: 1.1rem; font-weight: 700;
                    letter-spacing: 0.05em; margin-top: 8px; }
  div[data-testid="stTabs"] button { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    global_df = pd.read_csv("data/layoffs_global.csv", parse_dates=["date"])
    india_df  = pd.read_csv("data/layoffs_india.csv",  parse_dates=["date"])
    cluster_df = pd.read_csv("data/company_clusters.csv")
    global_df["year"]  = global_df["date"].dt.year
    global_df["month"] = global_df["date"].dt.to_period("M").astype(str)
    india_df["year"]   = india_df["date"].dt.year
    india_df["month"]  = india_df["date"].dt.to_period("M").astype(str)
    return global_df, india_df, cluster_df

global_df, india_df, cluster_df = load_data()

# ── sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filters")

    year_range = st.slider(
        "Year Range",
        min_value=2020, max_value=2026,
        value=(2020, 2026), step=1
    )

    all_industries = sorted(global_df["industry"].dropna().unique())
    sel_industries = st.multiselect(
        "Industries", all_industries, default=all_industries
    )

    st.markdown("---")
    st.markdown("## 📊 Display Metric")
    metric_mode = st.radio(
        "Show values as",
        ["Absolute Count", "% of Workforce"],
        help="Switch all charts between raw headcount and percentage laid off"
    )
    use_pct = (metric_mode == "% of Workforce")

    st.markdown("---")
    st.markdown("## 🔍 Comparison Mode")
    compare_type = st.radio("Compare by", ["Companies", "Cities"])
    if compare_type == "Companies":
        opts = sorted(global_df["company"].unique())
        item_a = st.selectbox("Entity A", opts, index=opts.index("Google") if "Google" in opts else 0)
        item_b = st.selectbox("Entity B", opts, index=opts.index("Amazon") if "Amazon" in opts else 1)
    else:
        city_opts = sorted(global_df["location"].dropna().unique())
        default_a = city_opts.index("SF Bay Area") if "SF Bay Area" in city_opts else 0
        default_b = city_opts.index("New York City") if "New York City" in city_opts else 1
        item_a = st.selectbox("City A", city_opts, index=default_a)
        item_b = st.selectbox("City B", city_opts, index=default_b)

    st.markdown("---")
    st.caption("Data: Kaggle (Swaptr) · layoffs.fyi · Indian Layoffs Tracker")
    st.caption("IIT Delhi — Entry 2025EEY7601")

# ── filtering ─────────────────────────────────────────────────────────────────
def apply_filters(df, year_col="year"):
    industries = sel_industries if sel_industries else df["industry"].dropna().unique().tolist()
    mask = (
        df[year_col].between(*year_range) &
        df["industry"].isin(industries)
    )
    return df[mask].copy()

gdf = apply_filters(global_df)
idf = apply_filters(india_df)

# ── metric helpers ───────────────────────────────────────────────────────────
def show_empty(msg="No data matches the current filters. Try adjusting the sidebar."):
    st.warning(msg)

def metric_col(df):
    """Return the column name and y-axis label based on toggle."""
    if use_pct:
        return "percentage_laid_off", "Avg % Laid Off"
    return "total_laid_off", "Total Laid Off"

def agg_metric(df, group_col):
    """Aggregate by group_col using the chosen metric."""
    col, label = metric_col(df)
    if use_pct:
        result = df.groupby(group_col)[col].mean().reset_index()
    else:
        result = df.groupby(group_col)[col].sum().reset_index()
    result = result.rename(columns={col: "Value"})
    return result, label

# ── KPI metrics ───────────────────────────────────────────────────────────────
if use_pct:
    total_global = f"{gdf['percentage_laid_off'].mean(skipna=True):.1%}"
    total_india  = f"{idf['percentage_laid_off'].mean(skipna=True):.1%}"
else:
    total_global = f"{int(gdf['total_laid_off'].sum(skipna=True)):,}"
    total_india  = f"{int(idf['total_laid_off'].sum(skipna=True)):,}"
num_companies = gdf["company"].nunique()
peak_year = (
    gdf.groupby("year")["total_laid_off"].sum().idxmax()
    if not gdf.empty else "N/A"
)
num_estimated = int(gdf['is_estimated'].sum()) if 'is_estimated' in gdf.columns else 0
pct_estimated = round(num_estimated / len(gdf) * 100, 1) if len(gdf) else 0

st.markdown(
    "<h1 style='color:#6366f1;margin-bottom:0'>📊 Navigating the Shift</h1>"
    "<p style='color:#94a3b8;margin-top:4px'>Global & India-Centric Visual Analytics of Tech Layoffs</p>",
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
kpi_label1 = "Avg % Laid Off (Global)" if use_pct else "Global Layoffs"
kpi_label2 = "Avg % Laid Off (India)"  if use_pct else "India Layoffs"
for col, val, label in [
    (c1, total_global, kpi_label1),
    (c2, total_india,  kpi_label2),
    (c3, str(num_companies), "Companies Affected"),
    (c4, str(peak_year), "Peak Year"),
]:
    col.markdown(
        f"<div class='metric-card'><h2>{val}</h2><p>{label}</p></div>",
        unsafe_allow_html=True,
    )


if num_estimated > 0:
    st.caption(
        f"⚠️ **{num_estimated} records ({pct_estimated}%)** had no reported headcount — "
        f"values were estimated using industry-median imputation. Treat totals as approximate."
    )
st.divider()

# ── tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🌍 Global Map",
    "🇮🇳 India Hub",
    "🏭 Industry Breakdown",
    "📅 Temporal Trends",
    "⚖️ Comparison Mode",
    "🤖 Clustering",
])

# ── TAB 1: Global Choropleth ──────────────────────────────────────────────────
with tab1:
    st.markdown("<div class='section-title'>GLOBAL LAYOFF INTENSITY MAP</div>", unsafe_allow_html=True)

    if gdf.empty:
        show_empty()
    else:
        country_agg, ylabel = agg_metric(gdf, "country")
        choro_title = f"{'Average % Laid Off' if use_pct else 'Total Layoffs'} by Country"
        fmt = ":.1%" if use_pct else ":,"

        fig_choro = px.choropleth(
            country_agg,
            locations="country",
            locationmode="country names",
            color="Value",
            color_continuous_scale="Reds",
            hover_name="country",
            hover_data={"Value": fmt},
            title=choro_title,
            template="plotly_dark",
        )
        fig_choro.update_layout(
            geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
            height=500,
            margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
        )
        st.plotly_chart(fig_choro, use_container_width=True)

        top10 = country_agg.nlargest(10, "Value")
        fig_bar = px.bar(
            top10, x="country", y="Value", color="Value",
            color_continuous_scale="Purples",
            title=f"Top 10 Countries by {ylabel}",
            template="plotly_dark",
        )
        fig_bar.update_layout(
            paper_bgcolor="#0f172a", plot_bgcolor="#131e32",
            showlegend=False, height=350,
            xaxis_title="", yaxis_title=ylabel,
        )
        if use_pct:
            fig_bar.update_layout(yaxis_tickformat=".0%")
        st.plotly_chart(fig_bar, use_container_width=True)

# ── TAB 2: India Bubble Map ───────────────────────────────────────────────────
with tab2:
    st.markdown("<div class='section-title'>INDIA TECH HUB DEEP-DIVE</div>", unsafe_allow_html=True)

    # Only confirmed major Indian tech hubs with ≥100 layoffs
    city_coords = {
        "Bengaluru":  (12.9716, 77.5946),
        "New Delhi":  (28.6139, 77.2090),
        "Gurugram":   (28.4595, 77.0266),
        "Noida":      (28.5355, 77.3910),
        "Mumbai":     (19.0760, 72.8777),
        "Hyderabad":  (17.3850, 78.4867),
        "Chennai":    (13.0827, 80.2707),
    }

    if idf.empty:
        show_empty("No India data matches the current filters.")
    else:
        city_agg, city_ylabel = agg_metric(idf, "city")
        city_agg = city_agg.rename(columns={"Value": "Layoffs"})
        city_ylabel = city_ylabel
        city_agg["lat"] = city_agg["city"].map(lambda c: city_coords.get(c, (20.5, 78.9))[0])
        city_agg["lon"] = city_agg["city"].map(lambda c: city_coords.get(c, (20.5, 78.9))[1])
        city_agg = city_agg[city_agg["Layoffs"] >= 100]

        fig_bubble = px.scatter_geo(
            city_agg,
            lat="lat", lon="lon",
            size="Layoffs",
            color="Layoffs",
            hover_name="city",
            hover_data={"Layoffs": ":,", "lat": False, "lon": False},
            color_continuous_scale="Oranges",
            size_max=60,
            title="India — Layoffs by Tech Hub",
            template="plotly_dark",
        )
        fig_bubble.update_layout(
            geo=dict(
                scope="asia",
                center=dict(lat=20.5, lon=78.9),
                projection_scale=5,
                showland=True, landcolor="#1e293b",
                showocean=True, oceancolor="#0f172a",
                showcountries=True, countrycolor="#334155",
            ),
            height=480,
            margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor="#0f172a",
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

        col_a, col_b = st.columns(2)
        t_col = "percentage_laid_off" if use_pct else "total_laid_off"
        t_agg = "mean" if use_pct else "sum"
        city_trend = (
            idf.groupby(["month", "city"])[t_col]
            .agg(t_agg).reset_index()
        )
        city_trend = city_trend.rename(columns={t_col: "total_laid_off"})
        with col_a:
            if not city_trend.empty:
                # Filter to top 5 cities by total for readability
                top_cities = (
                    city_trend.groupby("city")["total_laid_off"]
                    .sum().nlargest(5).index.tolist()
                )
                city_trend_top = city_trend[city_trend["city"].isin(top_cities)]
                fig_line = px.line(
                    city_trend_top, x="month", y="total_laid_off", color="city",
                    markers=False,
                    title="Monthly Layoffs by City (Top 5)",
                    template="plotly_dark",
                )
                # Annotate the May 2020 COVID spike
                fig_line.add_annotation(
                    x="2020-05", y=city_trend_top["total_laid_off"].max(),
                    text="COVID-19<br>lockdown wave",
                    showarrow=True, arrowhead=2, arrowcolor="#f472b6",
                    font=dict(color="#f472b6", size=11),
                    bgcolor="#1e293b", bordercolor="#f472b6", borderwidth=1,
                    ax=40, ay=-40,
                )
                fig_line.update_layout(
                    paper_bgcolor="#0f172a", plot_bgcolor="#131e32",
                    xaxis_tickangle=45, height=350,
                    legend=dict(orientation="h", y=-0.3),
                )
                st.plotly_chart(fig_line, use_container_width=True)

        with col_b:
            city_bar = city_agg.sort_values("Layoffs", ascending=True)
            fig_hbar = px.bar(
                city_bar, x="Layoffs", y="city", orientation="h",
                color="Layoffs", color_continuous_scale="YlOrRd",
                title="Cumulative Layoffs per Hub",
                template="plotly_dark",
            )
            fig_hbar.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#131e32",
                                   showlegend=False, height=350)
            st.plotly_chart(fig_hbar, use_container_width=True)

# ── TAB 3: Industry Breakdown ─────────────────────────────────────────────────
with tab3:
    st.markdown("<div class='section-title'>INDUSTRY VOLATILITY BREAKDOWN</div>", unsafe_allow_html=True)

    if gdf.empty:
        show_empty()
    else:
        # ── Treemap: Industry → Top-5 companies ──────────────────────────────
        st.markdown("<div class='section-title'>TREEMAP — INDUSTRY → TOP COMPANIES</div>", unsafe_allow_html=True)
        st.caption("Each rectangle is proportional to total layoffs. Shows top 5 companies per industry. Click any industry to zoom in.")

        comp_agg = (
            gdf.groupby(["industry", "company"])["total_laid_off"]
            .sum().dropna().reset_index()
        )
        top5_tree = (
            comp_agg.sort_values("total_laid_off", ascending=False)
            .groupby("industry").head(5)
            .reset_index(drop=True)
        )
        fig_tree = px.treemap(
            top5_tree,
            path=[px.Constant("All Industries"), "industry", "company"],
            values="total_laid_off",
            color="total_laid_off",
            color_continuous_scale="RdBu_r",
            template="plotly_dark",
        )
        fig_tree.update_traces(
            textinfo="label+value",
            textfont=dict(size=13),
            hovertemplate="<b>%{label}</b><br>Laid off: %{value:,}<extra></extra>",
        )
        fig_tree.update_layout(
            paper_bgcolor="#0f172a",
            height=520,
            margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_tree, use_container_width=True)

        # ── Donut (top 10) + India vs Global comparison ───────────────────────
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='section-title'>SHARE BY INDUSTRY (TOP 10)</div>", unsafe_allow_html=True)
            ind_agg, ind_ylabel = agg_metric(gdf, "industry")
            ind_agg = ind_agg.dropna().nlargest(10, "Value")
            fig_donut = px.pie(
                ind_agg, names="industry", values="Value",
                hole=0.48,
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig_donut.update_traces(
                textposition="inside",
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>",
            )
            fig_donut.update_layout(
                paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
                font_color="#e2e8f0", height=400,
                showlegend=False,
                margin=dict(l=0, r=0, t=10, b=0),
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        with col2:
            st.markdown("<div class='section-title'>INDIA vs GLOBAL — INDUSTRY COMPARISON</div>", unsafe_allow_html=True)
            india_only = gdf[gdf["country"] == "India"]

            # Union of global top 10 + India top 8 so Education/Travel appear
            global_top10 = set(
                gdf.groupby("industry")["total_laid_off"].sum().nlargest(10).index
            )
            india_top8 = set(
                india_only.groupby("industry")["total_laid_off"].sum().nlargest(8).index
            )
            combined_industries = sorted(global_top10 | india_top8)

            global_rank = (
                gdf.groupby("industry")["total_laid_off"]
                .sum().dropna().reset_index()
                .rename(columns={"total_laid_off": "Global"})
            )
            india_rank = (
                india_only.groupby("industry")["total_laid_off"]
                .sum().dropna().reset_index()
                .rename(columns={"total_laid_off": "India"})
            )
            merged = (
                pd.DataFrame({"industry": combined_industries})
                .merge(global_rank, on="industry", how="left")
                .merge(india_rank, on="industry", how="left")
                .fillna(0)
                .sort_values("Global", ascending=False)
            )
            fig_compare = go.Figure()
            fig_compare.add_trace(go.Bar(
                name="Global", x=merged["industry"], y=merged["Global"],
                marker_color="#6366f1", opacity=0.85,
            ))
            fig_compare.add_trace(go.Bar(
                name="India", x=merged["industry"], y=merged["India"],
                marker_color="#f472b6", opacity=0.85,
            ))
            fig_compare.update_layout(
                barmode="group",
                template="plotly_dark",
                paper_bgcolor="#0f172a", plot_bgcolor="#131e32",
                height=400,
                legend=dict(orientation="h", y=1.08),
                xaxis_tickangle=35,
                xaxis_title="", yaxis_title="Total Laid Off",
                margin=dict(l=0, r=0, t=30, b=0),
            )
            st.plotly_chart(fig_compare, use_container_width=True)

# ── TAB 4: Temporal Trends ───────────────────────────────────────────────────
with tab4:
    st.markdown("<div class='section-title'>TEMPORAL LAYOFF PATTERNS</div>", unsafe_allow_html=True)

    if gdf.empty:
        show_empty()
    else:
        m_col = "percentage_laid_off" if use_pct else "total_laid_off"
        m_agg = "mean" if use_pct else "sum"
        monthly = (
            gdf.groupby("month")[m_col]
            .agg(m_agg).reset_index()
            .rename(columns={m_col: "Layoffs"})
            .sort_values("month")
        )
        monthly["rolling_30d"] = monthly["Layoffs"].rolling(3, min_periods=1).mean()

        fig_time = go.Figure()
        fig_time.add_trace(go.Bar(
            x=monthly["month"], y=monthly["Layoffs"],
            name="Monthly % Laid Off" if use_pct else "Monthly Layoffs",
            marker_color="#6366f1", opacity=0.6,
        ))
        fig_time.add_trace(go.Scatter(
            x=monthly["month"], y=monthly["rolling_30d"],
            name="3-Month Rolling Avg",
            line=dict(color="#f472b6", width=2.5),
            mode="lines",
        ))

        # ── Key event annotations ──────────────────────────────────────────────
        key_events = [
            ("2020-03", "COVID-19 lockdown",   "#EF9F27"),
            ("2022-10", "Twitter buyout",       "#F472B6"),
            ("2022-11", "ChatGPT launched",     "#1D9E75"),
            ("2023-01", "Peak month (95K)",     "#E24B4A"),
            ("2024-01", "Recovery begins",      "#378ADD"),
        ]
        y_max = monthly["Layoffs"].max() if not monthly.empty else 1
        for month_str, label, color in key_events:
            # Only annotate if month is in the filtered data range
            if not monthly[monthly["month"] == month_str].empty:
                fig_time.add_vline(
                    x=month_str,
                    line=dict(color=color, width=1.5, dash="dot"),
                )
                fig_time.add_annotation(
                    x=month_str,
                    y=y_max * 0.95,
                    text=label,
                    showarrow=False,
                    font=dict(color=color, size=10),
                    bgcolor="#0f172a",
                    bordercolor=color,
                    borderwidth=1,
                    borderpad=3,
                    yanchor="top",
                )

        fig_time.update_layout(
            title="Global Monthly Layoffs + Rolling Average (Wave Detection)",
            template="plotly_dark",
            paper_bgcolor="#0f172a", plot_bgcolor="#131e32",
            height=450, xaxis_tickangle=45,
            legend=dict(orientation="h", y=1.08),
        )
        st.plotly_chart(fig_time, use_container_width=True)

        # Animated choropleth — only show when multiple years present
        st.markdown("<div class='section-title'>⏱️ TEMPORAL ANIMATION — BUBBLE MAP</div>", unsafe_allow_html=True)

        yearly_country = (
            gdf.groupby(["year", "country"])["total_laid_off"]
            .sum().reset_index()
            .rename(columns={"total_laid_off": "Layoffs"})
        )
        num_years = yearly_country["year"].nunique()

        if num_years < 2:
            st.info("Select at least 2 years in the sidebar to enable the animated map.")
        else:
            st.info("Press ▶ Play to watch layoff waves unfold year by year")
            fig_anim = px.choropleth(
                yearly_country,
                locations="country",
                locationmode="country names",
                color="Layoffs",
                animation_frame="year",
                color_continuous_scale="OrRd",
                range_color=[0, yearly_country["Layoffs"].quantile(0.95)],
                hover_name="country",
                title="Layoff Waves: Animated",
                template="plotly_dark",
            )
            fig_anim.update_layout(
                geo=dict(showframe=False, projection_type="natural earth"),
                height=480,
                margin=dict(l=0, r=0, t=50, b=0),
                paper_bgcolor="#0f172a",
            )
            # Guard the animation button access
            if fig_anim.layout.updatemenus and len(fig_anim.layout.updatemenus) > 0:
                menus = fig_anim.layout.updatemenus[0]
                if menus.buttons and len(menus.buttons) > 0:
                    fig_anim.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1200
            st.plotly_chart(fig_anim, use_container_width=True)

        # Heatmap
        st.markdown("<div class='section-title'>🔥 INDUSTRY × YEAR HEATMAP</div>", unsafe_allow_html=True)
        pivot = (
            gdf.groupby(["year", "industry"])["total_laid_off"]
            .sum().unstack(fill_value=0)
        )
        if not pivot.empty:
            fig_heat = px.imshow(
                pivot.T,
                color_continuous_scale="YlOrRd",
                aspect="auto",
                title="Layoff Intensity: Industry × Year",
                template="plotly_dark",
                labels=dict(x="Year", y="Industry", color="Layoffs"),
            )
            fig_heat.update_layout(paper_bgcolor="#0f172a", height=400)
            st.plotly_chart(fig_heat, use_container_width=True)

# ── TAB 5: Comparison Mode ───────────────────────────────────────────────────
with tab5:
    st.markdown("<div class='section-title'>⚖️ SIDE-BY-SIDE COMPARISON</div>", unsafe_allow_html=True)
    st.caption(f"Comparing **{item_a}** vs **{item_b}** (change entities in the sidebar)")

    if compare_type == "Companies":
        df_a = gdf[gdf["company"] == item_a]
        df_b = gdf[gdf["company"] == item_b]
        group_col = "month"
    else:
        df_a = gdf[gdf["location"] == item_a]
        df_b = gdf[gdf["location"] == item_b]
        group_col = "month"

    def monthly_agg(df, name):
        d = (
            df.groupby(group_col)["total_laid_off"]
            .sum().reset_index()
            .rename(columns={"total_laid_off": "Layoffs", group_col: "Period"})
        )
        d["Entity"] = name
        return d

    cmp_df = pd.concat([monthly_agg(df_a, item_a), monthly_agg(df_b, item_b)])

    if cmp_df.empty:
        show_empty("No data found for the selected entities.")
    else:
        fig_cmp = px.line(
            cmp_df, x="Period", y="Layoffs", color="Entity",
            markers=True,
            color_discrete_sequence=["#6366f1", "#f472b6"],
            title=f"Monthly Layoffs: {item_a} vs {item_b}",
            template="plotly_dark",
        )
        fig_cmp.update_layout(
            paper_bgcolor="#0f172a", plot_bgcolor="#131e32",
            height=400, xaxis_tickangle=45,
        )
        st.plotly_chart(fig_cmp, use_container_width=True)

    col_l, col_r = st.columns(2)
    for col, df_x, name in [(col_l, df_a, item_a), (col_r, df_b, item_b)]:
        total = int(df_x["total_laid_off"].sum(skipna=True))
        events = len(df_x)
        peak_m = (
            df_x.groupby("month")["total_laid_off"].sum().idxmax()
            if not df_x.empty and df_x["total_laid_off"].notna().any() else "N/A"
        )
        ind = df_x["industry"].mode()[0] if not df_x.empty else "N/A"
        col.markdown(f"""
        <div class='metric-card'>
            <h2>{total:,}</h2><p>Total Laid Off — <b>{name}</b></p>
        </div>
        <div class='metric-card'>
            <h2>{events}</h2><p>Layoff Events</p>
        </div>
        <div class='metric-card'>
            <h2 style='font-size:1.2rem'>{peak_m}</h2><p>Peak Month</p>
        </div>
        <div class='metric-card'>
            <h2 style='font-size:1.2rem'>{ind}</h2><p>Primary Sector</p>
        </div>
        """, unsafe_allow_html=True)

    if compare_type == "Companies" and not df_a.empty and not df_b.empty:
        metrics_a = {
            "Total Laid Off":  df_a["total_laid_off"].sum(skipna=True),
            "Avg % Laid Off":  df_a["percentage_laid_off"].mean(skipna=True) * 100,
            "# Events":        len(df_a),
            "Avg per Event":   df_a["total_laid_off"].mean(skipna=True),
        }
        metrics_b = {
            "Total Laid Off":  df_b["total_laid_off"].sum(skipna=True),
            "Avg % Laid Off":  df_b["percentage_laid_off"].mean(skipna=True) * 100,
            "# Events":        len(df_b),
            "Avg per Event":   df_b["total_laid_off"].mean(skipna=True),
        }
        cats = list(metrics_a.keys())
        vals_a = [v if not (isinstance(v, float) and np.isnan(v)) else 0 for v in metrics_a.values()]
        vals_b = [v if not (isinstance(v, float) and np.isnan(v)) else 0 for v in metrics_b.values()]
        max_v = [max(a, b, 1) for a, b in zip(vals_a, vals_b)]
        norm_a = [a / m for a, m in zip(vals_a, max_v)]
        norm_b = [b / m for b, m in zip(vals_b, max_v)]

        fig_radar = go.Figure()
        for vals, name, color in [(norm_a, item_a, "#6366f1"), (norm_b, item_b, "#f472b6")]:
            fig_radar.add_trace(go.Scatterpolar(
                r=vals + [vals[0]], theta=cats + [cats[0]],
                fill="toself", name=name,
                line_color=color, fillcolor=color,
                opacity=0.4,
            ))
        fig_radar.update_layout(
            polar=dict(bgcolor="#131e32"),
            paper_bgcolor="#0f172a",
            font_color="#e2e8f0",
            title=f"Profile Comparison: {item_a} vs {item_b}",
            template="plotly_dark",
            height=420,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# ── TAB 6: K-Means Clustering ─────────────────────────────────────────────────
with tab6:
    st.markdown("<div class='section-title'>🤖 K-MEANS COMPANY CLUSTERING</div>", unsafe_allow_html=True)
    st.markdown(
        "Companies are grouped into **4 clusters** using K-Means on 5 features: "
        "total laid off, number of events, average per event, average % laid off, and layoff span in years. "
        "Features were log-transformed and standardised before clustering (silhouette score = 0.45).",
        unsafe_allow_html=False,
    )

    CLUSTER_COLORS = {
        "Serial Downsizers": "#6366f1",
        "Moderate Cutters":  "#378ADD",
        "Acute Cutters":     "#EF9F27",
        "Shutdown Risk":     "#E24B4A",
    }
    CLUSTER_DESC = {
        "Serial Downsizers": "Large companies with repeated layoffs over multiple years — Big Tech restructuring (Amazon, Intel, Meta)",
        "Moderate Cutters":  "Mid-size companies with a single moderate round — the most common pattern",
        "Acute Cutters":     "Companies that laid off a very high % of staff in one go — often near-shutdowns",
        "Shutdown Risk":     "Small companies with near-100% workforce reduction — startups that effectively closed",
    }

    # ── Cluster overview cards ────────────────────────────────────────────────
    c_cols = st.columns(4)
    for col, (name, color) in zip(c_cols, CLUSTER_COLORS.items()):
        count = (cluster_df["cluster_name"] == name).sum()
        avg   = cluster_df[cluster_df["cluster_name"] == name]["total_laid_off"].mean()
        col.markdown(
            f"<div class='metric-card' style='border-left-color:{color}'>"
            f"<h2 style='color:{color}'>{count}</h2>"
            f"<p>{name}</p>"
            f"<p style='font-size:0.75rem;margin-top:4px'>avg {avg:,.0f} laid off</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Cluster filter ────────────────────────────────────────────────────────
    all_cluster_names = list(CLUSTER_COLORS.keys())
    sel_clusters = st.multiselect(
        "Filter clusters to display",
        options=all_cluster_names,
        default=all_cluster_names,
        help="Select one or more clusters to isolate them in the scatter plot",
    )
    filtered_cluster_df = cluster_df[cluster_df["cluster_name"].isin(sel_clusters)] if sel_clusters else cluster_df

    # ── Scatter: total_laid_off vs avg_per_event coloured by cluster ──────────
    col_l, col_r = st.columns(2)

    with col_l:
        if filtered_cluster_df.empty:
            show_empty("Select at least one cluster to display the scatter plot.")
        else:
            fig_scatter = px.scatter(
                filtered_cluster_df,
                x="num_events",
                y="total_laid_off",
                color="cluster_name",
                color_discrete_map=CLUSTER_COLORS,
                hover_name="company",
                hover_data={"avg_per_event": ":.0f", "pct_laid_off_avg": ":.0%",
                            "cluster_name": False, "num_events": True},
                size="avg_per_event",
                size_max=30,
                log_y=True,
                title="Cluster Map — Events vs Total Laid Off",
                template="plotly_dark",
            )
            fig_scatter.update_layout(
                paper_bgcolor="#0f172a", plot_bgcolor="#131e32",
                height=420, legend_title="Cluster",
                xaxis_title="Number of Layoff Events",
                yaxis_title="Total Laid Off (log scale)",
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    with col_r:
        # Box plot: distribution of % laid off per cluster
        fig_box = px.box(
            filtered_cluster_df[filtered_cluster_df["pct_laid_off_avg"].notna()],
            x="cluster_name",
            y="pct_laid_off_avg",
            color="cluster_name",
            color_discrete_map=CLUSTER_COLORS,
            title="% Workforce Laid Off — Distribution by Cluster",
            template="plotly_dark",
            points="outliers",
        )
        fig_box.update_layout(
            paper_bgcolor="#0f172a", plot_bgcolor="#131e32",
            height=420, showlegend=False,
            xaxis_title="", yaxis_title="Avg % Laid Off",
            yaxis_tickformat=".0%",
        )
        st.plotly_chart(fig_box, use_container_width=True)

    # ── Industry breakdown per cluster ────────────────────────────────────────
    st.markdown("<div class='section-title'>INDUSTRY COMPOSITION PER CLUSTER</div>", unsafe_allow_html=True)

    ind_cluster = (
        cluster_df.groupby(["cluster_name", "industry"])
        .size().reset_index(name="count")
    )
    fig_ind = px.bar(
        ind_cluster,
        x="count", y="cluster_name", color="industry",
        orientation="h",
        title="Industry Mix within Each Cluster",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_ind.update_layout(
        paper_bgcolor="#0f172a", plot_bgcolor="#131e32",
        height=360, xaxis_title="Number of Companies",
        yaxis_title="", legend_title="Industry",
    )
    st.plotly_chart(fig_ind, use_container_width=True)

    # ── Cluster descriptions + top companies ─────────────────────────────────
    st.markdown("<div class='section-title'>CLUSTER PROFILES</div>", unsafe_allow_html=True)
    for name, color in CLUSTER_COLORS.items():
        sub = cluster_df[cluster_df["cluster_name"] == name]
        top5 = sub.nlargest(5, "total_laid_off")[["company", "total_laid_off", "num_events", "pct_laid_off_avg", "industry"]]
        top5["total_laid_off"] = top5["total_laid_off"].apply(lambda x: f"{x:,.0f}")
        top5["pct_laid_off_avg"] = top5["pct_laid_off_avg"].apply(lambda x: f"{x:.0%}" if pd.notna(x) else "N/A")
        top5.columns = ["Company", "Total Laid Off", "Events", "Avg % Laid Off", "Industry"]

        with st.expander(f"**{name}** — {len(sub)} companies", expanded=False):
            st.markdown(
                f"<div style='border-left:3px solid {color};padding-left:10px;"
                f"color:#94a3b8;margin-bottom:8px'>{CLUSTER_DESC[name]}</div>",
                unsafe_allow_html=True,
            )
            st.dataframe(top5, use_container_width=True, hide_index=True)

    # ── Lookup: which cluster is a company in? ────────────────────────────────
    st.markdown("<div class='section-title'>🔍 COMPANY LOOKUP</div>", unsafe_allow_html=True)
    search = st.text_input("Type a company name to find its cluster", placeholder="e.g. Amazon, Byju's, Grab")
    if search:
        results = cluster_df[cluster_df["company"].str.contains(search, case=False, na=False)]
        if results.empty:
            st.warning("No company found. Try a different name.")
        else:
            for _, row in results.iterrows():
                color = CLUSTER_COLORS.get(row["cluster_name"], "#6366f1")
                st.markdown(
                    f"<div class='metric-card' style='border-left-color:{color}'>"
                    f"<h2 style='font-size:1.1rem;color:{color}'>{row['company']}</h2>"
                    f"<p>Cluster: <b>{row['cluster_name']}</b> · Industry: {row['industry']} · Country: {row['country']}</p>"
                    f"<p style='font-size:0.8rem'>Total laid off: {row['total_laid_off']:,.0f} · Events: {int(row['num_events'])} · Avg %: {row['pct_laid_off_avg']:.0%}</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
