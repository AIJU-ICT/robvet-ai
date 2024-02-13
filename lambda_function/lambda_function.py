# ----------------------------------------------------------------------------------
# Lambda Function
# ----------------------------------------------------------------------------------
#
# Description :
# This lambda function contains several functions
# with the final purpose of detecting items of image.
#
# The main function is lambda_handler() which is at the end of the file
# the others are auxiliar functions to help us work
#
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------------
import boto3
import json
import logging
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# SET UP
# ----------------------------------------------------------------------------------
# Set up logging.
logger = logging.getLogger(__name__)

# AWS Services
s3 = boto3.client("s3")
reko = boto3.client("rekognition", "{region_id}")
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# Vars
# ----------------------------------------------------------------------------------
Bucket_Name = "{bucket_name}"  # Bucket reference,
Image_S3_Path = "capture/photo.jpg"  # Target image reference
Model_ARN = "{model_arn}"  # Model reference
Prediction_Path = "prediction/prediction.json"  # Prefiction JSOSN reference
# ----------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------
# LOGIC
# ----------------------------------------------------------------------------------
def get_s3_image(bucket_name, image_path):
    """
    This function obtains the reference of an image stored in an S3 bucket.

    Parameters:
    bucket_name (str): The name of the S3 bucket where the image is stored.
    image_path (str): The path of the image within the S3 bucket.

    Returns:
    dict: A dictionary containing the S3 bucket name and the image path, which can be used to reference the image in S3.
    """
    return {"S3Object": {"Bucket": bucket_name, "Name": image_path}}


def safe_predictions(predictions, bucket, key):
    """
    This function takes the generated predictions, converts them into a JSON file, and then uploads them to an S3 bucket.

    Parameters:
    predictions (dict): A dictionary containing the predictions to be saved.
    bucket (str): The name of the S3 bucket where the predictions should be saved.
    key (str): The key under which the predictions should be saved in the S3 bucket.

    Returns:
    None. The function directly uploads the predictions to the S3 bucket.
    """
    # Convert the predictions to a JSON file
    file = bytes(json.dumps(predictions).encode("UTF-8"))
    # Upload the JSON file to the S3 bucket
    s3.put_object(Body=file, Bucket=bucket, Key=key)


def analize_image(image, model, min_confidence=90):
    """
    This function uses Amazon Rekognition to analyze an image based on a custom model.

    Parameters:
    image (dict): A dictionary containing the S3 bucket name and the image path, which can be used to reference the image in S3.
    model (str): The ARN of the custom model to use for the analysis.
    min_confidence (int, optional): The minimum confidence level for the returned predictions. Defaults to 90.

    Returns:
    list: A list of dictionaries, each containing a detected label and its confidence level.
    """
    # Call Rekognition
    response = reko.detect_custom_labels(
        Image=image,
        MinConfidence=min_confidence,
        ProjectVersionArn=model,
    )

    # Create prediction
    prediction = response["CustomLabels"]

    return prediction


# ----------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------
# Main - lambda_handler()
# ----------------------------------------------------------------------------------
def lambda_handler(event, context):
    """
    This is the handler function for AWS Lambda.

    Parameters:
    event (dict): The event object for the Lambda function. This contains information about the triggering event.
    context (obj): The context object for the Lambda function. This contains information about the runtime the function is executing in.

    Returns:
    None. The function directly uploads the predictions to an S3 bucket.
    """
    # Set the minimum confidence level for the predictions
    min_confidence = 90

    # Get the reference to the image stored in S3
    image = get_s3_image(Bucket_Name, Image_S3_Path)

    # Analyze the image using a custom model
    prediction = analize_image(image, Model_ARN, min_confidence)

    # Upload the predictions to an S3 bucket
    safe_predictions(prediction, Bucket_Name, Prediction_Path)
