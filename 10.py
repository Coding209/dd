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

def download_pdf(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, "wb") as f:
            f.write(response.content)
        st.success("✅ IRS Form 941 Schedule D downloaded successfully.")
    else:
        st.error("❌ Failed to download the form. Please check the URL.")

def extract_form_fields(pdf_path):
    reader = PdfReader(pdf_path)
    form_fields = reader.get_fields()
    # Debug: Print all form fields with their types
    if form_fields:
        st.write("Found form fields:", {k: type(v).__name__ for k, v in form_fields.items()})
    return form_fields if form_fields else {}

def generate_synthetic_data(num_entries=1):
    data = []
    for _ in range(num_entries):
        record = {
            "ein": fake.unique.random_number(digits=9, fix_len=True),
            "name": fake.company(),
            "quarter": random.choice(["1", "2", "3", "4"]),  # Changed to match PDF field format
            "year": str(fake.random_int(min=2020, max=2025)),
            "total_wages": f"${round(random.uniform(50000, 200000), 2):,.2f}",
            "withheld_taxes": f"${round(random.uniform(5000, 25000), 2):,.2f}",
            "adjustments": f"${round(random.uniform(-500, 500), 2):,.2f}",
            "total_liability": f"${round(random.uniform(6000, 30000), 2):,.2f}",
        }
        data.append(record)
    
    return pd.DataFrame(data)

def fill_pdf(data, template_pdf=TEMPLATE_PDF_PATH):
    if not os.path.exists(template_pdf):
        st.error("❌ Template PDF not found. Please download the form first.")
        return None

    reader = PdfReader(template_pdf)
    writer = PdfWriter()

    # Extract form fields
    form_fields = extract_form_fields(template_pdf)
    if not form_fields:
        st.error("❌ No fillable fields detected in this PDF.")
        return None

    # Updated field mappings based on actual PDF field names
    # These should match the exact field names from the PDF
    field_mappings = {
        "ein": "f941sd_EIN",  # Example field name, adjust based on actual PDF
        "name": "f941sd_BusinessName",
        "quarter": "f941sd_Quarter",
        "year": "f941sd_Year",
        "total_wages": "f941sd_TotalWages",
        "withheld_taxes": "f941sd_WithheldTaxes",
        "adjustments": "f941sd_Adjustments",
        "total_liability": "f941sd_TotalLiability"
    }

    # Get the first page
    page = reader.pages[0]
    
    # Create a dictionary for the form field values
    form_values = {}
    
    # Fill in the fields
    for data_field, pdf_field in field_mappings.items():
        if data_field in data and pdf_field in form_fields:
            form_values[pdf_field] = str(data[data_field])
            st.write(f"Filling field {pdf_field} with value: {data[data_field]}")
        else:
            st.warning(f"Field mapping not found: {data_field} -> {pdf_field}")

    # Update all fields at once
    if form_values:
        writer.update_page_form_field_values(page, form_values)
    
    # Add the modified page
    writer.add_page(page)

    # Save to buffer
    pdf_buffer = io.BytesIO()
    writer.write(pdf_buffer)
    pdf_buffer.seek(0)

    return pdf_buffer

# Streamlit UI
st.title("📄 IRS Form 941 Schedule D Auto-Fill")

# Download form if needed
if not os.path.exists(TEMPLATE_PDF_PATH):
    st.info("📥 Downloading form template...")
    download_pdf(FORM_URL, TEMPLATE_PDF_PATH)

# Debug button to show PDF fields
if st.button("🔍 Debug: Show PDF Fields"):
    fields = extract_form_fields(TEMPLATE_PDF_PATH)
    st.write("PDF Form Fields:", fields.keys())

# Input method selection
input_method = st.radio("Choose input method:", ["Generate Synthetic Data", "Manual Input"])

if input_method == "Generate Synthetic Data":
    num_records = st.number_input("Number of records:", 1, 5, 1)
    if st.button("Generate Data"):
        df = generate_synthetic_data(num_records)
        st.dataframe(df)
        
        # Use first record for filling
        record = df.iloc[0].to_dict()
        pdf_buffer = fill_pdf(record)
        
        if pdf_buffer:
            st.download_button(
                "📥 Download Filled Form",
                pdf_buffer,
                "filled_form_941sd.pdf",
                "application/pdf"
            )

else:
    # Manual input form
    input_data = {
        "ein": st.text_input("EIN:", "123456789"),
        "name": st.text_input("Business Name:", "Example Corp"),
        "quarter": st.selectbox("Quarter:", ["1", "2", "3", "4"]),
        "year": st.text_input("Year:", "2024"),
        "total_wages": st.text_input("Total Wages:", "$50,000.00"),
        "withheld_taxes": st.text_input("Withheld Taxes:", "$5,000.00"),
        "adjustments": st.text_input("Adjustments:", "$0.00"),
        "total_liability": st.text_input("Total Tax Liability:", "$5,000.00")
    }
    
    if st.button("Fill Form"):
        pdf_buffer = fill_pdf(input_data)
        if pdf_buffer:
            st.download_button(
                "📥 Download Filled Form",
                pdf_buffer,
                "filled_form_941sd.pdf",
                "application/pdf"
            )
