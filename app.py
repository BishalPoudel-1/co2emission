import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="CO2 Climate Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --ink-100: #f8fafc;
        --ink-200: #e2e8f0;
        --ink-300: #cbd5e1;
        --ink-400: #94a3b8;
        --panel-border: rgba(148, 163, 184, 0.18);
        --panel-bg: linear-gradient(145deg, rgba(23, 30, 47, 0.82), rgba(14, 20, 34, 0.88));
    }

    html, body, [class*="css"] {
        font-family: 'Manrope', sans-serif;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(1100px 550px at -10% -20%, rgba(34, 197, 94, 0.16), transparent 45%),
            radial-gradient(900px 500px at 120% -10%, rgba(59, 130, 246, 0.18), transparent 48%),
            linear-gradient(180deg, #0b1220 0%, #0a111d 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #101726 0%, #0d1422 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.16);
    }

    .hero-title {
        color: var(--ink-100);
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.25;
        margin-top: 0.3rem;
        margin-bottom: 0.5rem;
        letter-spacing: 0;
        max-width: 1240px;
    }

    .hero-subtitle {
        color: var(--ink-400);
        font-size: 0.92rem;
        margin-bottom: 1.05rem;
    }

    .meta-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin: 0.35rem 0 1rem 0;
    }

    .meta-item {
        border: 1px solid var(--panel-border);
        background: rgba(15, 23, 42, 0.45);
        color: var(--ink-300);
        border-radius: 999px;
        padding: 0.32rem 0.66rem;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.01em;
    }

    .metric-card {
        border-radius: 14px;
        border: 1px solid var(--panel-border);
        background: var(--panel-bg);
        backdrop-filter: blur(5px);
        padding: 0.95rem 1rem;
        min-height: 92px;
        box-shadow: 0 14px 30px rgba(2, 6, 23, 0.26);
    }

    .metric-label {
        color: #94a3b8;
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.2rem;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 1.9rem;
        font-weight: 800;
        line-height: 1.1;
    }

    .metric-sub {
        color: #cbd5e1;
        font-size: 0.78rem;
        margin-left: 0.3rem;
    }

    .section-title {
        color: var(--ink-200);
        font-size: 1.05rem;
        font-weight: 800;
        letter-spacing: 0.07em;
        margin: 0.45rem 0 0.2rem 0;
        text-transform: uppercase;
    }

    .section-subtitle {
        color: var(--ink-400);
        font-size: 0.82rem;
        margin-bottom: 0.45rem;
    }

    .verdict {
        border-radius: 10px;
        border: 1px solid rgba(59, 130, 246, 0.35);
        background: linear-gradient(90deg, rgba(2, 132, 199, 0.18), rgba(15, 23, 42, 0.15));
        color: #cfe8ff;
        padding: 0.65rem 0.75rem;
        margin: 0.35rem 0 0.8rem 0;
        font-size: 0.86rem;
        line-height: 1.35;
    }

    div[data-testid="stPlotlyChart"] {
        border: 1px solid var(--panel-border);
        border-radius: 12px;
        background: rgba(15, 23, 42, 0.48);
        padding: 0.35rem;
    }

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--panel-border);
    }

    .block-container {
        padding-top: 4.1rem;
        padding-bottom: 1.4rem;
    }

    [data-testid="stAppViewBlockContainer"] {
        padding-top: 4.1rem;
    }

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #d8e3f7;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_and_prepare_data():
    owid_path = "owid-co2-data.csv"
    energy_path = "global-data-on-sustainable-energy (1).csv"

    owid_raw = pd.read_csv(owid_path)
    energy_raw = pd.read_csv(energy_path)

    def standardize_country_names(df, col):
        mapping = {
            "United States of America": "United States",
            "Russian Federation": "Russia",
            "Viet Nam": "Vietnam",
            "Iran (Islamic Republic of)": "Iran",
            "Syrian Arab Republic": "Syria",
            "Republic of Korea": "South Korea",
            "Democratic People's Republic of Korea": "North Korea",
            "Democratic Republic of the Congo": "Democratic Republic of Congo",
            "Czech Republic": "Czechia",
            "Turkiye": "Turkey",
            "United Republic of Tanzania": "Tanzania",
            "Bolivia (Plurinational State of)": "Bolivia",
            "Venezuela (Bolivarian Republic of)": "Venezuela",
            "Lao People's Democratic Republic": "Laos",
            "Brunei Darussalam": "Brunei",
            "Cabo Verde": "Cape Verde",
            "Moldova, Republic of": "Moldova",
            "Timor-Leste": "East Timor",
        }
        out = df.copy()
        out[col] = out[col].replace(mapping)
        return out

    def add_region(df):
        region_map = (
            px.data.gapminder()[["country", "continent"]]
            .drop_duplicates()
            .rename(columns={"continent": "region"})
        )
        out = df.merge(region_map, on="country", how="left")
        fallback = {"Kosovo": "Europe", "South Sudan": "Africa", "World": "Other"}
        out["region"] = out["region"].fillna(out["country"].map(fallback)).fillna("Other")
        return out

    def prepare_dataset(owid_df, energy_df, start_year=2000, end_year=2022):
        owid = owid_df.copy()
        energy = energy_df.copy()

        energy = energy.rename(
            columns={
                "Entity": "country",
                "Year": "year",
                "Renewable energy share in the total final energy consumption (%)": "renewable_energy_share_pct",
                "Primary energy consumption per capita (kWh/person)": "energy_consumption_pc_energy",
                "Energy intensity level of primary energy (MJ/$2017 PPP GDP)": "energy_intensity_mj_per_gdp",
                "Value_co2_emissions_kt_by_country": "co2_kt_energy_dataset",
            }
        )

        owid = standardize_country_names(owid, "country")
        energy = standardize_country_names(energy, "country")

        iso_code = owid["iso_code"].astype("string")
        valid_iso = (
            iso_code.notna()
            & iso_code.str.len().eq(3)
            & ~iso_code.str.startswith("OWID", na=False)
        )
        owid = owid[valid_iso & owid["year"].between(start_year, end_year)].copy()
        energy = energy[energy["year"].between(start_year, end_year)].copy()

        owid = owid.sort_values(["country", "year"]).drop_duplicates(["country", "year"], keep="last")
        energy = energy.sort_values(["country", "year"]).drop_duplicates(["country", "year"], keep="last")

        energy_cols = [
            "country",
            "year",
            "renewable_energy_share_pct",
            "energy_consumption_pc_energy",
            "energy_intensity_mj_per_gdp",
            "gdp_per_capita",
            "gdp_growth",
            "Access to electricity (% of population)",
            "Low-carbon electricity (% electricity)",
        ]
        energy_cols = [c for c in energy_cols if c in energy.columns]

        df = owid.merge(energy[energy_cols], on=["country", "year"], how="left", validate="1:1")

        numeric_cols = [
            "co2",
            "co2_per_capita",
            "population",
            "gdp",
            "energy_per_capita",
            "renewable_energy_share_pct",
            "energy_intensity_mj_per_gdp",
            "gdp_per_capita",
            "energy_consumption_pc_energy",
            "primary_energy_consumption",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        counts = df.groupby("country")["co2"].count().reset_index(name="n")
        keep = counts[counts["n"] >= 10]["country"]
        df = df[df["country"].isin(keep)].copy()

        interp_cols = [c for c in numeric_cols if c in df.columns]
        df = df.sort_values(["country", "year"]).copy()
        df[interp_cols] = df.groupby("country")[interp_cols].transform(lambda x: x.interpolate(limit_direction="both"))
        for col in interp_cols:
            df[col] = df[col].fillna(df[col].median())

        df = add_region(df)
        df["renewable_share_final"] = df.get("renewable_energy_share_pct")
        df["gdp_per_capita_final"] = df.get("gdp_per_capita")
        df["development_status"] = np.where(df["gdp_per_capita_final"] >= 20000, "Developed", "Developing")
        return df

    df = prepare_dataset(owid_raw, energy_raw, start_year=2000, end_year=2022)
    latest_year = int(df["year"].max())
    latest_df = df[df["year"] == latest_year].copy()

    co2_2000 = df[df["year"] == 2000].set_index("country")["co2"]
    latest_df["co2_2000"] = latest_df["country"].map(co2_2000)
    latest_df["co2_reduction_pct_since_2000"] = (
        (latest_df["co2_2000"] - latest_df["co2"]) / latest_df["co2_2000"] * 100
    ).fillna(0)
    latest_df["success_label"] = latest_df["co2_reduction_pct_since_2000"].apply(
        lambda x: "Successful (>10% reduction)" if x > 10 else "Not successful"
    )
    latest_df["development_status"] = latest_df["gdp_per_capita_final"].apply(
        lambda x: "Developed" if x >= 20000 else "Developing"
    )

    return df, latest_df


def style_figure(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.55)",
        font=dict(color="#dbe7ff", family="Manrope"),
        margin=dict(l=35, r=20, t=55, b=35),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
        colorway=["#60a5fa", "#38bdf8", "#4ade80", "#f59e0b", "#f87171", "#c084fc", "#34d399"],
        hoverlabel=dict(bgcolor="rgba(15,23,42,0.96)", bordercolor="rgba(148,163,184,0.25)", font_color="#e2e8f0"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148,163,184,0.16)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.16)")
    return fig


