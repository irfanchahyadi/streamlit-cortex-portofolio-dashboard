import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Custom CSS for Glassmorphic Premium Theme
st.markdown("""
<style>
    /* Load Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap');

    /* Global page styling */
    .stAppViewContainer {
        background: radial-gradient(circle at top left, #f3f8fc, #e5eff9, #d0e3f5) !important;
        font-family: 'Outfit', 'Inter', sans-serif !important;
        color: #1e293b !important;
    }

    /* Main container padding override */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1.2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* Glassmorphic border containers */
    div[data-testid="stVBlockBorderContainer"] {
        background-color: rgba(255, 255, 255, 0.55) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.45) !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04) !important;
        padding: 1rem !important;
        margin-bottom: 0rem !important;
    }

    /* Card styling details */
    .card-header-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
    }
    
    .card-subtitle-small {
        font-size: 0.8rem;
        color: #64748b;
        font-weight: normal;
    }

    .kpi-title {
        font-size: 0.85rem;
        color: #475569;
        font-weight: 500;
    }

    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 0.15rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .badge-success {
        background-color: #d1fae5;
        color: #065f46;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.15rem 0.4rem;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
    }

    .badge-danger {
        background-color: #fee2e2;
        color: #991b1b;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.15rem 0.4rem;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
    }

    .badge-info {
        background-color: #e0f2fe;
        color: #075985;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.15rem 0.4rem;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
    }

    /* Header component styles */
    .header-logo {
        width: 34px;
        height: 34px;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white !important;
        font-weight: bold;
        font-size: 1.1rem;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);
    }

    .header-title {
        font-size: 1.55rem;
        font-weight: 700;
        color: #1e3a8a;
        margin: 0;
        line-height: 1.2;
    }

    .header-subtitle {
        font-size: 0.88rem;
        color: #475569;
        margin: 0;
        margin-top: 0.1rem;
    }

    /* Variance items in lists */
    .variance-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.45rem 0;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .variance-item:last-child {
        border-bottom: none;
    }

    .variance-sub-card {
        text-align: center;
        background: rgba(255, 255, 255, 0.4);
        border-radius: 8px;
        padding: 0.4rem;
        border: 1px solid rgba(255, 255, 255, 0.25);
    }
    
    .val-pos {
        color: #059669;
        font-size: 0.95rem;
        font-weight: 700;
    }
    
    .desc {
        color: #64748b;
        font-size: 0.7rem;
    }

    /* Override Streamlit Widget Margins */
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }
    
    /* Make slider handle blue without affecting labels */
    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #3b82f6 !important;
    }

    /* Reduce vertical gap between elements in a block */
    div[data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }

    /* Set checkbox label text color to black */
    div[data-testid="stCheckbox"] label, 
    div[data-testid="stCheckbox"] label p, 
    div[data-testid="stCheckbox"] label span {
        color: #000000 !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Helper Functions for KPI Cards -----------------
def render_kpi(label, value, badge_text=None, badge_type="success"):
    badge_html = ""
    if badge_text:
        badge_class = f"badge-{badge_type}"
        badge_html = f'<span class="{badge_class}">{badge_text}</span>'
    
    st.markdown(
        f'<div style="display: flex; flex-direction: column;">'
        f'<div class="kpi-title">{label}</div>'
        f'<div class="kpi-value">{value}{badge_html}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

# ----------------- Dynamic Chart Generation -----------------
def generate_scenario_chart(price, sector="Oil & Gas"):
    years = ['2024', '2025', '2026', '2027', '2028']
    
    # 3 different baselines for the 3 sectors with fluctuated trends
    sector_baselines = {
        "Oil & Gas": [10.5, 12.2, 11.0, 12.8, 13.5],
        "Power": [15.2, 14.5, 16.8, 16.0, 17.8],
        "Mining": [22.0, 26.5, 21.0, 27.2, 28.0]
    }
    baseline = sector_baselines.get(sector, sector_baselines["Oil & Gas"])
    
    # Confidence intervals for Baseline
    baseline_upper = [val * 1.12 for val in baseline]
    baseline_lower = [val * 0.90 for val in baseline]
    
    fig = go.Figure()
    
    # Shaded band for Baseline scenario
    fig.add_trace(go.Scatter(
        x=years + years[::-1],
        y=baseline_upper + baseline_lower[::-1],
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.12)',
        line=dict(color='rgba(255, 255, 255, 0)'),
        hoverinfo="skip",
        showlegend=False
    ))
    
    # Baseline border lines
    fig.add_trace(go.Scatter(
        x=years,
        y=baseline_upper,
        mode='lines',
        line=dict(color='rgba(59, 130, 246, 0.45)', width=1.2, dash='dot'),
        hoverinfo="skip",
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=years,
        y=baseline_lower,
        mode='lines',
        line=dict(color='rgba(59, 130, 246, 0.45)', width=1.2, dash='dot'),
        hoverinfo="skip",
        showlegend=False
    ))
    
    # Baseline line
    fig.add_trace(go.Scatter(
        x=years,
        y=baseline,
        mode='lines',
        name='Baseline',
        line=dict(color='#2563eb', width=2.5, dash='dash')
    ))
    
    fig.update_layout(
        margin=dict(l=35, r=10, t=10, b=20),
        height=190,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(
            tickprefix='$',
            ticksuffix='B',
            gridcolor='rgba(0,0,0,0.06)',
            zeroline=False,
            tickfont=dict(size=13, color='#64748b')
        ),
        xaxis=dict(
            gridcolor='rgba(0,0,0,0.06)',
            tickfont=dict(size=13, color='#64748b')
        ),
        showlegend=False,
        hovermode='x'
    )
    return fig

def generate_revenue_forecast_chart(sector="Oil & Gas", price_ref="$75/bbl"):
    # 1. Timeline from Jan 2025 until Dec 2026 (24 months) generated dynamically
    months = pd.date_range(start="2025-01-01", end="2026-12-01", freq="MS").strftime("%b%y").tolist()
    
    # 3 different actuals series for the 3 sectors with fluctuated trends
    sector_actuals = {
        "Oil & Gas": [5.5, 5.2, 6.4, 7.1, 7.3, 8.5, 8.8, 9.2, 8.4, 9.7],
        "Power": [10.0, 11.5, 10.8, 11.2, 11.5, 10.9, 11.1, 11.4, 12.5, 13.8],
        "Mining": [15.0, 14.2, 16.5, 15.2, 15.8, 14.9, 16.9, 16.3, 16.5, 17.2]
    }
    base_actuals = sector_actuals.get(sector, sector_actuals["Oil & Gas"])
    
    # Parse number from price_ref as factor (e.g. "$75/bbl" -> 75)
    try:
        price_num = float(price_ref.replace("$", "").split("/")[0])
    except Exception:
        price_num = 75.0
    factor = price_num / 75.0
    
    actuals = [val * factor for val in base_actuals]
    n = len(actuals)
    
    # 2. Dynamically calculate P50 forecast with a random walk (adding organic fluctuations)
    if n > 1:
        diffs = [actuals[i] - actuals[i-1] for i in range(1, n)]
        avg_increase = sum(diffs) / len(diffs)
    else:
        avg_increase = 0.0
        
    import random
    rng = random.Random(42)  # Seeded local generator for stable visual formatting
    
    p50_forecast = [actuals[-1]]
    for i in range(1, 24 - n + 1):
        # Add random noise step around the average growth increment
        noise = rng.uniform(-0.6, 0.6)
        next_val = p50_forecast[-1] + avg_increase + noise
        p50_forecast.append(next_val)
        
    p50 = [None] * (n - 1) + p50_forecast
    
    # 3. Dynamically calculate P90 and P95 confidence intervals around P50 forecast
    base_uncertainty = actuals[-1] * 0.08
    growth_rate = actuals[-1] * 0.04
    
    p90_upper_forecast = []
    p90_lower_forecast = []
    p95_upper_forecast = []
    p95_lower_forecast = []
    for i, p50_val in enumerate(p50_forecast):
        # Uncertainty expands over time
        uncertainty_p90 = base_uncertainty + growth_rate * (i ** 0.5)
        uncertainty_p95 = uncertainty_p90 * 1.35  # Wider band for P95 (approx 1.96 / 1.645 multiplier with scaling)
        p90_upper_forecast.append(p50_val + uncertainty_p90)
        p90_lower_forecast.append(p50_val - uncertainty_p90)
        p95_upper_forecast.append(p50_val + uncertainty_p95)
        p95_lower_forecast.append(p50_val - uncertainty_p95)
        
    p90_upper = [None] * (n - 1) + p90_upper_forecast
    p90_lower = [None] * (n - 1) + p90_lower_forecast
    p95_upper = [None] * (n - 1) + p95_upper_forecast
    p95_lower = [None] * (n - 1) + p95_lower_forecast
    
    fig = go.Figure()
    
    # Shaded band for P95 confidence interval (outermost, lighter color)
    x_fill = months[n-1:]
    fig.add_trace(go.Scatter(
        x=x_fill + x_fill[::-1],
        y=p95_upper[n-1:] + p95_lower[n-1:][::-1],
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.05)',
        line=dict(color='rgba(255, 255, 255, 0)'),
        hoverinfo="skip",
        showlegend=False
    ))
    
    # Shaded band for P90 confidence interval (inner, slightly darker)
    fig.add_trace(go.Scatter(
        x=x_fill + x_fill[::-1],
        y=p90_upper[n-1:] + p90_lower[n-1:][::-1],
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.10)',
        line=dict(color='rgba(255, 255, 255, 0)'),
        hoverinfo="skip",
        showlegend=False
    ))
    
    # P95 Upper Border Line
    fig.add_trace(go.Scatter(
        x=months[n-1:],
        y=p95_upper[n-1:],
        mode='lines',
        name='P95',
        line=dict(color='rgba(59, 130, 246, 0.55)', width=1.5, dash='dot'),
        showlegend=True,
        legendrank=4
    ))
    
    # P95 Lower Border Line
    fig.add_trace(go.Scatter(
        x=months[n-1:],
        y=p95_lower[n-1:],
        mode='lines',
        name='P95 Lower',
        line=dict(color='rgba(59, 130, 246, 0.55)', width=1.5, dash='dot'),
        showlegend=False
    ))
    
    # P90 Upper Border Line
    fig.add_trace(go.Scatter(
        x=months[n-1:],
        y=p90_upper[n-1:],
        mode='lines',
        name='P90',
        line=dict(color='rgba(59, 130, 246, 0.75)', width=1.5, dash='dash'),
        showlegend=True,
        legendrank=3
    ))
    
    # P90 Lower Border Line
    fig.add_trace(go.Scatter(
        x=months[n-1:],
        y=p90_lower[n-1:],
        mode='lines',
        name='P90 Lower',
        line=dict(color='rgba(59, 130, 246, 0.75)', width=1.5, dash='dash'),
        showlegend=False
    ))
    
    # Actual Revenue Line
    fig.add_trace(go.Scatter(
        x=months[:n],
        y=actuals,
        mode='lines+markers',
        name='Actual',
        line=dict(color='#1e3a8a', width=3),
        marker=dict(size=6, color='#1e3a8a'),
        legendrank=1
    ))
    
    # P50 Forecast Line
    fig.add_trace(go.Scatter(
        x=months[n-1:],
        y=p50[n-1:],
        mode='lines+markers',
        name='P50',
        line=dict(color='#3b82f6', width=2.5),
        marker=dict(size=4, color='#3b82f6'),
        legendrank=2
    ))
    
    fig.update_layout(
        margin=dict(l=35, r=10, t=10, b=55),
        height=220,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(
            tickprefix='$',
            ticksuffix='M',
            gridcolor='rgba(0,0,0,0.06)',
            zeroline=False,
            tickfont=dict(size=13, color='#64748b')
        ),
        xaxis=dict(
            categoryorder="array",
            categoryarray=months,
            gridcolor='rgba(0,0,0,0.06)',
            tickfont=dict(size=13, color='#64748b')
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.48,
            xanchor="center",
            x=0.5,
            font=dict(size=13, color='#64748b')
        ),
        hovermode='x unified'
    )
    return fig

def generate_variance_chart():
    categories = ['Revenue', 'Expenses', 'Budget', 'Profit (EBIT)']
    
    ytd_actual = [86.4, 55.2, 90.7, 31.2]
    forecast = [90.7, 58.5, 95.2, 32.2]
    budget = [120.0, 80.0, 120.0, 40.0]
    variance = [4.3, 1.2, 1.2, 8.1]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='YTD Actual',
        x=categories,
        y=ytd_actual,
        marker_color='#2563eb'
    ))
    
    fig.add_trace(go.Bar(
        name='Forecast',
        x=categories,
        y=forecast,
        marker_color='#60a5fa'
    ))
    
    fig.add_trace(go.Bar(
        name='Budget',
        x=categories,
        y=budget,
        marker_color='#1d4ed8'
    ))
    
    # Variance bars colored green or red depending on value
    var_colors = ['#10b981' if v >= 0 else '#ef4444' for v in variance]
    fig.add_trace(go.Bar(
        name='Variance',
        x=categories,
        y=variance,
        marker_color=var_colors
    ))
    
    fig.update_layout(
        barmode='group',
        margin=dict(l=35, r=10, t=10, b=55),
        height=220,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(
            tickprefix='$',
            ticksuffix='M',
            gridcolor='rgba(0,0,0,0.06)',
            zeroline=False,
            tickfont=dict(size=13, color='#64748b')
        ),
        xaxis=dict(
            gridcolor='rgba(0,0,0,0.06)',
            tickfont=dict(size=13, color='#64748b')
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.48,
            xanchor="center",
            x=0.5,
            font=dict(size=13, color='#64748b')
        ),
        hovermode='x unified'
    )
    return fig

# ----------------- Top Header Row -----------------
col_h_left, col_h_right = st.columns([0.8, 0.2])
with col_h_left:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.8rem;">
            <div class="header-logo">✓</div>
            <div>
                <h1 class="header-title">Budgeting & Forecasting</h1>
                <p class="header-subtitle">Rolling forecasts integrated with actuals.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
with col_h_right:
    st.markdown("""
        <div style="display: flex; justify-content: flex-end; align-items: center; gap: 15px; margin-top: 10px; color: #1e3a8a; font-size: 1.25rem;">
            <span style="cursor: pointer; opacity: 0.8;">⚙️</span>
            <span style="cursor: pointer; opacity: 0.8;">🎛️</span>
            <span style="cursor: pointer; background-color: #2563eb; color: white; width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.95rem; box-shadow: 0 4px 8px rgba(37, 99, 235, 0.2);">JD</span>
        </div>
    """, unsafe_allow_html=True)

# ----------------- Main Layout Grid -----------------
col_left, col_right = st.columns([0.68, 0.32], gap="medium")

# LEFT COLUMN: Core Charts and KPI Widgets
with col_left:
    # Row 1: KPI Metrics
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3, gap="small")
    with col_kpi1:
        with st.container(border=True):
            render_kpi("Annual Budget", "$120M")
            
    with col_kpi2:
        with st.container(border=True):
            render_kpi("Year-to-Date Actuals", "$86.4M")
            
    with col_kpi3:
        with st.container(border=True):
            render_kpi("YTD Forecast", "$90.7M", "▲ 5%", "success")

    st.markdown('<div style="margin-top: 0.2rem;"></div>', unsafe_allow_html=True)

    # Row 2: Revenue Forecast Chart
    with st.container(border=True):
        st.markdown('<div class="card-header-title">Revenue Forecast</div>', unsafe_allow_html=True)
        
        # Inline selectors inside the card body directly (1 level of nesting inside col_left)
        sel1, sel2, sel3 = st.columns(3)
        with sel1:
            selected_sector = st.selectbox("Sector", ["Oil & Gas", "Power", "Mining"], label_visibility="collapsed", key="forecast_sector")
        with sel2:
            selected_price_ref = st.selectbox("Price Reference", ["$75/bbl", "$80/bbl", "$90/bbl"], label_visibility="collapsed", key="forecast_price_ref")
        with sel3:
            st.checkbox("Probabilistic", value=True, key="prob_check")
                
        st.plotly_chart(generate_revenue_forecast_chart(selected_sector, selected_price_ref), use_container_width=True, key="rev_forecast_chart")

    st.markdown('<div style="margin-top: 0.2rem;"></div>', unsafe_allow_html=True)

    # Row 3: Variance Analysis
    with st.container(border=True):
        col_v_title, col_v_opt = st.columns([0.7, 0.3])
        with col_v_title:
            st.markdown('<div class="card-header-title">Variance Analysis: YTD vs. Budget</div>', unsafe_allow_html=True)
        with col_v_opt:
            st.selectbox("Analysis Mode", ["Automated", "Manual"], key="var_mode", label_visibility="collapsed")
            
        st.plotly_chart(generate_variance_chart(), use_container_width=True, key="variance_analysis_chart")
        
        # Sub-metrics below chart
        col_v1, col_v2, col_v3, col_v4 = st.columns(4, gap="small")
        with col_v1:
            st.markdown("""
                <div class="variance-sub-card">
                    <div class="val-pos">+$4.3M</div>
                    <div class="desc">before budget</div>
                </div>
            """, unsafe_allow_html=True)
        with col_v2:
            st.markdown("""
                <div class="variance-sub-card">
                    <div class="val-pos">+$1.2M</div>
                    <div class="desc">balance: (.1%)</div>
                </div>
            """, unsafe_allow_html=True)
        with col_v3:
            st.markdown("""
                <div class="variance-sub-card">
                    <div class="val-pos" style="color: #2563eb;">▲ $1.2M</div>
                    <div class="desc">[3% change]</div>
                </div>
            """, unsafe_allow_html=True)
        with col_v4:
            st.markdown("""
                <div class="variance-sub-card">
                    <div class="val-pos">▲ $8.1M</div>
                    <div class="desc">above budget</div>
                </div>
            """, unsafe_allow_html=True)

# RIGHT COLUMN: What-If Scenarios & Top Variances
with col_right:
    # Card 1: What-If Scenario Modeling
    with st.container(border=True):
        col_w_title, col_w_opt = st.columns([0.5, 0.5])
        with col_w_title:
            st.markdown('<div class="card-header-title" style="margin-top:4px;">What-If Scenario Modeling</div>', unsafe_allow_html=True)
        with col_w_opt:
            # Inline price selector
            commodity_price = st.selectbox(
                "Commodity Price:", 
                options=[60, 70, 75, 80, 90], 
                index=2,
                format_func=lambda x: f"${x}/bbl",
                key="scenario_price_selector"
            )
            
        # Chart
        # Pass the globally selected sector to the chart generator
        st.plotly_chart(generate_scenario_chart(commodity_price, selected_sector), use_container_width=True, key="scenario_chart")
        
        # Interactive Slider underneath the chart
        adjusted_price = st.slider(
            "Adjust Price", 
            min_value=60, 
            max_value=90, 
            value=commodity_price, 
            step=1,
            label_visibility="collapsed",
            key="scenario_slider"
        )
        
        # Adjusted Revenue calculation based on slider price sensitivity and dynamic sector baseline
        sector_base_revenues = {
            "Oil & Gas": 120.5,
            "Power": 180.0,
            "Mining": 250.0
        }
        base_revenue = sector_base_revenues.get(selected_sector, 120.5)
        calculated_rev = base_revenue * (adjusted_price / 75.0)
        
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem; padding: 0.5rem; background: rgba(255,255,255,0.4); border-radius: 8px;">
                <span class="kpi-title" style="color: #0f172a; font-weight:600; font-size:0.9rem;">Adjusted Revenue:</span>
                <span style="font-size:1.15rem; font-weight:700; color:#2563eb;">${calculated_rev:.1f}M</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 0.2rem;"></div>', unsafe_allow_html=True)

    # Card 2: Top Variances Widget 1
    with st.container(border=True):
        col_t1_title, col_t1_opt = st.columns([0.6, 0.4])
        with col_t1_title:
            st.markdown('<div class="card-header-title">Top Variances</div>', unsafe_allow_html=True)
        with col_t1_opt:
            st.selectbox("Filter 1", ["Automated", "Manual"], key="t1_filter", label_visibility="collapsed")
            
        # Dynamically render variances for Card 2
        variances_data = [
            {"label": "Oil Revenue", "val": 4.0, "pct": 8},
            {"label": "Labor Costs", "val": -0.8, "pct": -4},
            {"label": "Maintenance Costs", "val": -1.1, "pct": -7}
        ]
        
        items_html = ""
        for item in variances_data:
            pct_str = f"+{item['pct']}%" if item['pct'] >= 0 else f"{item['pct']}%"
            arrow = "▲" if item['val'] >= 0 else "▼"
            color = "#059669" if item['val'] >= 0 else "#dc2626"
            val_display = f"▲ ${item['val']:.1f}M" if item['val'] >= 0 else f"-${abs(item['val']):.1f}M"
            
            items_html += f"""
            <div class="variance-item">
                <span class="kpi-title" style="color:#0f172a; font-weight:600; display:flex; align-items:center; gap:6px;">
                    <span style="color:{color}; font-size: 0.75rem;">{arrow}</span>{item['label']}
                    <span class="card-subtitle-small" style="color:{color}; font-weight:500; margin-left:2px;">{pct_str}</span>
                </span>
                <span style="color:{color}; font-weight:700; font-size:0.9rem;">{val_display}</span>
            </div>
            """
        st.markdown(items_html, unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 0.2rem;"></div>', unsafe_allow_html=True)

    # Card 3: Top Variances Widget 2
    with st.container(border=True):
        st.markdown('<div class="card-header-title">Top Variances</div>', unsafe_allow_html=True)
        
        # Dynamically render variances based on positive/negative value sign
        variances_data = [
            {"label": "Oil Revenue", "val": 4.0, "pct": 8},
            {"label": "Labor Costs", "val": -0.8, "pct": -4},
            {"label": "Maintenance Costs", "val": -1.1, "pct": -7}
        ]
        
        items_html = ""
        for i, item in enumerate(variances_data):
            val_str = f"+${abs(item['val']):.1f}M" if item['val'] >= 0 else f"-${abs(item['val']):.1f}M"
            pct_str = f"+{item['pct']}%" if item['pct'] >= 0 else f"{item['pct']}%"
            arrow = "▲" if item['val'] >= 0 else "▼"
            color = "#059669" if item['val'] >= 0 else "#dc2626"
            badge_class = "badge-success" if item['val'] >= 0 else "badge-danger"
            padding_style = "padding-bottom: 0.5rem;" if i == 0 else ("padding: 0.5rem 0;" if i == 1 else "padding-top: 0.5rem; border:none;")
            
            items_html += f"""
            <div class="variance-item" style="{padding_style}">
                <span class="kpi-title" style="color:#0f172a; font-weight:600;">
                    <span style="color:{color}; font-size:0.75rem; margin-right:4px;">{arrow}</span>{item['label']} <span class="card-subtitle-small" style="color:{color}; font-weight:500; margin-left:2px;">{pct_str}</span>
                </span>
                <span class="{badge_class}" style="font-size:0.82rem; padding: 0.2rem 0.5rem;">{val_str}</span>
            </div>
            """
        st.markdown(items_html, unsafe_allow_html=True)
