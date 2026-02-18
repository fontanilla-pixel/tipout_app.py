import streamlit as st

st.title("Le Petit Tipout Calculator")
st.markdown("Enter shift data below. All amounts pre-tax, excludes hourly.")

col1, col2 = st.columns(2)

with col1:
    non_cash_servers = st.number_input("Non-cash tip (servers total)", min_value=0.0, value=2187.00, step=0.01)
    bev_sales = st.number_input("Bev/Liquor/Soft Drinks sales (total)", min_value=0.0, value=2300.85, step=0.01)
    wine_sales = st.number_input("Wine BTG+BTL sales (total)", min_value=0.0, value=1475.00, step=0.01)
    non_cash_bar = st.number_input("Non-cash tip (bar)", min_value=0.0, value=820.96, step=0.01)
    food_cost = st.number_input("Total food cost (for expo)", min_value=0.0, value=1148.75, step=0.01)

with col2:
    server_points_str = st.text_input("Server points (e.g. Bryan=2, Riley=2, Saige=2, Roxy=1.5)", 
                                     value="Bryan=2, Riley=2, Saige=2, Roxy=1.5")
    num_bussers = st.number_input("Number of bussers", min_value=0, value=3, step=1)
    barback = st.selectbox("Barback working?", ["No", "Yes"])
    sum_expo_bussers = st.selectbox("Sum Expo with Bussers payout?", ["No", "Yes"])

if st.button("Calculate Tipout"):
    try:
        # Parse server points
        server_points = {}
        total_server_pts = 0.0
        for pair in server_points_str.split(','):
            if '=' in pair:
                name, pts_str = pair.strip().split('=')
                pts = float(pts_str)
                server_points[name.strip()] = pts
                total_server_pts += pts

        busser_pts_per = 0.6
        total_busser_pts = num_bussers * busser_pts_per
        total_points = total_server_pts + total_busser_pts

        if total_points == 0:
            st.error("Total points cannot be zero.")
            st.stop()

        # Core calcs
        net_server_tips = non_cash_servers * 0.975
        bar_tip_out = (bev_sales * 0.10) + (wine_sales * 0.02)
        split_total = net_server_tips - bar_tip_out
        per_point = round(split_total / total_points, 2)

        # Servers
        server_results = []
        total_server_final = 0.0
        for name, pts in server_points.items():
            amt = round(pts * per_point, 2)
            server_results.append(f"{name}: **${amt:,.2f}**")
            total_server_final += amt

        # Bussers
        busser_per = round(busser_pts_per * per_point, 2)
        total_busser = round(total_busser_pts * per_point, 2)

        # Expo
        expo = round(food_cost * 0.03, 2)

        # Bar
        net_bar = non_cash_bar * 0.975
        bar_pool = net_bar + bar_tip_out - expo
        barback_amt = round(bar_pool * 0.20, 2) if barback == "Yes" else 0.0
        solo_bar = round(bar_pool - barback_amt, 2)

        if sum_expo_bussers == "Yes":
            total_busser += expo
            busser_per = round(total_busser / num_bussers, 2) if num_bussers > 0 else 0

        # Output
        st.success("Calculation complete")
        st.markdown("### Results")

        st.markdown(f"**Server Final Amt**  \n" + "  \n".join(server_results) + f"  \n**Total Servers**: **${total_server_final:,.2f}**")

        busser_text = f"${busser_per:,.2f} each" if num_bussers > 1 else f"${total_busser:,.2f}"
        st.markdown(f"**Busser Final Amt**  \n{busser_text} / **Total**: **${total_busser:,.2f}**")

        st.markdown(f"**Expo Final**: **${expo:,.2f}** (3% food cost)")

        st.markdown(f"**Barback Final**: **${barback_amt:,.2f}**")

        st.markdown(f"**Solo Bar Final** (pre-split): **${solo_bar:,.2f}**")

        st.markdown(f"**Verification**: Servers + Bussers = **${total_server_final + total_busser:,.2f}** (should ≈ split total)")

    except Exception as e:
        st.error(f"Error: {str(e)}\nCheck input format (points like Name=number, comma separated).")

st.markdown("---")
st.caption("Built for Le Petit tipout system • 2.5% house • 10% bev + 2% wine • 3% expo • 20% barback")
