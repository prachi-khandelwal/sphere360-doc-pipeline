import os
import tempfile
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..pipeline import Pipeline, BatchResult
from dataclasses import asdict


@api_view(['POST'])
def process_documents(request):
    """ Process uploaded documents and return structured data"""

    files = request.FILES.getlist('documents')

    if not files:
        return Response(
            {"error" : "No files Provided. Use 'documents' field "},
            status = status.HTTP_400_BAD_REQUEST
        )

    # Save files temporarily and collect paths
    temp_paths = []
    temp_dir = tempfile.mktemp()

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
            "documents" : [asdict(doc) for doc in result.documents],
            "metadata" : {
                "total" : result.total,
                "successful" : result.successful,
                "failed" : result.failed,
            }
        }

        return Response(response_data)

    finally:
        # Clean up temp files
        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
