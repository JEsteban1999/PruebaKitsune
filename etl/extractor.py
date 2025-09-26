import requests
import pandas as pd
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class CannabisDataExtractor:
    def __init__(self, base_url: str = "https://www.datos.gov.co/resource/f9u4-kiwb.json"):
        self.base_url = base_url
    
    def extract_data(self) -> List[Dict[str, Any]]:
        """
        Extrae los datos de la API de datos.gov.co
        Returns: List[Dict]: Lista de registros en formato JSON
        """
        try:
            logger.info(f"Iniciando extracción de datos...")
            response = requests.get(self.base_url)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Extraidos {len(data)} registros exitosamente")
            return data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la extracción: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            raise

# Función de prueba para verificar la extracción
def test_extraction():
    extractor = CannabisDataExtractor()
    data = extractor.extract_data()
    print(f"Primer registro: {data[0]}")
    return data

if __name__ == "__main__":
    test_extraction()