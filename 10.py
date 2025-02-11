import streamlit as st
import requests
import io
from pypdf import PdfReader, PdfWriter
from faker import Faker
import random

fake = Faker()

def download_and_analyze_pdf():
    """Download the PDF and analyze its structure."""
    url = "https://www.irs.gov/pub/irs-pdf/f941sd.pdf"
    
    try:
        # Download the PDF
        response = requests.get(url)
        if response.status_code != 200:
            st.error("Failed to download the PDF")
            return None
            
        # Save the PDF content to a buffer
        pdf_buffer = io.BytesIO(response.content)
        
        # Create a PDF reader
        reader = PdfReader(pdf_buffer)
        
        # Get form fields
        fields = reader.get_fields()
        
        # Display PDF information
        st.write("PDF Information:")
        st.write(f"Number of pages: {len(reader.pages)}")
        st.write(f"Is Encrypted: {reader.is_encrypted}")
        st.write("Form fields found:", "Yes" if fields else "No")
        
        if fields:
            st.write("Field names:")
            for field_name in fields.keys():
                st.write(f"- {field_name}")
        
        return pdf_buffer
        
    except Exception as e:
        st.error(f"Error analyzing PDF: {str(e)}")
        return None

def generate_test_data():
    """Generate test data with multiple field name patterns."""
    data = {
        # Try various field name patterns
        "f1_01": fake.numerify(text="#########"),
        "f1_01[0]": fake.numerify(text="#########"),
        "topmostSubform[0].Page1[0].f1_01[0]": fake.numerify(text="#########"),
        "TextField1": fake.company(),
        "Text1": fake.company(),
        # Add more variations...
    }
    return data

def attempt_fill_pdf(pdf_buffer, data):
    """Attempt to fill the PDF with multiple approaches."""
    try:
        # Create reader and writer
        reader = PdfReader(pdf_buffer)
        writer = PdfWriter()
        
        # Add the first page
        writer.add_page(reader.pages[0])
        
        # Try to fill fields
        st.write("Attempting to fill fields...")
        writer.update_page_form_field_values(writer.pages[0], data)
        
        # Save to new buffer
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)
        
        return output_buffer
        
    except Exception as e:
        st.error(f"Error filling PDF: {str(e)}")
        return None

# Main app
st.title("PDF Form Debug Tool")

# Analyze PDF structure
st.subheader("Step 1: Analyze PDF")
if st.button("Analyze PDF Structure"):
    pdf_buffer = download_and_analyze_pdf()
    if pdf_buffer:
        st.session_state['pdf_buffer'] = pdf_buffer
        st.success("PDF analyzed successfully")

# Generate and show test data
st.subheader("Step 2: Generate Test Data")
if st.button("Generate Test Data"):
    test_data = generate_test_data()
    st.session_state['test_data'] = test_data
    st.write("Generated test data:")
    st.json(test_data)

# Attempt to fill PDF
st.subheader("Step 3: Fill PDF")
if st.button("Attempt Fill"):
    if 'pdf_buffer' not in st.session_state or 'test_data' not in st.session_state:
        st.warning("Please complete steps 1 and 2 first")
    else:
        filled_pdf = attempt_fill_pdf(st.session_state['pdf_buffer'], st.session_state['test_data'])
        if filled_pdf:
            st.download_button(
                "Download Filled PDF",
                filled_pdf,
                "filled_form.pdf",
                "application/pdf"
            )
