import boto3

# Create an S3 client using the default profile
s3 = boto3.client('s3')  # No explicit credentials or profile name

bucket_name = 'sandeep-patharkar-gen-ai-bckt'  # Replace with your bucket name

try:
    # List the objects in the bucket
    response = s3.list_objects_v2(Bucket=bucket_name)

    # Print the object names
    if 'Contents' in response:
        print("Files in S3 bucket:")
        for obj in response['Contents']:
            print(f"  - {obj['Key']}")
    else:
        print("The bucket is empty.")

except Exception as e:
    print(f"Error: {e}")