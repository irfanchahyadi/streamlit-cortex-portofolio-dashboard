import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import math

# Custom CSS for Glassmorphic Blue Theme (Matching the user's mockup image)
st.markdown("""
<style>
    /* Load Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap');

    /* Global page styling */
    .stAppViewContainer {
        background: radial-gradient(circle at top left, #ebf4fc, #d5e6f7, #c1daf2) !important;
        font-family: 'Outfit', 'Inter', sans-serif !important;
        color: #1e3a8a !important;
    }

    /* Main container padding override */
    .block-container {
        padding-top: 3.8rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }

    /* Glassmorphic border containers */
    div[data-testid="stVBlockBorderContainer"] {
        background: linear-gradient(135deg, rgba(240, 249, 255, 0.7) 0%, rgba(219, 239, 255, 0.7) 100%) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-radius: 14px !important;
        border: 2px solid rgba(255, 255, 255, 0.85) !important;
        box-shadow: 0 10px 30px -5px rgba(59, 130, 246, 0.12), 0 8px 10px -6px rgba(59, 130, 246, 0.08) !important;
        padding: 0.8rem 1rem !important;
        margin-bottom: 0rem !important;
    }

    /* Reduce vertical gap between elements in a block */
    div[data-testid="stVerticalBlock"] {
        gap: 0.4rem !important;
    }

    /* Custom styles for headers and titles */
    .section-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #1e3a8a;
        margin-bottom: 0.6rem;
    }

    .chart-container-title {
        font-size: 1rem;
        font-weight: 600;
        color: #0369a1;
        margin-bottom: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Handle Interactivity & Query Params -----------------
if "asset" in st.query_params:
    st.session_state.selected_asset = st.query_params["asset"]
elif 'selected_asset' not in st.session_state:
    st.session_state.selected_asset = 'Asset B'

# Dummy data for active asset select details
asset_data = {
    'Asset A': {
        'budget': '$3.2M',
        'progress': 85,
        'issues': 2,
        'milestones': 12,
        'variance': '+2 Days',
        'dome_color': 'rgba(16, 185, 129, 0.12)',
        'dome_stroke': '#10b981',
        'progress_color': '#10b981',
        'needle_color': '#065f46',
        'issue_bars': [2, 1, 3, 2, 1, 2, 1],
        'issue_bar_color': '#34d399'
    },
    'Asset B': {
        'budget': '$4.5M',
        'progress': 65,
        'issues': 8,
        'milestones': 8,
        'variance': '+15 Days',
        'dome_color': 'rgba(37, 99, 235, 0.12)',
        'dome_stroke': '#2563eb',
        'progress_color': '#3b82f6',
        'needle_color': '#1e3a8a',
        'issue_bars': [4, 6, 3, 7, 5, 4, 6],
        'issue_bar_color': '#60a5fa'
    },
    'Asset C': {
        'budget': '$6.5M',
        'progress': 40,
        'issues': 14,
        'milestones': 5,
        'variance': '+32 Days',
        'dome_color': 'rgba(239, 68, 68, 0.12)',
        'dome_stroke': '#ef4444',
        'progress_color': '#f87171',
        'needle_color': '#991b1b',
        'issue_bars': [6, 9, 8, 12, 10, 11, 14],
        'issue_bar_color': '#f87171'
    }
}

# ----------------- Helper Functions for HTML & SVGs -----------------
def draw_html(html_str):
    """Draw HTML cleanly by replacing newlines to prevent markdown parsing errors."""
    st.markdown(html_str.replace('\n', ' '), unsafe_allow_html=True)

def render_dome_svg(stroke_color, fill_color):
    return f"""
    <svg viewBox="0 0 100 50" style="width: 100%; height: 50px; margin-top: 5px; display: block;">
        <path d="M 10 50 A 40 40 0 0 1 90 50 Z" fill="{fill_color}" stroke="{stroke_color}" stroke-width="2"/>
    </svg>
    """

def render_gauge_svg(progress_pct, stroke_color, needle_color):
    dash_array = (progress_pct / 100) * 125.6
    angle_deg = 180 - 180 * (progress_pct / 100)
    angle_rad = angle_deg * math.pi / 180
    dx = 30 * math.cos(angle_rad)
    dy = 30 * math.sin(angle_rad)
    x2 = 50 - dx
    y2 = 50 - dy
    return f"""
    <svg viewBox="0 0 100 50" style="width: 100%; height: 50px; margin-top: 5px; display: block;">
        <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#e2e8f0" stroke-width="7" stroke-linecap="round"/>
        <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="{stroke_color}" stroke-width="7" stroke-dasharray="{dash_array} 125.6" stroke-linecap="round"/>
        <line x1="50" y1="50" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{needle_color}" stroke-width="2.5" stroke-linecap="round"/>
        <circle cx="50" cy="50" r="3.5" fill="{needle_color}"/>
    </svg>
    """

def render_issue_bars_svg(bars, bar_color):
    max_val = max(bars) if bars else 1
    svg_rects = []
    width = 8
    spacing = 4
    start_x = 10
    for i, val in enumerate(bars):
        height = (val / max_val) * 28
        y = 35 - height
        x = start_x + i * (width + spacing)
        svg_rects.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="1.5" fill="{bar_color}"/>')
    
    return f"""
    <svg viewBox="0 0 100 40" style="width: 100%; height: 40px; margin-top: 5px; display: block;">
        {"".join(svg_rects)}
    </svg>
    """

# ----------------- Top Header Row -----------------
title_html = """
<div style="text-align: center; margin-bottom: 0.8rem; padding-top: 0.5rem; position: relative; width: 100%;">
    <div style="display: flex; align-items: center; justify-content: center; gap: 15px; width: 100%;">
        <div style="flex-grow: 1; height: 1.5px; background: linear-gradient(to right, rgba(30, 58, 138, 0), rgba(30, 58, 138, 0.4));"></div>
        <div style="font-family: 'Outfit', sans-serif; font-weight: 700; color: #1e3a8a; font-size: 1.8rem; margin: 0; padding: 0 15px; letter-spacing: -0.5px; white-space: nowrap;">Executive Portfolio Dashboard</div>
        <div style="flex-grow: 1; height: 1.5px; background: linear-gradient(to left, rgba(30, 58, 138, 0), rgba(30, 58, 138, 0.4));"></div>
    </div>
</div>
"""
draw_html(title_html)

# ----------------- Top Row: 5 KPI Columns -----------------
col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns([1, 1, 1, 1, 1.25], gap="small")

def render_top_kpi(title, value):
    draw_html(f"""
        <div style="text-align: center; padding: 0.2rem 0;">
            <div style="font-size: 0.82rem; color: #0284c7; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">{title}</div>
            <div style="height: 1px; background: rgba(0, 0, 0, 0.06); margin: 0.3rem auto 0.4rem auto; width: 65%;"></div>
            <div style="font-size: 1.85rem; font-weight: 700; color: #1e3a8a; letter-spacing: -0.5px;">{value}</div>
        </div>
    """)

with col_kpi1:
    with st.container(border=True):
        render_top_kpi("Total Portfolio", "$325M")

with col_kpi2:
    with st.container(border=True):
        render_top_kpi("Active Projects", "24")

with col_kpi3:
    with st.container(border=True):
        render_top_kpi("Completed", "56")

with col_kpi4:
    with st.container(border=True):
        render_top_kpi("At Risk", "5")

with col_kpi5:
    with st.container(border=True):
        fig_g = go.Figure(go.Indicator(
            mode = "gauge",
            value = 78,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100], 'visible': False},
                'bar': {'color': '#1e3a8a', 'thickness': 0.22},
                'bgcolor': 'rgba(0,0,0,0)',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 20], 'color': '#e0f2fe'},
                    {'range': [20, 40], 'color': '#bae6fd'},
                    {'range': [40, 60], 'color': '#7dd3fc'},
                    {'range': [60, 80], 'color': '#38bdf8'},
                    {'range': [80, 100], 'color': '#0284c7'}
                ],
            }
        ))
        fig_g.update_layout(
            margin=dict(l=5, r=5, t=5, b=5),
            height=70,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_g, use_container_width=True, key="top_gauge_chart", config={'displayModeBar': False})

st.markdown('<div style="margin-top: 0.1rem;"></div>', unsafe_allow_html=True)

# ----------------- Row 2: Left & Right -----------------
col_left, col_right = st.columns([0.5, 0.5], gap="small")

with col_left:
    # 1. Portfolio Performance Over Time Card
    with st.container(border=True):
        st.markdown('<div class="section-title">Portfolio Performance Over Time</div>', unsafe_allow_html=True)
        
        months = ['Jan', 'Mar', 'May', 'Jun', 'Jul', 'Sep', 'Nov']
        df_perf = pd.DataFrame({
            'Month': months,
            'Target': [16, 30, 27, 31, 27, 37, 44],
            'Actual': [10, 22, 18, 28, 24, 39, 36],
            'Forecast': [6, 12, 10, 15, 17, 20, 24]
        })
        
        fig_perf = go.Figure()
        fig_perf.add_trace(go.Scatter(x=df_perf['Month'], y=df_perf['Target'], mode='lines+markers', name='Target', line=dict(shape='linear', color='#1e3a8a', width=3), marker=dict(size=5)))
        fig_perf.add_trace(go.Scatter(x=df_perf['Month'], y=df_perf['Actual'], mode='lines+markers', name='Actual', line=dict(shape='linear', color='#2563eb', width=2.5), marker=dict(size=5)))
        fig_perf.add_trace(go.Scatter(x=df_perf['Month'], y=df_perf['Forecast'], mode='lines+markers', name='Forecast', line=dict(shape='linear', color='#60a5fa', width=2), marker=dict(size=5)))

        fig_perf.update_layout(
            margin=dict(l=30, r=10, t=10, b=10),
            height=165,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.06)', tickfont=dict(color='#1e3a8a', size=13)),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.06)', tickfont=dict(color='#1e3a8a', size=13), range=[0, 48])
        )
        st.plotly_chart(fig_perf, use_container_width=True, key="perf_line_chart", config={'displayModeBar': False})

    # 2. Asset Overview Card (Interactive selections using anchor links)
    with st.container(border=True):
        st.markdown('<div class="section-title">Asset Overview</div>', unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns(3, gap="small")
        
        # Asset A Card
        with col_a:
            is_sel_a = (st.session_state.selected_asset == 'Asset A')
            border_style = "border: 2px solid #2563eb;" if is_sel_a else "border: 1px solid rgba(0, 0, 0, 0.08);"
            bg_style = "background: linear-gradient(180deg, #ffffff 0%, #f0f9ff 100%);" if is_sel_a else "background: #ffffff;"
            shadow_style = "box-shadow: 0 0 12px rgba(37,99,235,0.2);" if is_sel_a else "box-shadow: 0 2px 4px rgba(0,0,0,0.03);"
            
            draw_html(f"""
                <a href="?asset=Asset%20A" target="_self" style="text-decoration: none; color: inherit; display: block;">
                    <div style="border-radius: 10px; {border_style} {shadow_style} {bg_style} overflow: hidden; text-align: center; display: flex; flex-direction: column; height: 115px; transition: transform 0.2s;">
                        <div style="background: #e0f2fe; padding: 4px; font-weight: 600; font-size: 0.85rem; color: #0369a1;">Asset A</div>
                        <div style="font-size: 1.55rem; font-weight: 700; color: #1e3a8a; padding: 10px 0; flex-grow:1; display:flex; align-items:center; justify-content:center; letter-spacing: -0.5px;">$85M</div>
                        <div style="background: #10b981; color: white; padding: 4px 0; font-weight: 600; font-size: 0.75rem;">On Track</div>
                    </div>
                </a>
            """)

        # Asset B Card
        with col_b:
            is_sel_b = (st.session_state.selected_asset == 'Asset B')
            border_style = "border: 2px solid #2563eb;" if is_sel_b else "border: 1px solid rgba(0, 0, 0, 0.08);"
            bg_style = "background: linear-gradient(180deg, #ffffff 0%, #f0f9ff 100%);" if is_sel_b else "background: #ffffff;"
            shadow_style = "box-shadow: 0 0 12px rgba(37,99,235,0.2);" if is_sel_b else "box-shadow: 0 2px 4px rgba(0,0,0,0.03);"
            
            draw_html(f"""
                <a href="?asset=Asset%20B" target="_self" style="text-decoration: none; color: inherit; display: block;">
                    <div style="border-radius: 10px; {border_style} {shadow_style} {bg_style} overflow: hidden; text-align: center; display: flex; flex-direction: column; height: 115px; transition: transform 0.2s;">
                        <div style="background: #e0f2fe; padding: 4px; font-weight: 600; font-size: 0.85rem; color: #0369a1;">Asset B</div>
                        <div style="font-size: 1.55rem; font-weight: 700; color: #1e3a8a; padding: 10px 0; flex-grow:1; display:flex; align-items:center; justify-content:center; letter-spacing: -0.5px;">$120M</div>
                        <div style="background: #f87171; color: white; padding: 4px 0; font-weight: 600; font-size: 0.75rem;">At Risk</div>
                    </div>
                </a>
            """)

        # Asset C Card
        with col_c:
            is_sel_c = (st.session_state.selected_asset == 'Asset C')
            border_style = "border: 2px solid #2563eb;" if is_sel_c else "border: 1px solid rgba(0, 0, 0, 0.08);"
            bg_style = "background: linear-gradient(180deg, #ffffff 0%, #f0f9ff 100%);" if is_sel_c else "background: #ffffff;"
            shadow_style = "box-shadow: 0 0 12px rgba(37,99,235,0.2);" if is_sel_c else "box-shadow: 0 2px 4px rgba(0,0,0,0.03);"
            
            draw_html(f"""
                <a href="?asset=Asset%20C" target="_self" style="text-decoration: none; color: inherit; display: block;">
                    <div style="border-radius: 10px; {border_style} {shadow_style} {bg_style} overflow: hidden; text-align: center; display: flex; flex-direction: column; height: 115px; transition: transform 0.2s;">
                        <div style="background: #e0f2fe; padding: 4px; font-weight: 600; font-size: 0.85rem; color: #0369a1;">Asset C</div>
                        <div style="font-size: 1.55rem; font-weight: 700; color: #1e3a8a; padding: 10px 0; flex-grow:1; display:flex; align-items:center; justify-content:center; letter-spacing: -0.5px;">$65M</div>
                        <div style="background: #3b82f6; color: white; padding: 4px 0; font-weight: 600; font-size: 0.75rem;">Delayed</div>
                    </div>
                </a>
            """)

with col_right:
    # 3. Selected Asset Details Card
    with st.container(border=True):
        selected_asset = st.session_state.selected_asset
        sel_data = asset_data[selected_asset]
        
        st.markdown(f'<div class="section-title">{selected_asset} - Project Details</div>', unsafe_allow_html=True)
        
        # Single CSS Grid block for details cards to prevent overlapping issues
        details_html = f"""
        <div style="display: flex; flex-direction: column; gap: 16px; width: 100%; margin-top: 5px;">
            <!-- Row 1: Budget, Progress, Issues -->
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
                <!-- Budget -->
                <div style="background: white; border-radius: 12px; border: 1.5px solid rgba(255,255,255,0.85); box-shadow: 0 4px 8px rgba(0,0,0,0.04); padding: 8px; text-align: center; display: flex; flex-direction: column; justify-content: space-between; height: 145px;">
                    <div style="font-size: 0.85rem; color: #0284c7; font-weight: 600;">Budget</div>
                    <div style="font-size: 1.55rem; font-weight: 700; color: #1e3a8a; margin: 4px 0; letter-spacing: -0.5px;">{sel_data['budget']}</div>
                    {render_dome_svg(sel_data['dome_stroke'], sel_data['dome_color'])}
                </div>
                <!-- Progress -->
                <div style="background: white; border-radius: 12px; border: 1.5px solid rgba(255,255,255,0.85); box-shadow: 0 4px 8px rgba(0,0,0,0.04); padding: 8px; text-align: center; display: flex; flex-direction: column; justify-content: space-between; height: 145px;">
                    <div style="font-size: 0.85rem; color: #0284c7; font-weight: 600;">Progress</div>
                    <div style="font-size: 1.55rem; font-weight: 700; color: #1e3a8a; margin: 4px 0; letter-spacing: -0.5px;">{sel_data['progress']}%</div>
                    {render_gauge_svg(sel_data['progress'], sel_data['progress_color'], sel_data['needle_color'])}
                </div>
                <!-- Issues -->
                <div style="background: white; border-radius: 12px; border: 1.5px solid rgba(255,255,255,0.85); box-shadow: 0 4px 8px rgba(0,0,0,0.04); padding: 8px; text-align: center; display: flex; flex-direction: column; justify-content: space-between; height: 145px;">
                    <div style="font-size: 0.85rem; color: #0284c7; font-weight: 600;">Issues</div>
                    <div style="font-size: 1.55rem; font-weight: 700; color: #1e3a8a; margin: 4px 0; letter-spacing: -0.5px;">{sel_data['issues']}</div>
                    {render_issue_bars_svg(sel_data['issue_bars'], sel_data['issue_bar_color'])}
                </div>
            </div>
            
            <!-- Row 2: Open Issues, Schedule Variance -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <!-- Open Issues -->
                <div style="background: white; border-radius: 12px; border: 1.5px solid rgba(255,255,255,0.85); box-shadow: 0 4px 8px rgba(0,0,0,0.04); padding: 10px; text-align: center; display: flex; flex-direction: column; justify-content: center; height: 115px;">
                    <div style="font-size: 0.85rem; color: #0284c7; font-weight: 600; margin-bottom: 2px;">Open Issues</div>
                    <div style="font-size: 1.6rem; font-weight: 700; color: #1e3a8a; letter-spacing: -0.5px;">{sel_data['issues']}</div>
                </div>
                <!-- Schedule Variance -->
                <div style="background: white; border-radius: 12px; border: 1.5px solid rgba(255,255,255,0.85); box-shadow: 0 4px 8px rgba(0,0,0,0.04); padding: 10px; text-align: center; display: flex; flex-direction: column; justify-content: center; height: 115px;">
                    <div style="font-size: 0.85rem; color: #0284c7; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 4px; margin-bottom: 2px;">
                        Schedule Variance
                        <span style="color: #2563eb; font-weight: 700; font-size: 1.05rem;">▲</span>
                    </div>
                    <div style="font-size: 1.6rem; font-weight: 700; color: #1e3a8a; letter-spacing: -0.5px;">{sel_data['variance']}</div>
                </div>
            </div>
            <!-- Bottom spacer to balance left column height -->
            <div style="height: 10px;"></div>
        </div>
        """
        draw_html(details_html)

st.markdown('<div style="margin-top: 0.1rem;"></div>', unsafe_allow_html=True)

# ----------------- Row 3: Work Package 2 Performance -----------------
with st.container(border=True):
    st.markdown('<div class="section-title">Work Package 2 Performance</div>', unsafe_allow_html=True)
    
    col_wp1, col_wp2, col_wp3 = st.columns(3, gap="small")
    
    # 1. Stacked Bar Chart
    with col_wp1:
        st.markdown('<div class="chart-container-title" style="text-align: center;">Monthly Physical Progress</div>', unsafe_allow_html=True)
        months_wp = ['Jan', 'Mar', 'May', 'Jun', 'Jul', 'Sep', 'Nov']
        df_wp1 = pd.DataFrame({
            'Month': months_wp,
            'Baseline Plan': [90, 140, 180, 220, 260, 300, 270],
            'Actual Progress': [30, 50, 60, 70, 80, 90, 80],
            'Forecast': [15, 25, 30, 35, 40, 45, 40]
        })
        
        fig_wp1 = go.Figure()
        fig_wp1.add_trace(go.Bar(
            x=df_wp1['Month'], 
            y=df_wp1['Baseline Plan'], 
            name='Baseline Plan', 
            marker_color='#1e3a8a',
            hovertemplate='Baseline Plan: %{y}<extra></extra>'
        ))
        fig_wp1.add_trace(go.Bar(
            x=df_wp1['Month'], 
            y=df_wp1['Actual Progress'], 
            name='Actual Progress', 
            marker_color='#2563eb',
            hovertemplate='Actual Progress: %{y}<extra></extra>'
        ))
        fig_wp1.add_trace(go.Bar(
            x=df_wp1['Month'], 
            y=df_wp1['Forecast'], 
            name='Forecast', 
            marker_color='#60a5fa',
            hovertemplate='Forecast: %{y}<extra></extra>'
        ))
        fig_wp1.update_layout(
            barmode='stack',
            margin=dict(l=30, r=10, t=10, b=30),
            height=155,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.65,
                xanchor="center",
                x=0.5,
                font=dict(size=10, color='#1e3a8a')
            ),
            xaxis=dict(showgrid=False, tickfont=dict(color='#1e3a8a', size=12)),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.06)', tickfont=dict(color='#1e3a8a', size=12))
        )
        st.plotly_chart(fig_wp1, use_container_width=True, key="wp1_bar_chart", config={'displayModeBar': False})
        
    # 2. Schedule Trend Line Chart
    with col_wp2:
        st.markdown('<div class="chart-container-title" style="text-align: center;">Schedule Trend</div>', unsafe_allow_html=True)
        months_trend = ['Jan', 'Mar', 'May', 'Jul', 'Sep', 'Nov']
        df_wp2 = pd.DataFrame({
            'Month': months_trend,
            'Baseline': [20, 28, 22, 29, 31, 35],
            'Current Plan': [15, 18, 25, 23, 22, 32],
            'Actual Progress': [8, 10, 12, 14, 11, 15]
        })
        
        fig_wp2 = go.Figure()
        fig_wp2.add_trace(go.Scatter(x=df_wp2['Month'], y=df_wp2['Baseline'], mode='lines+markers', name='Baseline', line=dict(color='#1e3a8a', width=2), marker=dict(size=4.5)))
        fig_wp2.add_trace(go.Scatter(x=df_wp2['Month'], y=df_wp2['Current Plan'], mode='lines+markers', name='Current Plan', line=dict(color='#2563eb', width=2), marker=dict(size=4.5)))
        fig_wp2.add_trace(go.Scatter(x=df_wp2['Month'], y=df_wp2['Actual Progress'], mode='lines+markers', name='Actual Progress', line=dict(color='#60a5fa', width=1.5), marker=dict(size=4.5)))

        fig_wp2.update_layout(
            margin=dict(l=30, r=10, t=10, b=30),
            height=155,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.65,
                xanchor="center",
                x=0.5,
                font=dict(size=10, color='#1e3a8a')
            ),
            xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.06)', tickfont=dict(color='#1e3a8a', size=12)),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.06)', tickfont=dict(color='#1e3a8a', size=12), range=[0, 42])
        )
        st.plotly_chart(fig_wp2, use_container_width=True, key="wp2_trend_chart", config={'displayModeBar': False})
        
    # 3. Issue Trend Area Chart
    with col_wp3:
        st.markdown('<div class="chart-container-title" style="text-align: center;">Issue Resolution Trend</div>', unsafe_allow_html=True)
        df_wp3 = pd.DataFrame({
            'Month': months_trend,
            'New Issues': [5, 12, 6, 11, 4, 13],
            'Closed Issues': [3, 7, 4, 8, 3, 9],
            'Open Backlog': [2, 5, 2, 3, 1, 4]
        })
        
        fig_wp3 = go.Figure()
        fig_wp3.add_trace(go.Scatter(
            x=df_wp3['Month'], 
            y=df_wp3['New Issues'], 
            fill='tozeroy', 
            mode='none', 
            fillcolor='rgba(30, 58, 138, 0.4)',
            name='New Issues'
        ))
        fig_wp3.add_trace(go.Scatter(
            x=df_wp3['Month'], 
            y=df_wp3['Closed Issues'], 
            fill='tozeroy', 
            mode='none', 
            fillcolor='rgba(37, 99, 235, 0.4)',
            name='Closed Issues'
        ))
        fig_wp3.add_trace(go.Scatter(
            x=df_wp3['Month'], 
            y=df_wp3['Open Backlog'], 
            fill='tozeroy', 
            mode='none', 
            fillcolor='rgba(96, 165, 250, 0.5)',
            name='Open Backlog'
        ))

        fig_wp3.update_layout(
            margin=dict(l=30, r=10, t=10, b=30),
            height=155,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.65,
                xanchor="center",
                x=0.5,
                font=dict(size=10, color='#1e3a8a')
            ),
            xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.06)', tickfont=dict(color='#1e3a8a', size=12)),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.06)', tickfont=dict(color='#1e3a8a', size=12), range=[0, 15])
        )
        st.plotly_chart(fig_wp3, use_container_width=True, key="wp3_area_chart", config={'displayModeBar': False})
