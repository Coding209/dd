import streamlit as st
import pandas as pd
import random
import fitz  # PyMuPDF for PDF handling
from faker import Faker
import io

# Initialize Faker
fake = Faker()

# Generate Synthetic Payroll Tax Data
def generate_synthetic_data(num_entries=1):
    data = []
    for _ in range(num_entries):
        record = {
            "EIN": fake.unique.random_number(digits=9, fix_len=True),
            "Employer Name": fake.company(),
            "Quarter": random.choice(["Q1", "Q2", "Q3", "Q4"]),
            "Year": fake.random_int(min=2020, max=2025),
            "Total Wages": round(random.uniform(50000, 200000), 2),
            "Withheld Taxes": round(random.uniform(5000, 25000), 2),
            "Adjustments": round(random.uniform(-500, 500), 2),
            "Total Tax Liability": round(random.uniform(6000, 30000), 2),
        }
        data.append(record)
    
    df = pd.DataFrame(data)
    return df

# Function to Fill PDF
def fill_pdf(data, template_pdf="941_schedule_d_template.pdf"):
    doc = fitz.open(template_pdf)  # Load the PDF template
    page = doc[0]  # Assume data goes on the first page

    # Field mappings (update these with actual coordinates)
    field_mappings = {
        "Employer Name": (50, 150),
        "EIN": (400, 150),
        "Quarter": (50, 180),
        "Year": (150, 180),
        "Total Wages": (50, 210),
        "Withheld Taxes": (50, 240),
        "Adjustments": (50, 270),
        "Total Tax Liability": (50, 300),
    }

    # Fill fields in PDF
    for field, (x, y) in field_mappings.items():
        page.insert_text((x, y), str(data[field]), fontsize=10)

    # Save filled PDF to a buffer
    pdf_buffer = io.BytesIO()
    doc.save(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

# Streamlit Web App
st.title("📄 IRS Form 941 Schedule D Auto-Fill")
st.write("Generate synthetic data or input manually to fill out Form 941 Schedule D.")

# Sidebar: User Options
option = st.sidebar.selectbox("Choose an option:", ["Generate Synthetic Data", "Manual Input"])

if option == "Generate Synthetic Data":
    num_entries = st.sidebar.slider("Number of records:", 1, 5, 1)
    if st.sidebar.button("Generate"):
        synthetic_data = generate_synthetic_data(num_entries)
        st.dataframe(synthetic_data)

        # Select a record for PDF filling
        selected_record = synthetic_data.iloc[0].to_dict()

        # Generate the PDF
        pdf_file = fill_pdf(selected_record)

        # Provide download link
        st.download_button(
            label="📥 Download Filled Form 941 Schedule D",
            data=pdf_file,
            file_name="941_schedule_d_filled.pdf",
            mime="application/pdf"
        )

elif option == "Manual Input":
    st.subheader("Enter Data Manually")
    manual_data = {
        "EIN": st.text_input("Employer Identification Number (EIN)", "123456789"),
        "Employer Name": st.text_input("Employer Name", "ABC Corp"),
        "Quarter": st.selectbox("Quarter", ["Q1", "Q2", "Q3", "Q4"]),
        "Year": st.number_input("Year", min_value=2020, max_value=2025, value=2024),
        "Total Wages": st.number_input("Total Wages ($)", min_value=0.0, step=1000.0, value=50000.0),
        "Withheld Taxes": st.number_input("Withheld Taxes ($)", min_value=0.0, step=100.0, value=5000.0),
        "Adjustments": st.number_input("Adjustments ($)", step=10.0, value=0.0),
        "Total Tax Liability": st.number_input("Total Tax Liability ($)", min_value=0.0, step=1000.0, value=6000.0),
    }

    if st.button("Generate PDF"):
        pdf_file = fill_pdf(manual_data)
        st.download_button(
            label="📥 Download Filled Form 941 Schedule D",
            data=pdf_file,
            file_name="941_schedule_d_filled.pdf",
            mime="application/pdf"
        )

