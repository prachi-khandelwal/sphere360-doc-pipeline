from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class DocumentExtraction(BaseModel):
    """ Schema for LLM extraction input """

    document_type: str = Field(
        description = "Type of document (e.g., driver_license, invoice, certificate)",
    )

    extracted_fields: Dict[str, Any] = Field(
        description = "Key Fields extracted from document"
    )

    expiry_date: Optional[str] = Field(
        description = "Expiry/expiration date in ISO format (YYYY-MM-DD). Look for: 'Valid Through', 'Expires', 'Expiry Date', 'Valid Until', 'Exp Date', 'Good Through'. Convert any date format found to YYYY-MM-DD.",
        default = None
    )

    activation_date: Optional[str] = Field(
        description = "Issue/start/activation date in ISO format (YYYY-MM-DD). Look for: 'Issue Date', 'Issued', 'Start Date', 'Effective Date', 'Date Issued', 'Created'. Convert any date format found to YYYY-MM-DD.",
        default = None
    )

    summary: str = Field(
    description = "Brief one-sentence summary of the document"
    )

    confidence: float = Field(
    description="Confidence score from 0.0 to 1.0"
    )

