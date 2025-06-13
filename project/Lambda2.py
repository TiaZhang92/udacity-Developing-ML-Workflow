import json
import sagemaker
import base64
from sagemaker.serializers import IdentitySerializer
from botocore.exceptions import ClientError

# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2025-06-12-09-52-20-702"

def lambda_handler(event, context):
    
    try:
        print(f"Raw event received: {json.dumps(event, indent=2, default=str)}")
        
        # Handle different event formats from Step Functions
        # Check if this is coming from another Lambda function with body wrapper
        if 'body' in event:
            if isinstance(event['body'], str):
                # Parse JSON string body
                body = json.loads(event['body'])
            else:
                # Direct body object
                body = event['body']
        else:
            # Direct event (no body wrapper)
            body = event
        
        print(f"Parsed body: {json.dumps(body, indent=2, default=str)}")
        
        # Validate required fields
        required_fields = ['image_data', 's3_bucket', 's3_key']
        for field in required_fields:
            if field not in body:
                raise Exception(f"Missing required field: {field}")
        
        # Check if image_data is present and not empty
        if not body['image_data']:
            raise Exception("image_data is empty")
            
        image = base64.b64decode(body['image_data'])
        print(f"Decoded image data, size: {len(image)} bytes")

        # Instantiate a Predictor
        predictor = sagemaker.predictor.Predictor(ENDPOINT)

        # For this model the IdentitySerializer needs to be "image/png"
        predictor.serializer = IdentitySerializer("image/png")
        
        # Make a prediction:
        print("Making prediction...")
        inferences = predictor.predict(image)
        print(f"Prediction result: {inferences}")
        print(f"Prediction result type: {type(inferences)}")
        
        # Handle different inference result types
        if hasattr(inferences, 'decode'):
            inference_data = inferences.decode('utf-8')
        else:
            inference_data = str(inferences)
        
        # We return the data back to the Step Function    
        body["inferences"] = inference_data
        
        return {
            'statusCode': 200,
            'body': body  # Return body directly, not as JSON string
        }
        
    except Exception as e:
        print(f"Error in image classification: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'error': str(e),
            'body': {
                "error": f"Failed to classify image: {str(e)}"
            }
        }
