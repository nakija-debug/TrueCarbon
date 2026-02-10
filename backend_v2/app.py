import streamlit as st
import pandas as pd
from fpdf import FPDF
from phases import phase2  # Import your logic!

# 1. Page Configuration
st.set_page_config(page_title="True Carbon", layout="wide")

st.title("🌱 True Carbon Verification System")
st.markdown("### Phase 2: Satellite Verification & Carbon Estimation")

# 2. Sidebar Controls
st.sidebar.header("Project Controls")
if st.sidebar.button("Run Satellite Analysis"):
    
    with st.spinner('Analyzing Sentinel-2 Imagery...'):
        # Call your function from phase2.py
        results = phase2.run_analysis()
        
    st.success("Analysis Complete!")

    # 3. Create Columns (Dashboard Layout)
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📍 Satellite Verification Map")
        # Display the Map
        results['map_object'].to_streamlit(height=500)

    with col2:
        st.subheader("📊 Carbon Statistics")
        
        # Display Metrics (Big Numbers)
        st.metric(label="New Vegetation (Hectares)", value=f"{results['new_tree_area_ha']:.2f} ha")
        st.metric(label="Carbon Sequestered", value=f"{results['carbon_tonnes']:.2f} tCO2")
        
        # Display Chart
        st.subheader("Land Cover Breakdown")
        chart_data = pd.DataFrame.from_dict(results['chart_data'], orient='index', columns=['Area'])
        st.bar_chart(chart_data)

    # 4. Generate PDF Report
    if st.button("📄 Generate PDF Report"):
        # Initialize PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Add Content
        pdf.cell(200, 10, txt="True Carbon Verification Report", ln=1, align="C")
        pdf.cell(200, 10, txt=f"Vegetation Area: {results['new_tree_area_ha']} ha", ln=1)
        pdf.cell(200, 10, txt=f"Carbon Credit Value: {results['carbon_tonnes']} tonnes", ln=1)
        
        # Save
        report_name = "reports/Carbon_Report.pdf"
        pdf.output(report_name)
        st.success(f"Report saved to {report_name}")
        
        # Add Download Button
        with open(report_name, "rb") as file:
            st.download_button(
                label="Download Report",
                data=file,
                file_name="TrueCarbon_Report.pdf",
                mime="application/pdf"
            )