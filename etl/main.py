import logging
import os
import sys

# Añadir el directorio actual al path para imports
sys.path.append(os.path.dirname(__file__))

from extractor import CannabisDataExtractor
from transformacion import CannabisDataTransformer
from carga import CannabisDataLoader

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def run_etl_pipeline():
    """
    Ejecuta el pipeline completo ETL
    """
    try:
        logger.info("Iniciando pipeline ETL...")
        
        # Extracción
        extractor = CannabisDataExtractor()
        raw_data = extractor.extract_data()
        
        # Transformación
        transformer = CannabisDataTransformer()
        transformed_data = transformer.transform_data(raw_data)
        
        # Carga
        loader = CannabisDataLoader()
        loader.create_database()
        loader.load_data(transformed_data)
        
        # Verificación
        success = loader.verify_data()
        
        if success:
            logger.info("Pipeline ETL completado exitosamente!")
            return True
        else:
            logger.error("Pipeline ETL completado con errores")
            return False
            
    except Exception as e:
        logger.error(f"Error en el pipeline ETL: {e}")
        return False

if __name__ == "__main__":
    run_etl_pipeline()