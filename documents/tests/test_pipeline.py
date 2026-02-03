

import pytest
import re
from documents.pipeline import Pipeline


# Shared pipeline instance
@pytest.fixture(scope="module")
def pipeline():
    return Pipeline()


# Requirement: Multiple data types work
@pytest.mark.parametrize("file_path,expected_type", [
    ("samples/imgfiles/credit_card.png", "image"),
    ("samples/txtfiles/trial_license.txt", "text"),
    ("samples/sample_PFD/warranty_card.pdf", "pdf"),
])
def test_multiple_file_types(pipeline, file_path, expected_type):
    """Test that different file types process successfully."""
    result = pipeline.process_single(file_path)
    assert result.error is None, f"Processing failed: {result.error}"
    assert result.source_type == expected_type


# Requirement: Expiry date in ISO format
def test_expiry_date_iso_format(pipeline):
    """Test that expiry dates are in YYYY-MM-DD format."""
    result = pipeline.process_single("samples/imgfiles/credit_card.png")
    assert result.expiry_date is not None, "No expiry date extracted"
    
    # Verify ISO format: YYYY-MM-DD
    iso_pattern = r"^\d{4}-\d{2}-\d{2}$"
    assert re.match(iso_pattern, result.expiry_date), \
        f"Date '{result.expiry_date}' not in ISO format YYYY-MM-DD"


# Requirement: Different date formats handled
@pytest.mark.parametrize("file_path,description", [
    ("samples/imgfiles/credit_card.png", "MM/YY format"),
    ("samples/txtfiles/gym_membership.txt", "DD-MON-YYYY format"),
    ("samples/txtfiles/ssl_certificate.txt", "DD/MM/YYYY format"),
])
def test_various_date_formats(pipeline, file_path, description):
    """Test that various date formats are normalized to ISO."""
    result = pipeline.process_single(file_path)
    
    # Should have at least one date extracted
    has_date = result.expiry_date is not None or result.activation_date is not None
    assert has_date, f"No dates extracted from {description}"
    
    # If expiry exists, should be ISO format
    if result.expiry_date:
        assert "-" in result.expiry_date, f"Expiry not ISO format: {result.expiry_date}"


# Requirement: JSON response has required fields
def test_response_has_required_fields(pipeline):
    """Test that response contains all required fields."""
    result = pipeline.process_single("samples/txtfiles/trial_license.txt")
    
    # Required fields per assignment
    assert hasattr(result, 'expiry_date'), "Missing expiry_date field"
    assert hasattr(result, 'activation_date'), "Missing activation_date field"
    assert hasattr(result, 'source_type'), "Missing source_type field"
    assert hasattr(result, 'confidence'), "Missing confidence field"
    assert hasattr(result, 'source'), "Missing source field"
    
    # Confidence should be a valid score
    assert 0.0 <= result.confidence <= 1.0, f"Invalid confidence: {result.confidence}"
