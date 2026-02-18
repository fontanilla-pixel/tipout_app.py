import streamlit as st
import pandas as pd

# Set page config for a premium, responsive feel
st.set_page_config(
    page_title="Le Petit Tip Pro", 
    page_icon="🍷", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a sophisticated, mobile-first aesthetic
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
    }
    
    /* Elegant Header */
    .app-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    .app-header h1 {
        margin: 0;
        font-size: 1.8rem;
        letter-spacing: -0.025em;
    }
    
    /* Modern Input Containers */
    div[data-testid="stExpander"] {
        border: none !important;
        background-color: white !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1) !important;
        margin-bottom: 1rem !important;
    }
    
    /* Button Styling */
    .stButton > button {
        width: 100%;
        background: #f59e0b !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: #d97706 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }

    /* Results Grid Styling */
    .result-card {
        background: white;
        padding: 1.25rem;
        border-radius: 12px;
        border-left: 4px solid #f59e0b;
        margin-bottom: 1rem;
        box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    }
    
    .result-label {
        color: #64748b;
        font-size: 0.75rem;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    
    .result-value {
        color: #0f172a;
        font-size: 1.25rem;
        font-weight: 600;
    }
    
    /* Mobile-specific adjustments */
    @media (max-width: 640px) {
        .app-header h1 { font-size: 1.5rem; }
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="app-header">
        <h1>🍷 Le Petit Marcel</h1>
        <p style="margin:0; opacity:0.8; font-size:0.9rem;">Tip Distribution Dashboard</p>
    </div>
""", unsafe_allow_html=True)

# --- INPUT SECTION ---
with st.expander("📊 Shift Financials", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        server_tips_raw = st.number_input("Server Non-Cash Tips ($)", min_value=0.0, step=0.01, format="%.2f")
        bev_sales = st.number_input("Bev/Liquor Sales ($)", min_value=0.0, step=0.01, format="%.2f")
        wine_sales = st.number_input("Wine Total Sales ($)", min_value=0.0, step=0.01, format="%.2f")
    with col2:
        bar_tips_raw = st.number_input("Bar Non-Cash Tips ($)", min_value=0.0, step=0.01, format="%.2f")
        food_cost = st.number_input("Total Food Cost ($)", min_value=0.0, step=0.01, format="%.2f")

with st.expander("👥 Staff & Adjustments", expanded=True):
    col3, col4 = st.columns(2)
    with col3:
        server_names_raw = st.text_input("Server Names (Bryan, Riley...)", placeholder="Bryan, Riley, Saige")
        head_busser_names_raw = st.text_input("Head Busser Names", placeholder="Virgilio")
        num_bussers = st.number_input("Standard Bussers", min_value=0, step=1, value=1)
    with col4:
        adjustment_input = st.text_area("Adjusted Pts (Roxy:1.5)", height=68)
        num_bartenders = st.number_input("Num. Bartenders", min_value=1, step=1, value=2)
        barback_working = st.checkbox("Barback Working? (20%)")

# --- CALCULATION LOGIC ---
if st.button("Generate Distribution"):
    try:
        # Core math
        net_server_tips = server_tips_raw * 0.975
        net_bar_tips = bar_tips_raw * 0.975
        bar_tipout_from_servers = (bev_sales * 0.10) + (wine_sales * 0.02)
        split_total = net_server_tips - bar_tipout_from_servers
        
        # Point System
        final_server_list = []
        total_floor_points = 0.0
        
        if server_names_raw:
            for n in [name.strip() for name in server_names_raw.split(',') if name.strip()]:
                final_server_list.append({'name': n, 'pts': 2.0})
                total_floor_points += 2.0
                
        if adjustment_input:
            for item in adjustment_input.replace('\n', ',').split(','):
                if ':' in item:
                    n, pts = item.split(':')
                    pts = float(pts)
                    final_server_list.append({'name': n.strip(), 'pts': pts})
                    total_floor_points += pts
        
        head_busser_list = []
        if head_busser_names_raw:
            for n in [name.strip() for name in head_busser_names_raw.split(',') if name.strip()]:
                head_busser_list.append(n)
                total_floor_points += 0.65
            
        total_floor_points += (num_bussers * 0.6)
        point_value = split_total / total_floor_points if total_floor_points > 0 else 0
        
        # Bar/Expo
        expo_final = round(food_cost * 0.03, 2)
        bar_pool_pre = net_bar_tips + bar_tipout_from_servers
        bar_pool_after_expo = bar_pool_pre - expo_final
        barback_final = round(bar_pool_after_expo * 0.20, 2) if barback_working else 0.0
        solo_bar_final = round(bar_pool_after_expo - barback_final, 2)
        bartender_each = round(solo_bar_final / num_bartenders, 2) if num_bartenders > 0 else solo_bar_final

        # --- MOBILE FRIENDLY RESULTS ---
        st.markdown("### 📋 Distribution Results")
        
        # Summary Row
        m1, m2 = st.columns(2)
        m1.metric("Split Total", f"${split_total:,.2f}")
        m2.metric("Point Value", f"${point_value:,.2f}")
        
        # Detailed Table
        table_rows = []
        for s in final_server_list:
            table_rows.append({"Staff": f"Server: {s['name']}", "Payout": f"${s['pts'] * point_value:,.2f}", "Detail": f"{s['pts']} pts"})
        
        for hb in head_busser_list:
            table_rows.append({"Staff": f"Head Busser: {hb}", "Payout": f"${0.65 * point_value:,.2f}", "Detail": "0.65 pts"})

        if num_bussers > 0:
            table_rows.append({"Staff": f"Bussers ({num_bussers})", "Payout": f"${0.6 * point_value:,.2f} ea", "Detail": "0.6 pts"})
            
        table_rows.append({"Staff": "Expo Final", "Payout": f"${expo_final:,.2f}", "Detail": "3% Food"})
        
        if barback_working:
            table_rows.append({"Staff": "Barback Final", "Payout": f"${barback_final:,.2f}", "Detail": "20% Pool"})
            
        table_rows.append({"Staff": "Bartender (Each)", "Payout": f"${bartender_each:,.2f}", "Detail": f"Split {num_bartenders}"})

        st.table(pd.DataFrame(table_rows))
        
    except Exception as e:
        st.error(f"Please check formatting: {e}")

st.markdown("---")
st.caption("Le Petit Marcel Management Console • v2.0")
