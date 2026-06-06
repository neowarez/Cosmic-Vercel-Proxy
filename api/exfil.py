import json

def handler(request):
    # This will return a 200 regardless of the method, 
    # helping us confirm if the 405 is gone.
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Endpoint is active", "method": request.method})
    }
