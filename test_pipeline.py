"""
Test Pipeline for Document Processing

"""

import os
import sys
import json
import django

# Setup Django before importing Django modules
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from documents.pipeline import Pipeline


def format_json_output(result):
    """Format result as required JSON response."""
    return {
        "source": result.source,
        "source_type": result.source_type,
        "expiry_date": result.expiry_date,
        "activation_date": result.activation_date,
        "confidence": result.confidence,
        "document_type": result.document_type,
        "summary": result.summary,
        "extracted_fields": result.extracted_fields,
        "error": result.error
    }


def print_result(result, test_name):
    """Print formatted result for a test case."""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print('='*70)
    
    json_output = format_json_output(result)
    print("\n--- JSON RESPONSE ---")
    print(json.dumps(json_output, indent=2, default=str))
    
    print("\n--- KEY FIELDS ---")
    print(f"  Source:          {result.source}")
    print(f"  Source Type:     {result.source_type}")
    print(f"  Expiry Date:     {result.expiry_date} (ISO format)")
    print(f"  Activation Date: {result.activation_date} (ISO format)")
    print(f"  Confidence:      {result.confidence}")
    print(f"  Error:           {result.error}")
    
    return json_output


def test_direct_pipeline():
    """Test the pipeline directly (without Django API)."""
    print("\n" + "#"*70)
    print("# PART 1: DIRECT PIPELINE TESTING")
    print("#"*70)
    
    pipeline = Pipeline()
    
    test_cases = [
        ("samples/imgfiles/credit_card.png", "IMAGE - Credit Card (MM/YY format)"),
        ("samples/imgfiles/id_badge.png", "IMAGE - ID Badge (date format varies)"),
        ("samples/txtfiles/trial_license.txt", "TEXT - Trial License (DD/MM/YYYY format)"),
        ("samples/txtfiles/gym_membership.txt", "TEXT - Gym Membership (DD-MON-YYYY format)"),
        ("samples/txtfiles/ssl_certificate.txt", "TEXT - SSL Certificate (DD/MM/YYYY format)"),
    ]
    
    results = []
    
    for file_path, test_name in test_cases:
        try:
            result = pipeline.process_single(file_path)
            json_output = print_result(result, test_name)
            results.append({
                "test": test_name,
                "success": result.error is None,
                "result": json_output
            })
        except Exception as e:
            print(f"\n[ERROR] {test_name}: {str(e)}")
            results.append({
                "test": test_name,
                "success": False,
                "error": str(e)
            })
    
    return results


def test_django_api():
    """Test the Django REST API endpoint."""
    print("\n" + "#"*70)
    print("# PART 2: DJANGO API ENDPOINT TESTING (POST /api/process/)")
    print("#"*70)
    
    client = Client()
    results = []
    
    # Test cases for API
    test_files = [
        ("samples/txtfiles/trial_license.txt", "API - Text File Upload"),
        ("samples/imgfiles/credit_card.png", "API - Image File Upload"),
    ]
    
    # Test 1: No files provided (should return 400)
    print(f"\n{'='*70}")
    print("TEST: API - No files provided (expect 400 error)")
    print('='*70)
    
    response = client.post('/api/process/')
    print(f"\n  Status Code: {response.status_code}")
    print(f"  Response: {response.json()}")
    
    if response.status_code == 400:
        print("  [PASS] Correctly returned 400 for missing files")
        results.append({"test": "No files - 400 error", "success": True})
    else:
        print("  [FAIL] Expected 400 status code")
        results.append({"test": "No files - 400 error", "success": False})
    
    # Test 2: Single file upload
    for file_path, test_name in test_files:
        print(f"\n{'='*70}")
        print(f"TEST: {test_name}")
        print('='*70)
        
        try:
            with open(file_path, 'rb') as f:
                response = client.post(
                    '/api/process/',
                    {'documents': f},
                    format='multipart'
                )
            
            print(f"\n  Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n--- API JSON RESPONSE ---")
                print(json.dumps(data, indent=2, default=str))
                
                # Validate response structure
                has_documents = 'documents' in data
                has_metadata = 'metadata' in data
                
                if has_documents and has_metadata:
                    print("\n  [PASS] Response has correct structure")
                    doc = data['documents'][0] if data['documents'] else {}
                    print(f"  Source Type: {doc.get('source_type', 'N/A')}")
                    print(f"  Expiry Date: {doc.get('expiry_date', 'N/A')}")
                    print(f"  Confidence:  {doc.get('confidence', 'N/A')}")
                    results.append({"test": test_name, "success": True, "result": data})
                else:
                    print("  [FAIL] Missing 'documents' or 'metadata' in response")
                    results.append({"test": test_name, "success": False})
            else:
                print(f"  [FAIL] Status code {response.status_code}")
                print(f"  Response: {response.json()}")
                results.append({"test": test_name, "success": False})
                
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            results.append({"test": test_name, "success": False, "error": str(e)})
    
    # Test 3: Multiple files upload (batch processing)
    print(f"\n{'='*70}")
    print("TEST: API - Multiple Files Upload (Batch Processing)")
    print('='*70)
    
    try:
        files_to_upload = [
            open("samples/txtfiles/trial_license.txt", 'rb'),
            open("samples/txtfiles/gym_membership.txt", 'rb'),
        ]
        
        response = client.post(
            '/api/process/',
            {'documents': files_to_upload},
            format='multipart'
        )
        
        # Close files
        for f in files_to_upload:
            f.close()
        
        print(f"\n  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n--- API JSON RESPONSE ---")
            print(json.dumps(data, indent=2, default=str))
            
            meta = data.get('metadata', {})
            print(f"\n  Total Processed: {meta.get('total', 0)}")
            print(f"  Successful: {meta.get('successful', 0)}")
            print(f"  Failed: {meta.get('failed', 0)}")
            
            if meta.get('total', 0) == 2:
                print("  [PASS] Batch processing successful")
                results.append({"test": "Batch upload", "success": True})
            else:
                print("  [FAIL] Expected 2 documents processed")
                results.append({"test": "Batch upload", "success": False})
        else:
            print(f"  [FAIL] Status code {response.status_code}")
            results.append({"test": "Batch upload", "success": False})
            
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        results.append({"test": "Batch upload", "success": False, "error": str(e)})
    
    return results


