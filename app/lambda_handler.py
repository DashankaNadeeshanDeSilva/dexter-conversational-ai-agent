"""
AWS Lambda handler for Dexter AI Agent.
This file bridges API Gateway events to FastAPI using Mangum.
"""

from mangum import Mangum
from app.api.main import app

# Create the Lambda handler
# This translates API Gateway events into ASGI calls
handler = Mangum(app, lifespan="off")

# Optional: Add logging for debugging
import logging
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """
    AWS Lambda entry point.
    
    Args:
        event: API Gateway event (HTTP request data)
        context: Lambda context (runtime info)
    
    Returns:
        API Gateway response format
    """
    try:
        method = event.get('requestContext', {}).get('http', {}).get('method') or event.get('httpMethod')
        path = event.get('requestContext', {}).get('http', {}).get('path') or event.get('path')
        logger.info(f"Lambda invoked with event: {method} {path}")
    except Exception:
        logger.info("Lambda invoked")
    
    # Let Mangum handle the conversion
    return handler(event, context)


