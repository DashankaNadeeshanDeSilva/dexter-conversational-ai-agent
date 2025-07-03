"""Main application entry point."""

import uvicorn
from app.config import settings
from app.utils.logging_utils import setup_logging

def main():
    """Run the application."""
    # Set up logging
    logger = setup_logging(
        app_name="ai_agent",
        log_level="DEBUG" if settings.DEBUG else "INFO"
    )
    
    logger.info("Starting AI Agent with Memory")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Metrics enabled: {settings.ENABLE_METRICS}")
    
    # Run the uvicorn server
    uvicorn.run(
        "app.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )

if __name__ == "__main__":
    main()
