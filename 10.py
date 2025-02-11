import streamlit as st
import requests
import io
from pypdf import PdfReader, PdfWriter
from faker import Faker
import random
from pypdf.generic import (
    DictionaryObject,
    NameObject,
    ArrayObject,
    createStringObject,
    NumberObject
)

fake = Faker()

def create_acroform_dictionary():
    """Create a basic AcroForm dictionary."""
    acroform = DictionaryObject()
    acroform.update({
        NameObject("/Fields"): ArrayObject(),
        NameObject("/NeedAppearances"): NameObject("/True"),
        NameObject("/SigFlags"): NumberObject(0),
    })
    return acroform

def create_text_field(name, value, x, y, width=100, height=20, page_number=0):
    """Create a text field at the specified position."""
    field = DictionaryObject()
    field.update({
        NameObject("/FT"): NameObject("/Tx"),  # Text field
        NameObject("/T"): createStringObject(name),  # Field name
        NameObject("/V"): createStringObject(value),  # Field value
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Widget"),
        NameObject("/F"): NumberObject(4),
        NameObject("/Rect"): ArrayObject([
            NumberObject(x), NumberObject(y),
            NumberObject(x + width), NumberObject(y + height)
        ]),
        NameObject("/P"): NumberObject(page_number),
    })
    return field

def add_form_fields(writer, data):
    """Add form fields to the PDF."""
    # Create AcroForm dictionary
    writer._root_object.update({
        NameObject("/AcroForm"): create_acroform_dictionary()
    })
    
    # Define field positions (these should match the form layout)
    field_positions = {
        "EIN": (50, 750),
        "Name": (150, 700),
        "TradeName": (150, 650),
        "Address": (150, 600),
        "City": (150, 550),
        "State": (350, 550),
        "ZIP": (450, 550),
        "Phone": (150, 500),
        "Year": (550, 750)
    }
    
    # Add fields
    for name, (x, y) in field_positions.items():
        value = data.get(name, "")
        field = create_text_field(name, value, x, y)
        writer._root_object["/AcroForm"]["/Fields"].append(field)

def generate_test_data():
    """Generate test data for the form."""
    return {
        "EIN": f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}",
        "Name": fake.company(),
        "TradeName": fake.company_suffix(),
        "Address": fake.street_address(),
        "City": fake.city(),
        "State": fake.state_abbr(),
        "ZIP": fake.zipcode(),
        "Phone": fake.phone_number(),
        "Year": str(random.randint(2020, 2024))
    }

def create_filled_pdf():
    """Create a PDF with form fields and fill them."""
    try:
        # Download the template
        url = "https://www.irs.gov/pub/irs-pdf/f941sd.pdf"
        response = requests.get(url)
        if response.status_code != 200:
            st.error("Failed to download template")
            return None
            
        # Create PDF reader and writer
        reader = PdfReader(io.BytesIO(response.content))
        writer = PdfWriter()
        
        # Add the first page
        writer.add_page(reader.pages[0])
        
        # Generate and add form data
        data = generate_test_data()
        st.write("Generated data:", data)
        
        # Add form fields with data
        add_form_fields(writer, data)
        
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

if st.button("Generate Filled Form"):
    pdf_buffer = create_filled_pdf()
    if pdf_buffer:
        st.download_button(
            label="Download Filled Form",
            data=pdf_buffer,
            file_name="filled_form_941sd.pdf",
            mime="application/pdf"
        )
