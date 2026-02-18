import streamlit as st
import pandas as pd

# Set page config for a premium, professional look
st.set_page_config(
    page_title="Le Petit Tip Pro", 
    page_icon="🍷", 
    layout="centered"
)

# Custom CSS for Maroon, Red, Black, and White aesthetic
st.markdown("""
    <style>
    /* Main Background */
    .main {
        background-color: #ffffff;
    }
    
    /* Global Heading Colors - Maroon */
    h1, h2, h3, h4, h5, h6 {
        color: #800000 !important;
        font-weight: 700 !important;
        margin-bottom: 10px !important;
    }
    
    /* Standard Text */
    p, span, label {
        color: #000000 !important;
    }

    /* Expander Styling */
    div[data-testid="stExpander"] {
        border: 1px solid #800000 !important;
        border-radius: 12px !important;
        background-color: #ffffff !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Input Fields */
    .stNumberInput input, .stTextInput input, .stTextArea textarea {
        border-radius: 8px !important;
        border: 1px solid #800000 !important;
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* Primary Button - Maroon/Red Gradient */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #800000 0%, #b22222 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: 0.3s;
    }
    
    .stButton > button:hover {
        background: #000000 !important;
        box-shadow: 0 4px 12px rgba(128, 0, 0, 0.3);
    }

    /* Table Styling */
    .stTable {
        background-color: white;
        border-radius: 10px;
        border: 1px solid #800000;
        overflow: hidden;
    }
    
    /* Results Header */
    .result-header {
        background-color: #800000;
        color: white;
        padding: 10px;
        border-radius: 8px;
        margin-top: 20px;
        margin-bottom: 10px;
        text-align: center;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center;">🍷 Le Petit Marcel</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.1rem; color: #800000 !important;">Official Tip Distribution System</p>', unsafe_allow_html=True)
st.markdown("<hr style='border-top: 2px solid #800000;'>", unsafe_allow_html=True)

# --- INPUT SECTION ---
st.markdown("### 📊 Sales & Tips Input")
with st.expander("Enter Shift Data", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        server_tips_raw = st.number_input("Server Non-Cash Tips ($)", min_value=0.0, step=0.01, format="%.2f")
        bev_sales = st.number_input("Bev/Liquor Sales ($)", min_value=0.0, step=0.01, format="%.2f")
        wine_sales = st.number_input("Wine Total Sales ($)", min_value=0.0, step=0.01, format="%.2f")
    with col2:
        bar_tips_raw = st.number_input("Bar Non-Cash Tips ($)", min_value=0.0, step=0.01, format="%.2f")
        food_cost = st.number_input("Total Food Cost ($)", min_value=0.0, step=0.01, format="%.2f")

st.markdown("### 👥 Staffing & Points")
with st.expander("Configure Staff on Shift", expanded=True):
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Standard Servers (2 Pts Each)**")
        server_names_raw = st.text_input("Names (comma separated)", placeholder="Bryan, Riley, Saige")
        
        st.markdown("**Support Staff**")
        head_busser_names_raw = st.text_input("Head Busser Names (0.65 Pts)", placeholder="Virgilio")
        num_bussers = st.number_input("Standard Bussers (0.6 Pts)", min_value=0, step=1, value=1)
    
    with col4:
        st.markdown("**Adjusted Points**")
        adjustment_input = st.text_area("Roxy:1.5, Riley:1...", height=68)
        
        st.markdown("**Bar Settings**")
        num_bartenders = st.number_input("Number of Bartenders", min_value=1, step=1, value=2)
        barback_working = st.checkbox("Barback Working? (20%)")

# --- CALCULATION LOGIC ---
if st.button("Generate Tipout Report"):
    try:
        # Core Math
        net_server_tips = server_tips_raw * 0.975
        net_bar_tips = bar_tips_raw * 0.975
        bar_tipout_from_servers = (bev_sales * 0.10) + (wine_sales * 0.02)
        split_total = net_server_tips - bar_tipout_from_servers
        
        # Staff Logic
        final_server_list = []
        total_floor_points = 0.0
        
        if server_names_raw:
            for name in [n.strip() for n in server_names_raw.split(',') if n.strip()]:
                final_server_list.append({'name': name, 'pts': 2.0})
                total_floor_points += 2.0
                
        if adjustment_input:
            for item in adjustment_input.replace('\n', ',').split(','):
                if ':' in item:
                    name, pts = item.split(':')
                    final_server_list.append({'name': name.strip(), 'pts': float(pts)})
                    total_floor_points += float(pts)
        
        head_busser_list = []
        if head_busser_names_raw:
            for name in [n.strip() for n in head_busser_names_raw.split(',') if n.strip()]:
                head_busser_list.append(name)
                total_floor_points += 0.65
            
        total_floor_points += (num_bussers * 0.6)
        point_value = split_total / total_floor_points if total_floor_points > 0 else 0
        
        # Bar/Expo Logic
        expo_final = round(food_cost * 0.03, 2)
        bar_pool_pre = net_bar_tips + bar_tipout_from_servers
        bar_pool_after_expo = bar_pool_pre - expo_final
        barback_final = round(bar_pool_after_expo * 0.20, 2) if barback_working else 0.0
        solo_bar_final = round(bar_pool_after_expo - barback_final, 2)
        bartender_each = round(solo_bar_final / num_bartenders, 2) if num_bartenders > 0 else solo_bar_final

        # --- RESULTS SUMMARY ---
        st.markdown('<div class="result-header">📋 DISTRIBUTION SUMMARY</div>', unsafe_allow_html=True)
        
        results = []
        for s in final_server_list:
            results.append({"Role/Person": f"Server: {s['name']}", "Payout": f"${s['pts']*point_value:,.2f}", "Detail": f"{s['pts']} pts"})
        
        for hb in head_busser_list:
            results.append({"Role/Person": f"Head Busser: {hb}", "Payout": f"${0.65*point_value:,.2f}", "Detail": "0.65 pts"})

        if num_bussers > 0:
            results.append({"Role/Person": f"Bussers ({num_bussers})", "Payout": f"${0.6*point_value:,.2f} ea", "Detail": "0.6 pts"})
            
        results.append({"Role/Person": "Expo Final", "Payout": f"${expo_final:,.2f}", "Detail": "3% Food Cost"})
        
        if barback_working:
            results.append({"Role/Person": "Barback Final", "Payout": f"${barback_final:,.2f}", "Detail": "20% Bar Pool"})
            
        results.append({"Role/Person": "Solo Bar Total", "Payout": f"${solo_bar_final:,.2f}", "Detail": f"${bartender_each:,.2f} each"})

        st.table(pd.DataFrame(results))
        st.info(f"**Floor Stats:** Point Value: ${point_value:,.2f} | Total Pts: {total_floor_points:.2f}")

    except Exception as e:
        st.error(f"Error: Please check your formatting. {e}")

st.markdown("<br><hr style='border-top: 1px solid #800000;'>", unsafe_allow_html=True)
st.caption("Le Petit Marcel Management Console • Consistency = Professionalism")
