import streamlit as st
import requests
import io
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

def generate_test_data():
    """Generate test data for form fields."""
    return {
        "ein1": str(random.randint(10, 99)),
        "ein2": str(random.randint(1000000, 9999999)),
        "business_name": fake.company(),
        "trade_name": fake.company_suffix(),
        "address": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip": fake.zipcode(),
        "phone": fake.phone_number(),
        "year": str(random.randint(2020, 2024))
    }

def analyze_pdf(pdf_buffer):
    """Analyze PDF structure and return information about it."""
    try:
        reader = PdfReader(pdf_buffer)
        info = {
            "version": reader.pdf_version,
            "num_pages": len(reader.pages),
            "encrypted": reader.is_encrypted,
            "fields": reader.get_fields()
        }
        return info
    except Exception as e:
        st.error(f"Error analyzing PDF: {str(e)}")
        return None

def create_field_patterns(data):
    """Create different patterns for field names."""
    patterns = {}
    for key, value in data.items():
        patterns[key] = value
        patterns[f"/{key}"] = value
        patterns[f"form1[0].{key}"] = value
        patterns[f"topmostSubform[0].Page1[0].{key}"] = value
    return patterns

def try_fill_pdf(data):
    """Attempt to fill the PDF form."""
    try:
        # Get template
        template_buffer = download_template()
        if not template_buffer:
            return None
            
        # Create reader and writer
        reader = PdfReader(template_buffer)
        writer = PdfWriter()
        
        # Add first page
        page = reader.pages[0]
        writer.add_page(page)
        
        # Create field patterns and try to update fields
        field_patterns = create_field_patterns(data)
        writer.update_page_form_field_values(writer.pages[0], field_patterns)
        
        # Save to buffer
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        return output
        
    except Exception as e:
        st.error(f"Error filling PDF: {str(e)}")
        return None

# Main Streamlit app
st.title("IRS Form 941 Schedule D Generator")

# Download and analyze template
if st.button("Analyze Template"):
    template_buffer = download_template()
    if template_buffer:
        info = analyze_pdf(template_buffer)
        if info:
            st.write("PDF Information:")
            st.write(f"- Version: {info['version']}")
            st.write(f"- Pages: {info['num_pages']}")
            st.write(f"- Encrypted: {info['encrypted']}")
            if info['fields']:
                st.write("Form Fields Found:")
                for field in info['fields'].keys():
                    st.write(f"- {field}")
            else:
                st.write("No fillable form fields found in the PDF")

# Generate Data button
if st.button("Generate Test Data"):
    st.session_state.form_data = generate_test_data()
    st.write("Generated Test Data:")
    for key, value in st.session_state.form_data.items():
        st.write(f"{key}: {value}")

# Try to fill PDF
if st.button("Try Fill PDF"):
    if not hasattr(st.session_state, 'form_data'):
        st.warning("Please generate test data first")
    else:
        filled_pdf = try_fill_pdf(st.session_state.form_data)
        if filled_pdf:
            st.download_button(
                label="Download Filled Form",
                data=filled_pdf,
                file_name="filled_form_941sd.pdf",
                mime="application/pdf"
            )
