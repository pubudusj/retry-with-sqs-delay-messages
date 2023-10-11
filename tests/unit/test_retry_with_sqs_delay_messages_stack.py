import aws_cdk as core
import aws_cdk.assertions as assertions

from retry_with_sqs_delay_messages.retry_with_sqs_delay_messages_stack import RetryWithSqsDelayMessagesStack

# example tests. To run these tests, uncomment this file along with the example
# resource in retry_with_sqs_delay_messages/retry_with_sqs_delay_messages_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = RetryWithSqsDelayMessagesStack(app, "retry-with-sqs-delay-messages")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
