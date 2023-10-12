import json
import os
import boto3
from datetime import datetime, timedelta
import uuid
import random

sqs = boto3.client("sqs")

MAX_RETRY_ATTEMPTS = 5
FINAL_DLQ_URL = os.environ["FINAL_DLQ_URL"]
TARGET_QUEUE_URL = os.environ["TARGET_QUEUE_URL"]


class MaxRetryAttemptsExceededException(Exception):
    """Max retry attempts exceeded exception"""


def _increment_retry_attempt(event):
    if "retry_attempt" in event["metadata"]:
        event["metadata"]["retry_attempt"] += 1
    else:
        event["metadata"]["retry_attempt"] = 1

    return event


def _check_if_max_retry_attempts_exceed(message):
    if message["metadata"]["retry_attempt"] > MAX_RETRY_ATTEMPTS:
        raise MaxRetryAttemptsExceededException(
            f"Max retry attempts {MAX_RETRY_ATTEMPTS} exceeded"
        )


def _send_to_final_dlq(original_message, error_type: str, exception: Exception):
    sqs.send_message(
        QueueUrl=FINAL_DLQ_URL,
        MessageBody=json.dumps(original_message),
        MessageAttributes={
            "ErrorType": {
                "DataType": "String",
                "StringValue": error_type,
            },
            "ErrorDetails": {
                "DataType": "String",
                "StringValue": str(exception),
            },
        },
    )
    print("Message was sent to final DLQ")


def _calculate_next_retry_time(message):
    """Calculate next retry time based on random value"""
    random_seconds = random.randint(0, 900)
    new_datetime = datetime.now() + timedelta(seconds=random_seconds)
    message["metadata"]["next_retry_time"] = new_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

    return random_seconds, message


def _resend_message(message, random_seconds):
    sqs.send_message(
        QueueUrl=TARGET_QUEUE_URL,
        MessageBody=json.dumps(message),
        DelaySeconds=random_seconds,
    )
    print("Message was sent to source queue")


def event_handler(event, context):
    event = event["Records"][0]
    message = json.loads(event["body"])

    # increment or add retry attempt
    _increment_retry_attempt(message)

    try:
        # Check no of retries exceed
        _check_if_max_retry_attempts_exceed(message)
    except MaxRetryAttemptsExceededException as e:
        print("Max retry attempts exceeded")
        _send_to_final_dlq(message, "RETRY_ATTEMPT_EXCEEDED", e)
        return

    # Calculate next retry time
    random_seconds, message = _calculate_next_retry_time(message)

    # Resend message to source queue with delay
    _resend_message(message, random_seconds)

    print(
        {
            "message_id": message["metadata"]["message_id"],
            "retry_attempt": message["metadata"]["retry_attempt"],
            "next_retry_time": message["metadata"]["next_retry_time"],
        }
    )