def section_header(title, subtitle=""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_chart(fig):
    st.plotly_chart(
        fig,
        width='stretch',
        config={
            "displaylogo": False,
            "responsive": True,
            "modeBarButtonsToRemove": ["lasso2d", "select2d", "toggleSpikelines"],
        },
    )


def metric_card(label, value, sub_text, accent):
    st.markdown(
        f"""
        <div class="metric-card" style="border-left: 2px solid {accent};">
            <div class="metric-label">{label}</div>
            <div><span class="metric-value">{value}</span><span class="metric-sub">{sub_text}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


df, latest_df = load_and_prepare_data()

st.sidebar.header("Filters")
regions = sorted(latest_df["region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect("Region", options=regions, default=regions)
success_mode = st.sidebar.selectbox("Progress Filter", ["All", "Successful only", "Not successful only"])

filtered_latest = latest_df[latest_df["region"].isin(selected_regions)].copy()
if success_mode == "Successful only":
    filtered_latest = filtered_latest[filtered_latest["success_label"] == "Successful (>10% reduction)"]
elif success_mode == "Not successful only":
    filtered_latest = filtered_latest[filtered_latest["success_label"] == "Not successful"]

country_options = sorted(filtered_latest["country"].dropna().unique().tolist())
selected_countries = st.sidebar.multiselect(
    "Country",
    options=country_options,
    default=country_options,
    placeholder="Select one or more countries",
)
filtered_latest = filtered_latest[filtered_latest["country"].isin(selected_countries)].copy()

if filtered_latest.empty:
    st.warning("No data available with selected filters. Please broaden your filters.")
    st.stop()

filtered_countries = filtered_latest["country"].unique().tolist()
filtered_df = df[df["country"].isin(filtered_countries)].copy()

latest_year = int(filtered_latest["year"].max())
total_co2_tonnes = filtered_latest["co2"].sum() * 1_000_000
total_co2_b = total_co2_tonnes / 1_000_000_000
avg_co2_pc = filtered_latest["co2_per_capita"].mean()
avg_renew = filtered_latest["renewable_share_final"].mean()
on_track = int((filtered_latest["co2_reduction_pct_since_2000"] > 10).sum())

st.markdown(
    """
    <div class="hero-title">
        SDG 13 Climate Performance Dashboard
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    "<div class=\"hero-subtitle\">Policy-focused view of emission reduction performance and key economic or energy predictors.</div>",
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)
with k1:
    metric_card("Total CO2", f"{total_co2_b:.1f}B", "tonnes", "#60a5fa")
with k2:
    metric_card("Avg CO2", f"{avg_co2_pc:.1f}t", "per capita", "#22d3ee")
with k3:
    metric_card("Renewable", f"{avg_renew:.1f}%", "global share", "#4ade80")
with k4:
    metric_card("On-Track", f"{on_track}", "countries", "#fca5a5")

st.markdown(
    f"""
    <div class="meta-strip">
        <div class="meta-item">Coverage: {len(filtered_countries)} countries</div>
        <div class="meta-item">Snapshot Year: {latest_year}</div>
        <div class="meta-item">Region Filters: {len(selected_regions)}</div>
        <div class="meta-item">Country Filters: {len(selected_countries)}</div>
        <div class="meta-item">Progress Filter: {success_mode}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

left_top, right_top = st.columns([2, 1])

with left_top:
    section_header("Top 5 Emission Reducers - CO2 Per Capita Trend", "Long-term trajectories of strongest reducers")
    top5_reducers = (
        filtered_latest.nlargest(5, "co2_reduction_pct_since_2000")[["country", "co2_reduction_pct_since_2000"]]
        .sort_values("co2_reduction_pct_since_2000", ascending=False)
    )
    top5_names = top5_reducers["country"].tolist()
    trend_df = filtered_df[filtered_df["country"].isin(top5_names)].copy()
    fig_trend = px.line(
        trend_df,
        x="year",
        y="co2_per_capita",
        color="country",
        markers=False,
        title="",
        labels={"co2_per_capita": "CO2 Per Capita (t)", "year": "Year"},
    )
    fig_trend = style_figure(fig_trend)
    render_chart(fig_trend)

    st.markdown(
        """
        <div class="verdict">
            Top performers show sustained CO2-per-capita decline since 2000, indicating that decoupling is possible when
            policy consistency and clean energy adoption move together.
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_top:
    section_header("Top 5 Emission Reducers", "Ranked by reduction since 2000")
    fig_rank = px.bar(
        top5_reducers.sort_values("co2_reduction_pct_since_2000"),
        x="co2_reduction_pct_since_2000",
        y="country",
        orientation="h",
        color="co2_reduction_pct_since_2000",
        color_continuous_scale="Tealgrn",
        labels={"co2_reduction_pct_since_2000": "Reduction since 2000 (%)", "country": ""},
        title="",
    )
    fig_rank = style_figure(fig_rank)
    fig_rank.update_layout(showlegend=False, coloraxis_showscale=False)
    render_chart(fig_rank)
    st.markdown(
        """
        <div class="verdict">
            These countries are not necessarily the largest economies; successful emission reduction is driven more by
            structural transition than income alone.
        </div>
        """,
        unsafe_allow_html=True,
    )

mid_left, mid_right = st.columns([2, 1])

with mid_left:
    section_header("Global Emission Change Map", "Country-level reduction and increase distribution")
    map_df = filtered_latest[["country", "iso_code", "co2_reduction_pct_since_2000"]].dropna(subset=["iso_code"]).copy()
    fig_map = px.choropleth(
        map_df,
        locations="iso_code",
        color="co2_reduction_pct_since_2000",
        hover_name="country",
        color_continuous_scale="RdYlGn",
        title="",
        labels={"co2_reduction_pct_since_2000": "% change since 2000"},
    )
    fig_map = style_figure(fig_map)
    fig_map.update_geos(showframe=False, showcoastlines=False, bgcolor="rgba(0,0,0,0)")
    render_chart(fig_map)

with mid_right:
    section_header("GDP vs CO2 Emissions", "Scale vs wealth relationship")
    sc_income = filtered_latest[(filtered_latest["gdp_per_capita_final"] > 0) & (filtered_latest["co2"] > 0)].copy()
    fig_income = px.scatter(
        sc_income,
        x="gdp_per_capita_final",
        y="co2",
        color="region",
        hover_name="country",
        size="population",
        log_x=True,
        log_y=True,
        size_max=50,
        title="",
        labels={"gdp_per_capita_final": "GDP per Capita (log)", "co2": "Total CO2 (Mt, log)"},
    )
    fig_income.update_traces(marker=dict(size=11, opacity=0.85, line=dict(width=0.3, color="white")), selector=dict(mode="markers"))
    fig_income = style_figure(fig_income)
    render_chart(fig_income)

row3_left, row3_right = st.columns(2)

with row3_left:
    section_header("Renewables vs CO2 Per Capita", "Energy transition signal")
    sc6 = filtered_latest[
        (filtered_latest["renewable_share_final"].notna()) & (filtered_latest["co2_per_capita"].notna())
    ].copy()
    fig_renew = px.scatter(
        sc6,
        x="renewable_share_final",
        y="co2_per_capita",
        color="region",
        hover_name="country",
        title="",
        labels={"renewable_share_final": "Renewable Share (%)", "co2_per_capita": "CO2 per Capita (t/person)"},
    )
    if len(sc6) >= 2:
        x = sc6["renewable_share_final"].to_numpy()
        y = sc6["co2_per_capita"].to_numpy()
        m, b = np.polyfit(x, y, 1)
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = m * x_line + b
        fig_renew.add_trace(
            go.Scatter(x=x_line, y=y_line, mode="lines", name="Trend line", line=dict(color="#f43f5e", width=2))
        )
    fig_renew.update_traces(marker=dict(size=10, opacity=0.75), selector=dict(mode="markers"))
    fig_renew = style_figure(fig_renew)
    render_chart(fig_renew)

with row3_right:
    section_header("Scale and Success Bubble Chart", "Population-weighted burden")
    sc7 = filtered_latest[
        (filtered_latest["gdp_per_capita_final"] > 0)
        & (filtered_latest["co2"] > 0)
        & (filtered_latest["population"] > 0)
    ].copy()
    x_low, x_high = sc7["gdp_per_capita_final"].quantile([0.01, 0.99])
    sc7_plot = sc7[sc7["gdp_per_capita_final"].between(x_low, x_high)].copy()
    fig_scale = px.scatter(
        sc7_plot,
        x="gdp_per_capita_final",
        y="co2",
        size="population",
        color="success_label",
        hover_name="country",
        log_x=True,
        size_max=55,
        title="",
        labels={"gdp_per_capita_final": "GDP per Capita (log)", "co2": "CO2 (Mt)"},
    )
    fig_scale.update_traces(marker=dict(sizemin=5), selector=dict(mode="markers"))
    fig_scale = style_figure(fig_scale)
    render_chart(fig_scale)

row4_left, row4_right = st.columns(2)

with row4_left:
    section_header("Correlation Matrix", "Predictor structure overview")
    corr_cols = [
        "co2",
        "co2_per_capita",
        "co2_reduction_pct_since_2000",
        "renewable_share_final",
        "energy_intensity_mj_per_gdp",
        "gdp_per_capita_final",
        "population",
        "primary_energy_consumption",
    ]
    corr_cols = [col for col in corr_cols if col in filtered_df.columns]
    corr_df = filtered_df[corr_cols].dropna()
    corr_mat = corr_df.corr(numeric_only=True)
    fig_corr = px.imshow(
        corr_mat,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        labels=dict(x="Variable", y="Variable", color="Correlation"),
        title="",
    )
    fig_corr = style_figure(fig_corr)
    render_chart(fig_corr)

with row4_right:
    section_header("Regional Emission Dispersion", "Equity and variation across regions")
    sc9 = filtered_latest[filtered_latest["region"].isin(["Africa", "Americas", "Asia", "Europe", "Oceania"])].copy()
    fig_region = px.box(
        sc9,
        x="region",
        y="co2_per_capita",
        color="region",
        points="outliers",
        hover_name="country",
        labels={"region": "Region", "co2_per_capita": "CO2 per Capita (t/person)"},
        title="",
    )
    fig_region = style_figure(fig_region)
    fig_region.update_layout(showlegend=False)
    render_chart(fig_region)

section_header("3D Transition View (GDP, CO2, Renewables)", "Multidimensional transition lens")
plot3d_df = filtered_latest[
    (filtered_latest["gdp_per_capita_final"] > 0)
    & (filtered_latest["co2"] > 0)
    & (filtered_latest["renewable_share_final"].notna())
].copy()
fig_3d = px.scatter_3d(
    plot3d_df,
    x="gdp_per_capita_final",
    y="co2",
    z="renewable_share_final",
    color="region",
    hover_name="country",
    log_x=True,
    log_y=True,
    opacity=0.82,
    title="",
    labels={
        "gdp_per_capita_final": "GDP per Capita (log)",
        "co2": "CO2 (Mt, log)",
        "renewable_share_final": "Renewable Share (%)",
    },
)
fig_3d = style_figure(fig_3d)
fig_3d.update_traces(marker=dict(size=6))
render_chart(fig_3d)


table_left, table_right = st.columns(2)
with table_left:
    section_header(
        "Developed Economies Tend to Decarbonize Earlier and Faster",
        "Average per-capita emissions trajectory by development status",
    )
    dev_trend_series = filtered_df.groupby(["development_status", "year"], as_index=False)["co2_per_capita"].mean()
    fig_dev = px.line(
        dev_trend_series,
        x="year",
        y="co2_per_capita",
        color="development_status",
        markers=True,
        labels={
            "year": "Year",
            "co2_per_capita": "Average CO2 per Capita (t/person)",
            "development_status": "Development Status",
        },
    )
    fig_dev = style_figure(fig_dev)
    fig_dev.update_layout(legend_title_text="Development Status", height=330)
    render_chart(fig_dev)

    section_header("Top 5 Emission Reducers", "Highest CO2 reduction since 2000")
    top5 = filtered_latest.nlargest(5, "co2_reduction_pct_since_2000")[
        ["country", "co2", "co2_reduction_pct_since_2000", "renewable_share_final", "gdp_per_capita_final"]
    ].rename(
        columns={
            "country": "Country",
            "co2": "CO2 (Mt)",
            "co2_reduction_pct_since_2000": "Reduction Since 2000 (%)",
            "renewable_share_final": "Renewable Share (%)",
            "gdp_per_capita_final": "GDP per Capita (USD)",
        }
    )
    st.dataframe(top5, width='stretch', hide_index=True)

with table_right:
    dev_trend = (
        filtered_df.groupby("country")
        .apply(
            lambda x: pd.Series(
                {
                    "co2_2020": x[x["year"] >= 2018]["co2"].mean(),
                    "co2_2000": x[x["year"] <= 2002]["co2"].mean(),
                    "renewable_avg": x["renewable_share_final"].mean(),
                }
            )
        )
        .reset_index()
    )
    dev_trend["5yr_growth_pct"] = ((dev_trend["co2_2020"] - dev_trend["co2_2000"]) / dev_trend["co2_2000"] * 100).fillna(0)
    dev_trend["status"] = dev_trend.apply(
        lambda x: "Improving" if x["5yr_growth_pct"] < -5 and x["renewable_avg"] > 15 else "Worsening", axis=1
    )

    section_header("SDG 13 Status (On-Track vs Off-Track)", "Countries ranked by recent 5-year trajectory")

    def growth_cell_style(v):
        if pd.isna(v):
            return ""
        if v <= 0:
            intensity = min(abs(v) / 12, 1.0)
            alpha = 0.28 + 0.42 * intensity
            return f"background-color: rgba(22,163,74,{alpha:.2f}); color: #d1fae5; font-weight: 700;"
        intensity = min(v / 12, 1.0)
        alpha = 0.28 + 0.42 * intensity
        return f"background-color: rgba(239,68,68,{alpha:.2f}); color: #fee2e2; font-weight: 700;"

    sdg_table = (
        dev_trend[["country", "5yr_growth_pct", "renewable_avg", "status"]]
        .sort_values(
            by=["status", "5yr_growth_pct"],
            key=lambda s: s.map({"Improving": 0, "Worsening": 1}) if s.name == "status" else s,
            ascending=[True, True],
        )
        .rename(
            columns={
                "country": "Country",
                "5yr_growth_pct": "5yr Growth Trend",
                "renewable_avg": "Renewable %",
                "status": "Status",
            }
        )
    )
    sdg_table["Status"] = sdg_table["Status"].map(lambda s: "🟢 Improving" if s == "Improving" else "🔴 Worsening")
    sdg_table["Renewable %"] = sdg_table["Renewable %"].map(lambda v: "None" if pd.isna(v) else f"{v:.1f}%")

    styled_sdg = (
        sdg_table.style
        .format({"5yr Growth Trend": "{:.2f}%"})
        .map(growth_cell_style, subset=["5yr Growth Trend"])
        .set_properties(
            **{
                "background-color": "rgba(15,23,42,0.35)",
                "color": "#e2e8f0",
                "border-color": "rgba(148,163,184,0.14)",
            }
        )
        .set_properties(subset=["Status"], **{"font-weight": "700"})
    )

    st.dataframe(styled_sdg, width='stretch', hide_index=True)

    status_summary = dev_trend["status"].value_counts()
    st.markdown(
        f"""
        <div class="verdict">
            <b>VERDICT - SDG 13 STATUS TABLE</b><br>
            Countries labeled <b>Improving</b>: {int(status_summary.get('Improving', 0))}.<br>
            Countries labeled <b>Worsening</b>: {int(status_summary.get('Worsening', 0))}.<br>
            Classification is based on 5-year CO2 trend direction and renewable-energy penetration.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.sidebar.markdown("---")
st.sidebar.caption(f"Analysis window: 2000-2022 | Latest year: {latest_year}")
st.sidebar.caption("Data sources: OWID + Global Sustainable Energy")
