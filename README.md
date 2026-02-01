# Sphere360 Document Pipeline

AI-powered document processing pipeline for extracting structured data from documents.

## Overview

Processes multiple documents (PDFs, images, text files) in batch, extracts key information using OCR and LLM, and returns structured JSON output with confidence scores.

**Key Features:**
- Batch processing of multiple documents
- Support for PDF, images (OCR), and text files
- Date extraction with ISO normalization
- Confidence scoring for extraction quality
- Privacy-first: Default local LLM (Ollama)

## Architecture

```
Input (PDF/Image/Text) → Loader (Factory) → Text Extraction → LLM Processing → JSON Output
```

### Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| LLM Provider | Ollama (local) | Data privacy - documents never leave system |
| LLM Framework | LangChain | Structured output, provider-agnostic |
| OCR | Tesseract | Free, open-source, reliable |
| PDF | PyMuPDF | Fast text extraction |

## Quick Start

### Option 1: Local LLM (Ollama) - Recommended

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2

# Install dependencies
poetry install

# Run
python manage.py runserver
```

### Option 2: Cloud LLM (Groq) - No local setup

```bash
export LLM_PROVIDER=groq
export GROQ_API_KEY=your_key

poetry install
python manage.py runserver
```

## API Usage

```bash
# Process documents
curl -X POST http://localhost:8000/api/process/ \
  -F "documents=@license.pdf" \
  -F "documents=@insurance.png"
```

## Output Schema

```json
{
  "documents": [
    {
      "source": "license.pdf",
      "source_type": "pdf",
      "document_type": "driver_license",
      "extracted_fields": {
        "holder_name": "John Doe",
        "license_number": "D1234567"
      },
      "expiry_date": "2027-03-15",
      "activation_date": "2022-03-15",
      "confidence": 0.92,
      "summary": "Driver's license for John Doe, expires March 2027"
    }
  ],
  "processing_metadata": {
    "total_documents": 1,
    "successful": 1,
    "failed": 0
  }
}
```

## Project Structure

```
sphere360-doc-pipeline/
├── documents/           # Main Django app
│   ├── loaders/        # Document loaders (PDF, Image, Text)
│   ├── extractors/     # Date extraction, confidence scoring
│   ├── llm/            # LLM integration
│   └── api/            # REST endpoints
└── samples/            # Sample documents for testing
```
