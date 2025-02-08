import streamlit as st
import pandas as pd
import zipfile
import io
import random
from faker import Faker
from pdfrw import PdfReader, PdfWriter, PageMerge

# Initialize Faker for generating synthetic data
fake = Faker()

# Generate synthetic Form 1040 data
def generate_synthetic_1040():
    return {
        "f1_01(0)": fake.first_name(),  # First Name
        "f1_02(0)": fake.last_name(),  # Last Name
        "f1_03(0)": f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}",  # SSN
        "f1_04(0)": fake.street_address(),  # Address
        "f1_05(0)": fake.city(),  # City
        "f1_06(0)": fake.state_abbr(),  # State
        "f1_07(0)": fake.zipcode(),  # ZIP Code
        "f1_08(0)": random.choice(["Single", "Married Filing Jointly", "Married Filing Separately", "Head of Household"]),
        "f1_09(0)": round(random.uniform(15000, 120000), 2),  # Wages
        "f1_10(0)": round(random.uniform(0, 5000), 2),  # Interest Income
        "f1_11(0)": round(random.uniform(15000, 120000), 2),  # Adjusted Gross Income
        "f1_12(0)": round(random.uniform(10000, 100000), 2),  # Taxable Income
        "f1_13(0)": round(random.uniform(500, 20000), 2),  # Total Tax
        "f1_14(0)": round(random.uniform(500, 15000), 2),  # Federal Income Tax Withheld
        "f1_15(0)": round(random.uniform(0, 5000), 2),  # Refund Amount
        "f1_16(0)": round(random.uniform(0, 5000), 2),  # Amount Owed
    }

# Function to fill the IRS 1040 PDF
def fill_1040_pdf(template_path, data):
    template_pdf = PdfReader(template_path)
    
    # Get the first page
    for page in template_pdf.pages:
        annotations = page.Annots or []
        for annotation in annotations:
            if annotation.T:
                field_name = annotation.T[1:-1]  # Extract field name
                if field_name in data:
                    annotation.V = data[field_name]  # Fill field with synthetic data

    # Save the filled PDF to a buffer
    buffer = io.BytesIO()
    PdfWriter(buffer, trailer=template_pdf).write()
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("Synthetic IRS Form 1040 Generator")
st.write("This tool generates **synthetic IRS Form 1040 PDFs** with random taxpayer data.")

# User input for number of forms
num_forms = st.number_input("How many 1040 forms do you want to generate?", min_value=1, max_value=50, value=1)

# Upload the fillable Form 1040 PDF template
template_path = "f1040.pdf"  # Make sure this file exists in your repo

if st.button("Generate and Download Forms"):
    pdf_files = []
    
    for i in range(num_forms):
        synthetic_data = generate_synthetic_1040()
        pdf_buffer = fill_1040_pdf(template_path, synthetic_data)
        pdf_files.append((f"synthetic_1040_{i+1}.pdf", pdf_buffer.getvalue()))
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for filename, pdf_data in pdf_files:
            zipf.writestr(filename, pdf_data)
    
    zip_buffer.seek(0)

    st.download_button(
        label="Download All 1040 Forms (ZIP)",
        data=zip_buffer,
        file_name="synthetic_1040_forms.zip",
        mime="application/zip"
    )

    st.success(f"{num_forms} Form 1040 PDFs Generated and Ready for Download! ✅")

    )

    st.success(f"{num_forms} Form 1040 PDFs Generated and Ready for Download! ✅")
