import streamlit as st
import requests
import io
import os
from pypdf import PdfReader, PdfWriter
from faker import Faker
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

fake = Faker()

def generate_data():
    """Generate synthetic form data."""
    ein = f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}"
    return {
        "ein": ein,
        "business_name": fake.company(),
        "trade_name": fake.company_suffix(),
        "address": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip_code": fake.zipcode(),
        "phone": fake.phone_number(),
        "year": str(random.randint(2020, 2024))
    }

def create_overlay(data):
    """Create a PDF overlay with the form data."""
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    
    # Position data on the form (coordinates need to be adjusted)
    positions = {
        "ein": (100, 700),
        "business_name": (150, 660),
        "trade_name": (150, 620),
        "address": (150, 580),
        "city": (150, 540),
        "state": (350, 540),
        "zip_code": (400, 540),
        "phone": (150, 500),
        "year": (500, 700)
    }
    
    # Add text to the canvas
    for field, value in data.items():
        x, y = positions[field]
        c.drawString(x, y, str(value))
    
    c.save()
    packet.seek(0)
    return packet

def merge_pdfs(template_url, overlay_pdf):
    """Merge the template with the overlay."""
    try:
        # Download template
        response = requests.get(template_url)
        if response.status_code != 200:
            st.error("Failed to download template")
            return None
            
        # Create PDF readers
        template_pdf = PdfReader(io.BytesIO(response.content))
        overlay = PdfReader(overlay_pdf)
        
        # Create writer
        writer = PdfWriter()
        
        # Merge pages
        page = template_pdf.pages[0]
        page.merge_page(overlay.pages[0])
        writer.add_page(page)
        
        # Write to buffer
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)
        
        return output_buffer
        
    except Exception as e:
        st.error(f"Error merging PDFs: {str(e)}")
        return None

# Main Streamlit app
st.title("IRS Form 941 Schedule D Generator")

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
        # Create overlay with form data
        overlay_pdf = create_overlay(st.session_state.form_data)
        
        # Merge with template
        url = "https://www.irs.gov/pub/irs-pdf/f941sd.pdf"
        pdf_buffer = merge_pdfs(url, overlay_pdf)
        
        if pdf_buffer:
            st.download_button(
                label="Download Filled Form",
                data=pdf_buffer,
                file_name="filled_form_941sd.pdf",
                mime="application/pdf"
            )

# Debug information
if st.checkbox("Show Debug Information"):
    st.write("Template URL:", "https://www.irs.gov/pub/irs-pdf/f941sd.pdf")
    if hasattr(st.session_state, 'form_data'):
        st.write("Current Form Data:", st.session_state.form_data)
