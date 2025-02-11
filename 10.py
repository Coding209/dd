import streamlit as st
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
    return {
        "f1_01[0]": str(fake.unique.random_number(digits=9, fix_len=True)),  # EIN
        "f1_02[0]": str(fake.company()),  # Business Name
        "f1_03[0]": str(random.randint(2020, 2024)),  # Year
        "f1_04[0]": str(random.randint(1, 4)),  # Quarter
        "f1_05[0]": str(round(random.uniform(50000, 200000), 2)),  # Total Wages
        "f1_06[0]": str(round(random.uniform(5000, 25000), 2)),  # Withheld Taxes
        "f1_07[0]": str(round(random.uniform(-500, 500), 2)),  # Adjustments
        "f1_08[0]": str(round(random.uniform(6000, 30000), 2))  # Total Liability
    }

def create_filled_pdf(data):
    """Create a filled PDF using the template and provided data."""
    if not os.path.exists("template.pdf"):
        st.error("Template file not found. Please ensure it was downloaded correctly.")
        return None

    try:
        # Read the template
        reader = PdfReader("template.pdf")
        writer = PdfWriter()
        
        # Get the first page
        if len(reader.pages) == 0:
            st.error("The template PDF appears to be empty")
            return None
            
        # Copy the first page
        page = reader.pages[0]
        writer.add_page(page)

        # Try to update fields
        try:
            writer.update_page_form_field_values(writer.pages[0], data)
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

# Show debug information
if st.checkbox("Show PDF Field Information"):
    try:
        if os.path.exists("template.pdf"):
            reader = PdfReader("template.pdf")
            fields = reader.get_fields()
            if fields:
                st.write("PDF Fields found:", fields.keys())
            else:
                st.warning("No fillable fields found in the PDF")
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
