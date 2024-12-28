import logging
from celery import shared_task
from .models import OneCConnection

logger = logging.getLogger(__name__)

@shared_task
def check_connections():
    connections = OneCConnection.objects.all()  # Fetch all connections

    for connection in connections:
        logger.info(f"Checking connection: {connection.url}/{connection.database}")

        # Try connecting
        try:
            client = create_client(
                url=connection.url,
                database=connection.database,
                username=connection.username,
                password=connection.password,
            )
            logger.info(f"Successfully connected to {connection.url}/{connection.database}")
        except Exception as e:
            logger.error(f"Connection error for {connection.url}: {e}")