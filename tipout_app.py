import streamlit as st
import pandas as pd

# Set page config for a premium look
st.set_page_config(page_title="Le Petit Tip Calculator", page_icon="🍷", layout="centered")

# Custom CSS for a sophisticated "Le Petit" aesthetic
st.markdown("""
    <style>
    .main {
        background-color: #fcfcfc;
    }
    .stNumberInput, .stTextInput {
        border-radius: 8px;
    }
    .result-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    /* Make the table look cleaner */
    .stTable {
        border-radius: 10px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍷 Le Petit Marcel")
st.subheader("Official Tip Distribution Calculator")

# --- INPUT SECTION ---
with st.expander("📊 Sales & Tips Input", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        server_tips_raw = st.number_input("Server Non-Cash Tips ($)", min_value=0.0, step=0.01, format="%.2f")
        bev_sales = st.number_input("Bev/Liquor/Soft Drinks Sales ($)", min_value=0.0, step=0.01, format="%.2f")
        wine_sales = st.number_input("Wine BTG+BTL Sales ($)", min_value=0.0, step=0.01, format="%.2f")
    
    with col2:
        bar_tips_raw = st.number_input("Bar Non-Cash Tips ($)", min_value=0.0, step=0.01, format="%.2f")
        food_cost = st.number_input("Total Food Cost ($)", min_value=0.0, step=0.01, format="%.2f")

with st.expander("👥 Staffing & Points", expanded=True):
    col3, col4 = st.columns(2)
    
    with col3:
        st.write("**Standard Servers (2 Pts Each)**")
        server_names_raw = st.text_input("Server Names (comma separated)", placeholder="Bryan, Riley, Saige")
        
        st.write("**Support Staff**")
        head_busser_names_raw = st.text_input("Head Busser Names (0.65 Pts each)", placeholder="Virgilio, Name2")
        num_bussers = st.number_input("Number of Standard Bussers (0.6 Pts Each)", min_value=0, step=1, value=1)
    
    with col4:
        st.write("**Adjusted Servers (Manual Points)**")
        adjustment_input = st.text_area("Non-standard Points (e.g., Roxy:1.5)", height=68, placeholder="Roxy:1.5, Sam:1")
        
        st.write("**Bar Settings**")
        num_bartenders = st.number_input("Number of Bartenders", min_value=1, step=1, value=2)
        barback_working = st.checkbox("Barback Working? (20% Tipout)")

# --- CALCULATION LOGIC ---
if st.button("Calculate Tipout", type="primary"):
    try:
        # 1. House Fees (0.975 multiplier for 2.5% fee)
        net_server_tips = server_tips_raw * 0.975
        net_bar_tips = bar_tips_raw * 0.975
        
        # 2. Bar Tip-out from Servers (10% Bev + 2% Wine)
        bar_tipout_from_servers = (bev_sales * 0.10) + (wine_sales * 0.02)
        
        # 3. Split Total for Floor Pool
        split_total = net_server_tips - bar_tipout_from_servers
        
        # 4. Parse Staff
        final_server_list = []
        total_floor_points = 0.0
        
        # Handle Standard Servers (2 pts)
        if server_names_raw:
            standard_names = [name.strip() for name in server_names_raw.split(',') if name.strip()]
            for name in standard_names:
                final_server_list.append({'name': name, 'pts': 2.0})
                total_floor_points += 2.0
                
        # Handle Adjusted Servers (Custom pts)
        if adjustment_input:
            adj_entries = adjustment_input.replace('\n', ',').split(',')
            for item in adj_entries:
                if ':' in item:
                    name, pts = item.split(':')
                    pts = float(pts)
                    final_server_list.append({'name': name.strip(), 'pts': pts})
                    total_floor_points += pts
        
        # Handle Head Bussers (0.65 pts each)
        head_busser_list = []
        if head_busser_names_raw:
            hb_names = [name.strip() for name in head_busser_names_raw.split(',') if name.strip()]
            for name in hb_names:
                head_busser_list.append(name)
                total_floor_points += 0.65
            
        # Handle Standard Bussers (0.6 pts each)
        busser_points_total = num_bussers * 0.6
        total_floor_points += busser_points_total
        
        # 5. Per-Point Value
        if total_floor_points > 0:
            point_value = split_total / total_floor_points
        else:
            point_value = 0
            
        # 6. Expo Final (3% of food cost)
        expo_final = round(food_cost * 0.03, 2)
        
        # 7. Bar Pool Logic
        bar_pool_pre = net_bar_tips + bar_tipout_from_servers
        bar_pool_after_expo = bar_pool_pre - expo_final
        
        barback_final = 0.0
        if barback_working:
            barback_final = round(bar_pool_after_expo * 0.20, 2)
            
        solo_bar_final = round(bar_pool_after_expo - barback_final, 2)
        bartender_each = round(solo_bar_final / num_bartenders, 2) if num_bartenders > 0 else solo_bar_final

        # --- PREPARE DATA FOR TABLE ---
        table_rows = []
        
        # Individual Server Payouts
        for s in final_server_list:
            final_amt = round(s['pts'] * point_value, 2)
            table_rows.append({
                "Role/Person": f"Server: {s['name']}",
                "Payout": f"${final_amt:,.2f}",
                "Notes": f"{s['pts']} points @ ${point_value:,.4f}/pt"
            })
            
        # Head Busser Rows (Individual)
        for hb_name in head_busser_list:
            head_busser_amt = round(0.65 * point_value, 2)
            table_rows.append({
                "Role/Person": f"Head Busser: {hb_name}",
                "Payout": f"${head_busser_amt:,.2f}",
                "Notes": f"Seniority rate (0.65 pts)"
            })

        # Standard Busser Row
        if num_bussers > 0:
            busser_final_each = round(0.6 * point_value, 2)
            table_rows.append({
                "Role/Person": f"Bussers ({num_bussers})",
                "Payout": f"${busser_final_each:,.2f} each",
                "Notes": f"Total: ${round(busser_final_each * num_bussers, 2):,.2f} (0.6 pts each)"
            })
            
        # Expo Row
        table_rows.append({
            "Role/Person": "Expo Final",
            "Payout": f"${expo_final:,.2f}",
            "Notes": "3% of total food cost"
        })
        
        # Barback Row
        if barback_working:
            table_rows.append({
                "Role/Person": "Barback Final",
                "Payout": f"${barback_final:,.2f}",
                "Notes": "20% deduction from bar pool"
            })
            
        # Bartender Row
        table_rows.append({
            "Role/Person": "Solo Bar Total",
            "Payout": f"${solo_bar_final:,.2f}",
            "Notes": f"Split: ${bartender_each:,.2f} each ({num_bartenders} bartenders)"
        })

        # --- OUTPUT TABLE ---
        st.markdown("### 📋 Results Summary")
        df_results = pd.DataFrame(table_rows)
        st.table(df_results)

        # Verification
        st.info(f"**Floor Pool Stats:** Raw Split Total: ${split_total:,.2f} | Total Points: {total_floor_points:.2f}")

    except Exception as e:
        st.error(f"Error in calculation. Please check your formatting. Details: {e}")

st.markdown("---")
st.caption("Le Petit Marcel Management Tools • Consistency = Professionalism")
