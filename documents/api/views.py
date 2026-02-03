import os
import tempfile
import shutil
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..pipeline import Pipeline
from dataclasses import asdict


@api_view(['POST'])
def process_documents(request):
    """
    Process uploaded documents and return structured data.
    
    POST /api/process/
    Content-Type: multipart/form-data
    Body: documents[] - one or more files
    
    

    """
    files = request.FILES.getlist('documents')

    if not files:
        return Response(
            {"error": "No files provided. Use 'documents' field to upload files."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create temp directory properly 
    temp_dir = tempfile.mkdtemp(prefix='doc_pipeline_')
    temp_paths = []

    try:
        for file in files:
            temp_path = os.path.join(temp_dir, file.name)
            with open(temp_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            temp_paths.append(temp_path)

        # Process through pipeline
        pipeline = Pipeline()
        result = pipeline.process_batch(temp_paths)

        response_data = {
            "documents": [asdict(doc) for doc in result.documents],
            "metadata": {
                "total": result.total,
                "successful": result.successful,
                "failed": result.failed,
            }
        }

        return Response(response_data)

    except Exception as e:
        return Response(
            {"error": f"Processing failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    finally:
        # Clean up entire temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
