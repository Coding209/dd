import streamlit as st
import random
import io
import os
from faker import Faker
from pypdf import PdfReader, PdfWriter
import requests
from datetime import datetime

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
    """Generate synthetic form data matching the actual form fields."""
    # Generate base data
    ein = f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}"
    company_name = fake.company()
    year = str(random.randint(2020, 2024))
    
    # Try multiple field name variations
    data = {}
    
    # EIN field variations
    ein_fields = [
        "EIN", "ein", "EmployerID", "employerId",
        "form1.#subform[0].#area[0].EIN[0]",
        "form1.#subform[0].EmployerID[0]",
        "f1_01[0]", "f1_02[0]"
    ]
    for field in ein_fields:
        data[field] = ein
        
    # Name field variations
    name_fields = [
        "Name", "name", "BusinessName", "businessName",
        "form1.#subform[0].#area[0].Name[0]",
        "form1.#subform[0].BusinessName[0]",
        "f1_03[0]"
    ]
    for field in name_fields:
        data[field] = company_name
        
    # Year field variations
    year_fields = [
        "Year", "year", "TaxYear", "taxYear",
        "form1.#subform[0].#area[0].Year[0]",
        "form1.#subform[0].TaxYear[0]",
        "f1_11[0]"
    ]
    for field in year_fields:
        data[field] = year
        
    # Add additional data with various field name patterns
    base_fields = {
        "TradeName": fake.company_suffix(),
        "Address": fake.street_address(),
        "City": fake.city(),
        "State": fake.state_abbr(),
        "ZipCode": fake.zipcode(),
        "PhoneNumber": fake.phone_number()
    }
    
    # Add variations of each base field
    for base_name, value in base_fields.items():
        variations = [
            base_name,
            base_name.lower(),
            f"form1.#subform[0].{base_name}[0]",
            f"form1.#subform[0].#area[0].{base_name}[0]"
        ]
        for field in variations:
            data[field] = value
    
    return data

def create_filled_pdf(data):
    """Create a filled PDF using the template and provided data."""
    if not os.path.exists("template.pdf"):
        st.error("Template file not found. Please ensure it was downloaded correctly.")
        return None

    try:
        # Read the template
        reader = PdfReader("template.pdf")
        writer = PdfWriter()
        
        # Show available fields for debugging
        fields = reader.get_fields()
        if fields:
            st.write("Available fields in PDF:", fields.keys())
        
        # Get the first page
        if len(reader.pages) == 0:
            st.error("The template PDF appears to be empty")
            return None
            
        # Copy the first page
        page = reader.pages[0]
        writer.add_page(page)

        # Try to update fields
        try:
            # First attempt with direct field mapping
            writer.update_page_form_field_values(writer.pages[0], data)
            
            # Second attempt with alternative field names if needed
            alt_data = {f"form1[0].{k}": v for k, v in data.items()}
            writer.update_page_form_field_values(writer.pages[0], alt_data)
            
        except Exception as e:
            st.warning(f"Warning while updating fields: {str(e)}")
        
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

# Show field information immediately for debugging
try:
    if os.path.exists("template.pdf"):
        reader = PdfReader("template.pdf")
        fields = reader.get_fields()
        if fields:
            st.write("Found fields in PDF:", fields.keys())
        else:
            st.warning("No fillable fields found in the PDF.")
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
