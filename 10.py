import streamlit as st
import pandas as pd
import fitz  # PyMuPDF for PDF filling
import zipfile
import io
import random
from faker import Faker

# Initialize Faker for generating synthetic data
fake = Faker()

# Generate synthetic Form 1040 data
def generate_synthetic_1040():
    return {
        "Your first name and middle initial": fake.first_name(),
        "Last name": fake.last_name(),
        "Your social security number": f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}",
        "Spouse’s social security number": f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}",
        "Home address (number and street)": fake.street_address(),
        "City, town or post office": fake.city(),
        "State": fake.state_abbr(),
        "ZIP code": fake.zipcode(),
        "Wages, salaries, tips, etc.": round(random.uniform(15000, 120000), 2),
        "Interest income": round(random.uniform(0, 5000), 2),
        "Adjusted Gross Income": round(random.uniform(15000, 120000), 2),
        "Taxable income": round(random.uniform(10000, 100000), 2),
        "Total tax": round(random.uniform(500, 20000), 2),
        "Federal income tax withheld": round(random.uniform(500, 15000), 2),
        "Refund Amount": round(random.uniform(0, 5000), 2),
        "Amount Owed": round(random.uniform(0, 5000), 2),
    }

# Fill the IRS 1040 PDF template
def fill_1040_pdf(template_path, data):
    doc = fitz.open(template_path)
    page = doc[0]

    # Define positions for form fields (adjust based on your template)
    fields_positions = {
        "Your first name and middle initial": (60, 680),
        "Last name": (180, 680),
        "Your social security number": (460, 680),
        "Spouse’s social security number": (460, 655),
        "Home address (number and street)": (60, 640),
        "City, town or post office": (60, 620),
        "State": (300, 620),
        "ZIP code": (400, 620),
        "Wages, salaries, tips, etc.": (460, 570),
        "Interest income": (460, 550),
        "Adjusted Gross Income": (460, 530),
        "Taxable income": (460, 510),
        "Total tax": (460, 490),
        "Federal income tax withheld": (460, 470),
        "Refund Amount": (460, 450),
        "Amount Owed": (460, 430),
    }

    # Fill fields in the PDF
    for field, pos in fields_positions.items():
        page.insert_text(pos, str(data[field]), fontsize=10, fontname="helv")

    # Save filled PDF to a buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("Synthetic IRS Form 1040 Generator")
st.write("This tool generates **synthetic IRS Form 1040 PDFs** with random taxpayer data.")

# User input for number of forms to generate
num_forms = st.number_input("How many 1040 forms do you want to generate?", min_value=1, max_value=50, value=1)

# Upload the fillable Form 1040 PDF template
template_path = "f1040.pdf"  # Make sure the fillable Form 1040 is in the same directory

# Generate and download multiple forms
if st.button("Generate and Download Forms"):
    pdf_files = []
    
    for i in range(num_forms):
        synthetic_data = generate_synthetic_1040()
        pdf_buffer = fill_1040_pdf(template_path, synthetic_data)
        pdf_files.append((f"synthetic_1040_{i+1}.pdf", pdf_buffer.getvalue()))
    
    # Create a ZIP file containing all generated PDFs
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for filename, pdf_data in pdf_files:
            zipf.writestr(filename, pdf_data)
    
    zip_buffer.seek(0)

    # Download the ZIP file
    st.download_button(
        label="Download All 1040 Forms (ZIP)",
        data=zip_buffer,
        file_name="synthetic_1040_forms.zip",
        mime="application/zip"
    )

    st.success(f"{num_forms} Form 1040 PDFs Generated and Ready for Download! ✅")
