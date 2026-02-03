# Sphere360 Document Processing Pipeline

AI-powered document processing pipeline that extracts structured data from documents using OCR and LLM.

## Features

- **Multi-format Support**: PDF, Images (PNG, JPG, TIFF), Text, Word documents
- **OCR for Scanned Documents**: Tesseract support
- **Intelligent Date Extraction**: Normalizes various date formats to ISO (YYYY-MM-DD)
- **Chunking for Large Documents**: Splits and merges results from multi-page documents
- **Privacy-First**: Default local LLM (Ollama) - documents never leave your system
- **Switchable LLM Providers**: Ollama (local) or any other Provider
- **REST API**: Django DRF endpoint for document upload
- **Confidence Scoring**: Each extraction includes a confidence score (0.0-1.0)




### Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Framework | Django + DRF | Familiar, batteries included, easy API |
| LLM Provider | Ollama (local) | Data privacy, no API costs |
| LLM Framework | LangChain | Structured output, provider switching |
| OCR | Tesseract | Free, open-source, multilingual |
| PDF Parsing | PyMuPDF (fitz) | Fast, handles both text and scanned PDFs |
| Structured Output | Pydantic | Type safety, validation |

## Quick Start

### Prerequisites

- Python 3.11+
- Poetry
- Tesseract OCR (for scanned documents)

### Installation

```bash
# Clone the repository
git clone https://github.com/prachi-khandelwal/sphere360-doc-pipeline.git
cd sphere360-doc-pipeline

# Install Tesseract OCR (macOS)
brew install tesseract tesseract-lang

# Install Tesseract OCR (Ubuntu)
sudo apt-get install tesseract-ocr tesseract-ocr-hin

# Install Python dependencies
poetry install

# Copy environment file
cp .env.example .env
```

### Option 1: Local LLM with Ollama (Recommended)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull llama3.2

# Start the server
poetry run python manage.py runserver
```



# Start the server
poetry run python manage.py runserver
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `ollama` | LLM provider: `ollama` or `groq` |
| `OLLAMA_MODEL` | `llama3.1:8b` | Ollama model to use |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `GROQ_API_KEY` | - | Groq API key (required if using groq) |
| `DEBUG` | `True` | Django debug mode |


## API Usage

### Process Documents

**Endpoint:** `POST /api/process/`

**Content-Type:** `multipart/form-data`

```bash
# Single document
curl -X POST http://localhost:8000/api/process/ \
  -F "documents=@samples/txtfiles/trial_license.txt"

# Multiple documents
curl -X POST http://localhost:8000/api/process/ \
  -F "documents=@samples/imgfiles/credit_card.png" \
  -F "documents=@samples/sample_PFD/warranty_card.pdf" \
  -F "documents=@samples/txtfiles/gym_membership.txt"
```

### Response Schema

```json
{
  "documents": [
    {
      "source": "credit_card.png",
      "source_type": "image",
      "document_type": "credit_card",
      "extracted_fields": {
        "card_holder": "PRACHI KHANDELWAL",
        "card_number": "**** **** **** 1234",
        "bank": "HDFC Bank"
      },
      "expiry_date": "2028-09-01",
      "activation_date": null,
      "confidence": 0.92,
      "summary": "HDFC Bank credit card for Prachi Khandelwal",
      "error": null
    }
  ],
  "metadata": {
    "total": 1,
    "successful": 1,
    "failed": 0
  }
}
```

### Error Response

```json
{
  "documents": [
    {
      "source": "corrupted.pdf",
      "source_type": "pdf",
      "document_type": "unknown",
      "extracted_fields": {},
      "expiry_date": null,
      "activation_date": null,
      "confidence": 0.0,
      "summary": "",
      "error": "No text extracted even with OCR"
    }
  ],
  "metadata": {
    "total": 1,
    "successful": 0,
    "failed": 1
  }
}
```

## Supported File Types

| Type | Extensions | Method |
|------|------------|--------|
| PDF | `.pdf` | Direct text extraction, fallback to OCR |
| Images | `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp` | Tesseract OCR |
| Text | `.txt`, `.text` | Direct read (UTF-8) |
| Word | `.docx` | python-docx |

## Document Types Detected

The pipeline classifies documents into:
- `driver_license`
- `passport`
- `credit_card`
- `id_card`
- `invoice`
- `insurance_card`
- `certificate`
- `contract`
- `other`



## Testing

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest documents/tests/test_pipeline.py

# Run with coverage
poetry run pytest --cov=documents
```

## Development

```bash
# Start development server
poetry run python manage.py runserver


```

## Chunking Strategy

For large documents that exceed the LLM context window:

1. **Split**: Document is split into chunks (3000 chars, 200 overlap)
2. **Process**: Each chunk is processed independently
3. **Merge**: Results are intelligently merged:
   - `extracted_fields`: Combined from ALL chunks
   - `expiry_date`: From most confident chunk
   - `activation_date`: From most confident chunk
   - `document_type`: Voting (most common)
   - `confidence`: Weighted average


## Known Limitations

1. **Synchronous Processing**: API blocks during processing (async support planned)
2. **No Authentication**: API is open (add auth for production)
3. **OCR Language**: Currently English + Hindi only
4. **File Size**: No explicit limits (add for production)



## License

MIT

## Author

Prachi Khandelwal
