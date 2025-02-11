import streamlit as st
import pandas as pd
import random
import io
from faker import Faker
from pypdf import PdfReader, PdfWriter
import requests

# Initialize Faker
fake = Faker()

def download_template():
    """Download the IRS form template."""
    url = "https://www.irs.gov/pub/irs-pdf/f941sd.pdf"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open("template.pdf", "wb") as f:
                f.write(response.content)
            return True
    except Exception as e:
        st.error(f"Failed to download template: {str(e)}")
    return False

def generate_data():
    """Generate synthetic form data."""
    return {
        "f1_1": fake.unique.random_number(digits=9, fix_len=True),  # EIN
        "f1_2": fake.company(),  # Business Name
        "f1_3": str(random.randint(2020, 2024)),  # Year
        "f1_4": str(random.randint(1, 4)),  # Quarter
        "f1_5": f"{random.uniform(50000, 200000):.2f}",  # Total Wages
        "f1_6": f"{random.uniform(5000, 25000):.2f}",  # Withheld Taxes
        "f1_7": f"{random.uniform(-500, 500):.2f}",  # Adjustments
        "f1_8": f"{random.uniform(6000, 30000):.2f}"  # Total Liability
    }

def create_filled_pdf(data):
    """Create a filled PDF using the template and provided data."""
    try:
        # Read the template
        reader = PdfReader("template.pdf")
        writer = PdfWriter()

        # Get the first page
        page = reader.pages[0]

        # Update form fields
        writer.add_page(page)
        writer.update_page_form_field_values(writer.pages[0], data)

        # Save to buffer
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)
        
        return output_buffer
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        return None

# Main Streamlit app
st.title("IRS Form 941 Schedule D Generator")

# Download template if needed
if 'template_downloaded' not in st.session_state:
    st.session_state.template_downloaded = download_template()

# Generate Data button
if st.button("Generate New Data"):
    st.session_state.form_data = generate_data()
    st.write("Generated Data:")
    for key, value in st.session_state.form_data.items():
        st.write(f"{key}: {value}")

# Create and Download PDF button
if st.button("Create and Download PDF"):
    if hasattr(st.session_state, 'form_data'):
        pdf_buffer = create_filled_pdf(st.session_state.form_data)
        if pdf_buffer:
            st.download_button(
                label="Download Filled Form",
                data=pdf_buffer,
                file_name="filled_form_941sd.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Please generate data first before creating PDF.")

# Add debug information
if st.checkbox("Show Debug Information"):
    try:
        reader = PdfReader("template.pdf")
        fields = reader.get_fields()
        st.write("Available PDF Fields:", fields.keys())
    except Exception as e:
        st.error(f"Error reading PDF fields: {str(e)}")
