import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables from .env file
load_dotenv()

# Get the service resources
dynamodb = boto3.client("dynamodb")
s3 = boto3.client("s3")
lambda_client = boto3.client("lambda")
apigateway = boto3.client("apigateway")

# Constants
DYNAMODB_TABLE_NAME = "Movies"
S3_BUCKET_NAME = "movies-theme-song-bucket"
LAMBDA_FUNCTION_NAME = "MovieThemeFinderAPI"
API_NAME = "MovieThemeFinderAPI"

# Create DynamoDB table
def create_table():
    try:
        response = dynamodb.create_table(
            TableName=DYNAMODB_TABLE_NAME,
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        print(f"DynamoDB table {DYNAMODB_TABLE_NAME} was created successfully")
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"DynamoDB Table {DYNAMODB_TABLE_NAME} already exists!")

# Create S3 bucket
def create_bucket():
    try:
        response = s3.create_bucket(
            Bucket=S3_BUCKET_NAME,
            # Not needed for US East-1
            # CreateBucketConfiguration={"LocationConstraint": boto3.session.Session().region_name},
        )
        print(f"S3 bucket {S3_BUCKET_NAME} created successfully")
        return response
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyOwnedByYou':
            print(f"S3 bucket {S3_BUCKET_NAME} already exists!")
        elif error_code == 'BucketAlreadyExists':
            print(f"S3 bucket name {S3_BUCKET_NAME} is already taken by another user!")
        else: print(f"Error creating S3 bucket: {str(e)}")

# Create Lambda function
def deploy_lambda():
    with open("lambda_function.zip", "rb") as f:
        zip_data = f.read()
    try:
        response = lambda_client.create_function(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Runtime="python3.13",
            Role=os.getenv("AWS_LAMBDA_ROLE_ARN"),
            Handler="main.handler",
            Code={"ZipFile": zip_data},
            Environment={
                "Variables": {
                    "MOVIE_TABLE": DYNAMODB_TABLE_NAME,
                    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                }
            },
        )
        print(f"Lambda function {LAMBDA_FUNCTION_NAME} deployed successfully")
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceConflictException':
            print(f"Lambda function {LAMBDA_FUNCTION_NAME} already exists!")

# Create API Gateway
def create_api_gateway():
    try:
        response = apigateway.create_rest_api(
            name=API_NAME,
            description="API for Movie Theme Song Finder",
        )
        api_id = response["id"]
        print(f"API Gateway {API_NAME} created with ID: {api_id}")
        return api_id
    except Exception as e:
        print(f"Error creating API Gateway: {str(e)}")

if __name__ == "__main__":
    print("Setting up infrastructure...")
    create_table() 
    create_bucket()
    deploy_lambda()
    api_id = create_api_gateway()
    print("Infrastructure setup completed.")
