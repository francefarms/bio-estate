import streamlit as st
import pandas as pd
import requests

def commodities_page():
    st.title("🌾 Agricultural Market Intelligence")
    st.markdown("### Real-time & Historical Commodity Prices")

    # 1. Top Row: Key Metrics (The "FocusEconomics" Cards)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cocoa (ICCO)", "$9,558", "+1.7%")
    col2.metric("Coffee Arabica", "$376", "+5.2%")
    col3.metric("Corn (CBOT)", "$474", "-0.8%")
    col4.metric("Rice", "$455", "+2.1%")

    # 2. The Data Table (The "Historical" View)
    st.markdown("---")
    st.subheader("Historical Price Data (Quarterly)")
    
    # This matches the FocusEconomics structure you liked
    data = {
        "Commodity": ["Rice", "Coffee Arabica", "Cotton ICE", "Sugar ISA", "Palm Oil", "Corn CBOT", "Soybeans CBOT", "Wheat CBOT", "Cocoa ICCO"],
        "Q3 2024": [589, 246, 69.41, 19.36, 1082, 395, 1036, 551, 6803],
        "Q4 2024": [520, 289, 70.47, 20.19, 1353, 428, 995, 562, 8285],
        "Q1 2025": [455, 376, 66.62, 18.65, 1475, 474, 1028, 558, 9558],
        "Q2 2025 (Est)": [420, 366, 66.00, 17.53, 1303, 453, 1045, 537, 8521]
    }
    
    df = pd.DataFrame(data)
    st.dataframe(df.style.highlight_max(axis=1, color='#4CAF50'), use_container_width=True)

    # 3. Interactive Chart
    st.subheader("Market Trends")
    selected_commodity = st.selectbox("Select a commodity to view trend:", df["Commodity"])
    
    # Filter data for the chart
    chart_data = df[df["Commodity"] == selected_commodity].drop("Commodity", axis=1).T
    st.line_chart(chart_data)

    st.info("💡 Data is updated twice daily via Françe Farms Cloud Operations.")

# Call the function
commodities_page()