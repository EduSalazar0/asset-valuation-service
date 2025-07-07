import json
import logging
from kafka import KafkaProducer, errors

from core.config import settings
from domain.entities.asset import Asset
from domain.repositories.messaging_producer import IMessagingProducer

logger = logging.getLogger(__name__)

class KafkaMessagingProducer(IMessagingProducer):
    def __init__(self):
        # Es crucial inicializar el atributo ANTES del try/except.
        self.producer = None
        try:
            # Intentamos crear la instancia del productor.
            self.producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                # Aumentamos el tiempo de espera para la conexión inicial.
                api_version_auto_timeout_ms=5000 
            )
            logger.info("Kafka producer conectado exitosamente.")
        # Capturamos el error específico si no se puede conectar.
        except errors.NoBrokersAvailable as e:
            logger.error(f"Error Crítico: No se pudo conectar al broker de Kafka. El productor no estará disponible. Error: {e}")
        except Exception as e:
            logger.error(f"Error inesperado al inicializar el productor de Kafka: {e}")

    def publish_asset_valuated(self, asset: Asset) -> None:
        # Ahora esta comprobación siempre funcionará, incluso si la conexión falló.
        if not self.producer:
            logger.error("No se puede publicar el mensaje porque el productor de Kafka no está disponible.")
            return

        message = {
            "asset_id": str(asset.id),
            "scan_id": str(asset.scan_id),
            "asset_type": asset.asset_type.value, # Asegúrate de enviar el valor del enum
            "value": asset.value,
            "sca_score": asset.sca
        }
        
        try:
            self.producer.send(settings.KAFKA_DESTINATION_TOPIC, value=message)
            self.producer.flush()
            logger.info(f"Published 'asset.valuated' event for asset_id: {asset.id}")
        except Exception as e:
            logger.error(f"Fallo al publicar mensaje para asset_id {asset.id}: {e}")