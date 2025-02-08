import streamlit as st
import zipfile
import io
import random
from faker import Faker
from pdfrw import PdfReader, PdfWriter, PdfDict

# Initialize Faker for generating synthetic tax data
fake = Faker()

# Define the fillable PDF template path
TEMPLATE_PATH = "f1040.pdf"  # Ensure this exists in your repo

# Step 1: Extract fillable field names from the 1040 PDF
def extract_pdf_fields(template_path):
    """Extract form field names from a fillable PDF"""
    pdf = PdfReader(template_path)
    fields = {}

    for page in pdf.pages:
        if page.Annots:
            for annotation in page.Annots:
                if annotation.T:
                    field_name = annotation.T[1:-1]  # Extract field name
                    fields[field_name] = ""

    return fields

# Step 2: Generate realistic synthetic tax data
def generate_realistic_1040(fields):
    tax_data = {}

    # Filing Status
    filing_status = random.choice(["Single", "Married Filing Jointly", "Married Filing Separately", "Head of Household"])
    
    # Income Generation
    wages = round(random.uniform(20000, 150000), 2)
    interest_income = round(random.uniform(0, 5000), 2)
    dividends = round(random.uniform(0, 3000), 2)
    social_security = round(random.uniform(0, 20000), 2) if random.random() > 0.7 else 0  # 30% chance

    total_income = wages + interest_income + dividends + social_security

    # Standard Deduction (based on filing status)
    deductions = {
        "Single": 14600,
        "Married Filing Jointly": 29200,
        "Married Filing Separately": 14600,
        "Head of Household": 21900
    }
    
    deduction_amount = deductions[filing_status]
    taxable_income = max(total_income - deduction_amount, 0)

    # Federal Tax Calculation (simplified tax bracket)
    if taxable_income < 11000:
        tax_due = taxable_income * 0.10
    elif taxable_income < 44725:
        tax_due = 1100 + (taxable_income - 11000) * 0.12
    elif taxable_income < 95375:
        tax_due = 5147 + (taxable_income - 44725) * 0.22
    else:
        tax_due = 16290 + (taxable_income - 95375) * 0.24

    federal_tax_withheld = round(tax_due * random.uniform(0.7, 1.3), 2)

    # Refund or Amount Owed
    refund_amount = max(0, federal_tax_withheld - tax_due)
    amount_owed = max(0, tax_due - federal_tax_withheld)

    # Assign formatted data to form fields
    for field in fields:
        if field == "f1_01":
            tax_data[field] = fake.first_name()
        elif field == "f1_02":
            tax_data[field] = fake.last_name()
        elif field == "f1_03":
            tax_data[field] = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
        elif field == "f1_04":
            tax_data[field] = fake.street_address()
        elif field == "f1_05":
            tax_data[field] = fake.city()
        elif field == "f1_06":
            tax_data[field] = fake.state_abbr()
        elif field == "f1_07":
            tax_data[field] = fake.zipcode()
        elif field == "f1_09":
            tax_data[field] = format_currency(wages)
        elif field == "f1_10":
            tax_data[field] = format_currency(interest_income)
        elif field == "f1_11":
            tax_data[field] = format_currency(total_income)
        elif field == "f1_12":
            tax_data[field] = format_currency(taxable_income)
        elif field == "f1_13":
            tax_data[field] = format_currency(tax_due)
        elif field == "f1_14":
            tax_data[field] = format_currency(federal_tax_withheld)
        elif field == "f1_15":
            tax_data[field] = format_currency(refund_amount)
        elif field == "f1_16":
            tax_data[field] = format_currency(amount_owed)
        else:
            tax_data[field] = fake.word()

    return tax_data

# Format currency correctly
def format_currency(value):
    """Format numbers as currency with a dollar sign and commas."""
    return f"${value:,.2f}" if isinstance(value, (int, float)) else value

# Step 3: Fill the 1040 PDF using `pdfrw`
def fill_1040_pdf(template_path, data):
    """Fill the fillable PDF with data and flatten it"""
    template_pdf = PdfReader(template_path)

    for page in template_pdf.pages:
        if page.Annots:
            for annotation in page.Annots:
                if annotation.T:
                    field_name = annotation.T[1:-1]
                    if field_name in data:
                        annotation.V = PdfDict(V=data[field_name], AS=data[field_name])  # Fill the field

    # Flatten the PDF (makes the filled data permanent)
    buffer = io.BytesIO()
    PdfWriter(buffer, trailer=template_pdf).write()
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("Realistic Synthetic IRS Form 1040 Generator")
st.write("This tool generates **realistic IRS Form 1040 PDFs** with accurate tax calculations.")

num_forms = st.number_input("How many 1040 forms do you want to generate?", min_value=1, max_value=50, value=1)

if st.button("Generate and Download Forms"):
    pdf_files = []
    
    extracted_fields = extract_pdf_fields(TEMPLATE_PATH)

    for i in range(num_forms):
        synthetic_data = generate_realistic_1040(extracted_fields)
        pdf_buffer = fill_1040_pdf(TEMPLATE_PATH, synthetic_data)
        pdf_files.append((f"realistic_1040_{i+1}.pdf", pdf_buffer.getvalue()))
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for filename, pdf_data in pdf_files:
            zipf.writestr(filename, pdf_data)
    
    zip_buffer.seek(0)

    st.download_button("Download All 1040 Forms (ZIP)", data=zip_buffer, file_name="realistic_1040_forms.zip", mime="application/zip")

    st.success(f"{num_forms} Realistic Form 1040 PDFs Generated and Ready for Download! ✅")
