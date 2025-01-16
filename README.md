# AI Document Processing Pipeline: Transform Your Document Workflow with Intelligent OCR and AI.

## Elevate Your Document Processing with Cutting-Edge Technology

Unlock the power of your documents with our Python-based AI Document Processing Pipeline. Combining the precision of Google Cloud Vision OCR with the intelligence of PortKey AI, this system delivers accurate text extraction and advanced analysis, transforming unstructured data into actionable insights.

## Key Features
- **High-Accuracy OCR**: Leverage Google Cloud Vision API to extract text from PDF, Images, etc of documents.
- **Intelligent Text Analysis**: Leverage **PortKey AI** for advanced Prompt Management, seamless experimentation with multiple LLM models, and comprehensive Cost Analysis to optimize AI-driven workflows.
- **Scalable and Flexible**: Designed to handle diverse document types and volumes, ensuring seamless integration into your workflow.
- **Robust Data Validation**: Pydantic ensures data integrity and type safety, minimizing errors and inconsistencies.
- **Comprehensive Logging and Monitoring**: LogFire provides real-time insights, error tracking, and performance monitoring.

## How It Works
1. **Upload Your Documents**: Place your PDFs in Google Cloud Storage can extend it to upload via API as well.
2. **Automated OCR Processing**: The pipeline retrieves documents and performs OCR using Google Cloud Vision API.
3. **Advanced Text Analysis**: PortKey AI processes the extracted text using cutting-edge LLM models and Dynamic Prompts, enabling the generation of actionable insights and empowering data-driven decision-making.
4. **Structured JSON Output**: Receive the processed data in a clean, structured JSON format, ready for further use.


## Get Started

### Setup and Configuration

1. **Install Dependencies**
   ```bash
   make install
   ```

2. **Configure Google Cloud**
   - Enable Google Cloud Vision API.
   - Set up a service account and download credentials.
   - Create a storage bucket for your documents.
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
   ```

3. **Set Environment Variables**
   Create a `.env` file with your API keys and paths:
   ```env
   PORTKEY_API_KEY=your_portkey_api_key
   INPUT_DOCUMENT_PATH=gs://your-bucket/input.pdf
   OUTPUT_DOCUMENT_PATH=gs://your-bucket/output/
   LOGFIRE_TOKEN=your_logfire_token
   PORTKEY_PROMPT_ID=your_prompt_id
   ```

### Run the Pipeline

1. **Upload Your Document**
   ```bash
   gsutil cp your_document.pdf gs://your-bucket/
   ```

2. **Execute the Processing**
   ```bash
   make run
   ```

## Project Structure

```
.
├── main.py                 # The heart of the application
├── requirements.txt        # Manage Python dependencies effortlessly
├── Makefile                # Simplify build and run operations
└── .env                    # Securely store environment variables
```

## Flow Diagram

```
Document (PDF) → Google Cloud Storage → Vision API OCR 
    → Text Extraction → PortKey AI Processing → Structured JSON Output
```

## Development and Maintenance

- **Code Formatting**
  ```bash
  make format
  ```
- **Run Tests**
  ```bash
  make test
  ```
- **Code Linting**
  ```bash
  make lint
  ```

## Resources

- [Google Cloud Vision Documentation](https://cloud.google.com/vision/docs/samples/vision-text-detection-pdf-gcs)
- [PortKey AI Documentation](https://portkey.ai/)
- [Pydantic Documentation](https://pydantic.dev/)
- [LogFire Documenation](https://pydantic.dev/logfire)

## License

MIT
