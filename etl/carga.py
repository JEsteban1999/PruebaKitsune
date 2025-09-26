# etl/loader.py
import sqlite3
import logging
from typing import List, Dict, Any
import os

from extractor import CannabisDataExtractor
from transformacion import CannabisDataTransformer

logger = logging.getLogger(__name__)

class CannabisDataLoader:
    def __init__(self, db_path: str = "cannabis_licencias.db"):
        # Usar ruta absoluta para evitar problemas de directorio
        self.db_path = os.path.abspath(db_path)
        self._ensure_database_dir()
    
    def _ensure_database_dir(self):
        """Asegura que el directorio de la base de datos exista"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:  # Solo crear directorio si la ruta incluye uno
            os.makedirs(db_dir, exist_ok=True)
    
    def create_database(self):
        """Crea la base de datos y las tablas necesarias"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS licencias (
                        id INTEGER PRIMARY KEY,
                        departamento TEXT NOT NULL,
                        municipio TEXT NOT NULL,
                        no_psico INTEGER DEFAULT 0,
                        psico INTEGER DEFAULT 0,
                        semillas INTEGER DEFAULT 0,
                        total INTEGER DEFAULT 0,
                        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(departamento, municipio)
                    )
                ''')
                
                # Crear índices para mejorar performance de búsquedas
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_departamento 
                    ON licencias(departamento)
                ''')
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_total 
                    ON licencias(total DESC)
                ''')
                
                logger.info(f"Base de datos creada en: {self.db_path}")
                
        except sqlite3.Error as e:
            logger.error(f"Error creando la base de datos: {e}")
            raise
    
    def load_data(self, data: List[Dict[str, Any]]):
        """Carga los datos transformados a la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Limpiar tabla existente antes de cargar nuevos datos
                conn.execute("DELETE FROM licencias")
                
                # Insertar nuevos datos
                for record in data:
                    conn.execute('''
                        INSERT INTO licencias 
                        (id, departamento, municipio, no_psico, psico, 
                         semillas, total)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        record['id'],
                        record['departamento'],
                        record['municipio'],
                        record['no_psico'],
                        record['psico'],
                        record['semillas'],
                        record['total']
                    ))
                
                conn.commit()
                logger.info(f"Datos cargados exitosamente: {len(data)} registros")
                
        except sqlite3.Error as e:
            logger.error(f"Error cargando datos: {e}")
            raise
    
    def verify_data(self) -> bool:
        """Verifica que los datos se hayan cargado correctamente"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM licencias")
                count = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT * FROM licencias LIMIT 1")
                sample = cursor.fetchone()
                
                logger.info(f"Verificación: {count} registros en la base de datos")
                if sample:
                    logger.info(f"Registro de muestra: {sample}")
                
                return count > 0
                
        except sqlite3.Error as e:
            logger.error(f"Error verificando datos: {e}")
            return False

    def show_sample_data(self, limit: int = 5):
        """Muestra una muestra de los datos cargados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, departamento, municipio, no_psico, psico, semillas, total 
                    FROM licencias 
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                print(f"\n--- Muestra de datos ({len(rows)} registros) ---")
                for row in rows:
                    print(f"ID: {row[0]}, {row[1]} - {row[2]}: "
                          f"NoPsico: {row[3]}, Psico: {row[4]}, Semillas: {row[5]}, Total: {row[6]}")
                return rows
                
        except sqlite3.Error as e:
            logger.error(f"Error mostrando datos: {e}")
            return []

def test_loading():
    
    try:
        # Extraer y transformar datos
        print("Extrayendo datos...")
        extractor = CannabisDataExtractor()
        raw_data = extractor.extract_data()
        print(f"Extraídos {len(raw_data)} registros")
        
        print("Transformando datos...")
        transformer = CannabisDataTransformer()
        transformed_data = transformer.transform_data(raw_data)
        print(f"Transformados {len(transformed_data)} registros")
        
        # Cargar datos
        print("Cargando datos...")
        loader = CannabisDataLoader()
        loader.create_database()
        loader.load_data(transformed_data)
        
        # Verificar
        success = loader.verify_data()
        print(f"Carga de datos: {'Éxito' if success else 'Fallo'}")
        
        if success:
            loader.show_sample_data(5)
        
        return success
        
    except Exception as e:
        print(f"Error en test_loading: {e}")
        return False

if __name__ == "__main__":
    test_loading()