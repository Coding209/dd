import streamlit as st
import pandas as pd
import random
import io
import os
import requests
from faker import Faker
from pypdf import PdfReader, PdfWriter

# Initialize Faker
fake = Faker()

# IRS Form 941 Schedule D URL
FORM_URL = "https://www.irs.gov/pub/irs-pdf/f941sd.pdf"
TEMPLATE_PDF_PATH = "f941sd_template.pdf"

# Function to download IRS PDF form
def download_pdf(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, "wb") as f:
            f.write(response.content)
        st.success("✅ IRS Form 941 Schedule D downloaded successfully.")
    else:
        st.error("❌ Failed to download the form. Please check the URL.")

# Function to extract form field names
def extract_form_fields(pdf_path):
    reader = PdfReader(pdf_path)
    return reader.get_fields() if reader.get_fields() else {}

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

# Function to correctly fill PDF form fields
def fill_pdf(data, template_pdf=TEMPLATE_PDF_PATH):
    if not os.path.exists(template_pdf):
        st.error("❌ Template PDF not found. Please download the form first.")
        return None

    reader = PdfReader(template_pdf)
    writer = PdfWriter()

    # Extract form fields
    form_fields = reader.get_fields()
    if not form_fields:
        st.error("❌ No fillable fields detected in this PDF.")
        return None

    # Debug: Show extracted form fields
    st.write("🔍 Extracted Form Fields:", list(form_fields.keys()))

    # Define correct field mappings based on extracted names
    field_mappings = {
        "f1-1[0]": "EIN",
        "f1-2[0]": "Employer Name",
        "f1-3[0]": "Quarter",
        "f1-4[0]": "Year",
        "f1-5[0]": "Total Wages",
        "f1-6[0]": "Withheld Taxes",
        "f1-7[0]": "Adjustments",
        "f1-8[0]": "Total Tax Liability",
    }

    # Create a new dictionary to store modified form field values
    updated_fields = {}

    # Fill form fields
    for pdf_field, data_key in field_mappings.items():
        if pdf_field in form_fields and data_key in data:
            updated_fields[pdf_field] = str(data[data_key])

    # Apply updates to the form fields
    writer.add_page(reader.pages[0])
    writer.update_page_form_field_values(writer.pages[0], updated_fields)

    # Debug: Show filled fields
    st.write("📌 Fields Filled:", updated_fields)

    # Save filled PDF to a buffer
    pdf_buffer = io.BytesIO()
    writer.write(pdf_buffer)
    pdf_buffer.seek(0)

    return pdf_buffer

# Streamlit Web App
st.title("📄 IRS Form 941 Schedule D Auto-Fill")
st.write("Generate synthetic data or manually input values to auto-fill Form 941 Schedule D.")

# Download the form if it doesn't exist
if not os.path.exists(TEMPLATE_PDF_PATH):
    st.info("📥 Form template not found. Downloading...")
    download_pdf(FORM_URL, TEMPLATE_PDF_PATH)

# Show extracted form fields (for debugging)
if st.sidebar.button("🔍 Show Form Fields"):
    extracted_fields = extract_form_fields(TEMPLATE_PDF_PATH)
    st.sidebar.write("Extracted Fields:", list(extracted_fields.keys()))

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

        if pdf_file:
            st.download_button(
                label="📥 Download Filled Form 941 Schedule D",
                data=pdf_file,
                file_name="941_schedule_d_filled.pdf",
                mime="application/pdf"
            )

elif option == "Manual Input":
    st.subheader("✍ Enter Data Manually")
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
        if pdf_file:
            st.download_button(
                label="📥 Download Filled Form 941 Schedule D",
                data=pdf_file,
                file_name="941_schedule_d_filled.pdf",
                mime="application/pdf"
            )

                data=pdf_file,
                file_name="941_schedule_d_filled.pdf",
                mime="application/pdf"
            )


