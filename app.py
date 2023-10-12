#!/usr/bin/env python3
import os

import aws_cdk as cdk

from retry_with_sqs_delay_messages.retry_with_sqs_delay_messages_stack import (
    RetryWithSqsDelayMessagesStack,
)


app = cdk.App()
RetryWithSqsDelayMessagesStack(app, "RetryWithSqsDelayMessagesStack")

app.synth()
