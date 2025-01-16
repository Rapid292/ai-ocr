import os
import re
import json
from dotenv import load_dotenv
from typing import List
from google.cloud import vision, storage
from enum import Enum
from portkey_ai import Portkey
from pydantic import BaseModel, ValidationError, Field
import logfire


# Load environment variables
load_dotenv()

# Configure logging
logfire.configure(token=os.getenv('LOGFIRE_TOKEN'))

# Google Vision Client
class GoogleVisionClient:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    def async_detect_document(self, gcs_source_uri: str, gcs_destination_uri: str, mime_type: str = "application/pdf", batch_size: int = 2) -> List[storage.Blob]:
        """Perform OCR on a PDF/TIFF file stored in GCS."""
        gcs_source = vision.GcsSource(uri=gcs_source_uri)
        input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)

        gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
        output_config = vision.OutputConfig(gcs_destination=gcs_destination, batch_size=batch_size)

        async_request = vision.AsyncAnnotateFileRequest(
            features=[vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)],
            input_config=input_config,
            output_config=output_config,
        )

        operation = self.client.async_batch_annotate_files(requests=[async_request])
        logfire.info("Waiting for the operation to finish.")
        operation.result(timeout=420)

        # List output files in GCS
        storage_client = storage.Client()
        match = re.match(r"gs://([^/]+)/(.+)", gcs_destination_uri)
        bucket_name = match.group(1)
        prefix = match.group(2)

        bucket = storage_client.get_bucket(bucket_name)
        blob_list = [
            blob
            for blob in list(bucket.list_blobs(prefix=prefix))
            if not blob.name.endswith("/")
        ]

        return blob_list

# Text Extractor
class TextExtractor:
    @staticmethod
    def get_combined_extract_text(blob_list: List[storage.Blob]) -> str:
        """Combine text from all blobs."""
        combined_text = ""
        for blob in blob_list:
            json_string = blob.download_as_bytes().decode("utf-8")
            try:
                response = json.loads(json_string)
                for page_response in response["responses"]:
                    # Extract the full text annotation
                    annotation = page_response["fullTextAnnotation"]
                    # Append the text to the combined_text string
                    combined_text += annotation["text"] + "\n"

            except ValidationError as e:
                logfire.error(f"Validation error in JSON response: {e}")
                raise

        logfire.info("Combined text extracted successfully.")
        return combined_text

# Portkey Client
class PortkeyClient:
    def __init__(self, api_key: str, base_url: str = "https://api.portkey.ai/v1"):
        self.client = Portkey(api_key=api_key, base_url=base_url)

    def send_to_portkey(self, prompt_id: str, text: str) -> dict:
        """Send text to Portkey for processing."""
        payload = {
            "prompt_id": prompt_id,
            "variables": {"text": text},
        }
        logfire.info("Sending request to Portkey with payload.")
        try:
            response = self.client.prompts.completions.create(**payload)
            logfire.info("Portkey response received.")
            return response
        except Exception as e:
            logfire.error(f"Error sending request to Portkey: {e}")
            raise

# Main Orchestrator
class DocumentProcessor:
    def __init__(self, vision_client: GoogleVisionClient, text_extractor: TextExtractor, portkey_client: PortkeyClient):
        self.vision_client = vision_client
        self.text_extractor = text_extractor
        self.portkey_client = portkey_client

    def process_document(self, gcs_source_uri: str, gcs_destination_uri: str, prompt_id: str) -> dict:
        """Process a document and extract structured data using Portkey."""
        # Step 1: Extract text using Google Vision
        blob_list = self.vision_client.async_detect_document(gcs_source_uri, gcs_destination_uri)
        combined_text = self.text_extractor.get_combined_extract_text(blob_list)

        # Step 2: Send text to Portkey
        response = self.portkey_client.send_to_portkey(prompt_id, combined_text)

        # Step 3: Parse and validate the response
        extracted_json = self.parse_and_validate_response(response)
        return extracted_json

    def parse_and_validate_response(self, response: dict) -> dict:
        """Parse and validate the response from Portkey."""
        content = response.choices[0].message.content

        # Remove the Markdown code block (```json and ```)
        if content.startswith("```json") and content.endswith("```"):
            content = content[7:-3].strip()  # Remove ```json and ```

        try:
            extracted_json = json.loads(content)
            logfire.info("Extracted JSON validated successfully.")
            return extracted_json
        except ValidationError as e:
            logfire.error(f"Validation error in extracted JSON: {e}")
            raise

# Factory for Dependency Injection
class ClientFactory:
    @staticmethod
    def create_vision_client() -> GoogleVisionClient:
        return GoogleVisionClient()

    @staticmethod
    def create_text_extractor() -> TextExtractor:
        return TextExtractor()

    @staticmethod
    def create_portkey_client(api_key: str) -> PortkeyClient:
        return PortkeyClient(api_key=api_key)

# Main Function
def main():
    gcs_destination_uri = os.getenv('OUTPUT_DOCUMENT_PATH')
    gcs_source_uri = os.getenv('INPUT_DOCUMENT_PATH')
    portkey_prompt_id = os.getenv('PORTKEY_PROMPT_ID')
    portkey_api_key = os.getenv('PORTKEY_API_KEY')

    # Initialize clients
    logfire.info("Initialize Vision Client.")
    vision_client = ClientFactory.create_vision_client()

    logfire.info("Initialize Text Extractor")
    text_extractor = ClientFactory.create_text_extractor()

    logfire.info("Initialized PortKey Client.")
    portkey_client = ClientFactory.create_portkey_client(portkey_api_key)

    # Process document
    processor = DocumentProcessor(vision_client, text_extractor, portkey_client)
    try:
        logfire.info("Document processing Started.")
        result = processor.process_document(gcs_source_uri, gcs_destination_uri, portkey_prompt_id)
        logfire.info("Document processing completed successfully.")
        print("Extracted JSON Output:")
        print(json.dumps(result, indent=4))
    except Exception as e:
        logfire.error(f"Document processing failed: {e}")

if __name__ == "__main__":
    main()