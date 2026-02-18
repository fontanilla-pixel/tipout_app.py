import streamlit as st
import pandas as pd

# Set page config for a premium, professional feel
st.set_page_config(
    page_title="Le Petit Marcel | Tip Pro", 
    page_icon="🍷", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a sophisticated, high-end "Le Petit" aesthetic
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #F8F9FA;
    }
    
    /* Header Styling */
    .app-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .app-header h1 {
        margin: 0;
        font-weight: 600;
        letter-spacing: -1px;
    }
    
    /* Input Card Styling */
    div[data-testid="stExpander"] {
        background-color: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 1rem !important;
    }
    
    /* Primary Button */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%) !important;
        color: #1e293b !important;
        border: none !important;
        padding: 0.75rem !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        transition: transform 0.1s ease !important;
    }
    
    .stButton > button:active {
        transform: scale(0.98);
    }
    
    /* Result Section Header */
    .result-section {
        background: #ffffff;
        border-left: 5px solid #f59e0b;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 600;
        color: #1e293b;
    }
    
    /* Metrics Display */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        color: #1e293b !important;
    }
    
    /* Custom Table Styling */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        border-radius: 8px 8px 0 0;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.markdown("""
    <div class="app-header">
        <h1>Le Petit Marcel</h1>
        <p style="opacity: 0.8; font-weight: 300;">Professional Tip Management System</p>
    </div>
""", unsafe_allow_html=True)

# --- INPUT SECTION ---
st.markdown("### 📥 Shift Data Entry")

with st.expander("💰 Tips & Category Sales", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        server_tips_raw = st.number_input("Server Non-Cash Tips ($)", min_value=0.0, step=0.01, format="%.2f", help="Total CC tips from server checkout")
        bev_sales = st.number_input("Liquor/Bev/Soft Sales ($)", min_value=0.0, step=0.01, format="%.2f")
        wine_sales = st.number_input("Wine BTG+BTL Sales ($)", min_value=0.0, step=0.01, format="%.2f")
    with c2:
        bar_tips_raw = st.number_input("Bar Non-Cash Tips ($)", min_value=0.0, step=0.01, format="%.2f")
        food_cost = st.number_input("Total Food Sales ($)", min_value=0.0, step=0.01, format="%.2f")

with st.expander("👥 Staffing Configuration", expanded=True):
    c3, c4 = st.columns(2)
    with c3:
        server_names_raw = st.text_input("Servers (2 Pts Each)", placeholder="Bryan, Riley, Saige")
        head_busser_names_raw = st.text_input("Head Bussers (0.65 Pts)", placeholder="Virgilio")
        num_bussers = st.number_input("Standard Bussers (0.6 Pts)", min_value=0, step=1, value=1)
    with c4:
        adjustment_input = st.text_area("Custom Pts (e.g. Roxy:1.5)", height=68, help="Use Name:Point format")
        num_bartenders = st.number_input("Bartenders on Shift", min_value=1, step=1, value=2)
        barback_working = st.checkbox("Include Barback (20% Tipout)")

# --- CALCULATION LOGIC ---
if st.button("Generate Tipout Report"):
    try:
        # Financial logic
        net_server_tips = server_tips_raw * 0.975
        net_bar_tips = bar_tips_raw * 0.975
        
        # Tip-outs
        bar_tipout_from_servers = (bev_sales * 0.10) + (wine_sales * 0.02)
        split_total = net_server_tips - bar_tipout_from_servers
        
        # Staff Point Parsing
        final_server_list = []
        total_floor_points = 0.0
        
        # Standard Servers
        if server_names_raw:
            for name in [n.strip() for n in server_names_raw.split(',') if n.strip()]:
                final_server_list.append({'name': name, 'pts': 2.0})
                total_floor_points += 2.0
        
        # Adjusted Servers
        if adjustment_input:
            for item in adjustment_input.replace('\n', ',').split(','):
                if ':' in item:
                    name, pts = item.split(':')
                    pts = float(pts)
                    final_server_list.append({'name': name.strip(), 'pts': pts})
                    total_floor_points += pts
        
        # Head Bussers
        head_busser_list = []
        if head_busser_names_raw:
            for name in [n.strip() for n in head_busser_names_raw.split(',') if n.strip()]:
                head_busser_list.append(name)
                total_floor_points += 0.65
        
        # Standard Bussers
        total_floor_points += (num_bussers * 0.6)
        
        # Point Value Calculation
        point_value = split_total / total_floor_points if total_floor_points > 0 else 0
        
        # Bar/Expo Logic
        expo_final = round(food_cost * 0.03, 2)
        bar_pool_pre = net_bar_tips + bar_tipout_from_servers
        bar_pool_after_expo = bar_pool_pre - expo_final
        
        barback_final = round(bar_pool_after_expo * 0.20, 2) if barback_working else 0.0
        solo_bar_final = round(bar_pool_after_expo - barback_final, 2)
        bartender_each = round(solo_bar_final / num_bartenders, 2) if num_bartenders > 0 else 0

        # --- OUTPUT PRESENTATION ---
        st.markdown('<div class="result-section">📍 FLOOR POOL DISTRIBUTION</div>', unsafe_allow_html=True)
        
        floor_rows = []
        for s in final_server_list:
            floor_rows.append({"Staff": f"Server: {s['name']}", "Amt": f"${round(s['pts']*point_value, 2):,.2f}", "Weight": f"{s['pts']} Pts"})
        
        for hb in head_busser_list:
            floor_rows.append({"Staff": f"Head Busser: {hb}", "Amt": f"${round(0.65*point_value, 2):,.2f}", "Weight": "0.65 Pts"})
            
        if num_bussers > 0:
            busser_amt = round(0.6 * point_value, 2)
            floor_rows.append({"Staff": f"Bussers ({num_bussers})", "Amt": f"${busser_amt:,.2f} ea", "Weight": "0.60 Pts"})
            
        st.table(pd.DataFrame(floor_rows))

        st.markdown('<div class="result-section">🍹 BAR & EXPO POOL</div>', unsafe_allow_html=True)
        
        bar_rows = [
            {"Item": "Expo Final Payout", "Amt": f"${expo_final:,.2f}", "Basis": "3% Food Cost"},
            {"Item": "Barback Final", "Amt": f"${barback_final:,.2f}", "Basis": "20% Pool (if applicable)"},
            {"Item": "SOLO BAR TOTAL", "Amt": f"${solo_bar_final:,.2f}", "Basis": f"Split between {num_bartenders}"},
            {"Item": "Bartender Payout (Each)", "Amt": f"${bartender_each:,.2f}", "Basis": "Individual Final"}
        ]
        st.table(pd.DataFrame(bar_rows))

        # Financial Health Check
        st.markdown("---")
        m1, m2 = st.columns(2)
        m1.metric("Split Total", f"${split_total:,.2f}")
        m2.metric("Pt Value", f"${point_value:,.2f}")

    except Exception as e:
        st.error("Input Error: Please ensure server list follows 'Name:Points' format.")

st.markdown("""
    <div style="text-align: center; margin-top: 3rem; color: #94a3b8; font-size: 0.8rem;">
        Le Petit Marcel Management Console v2.5<br>
        <i>"Consistency = Professionalism"</i>
    </div>
""", unsafe_allow_html=True)
