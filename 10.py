import streamlit as st
import pandas as pd
import zipfile
import io
import random
from faker import Faker
from pdfrw import PdfReader, PdfWriter

# Initialize Faker for generating synthetic tax data
fake = Faker()

# Define the template PDF path (ensure this file exists in your repo)
TEMPLATE_PATH = "f1040.pdf"

# Step 1: Extract actual form field names from the 1040 PDF
def extract_pdf_fields(template_path):
    pdf = PdfReader(template_path)
    fields = {}

    for page in pdf.pages:
        if page.Annots:
            for annotation in page.Annots:
                if annotation.T:
                    field_name = annotation.T[1:-1]  # Extract field name
                    fields[field_name] = ""  # Store as key for filling

    return fields

# Step 2: Generate synthetic data based on extracted field names
def generate_synthetic_1040(fields):
    tax_data = {}
    
    # Map field names dynamically
    for field in fields:
        if "first name" in field.lower():
            tax_data[field] = fake.first_name()
        elif "last name" in field.lower():
            tax_data[field] = fake.last_name()
        elif "social security" in field.lower():
            tax_data[field] = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
        elif "address" in field.lower():
            tax_data[field] = fake.street_address()
        elif "city" in field.lower():
            tax_data[field] = fake.city()
        elif "state" in field.lower():
            tax_data[field] = fake.state_abbr()
        elif "zip" in field.lower():
            tax_data[field] = fake.zipcode()
        elif "income" in field.lower():
            tax_data[field] = str(round(random.uniform(15000, 120000), 2))
        elif "tax" in field.lower():
            tax_data[field] = str(round(random.uniform(500, 20000), 2))
        elif "refund" in field.lower():
            tax_data[field] = str(round(random.uniform(0, 5000), 2))
        elif "owed" in field.lower():
            tax_data[field] = str(round(random.uniform(0, 5000), 2))
        else:
            tax_data[field] = fake.word()  # Default random data
    
    return tax_data

# Step 3: Fill the 1040 PDF using extracted field names
def fill_1040_pdf(template_path, data):
    template_pdf = PdfReader(template_path)

    for page in template_pdf.pages:
        annotations = page.Annots or []
        for annotation in annotations:
            if annotation.T:
                field_name = annotation.T[1:-1]  # Extract the field name
                if field_name in data:
                    annotation.V = data[field_name]  # Fill form field with synthetic data

    # Save filled PDF to a buffer
    buffer = io.BytesIO()
    PdfWriter(buffer, trailer=template_pdf).write()
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("Synthetic IRS Form 1040 Generator")
st.write("This tool generates **synthetic IRS Form 1040 PDFs** with random taxpayer data.")

# User input for number of forms
num_forms = st.number_input("How many 1040 forms do you want to generate?", min_value=1, max_value=50, value=1)

if st.button("Generate and Download Forms"):
    pdf_files = []
    
    # Step 1: Extract field names from the fillable PDF
    extracted_fields = extract_pdf_fields(TEMPLATE_PATH)

    for i in range(num_forms):
        # Step 2: Generate synthetic data for the extracted fields
        synthetic_data = generate_synthetic_1040(extracted_fields)

        # Step 3: Fill the 1040 form with synthetic data
        pdf_buffer = fill_1040_pdf(TEMPLATE_PATH, synthetic_data)
        pdf_files.append((f"synthetic_1040_{i+1}.pdf", pdf_buffer.getvalue()))
    
    # Create a ZIP file containing all generated PDFs
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for filename, pdf_data in pdf_files:
            zipf.writestr(filename, pdf_data)
    
    zip_buffer.seek(0)

    # Provide download button for the ZIP file
    st.download_button(
        label="Download All 1040 Forms (ZIP)",
        data=zip_buffer,
        file_name="f1040.pdf",
        mime="application/zip"
    )

    st.success(f"{num_forms} Form 1040 PDFs Generated and Ready for Download! ✅")