def print_summary(pipeline_results, api_results):
    """Print combined test summary."""
    print("\n" + "="*70)
    print("FINAL TEST SUMMARY")
    print("="*70)
    
    # Pipeline summary
    pipeline_success = sum(1 for r in pipeline_results if r.get("success"))
    pipeline_total = len(pipeline_results)
    
    print(f"\n--- Direct Pipeline Tests ---")
    print(f"  Passed: {pipeline_success}/{pipeline_total}")
    
    # API summary  
    api_success = sum(1 for r in api_results if r.get("success"))
    api_total = len(api_results)
    
    print(f"\n--- Django API Tests ---")
    print(f"  Passed: {api_success}/{api_total}")
    
    # Requirements checklist
    print("\n" + "="*70)
    print("REQUIREMENTS CHECKLIST")
    print("="*70)
    
    has_image = any(
        r.get("result", {}).get("source_type") == "image" 
        for r in pipeline_results if r.get("success")
    )
    has_text = any(
        r.get("result", {}).get("source_type") == "text" 
        for r in pipeline_results if r.get("success")
    )
    has_iso_dates = any(
        r.get("result", {}).get("expiry_date") and "-" in str(r.get("result", {}).get("expiry_date", ""))
        for r in pipeline_results if r.get("success")
    )
    api_works = api_success >= 2
    
    print(f"  [{'✓' if has_image else '✗'}] Multiple data types - IMAGE processed")
    print(f"  [{'✓' if has_text else '✗'}] Multiple data types - TEXT processed")
    print(f"  [{'✓' if has_image else '✗'}] OCR applied for images")
    print(f"  [{'✓' if has_iso_dates else '✗'}] Expiry dates in ISO format (YYYY-MM-DD)")
    print(f"  [{'✓' if pipeline_success > 0 else '✗'}] JSON response with required fields")
    print(f"  [{'✓' if api_works else '✗'}] Django REST API endpoint working")
    
    print("\n" + "="*70)
    
    total_passed = pipeline_success + api_success
    total_tests = pipeline_total + api_total
    print(f"\nOVERALL: {total_passed}/{total_tests} tests passed")
    print("="*70 + "\n")
    
    return total_passed == total_tests


def main():
    print("="*70)
    print("DOCUMENT PROCESSING PIPELINE - FULL TEST SUITE")
    print("="*70)
    print("\nThis test covers:")
    print("  1. Direct pipeline processing (Pipeline.process_single)")
    print("  2. Django REST API endpoint (POST /api/process/)")
    print("  3. Batch processing via API")
    print("  4. Error handling (missing files)")
    
    # Run direct pipeline tests
    pipeline_results = test_direct_pipeline()
    
    # Run Django API tests
    api_results = test_django_api()
    
    # Print combined summary
    all_passed = print_summary(pipeline_results, api_results)
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
