import streamlit as st
import requests
import io
import os
from pypdf import PdfReader, PdfWriter
from faker import Faker
import random

fake = Faker()

def download_template():
    """Download the IRS form template."""
    url = "https://www.irs.gov/pub/irs-pdf/f941sd.pdf"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return io.BytesIO(response.content)
        else:
            st.error(f"Failed to download template. Status code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Failed to download template: {str(e)}")
        return None

def generate_data():
    """Generate synthetic form data."""
    return {
        "/ein1": str(random.randint(10, 99)),
        "/ein2": str(random.randint(1000000, 9999999)),
        "/name": fake.company(),
        "/trade_name": fake.company_suffix(),
        "/address": fake.street_address(),
        "/city": fake.city(),
        "/state": fake.state_abbr(),
        "/zip": fake.zipcode(),
        "/phone": fake.phone_number(),
        "/year": str(random.randint(2020, 2024))
    }

def create_filled_pdf(data):
    """Create a filled PDF using the template."""
    try:
        # Get template
        template_buffer = download_template()
        if not template_buffer:
            return None
            
        # Create reader and writer
        reader = PdfReader(template_buffer)
        writer = PdfWriter()

        # Get the first page
        page = reader.pages[0]
        writer.add_page(page)
        
        # Try to get form fields
        fields = reader.get_fields()
        if fields:
            st.write("Found form fields:", fields.keys())
        
        # Try to fill in the form
        writer.update_page_form_field_values(
            writer.pages[0],
            data
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

# Add debug toggle
debug_mode = st.checkbox("Enable Debug Mode")

# Show template information
if debug_mode:
    st.subheader("Template Information")
    template_buffer = download_template()
    if template_buffer:
        reader = PdfReader(template_buffer)
        st.write("PDF Version:", reader.pdf_version)
        st.write("Number of Pages:", len(reader.pages))
        st.write("Is Encrypted:", reader.is_encrypted)
        fields = reader.get_fields()
        if fields:
            st.write("Form Fields Found:", list(fields.keys()))
        else:
            st.write("No form fields found in template")

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

# Add additional debugging information
if debug_mode:
    st.subheader("Debug Information")
    if hasattr(st.session_state, 'form_data'):
        st.write("Current form data:", st.session_state.form_data)
# Debug information
if st.checkbox("Show Debug Information"):
    st.write("Template URL:", "https://www.irs.gov/pub/irs-pdf/f941sd.pdf")
    if hasattr(st.session_state, 'form_data'):
        st.write("Current Form Data:", st.session_state.form_data)
