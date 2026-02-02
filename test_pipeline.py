# Test full pipeline with scanned PDF
from documents.pipeline import Pipeline

pipeline = Pipeline()

# Test with the scanned driver license PDF
result = pipeline.process_single("samples/sample_PFD/professional_certification.pdf")

print("--- FULL PIPELINE RESULT ---")
print(f"Source: {result.source}")
print(f"Error: {result.error}")
print(f"Document Type: {result.document_type}")
print(f"Expiry Date: {result.expiry_date}")
print(f"Activation Date: {result.activation_date}")
print(f"Confidence: {result.confidence}")
print(f"Summary: {result.summary}")
print(f"\nExtracted Fields:")
for key, value in result.extracted_fields.items():
    print(f"  {key}: {value}")
