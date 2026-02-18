import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Le Petit Marcel - Tip Calculator",
    page_icon="🍷",
    layout="centered"
)

# Custom CSS for a clean, professional look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stNumberInput > div > div > input {
        background-color: #ffffff;
    }
    .report-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .metric-label {
        color: #6c757d;
        font-size: 0.9rem;
    }
    .metric-value {
        color: #212529;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .total-value {
        color: #1a73e8;
        font-size: 2rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("🍷 Le Petit Marcel")
    st.subheader("Shift Tip Calculator")
    st.write("Enter your sales data from the Toast summary to calculate your final payout.")

    # --- INPUT SECTION ---
    with st.container():
        st.markdown('<div class="report-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💰 Tips & Beverage Sales")
            non_cash_tips = st.number_input("Total Non-cash Tips ($)", min_value=0.0, step=0.01, format="%.2f")
            bev_sales = st.number_input("Bev/Liquor/Soft Drinks Sales ($)", min_value=0.0, step=0.01, format="%.2f")
            wine_sales = st.number_input("Wine BTL+GLS Sales ($)", min_value=0.0, step=0.01, format="%.2f")
            
        with col2:
            st.markdown("### 🍱 Food Sales")
            food_sales = st.number_input("Total Food Cost/Sales ($)", min_value=0.0, step=0.01, format="%.2f")
            st.markdown("---")
            st.info("The calculator applies the standard house rules: 10% Bar (Bev), 2% Bar (Wine), and 3% Expo (Food).")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- CALCULATIONS ---
    # House Keeps (2.5% of non-cash tips as seen in your sheets)
    house_keeps = non_cash_tips * 0.025
    net_tips = non_cash_tips - house_keeps
    
    # Bar Tip-outs
    bar_tip_out_bev = bev_sales * 0.10
    bar_tip_out_wine = wine_sales * 0.02
    total_to_bar = bar_tip_out_bev + bar_tip_out_wine
    
    # Expo Tip-out (3% of food)
    expo_final = food_sales * 0.03
    
    # Split Total (Logic from your sheet: Tips - Bar Tipout)
    split_total = net_tips - total_to_bar
    
    # Final Payout (Simplification of your 2.0 vs 0.6 point system for a solo calculator)
    # Typically, the server keeps their share of the split total.
    # In your sheet, Server Final = Split Total / Total Pts * 2.0
    # Assuming standard shift: 1 Server (2pts), 1 Busser (0.6pts based on sheet logic)
    total_pts = 2.6
    server_final = (split_total / total_pts * 2.0) if split_total > 0 else 0
    busser_final = (split_total / total_pts * 0.6) if split_total > 0 else 0

    # --- OUTPUT SECTION ---
    st.markdown("### 📊 Distribution Breakdown")
    
    res_col1, res_col2, res_col3 = st.columns(3)
    
    with res_col1:
        st.markdown(f"""
            <div class="report-card">
                <p class="metric-label">To Bar</p>
                <p class="metric-value">${total_to_bar:,.2f}</p>
                <small>(10% Bev + 2% Wine)</small>
            </div>
        """, unsafe_allow_html=True)
        
    with res_col2:
        st.markdown(f"""
            <div class="report-card">
                <p class="metric-label">To Expo</p>
                <p class="metric-value">${expo_final:,.2f}</p>
                <small>(3% of Food Sales)</small>
            </div>
        """, unsafe_allow_html=True)

    with res_col3:
        st.markdown(f"""
            <div class="report-card">
                <p class="metric-label">To Busser</p>
                <p class="metric-value">${busser_final:,.2f}</p>
                <small>(Point-weighted split)</small>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="report-card" style="text-align: center; border: 2px solid #1a73e8;">
            <p class="metric-label" style="font-size: 1.2rem;">Server Take-Home (Net)</p>
            <p class="total-value">${server_final:,.2f}</p>
            <p style="color: #6c757d;">Calculated after all tip-outs and house fees.</p>
        </div>
    """, unsafe_allow_html=True)

    # Footer note
    st.markdown("---")
    st.caption("Note: Amounts shown are pre-tax and do not include hourly wages. Formula based on Le Petit Marcel standard reporting logic.")

if __name__ == "__main__":
    main()
