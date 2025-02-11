import streamlit as st
import pandas as pd
import random
import io
import os
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
            st.success("Template downloaded successfully")
            return True
        else:
            st.error(f"Failed to download template. Status code: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Failed to download template: {str(e)}")
        return False

def generate_data():
    """Generate synthetic form data."""
    data = {
        "f1_01[0]": fake.unique.random_number(digits=9, fix_len=True),  # EIN
        "f1_02[0]": fake.company(),  # Business Name
        "f1_03[0]": str(random.randint(2020, 2024)),  # Year
        "f1_04[0]": str(random.randint(1, 4)),  # Quarter
        "f1_05[0]": f"{random.uniform(50000, 200000):.2f}",  # Total Wages
        "f1_06[0]": f"{random.uniform(5000, 25000):.2f}",  # Withheld Taxes
        "f1_07[0]": f"{random.uniform(-500, 500):.2f}",  # Adjustments
        "f1_08[0]": f"{random.uniform(6000, 30000):.2f}"  # Total Liability
    }
    
    # Add alternative field names
    alt_data = {}
    for key, value in data.items():
        alt_data[f"topmostSubform[0].Page1[0].{key}"] = value
        alt_data[key.replace("[0]", "")] = value
        alt_data[key] = value
    
    return alt_data

def create_filled_pdf(data):
    """Create a filled PDF using the template and provided data."""
    if not os.path.exists("template.pdf"):
        st.error("Template file not found. Please ensure it was downloaded correctly.")
        return None

    try:
        # Read the template
        reader = PdfReader("template.pdf")
        
        # Verify the PDF has pages
        if len(reader.pages) == 0:
            st.error("The template PDF appears to be empty")
            return None
            
        # Debug info about the PDF
        st.write("PDF Information:")
        st.write(f"Number of pages: {len(reader.pages)}")
        st.write("Fields found:", reader.get_fields())
        
        # Create writer and copy page
        writer = PdfWriter()
        writer.add_page(reader.pages[0])
        
        # Copy form fields
        writer.clone_reader_document_root(reader)
        
        # Try to update fields
        writer.update_page_form_field_values(
            writer.pages[0],
            data,
            auto_regenerate=False
        )
        
        # Save to buffer
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)
        
        return output_buffer
        
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        import traceback
        st.write("Detailed error:", traceback.format_exc())
        return None

# Main Streamlit app
st.title("IRS Form 941 Schedule D Generator")

# Download template if needed
if 'template_downloaded' not in st.session_state:
    if os.path.exists("template.pdf"):
        st.session_state.template_downloaded = True
    else:
        st.session_state.template_downloaded = download_template()

# Show debug information first to help diagnose issues
st.subheader("Debug Information")
if st.checkbox("Show PDF Field Information"):
    try:
        if os.path.exists("template.pdf"):
            reader = PdfReader("template.pdf")
            fields = reader.get_fields()
            st.write("PDF Fields found:", fields)
            if fields:
                st.write("Individual field names:")
                for field_name in fields.keys():
                    st.write(f"- {field_name}")
            else:
                st.warning("No fillable fields found in the PDF")
        else:
            st.error("Template PDF file not found")
    except Exception as e:
        st.error(f"Error reading PDF fields: {str(e)}")

# Generate Data button
if st.button("Generate New Data"):
    st.session_state.form_data = generate_data()
    st.write("Generated Data:")
    for key, value in st.session_state.form_data.items():
        st.write(f"{key}: {value}")

# Create and Download PDF button
if st.button("Create and Download PDF"):
    if not hasattr(st.session_state, 'form_data'):
        st.warning("Please generate data first before creating PDF.")
    else:
        pdf_buffer = create_filled_pdf(st.session_state.form_data)
        if pdf_buffer:
            st.download_button(
                label="Download Filled Form",
                data=pdf_buffer,
                file_name="filled_form_941sd.pdf",
                mime="application/pdf"
            )
