# Lambda Function 3: Filter Low Confidence Inferences (Improved with error handling)
import json

THRESHOLD = 0.93

def lambda_handler(event, context):
    
    try:
        print(f"Filter event received: {json.dumps(event, indent=2, default=str)}")
        
        # Parse the event body if it's a string
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        elif 'body' in event:
            body = event['body']
        else:
            body = event
        
        # Grab the inferences from the event
        if 'inferences' not in body:
            raise Exception("No inferences found in event body")
            
        inferences_str = body['inferences']
        print(f"Raw inferences: {inferences_str}")
        
        # Parse inferences JSON
        try:
            inferences = json.loads(inferences_str)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse inferences JSON: {str(e)}")
        
        print(f"Parsed inferences: {inferences}")
        print(f"Inferences type: {type(inferences)}")
        
        # Check if any values in our inferences are above THRESHOLD
        meets_threshold = False
        
        if isinstance(inferences, list):
            # Handle list of confidence scores
            confidence_scores = [float(score) for score in inferences if isinstance(score, (int, float, str))]
            meets_threshold = any(score >= THRESHOLD for score in confidence_scores)
            max_confidence = max(confidence_scores) if confidence_scores else 0
        elif isinstance(inferences, dict):
            # Handle dictionary with confidence values
            confidence_scores = [float(score) for score in inferences.values() if isinstance(score, (int, float, str))]
            meets_threshold = any(score >= THRESHOLD for score in confidence_scores)
            max_confidence = max(confidence_scores) if confidence_scores else 0
        else:
            # Handle single inference value
            max_confidence = float(inferences)
            meets_threshold = max_confidence >= THRESHOLD
        
        print(f"Max confidence: {max_confidence}, Threshold: {THRESHOLD}, Meets threshold: {meets_threshold}")
        
        # If our threshold is met, pass our data back out of the
        # Step Function, else, end the Step Function with an error
        if meets_threshold:
            print("Threshold met, passing data through")
            return {
                'statusCode': 200,
                'body': json.dumps(body)
            }
        else:
            print(f"Threshold not met. Max confidence: {max_confidence} < {THRESHOLD}")
            raise Exception(f"THRESHOLD_CONFIDENCE_NOT_MET: Max confidence {max_confidence} < {THRESHOLD}")
            
    except Exception as e:
        print(f"Error in confidence filter: {str(e)}")
        return {
            'statusCode': 500,
            'error': str(e),
            'body': json.dumps({
                "error": f"Failed to filter inferences: {str(e)}"
            })
        }

