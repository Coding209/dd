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
    # Generate EIN segments
    ein_first = str(random.randint(10, 99))
    ein_second = str(random.randint(1000000, 9999999))
    
    # Generate address components
    street_num = str(random.randint(100, 9999))
    street_name = fake.street_name()
    city = fake.city()
    state = fake.state_abbr()
    zip_code = fake.zipcode()
    
    return {
        # Main company info
        "topmostSubform[0].Page1[0].EntityArea[0].f1_1[0]": ein_first,  # First part of EIN
        "topmostSubform[0].Page1[0].EntityArea[0].f1_2[0]": ein_second,  # Second part of EIN
        "topmostSubform[0].Page1[0].EntityArea[0].f1_3[0]": fake.company(),  # Company name
        "topmostSubform[0].Page1[0].EntityArea[0].f1_4[0]": fake.company_suffix(),  # Trade name
        
        # Address fields
        "topmostSubform[0].Page1[0].EntityArea[0].f1_5[0]": f"{street_num} {street_name}",  # Street address
        "topmostSubform[0].Page1[0].EntityArea[0].f1_6[0]": fake.secondary_address(),  # Suite/Room
        "topmostSubform[0].Page1[0].EntityArea[0].f1_7[0]": city,  # City
        "topmostSubform[0].Page1[0].EntityArea[0].f1_8[0]": state,  # State
        "topmostSubform[0].Page1[0].EntityArea[0].f1_9[0]": zip_code,  # ZIP
        "topmostSubform[0].Page1[0].EntityArea[0].f1_10[0]": fake.phone_number(),  # Phone
        
        # Tax Year
        "topmostSubform[0].Page1[0].YearArea[0].f1_11[0]": str(random.randint(2020, 2024)),
        
        # Type of Submission checkboxes
        "topmostSubform[0].Page1[0].TypeArea[0].c1_1[0]": "1",  # Original submission
        "topmostSubform[0].Page1[0].TypeArea[0].c1_1[1]": "0",  # Corrected submission
        
        # Filing Status checkboxes
        "topmostSubform[0].Page1[0].StatusArea[0].c1_2[0]": "1",  # Statutory merger checkbox
        "topmostSubform[0].Page1[0].StatusArea[0].c1_3[0]": "1",  # Acquired corporation
        
        # Effective Date
        "topmostSubform[0].Page1[0].DateArea[0].f1_12[0]": datetime.now().strftime("%m/%d/%Y"),
        
        # Other Party Information
        "topmostSubform[0].Page1[0].OtherPartyArea[0].f1_13[0]": str(random.randint(10, 99)),  # Other EIN first part
        "topmostSubform[0].Page1[0].OtherPartyArea[0].f1_14[0]": str(random.randint(1000000, 9999999)),  # Other EIN second part
        "topmostSubform[0].Page1[0].OtherPartyArea[0].f1_15[0]": fake.company(),  # Other party name
        "topmostSubform[0].Page1[0].OtherPartyArea[0].f1_16[0]": fake.company_suffix(),  # Other trade name
        "topmostSubform[0].Page1[0].OtherPartyArea[0].f1_17[0]": f"{fake.street_address()}",  # Other address
        "topmostSubform[0].Page1[0].OtherPartyArea[0].f1_18[0]": fake.secondary_address(),  # Other suite
        "topmostSubform[0].Page1[0].OtherPartyArea[0].f1_19[0]": fake.city(),  # Other city
        "topmostSubform[0].Page1[0].OtherPartyArea[0].f1_20[0]": fake.state_abbr(),  # Other state
        "topmostSubform[0].Page1[0].OtherPartyArea[0].f1_21[0]": fake.zipcode(),  # Other ZIP
        "topmostSubform[0].Page1[0].OtherPartyArea[0].f1_22[0]": fake.phone_number()  # Other phone
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
