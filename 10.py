import pandas as pd
from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions
from typing import Dict, List


def process_form(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str = "application/pdf",
) -> Dict:
    """
    Process a form using Document AI Form Parser
    Returns extracted fields and their values
    """
    # Initialize the client
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    # Get full resource name of the processor
    resource_name = client.processor_path(project_id, location, processor_id)

    # Read the file
    with open(file_path, "rb") as file:
        file_content = file.read()

    # Create the document object
    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)

    # Configure the process request
    request = documentai.ProcessRequest(
        name=resource_name,
        raw_document=raw_document
    )

    try:
        # Process the document
        result = client.process_document(request=request)
        document = result.document
        
        # Extract fields from the document
        extracted_fields = {}
        
        print("\nExtracted fields:")
        # Get all fields from the document
        for page in document.pages:
            for field in page.form_fields:
                # Get field name and value
                field_name = get_text(field.field_name, document)
                field_value = get_text(field.field_value, document)
                confidence = field.confidence
                
                # Store in dictionary with confidence score
                extracted_fields[field_name] = {
                    'value': field_value,
                    'confidence': f"{confidence:.2%}"
                }
                
                print(f"{field_name}: {field_value} (Confidence: {confidence:.2%})")
        
        return extracted_fields

    except Exception as e:
        print(f"Error processing document: {str(e)}")
        raise


def get_text(doc_element: dict, document: documentai.Document) -> str:
    """
    Extract text from a document element
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in doc_element.text_anchor.text_segments:
        start_index = (
            int(segment.start_index)
            if segment in doc_element.text_anchor.text_segments
            else 0
        )
        end_index = int(segment.end_index)
        response += document.text[start_index:end_index]
    return response.strip()


def create_summary_dataframe(extracted_fields: Dict) -> pd.DataFrame:
    """
    Convert extracted fields to a DataFrame
    """
    data = []
    for field_name, field_info in extracted_fields.items():
        data.append({
            'Field Name': field_name,
            'Value': field_info['value'],
            'Confidence': field_info['confidence']
        })
    
    return pd.DataFrame(data)


if __name__ == "__main__":
    # Configuration
    PROJECT_ID = "YOUR_PROJECT_ID"
    LOCATION = "YOUR_PROJECT_LOCATION"  # Format is 'us' or 'eu'
    PROCESSOR_ID = "YOUR_FORM_PROCESSOR_ID"  # Make sure this is a Form Parser processor
    FILE_PATH = "your_form.pdf"

    try:
        # Process the form
        print(f"Processing form: {FILE_PATH}")
        extracted_fields = process_form(
            project_id=PROJECT_ID,
            location=LOCATION,
            processor_id=PROCESSOR_ID,
            file_path=FILE_PATH
        )

        # Create summary DataFrame
        df = create_summary_dataframe(extracted_fields)
        
        # Save results
        output_file = "form_processing_results.csv"
        df.to_csv(output_file, index=False)
        print(f"\nResults saved to {output_file}")

    except Exception as e:
        print(f"Error in main process: {str(e)}")
