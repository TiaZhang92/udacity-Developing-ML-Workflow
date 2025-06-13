# Lambda Function 1: serializeImageData (Improved with error handling)
import json
import boto3
import base64
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    try:
        # Get the s3 address from the Step Function event input
        key = event['s3_key']
        bucket = event['s3_bucket']
        
        print(f"Attempting to download: s3://{bucket}/{key}")
        
        # Check if the object exists first
        try:
            s3.head_object(Bucket=bucket, Key=key)
            print("Object exists, proceeding with download")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '403':
                raise Exception(f"Access denied to s3://{bucket}/{key}. Check IAM permissions.")
            elif error_code == '404':
                raise Exception(f"Object not found: s3://{bucket}/{key}")
            else:
                raise Exception(f"Error accessing object: {str(e)}")
        
        # Download the data from s3 to /tmp/image.png
        s3.download_file(bucket, key, '/tmp/image.png')
        print("File downloaded successfully")
        
        # We read the data from a file
        with open("/tmp/image.png", "rb") as f:
            image_data = base64.b64encode(f.read())

        # Pass the data back to the Step Function
        print("Event:", event.keys())
        return {
            'statusCode': 200,
            'body': {
                "image_data": image_data.decode('utf-8'),
                "s3_bucket": bucket,
                "s3_key": key,
                "inferences": []
            }
        }
        
    except Exception as e:
        print(f"Error in serializeImageData: {str(e)}")
        return {
            'statusCode': 500,
            'error': str(e),
            'body': {
                "error": f"Failed to process image: {str(e)}"
            }
        }
