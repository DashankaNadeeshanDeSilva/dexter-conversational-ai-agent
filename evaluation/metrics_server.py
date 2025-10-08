"""Standalone metrics server for Prometheus scraping."""

import logging
import time
from prometheus_client import start_http_server
from evaluation.config import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def start_metrics_server(port: int = None, host: str = None):
    """
    Start the Prometheus metrics HTTP server.
    
    Args:
        port: Port to listen on (default from config)
        host: Host to bind to (default from config)
    """
    port = port or config.METRICS_PORT
    host = host or config.METRICS_HOST
    
    try:
        start_http_server(port, addr=host)
        logger.info(f"Metrics server started on {host}:{port}")
        logger.info(f"Prometheus endpoint: http://{host}:{port}/metrics")
        
        # Keep the server running
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Metrics server stopped by user")
    except Exception as e:
        logger.error(f"Error starting metrics server: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start Prometheus metrics server")
    parser.add_argument(
        "--port",
        type=int,
        default=config.METRICS_PORT,
        help=f"Port to listen on (default: {config.METRICS_PORT})"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=config.METRICS_HOST,
        help=f"Host to bind to (default: {config.METRICS_HOST})"
    )
    
    args = parser.parse_args()
    
    start_metrics_server(port=args.port, host=args.host)

