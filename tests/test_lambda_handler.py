"""
Test script to verify Lambda handler works locally.
This simulates an API Gateway event.
"""

from app.lambda_handler import lambda_handler

# Simulate an API Gateway event for GET /health
test_event = {
    "version": "2.0",
    "routeKey": "GET /health",
    "rawPath": "/health",
    "rawQueryString": "",
    "headers": {
        "content-type": "application/json",
        "host": "localhost"
    },
    "requestContext": {
        "http": {
            "method": "GET",
            "path": "/health",
            "sourceIp": "127.0.0.1",
            "userAgent": "local-test",
            "protocol": "HTTP/1.1"
        }
    },
    "body": None,
    "isBase64Encoded": False
}


class MockContext:
    def __init__(self):
        self.function_name = "test-function"
        self.function_version = "1"
        self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
        self.memory_limit_in_mb = 128
        self.remaining_time_in_millis = 30000


def test_lambda_health_invoke():
    ctx = MockContext()
    resp = lambda_handler(test_event, ctx)
    assert resp.get("statusCode") == 200


