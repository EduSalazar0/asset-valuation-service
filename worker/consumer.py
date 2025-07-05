import json
import logging
import sys
from kafka import KafkaConsumer
from sqlalchemy.orm import Session
from pydantic import ValidationError

from core.config import settings
from domain.entities.asset_event import AssetDiscoveredEvent
from application.use_cases.value_asset import ValueAssetUseCase
from application.services.cia_calculator import CIACalculatorService
from infrastructure.database.connection import SessionLocal
from infrastructure.repositories.postgres_asset_repository import PostgresAssetRepository
from infrastructure.messaging.kafka_producer import KafkaMessagingProducer

# ... (logging setup is identical to previous worker) ...

class AssetValuationConsumer:
    # ... (constructor is identical to previous worker, just listens to a different topic) ...

    def run(self):
        logger.info(f"Worker started. Listening for messages on topic '{settings.KAFKA_SOURCE_TOPIC}'...")
        
        for message in self.consumer:
            logger.info(f"Received message: {message.value}")
            
            try:
                asset_event = AssetDiscoveredEvent(**message.value)
            except ValidationError as e:
                logger.error(f"Invalid message format: {e}. Skipping message.")
                continue

            db_session: Session = SessionLocal()
            try:
                # Dependency Injection
                asset_repo = PostgresAssetRepository(db_session)
                producer = KafkaMessagingProducer()
                calculator = CIACalculatorService()
                use_case = ValueAssetUseCase(asset_repo, producer, calculator)
                
                # Execute
                use_case.execute(asset_event)
                
                logger.info(f"Successfully processed message for asset_id: {asset_event.asset_id}")
            except Exception as e:
                logger.error(f"An error occurred while processing asset_id {asset_event.asset_id}: {e}", exc_info=True)
            finally:
                db_session.close()

def start_worker():
    worker = AssetValuationConsumer()
    worker.run()