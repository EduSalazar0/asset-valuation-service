import json
import logging
import time # <-- Importado
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable # <-- Importado
from sqlalchemy.orm import Session
from pydantic import ValidationError

from core.config import settings
from domain.entities.asset_event import AssetDiscoveredEvent
from application.use_cases.value_asset import ValueAssetUseCase
from application.services.cia_calculator import CIACalculatorService
from infrastructure.database.connection import SessionLocal
from infrastructure.repositories.postgres_asset_repository import PostgresAssetRepository
from infrastructure.messaging.kafka_producer import KafkaMessagingProducer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AssetValuationConsumer:
    def __init__(self):
        """
        Inicializa el consumidor de Kafka con una lógica de reintentos
        para ser más resiliente en un entorno de Kubernetes.
        """
        max_retries = 10
        retry_delay = 5  # segundos

        for attempt in range(max_retries):
            try:
                logger.info(f"Intentando conectar a Kafka (Intento {attempt + 1}/{max_retries})...")
                self.consumer = KafkaConsumer(
                    settings.KAFKA_SOURCE_TOPIC,
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    group_id=settings.KAFKA_CONSUMER_GROUP,
                    auto_offset_reset='earliest',
                    session_timeout_ms=10000,
                    request_timeout_ms=30000,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
                )
                logger.info("¡Conexión a Kafka exitosa!")
                return
            except NoBrokersAvailable:
                logger.warning(f"No se pudo conectar a Kafka. Reintentando en {retry_delay} segundos...")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.critical("No se pudo conectar a Kafka después de varios intentos. Rindiéndose.")
                    raise

    def run(self):
        """
        Ejecuta el bucle del consumidor, escuchando y procesando mensajes.
        """
        logger.info(f"Worker started. Listening for messages on topic '{settings.KAFKA_SOURCE_TOPIC}'...")
        
        for message in self.consumer:
            logger.info(f"Received message: {message.value}")
            
            try:
                # El evento esperado aquí es un 'AssetDiscoveredEvent'
                asset_event = AssetDiscoveredEvent(**message.value)
            except ValidationError as e:
                logger.error(f"Invalid message format: {e}. Skipping message.")
                continue

            # Crear una sesión de BD por cada mensaje para asegurar que sea atómico
            db_session: Session = SessionLocal()
            try:
                # Inyección de Dependencias para el caso de uso de valoración
                asset_repo = PostgresAssetRepository(db_session)
                producer = KafkaMessagingProducer()
                calculator = CIACalculatorService()
                use_case = ValueAssetUseCase(asset_repo, producer, calculator)
                
                # Ejecutar la lógica de negocio
                use_case.execute(asset_event)
                
                logger.info(f"Successfully processed message for asset_id: {asset_event.asset_id}")
            except Exception as e:
                logger.error(f"An error occurred while processing asset_id {asset_event.asset_id}: {e}", exc_info=True)
            finally:
                db_session.close()

def start_worker():
    """
    Función de entrada para iniciar el worker.
    """
    worker = AssetValuationConsumer()
    worker.run()
