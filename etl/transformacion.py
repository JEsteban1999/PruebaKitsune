import pandas as pd
import logging
from typing import List, Dict, Any

from extractor import CannabisDataExtractor

logger = logging.getLogger(__name__)

class CannabisDataTransformer:
    def __init__(self):
        self.required_columns = [
            'departamento', 'municipio', 'no_psico', 'psico', 
            'semillas', 'total'
        ]
    
    def transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transforma y normaliza los datos crudos
        """
        try:
            logger.info("Iniciando transformación de datos...")
            
            # Convertir a DataFrame para facilitar la transformación
            df = pd.DataFrame(raw_data)
            
            # Verificar columnas requeridas
            self._validate_columns(df)
            
            # Limpiar y normalizar datos
            df_clean = self._clean_data(df)
            
            # Crear campos adicionales
            df_enhanced = self._enhance_data(df_clean)
            
            # Convertir de vuelta a lista de diccionarios
            transformed_data = df_enhanced.to_dict('records')
            
            logger.info("Transformación completada exitosamente")
            return transformed_data
            
        except Exception as e:
            logger.error(f"Error en la transformación: {e}")
            raise
    
    def _validate_columns(self, df: pd.DataFrame):
        """Valida que estén presentes las columnas requeridas"""
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            # Mostrar las columnas que sí están disponibles
            available_columns = list(df.columns)
            print(f"Columnas disponibles: {available_columns}")
            raise ValueError(f"Columnas faltantes: {missing_columns}")
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y normaliza los datos"""
        df_clean = df.copy()
        
        # Convertir tipos de datos numéricos
        numeric_columns = ['no_psico', 'psico', 'semillas', 'total']
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0).astype(int)
        
        # Limpiar textos (eliminar espacios extras, etc.)
        text_columns = ['departamento', 'municipio']
        for col in text_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip().str.title()
        
        # Eliminar duplicados basados en municipio
        if 'municipio' in df_clean.columns and 'departamento' in df_clean.columns:
            numeric_cols = ['no_psico', 'psico', 'semillas', 'total']
            df_clean = df_clean.groupby(['departamento', 'municipio'])[numeric_cols].sum().reset_index()
            
        df_clean = df_clean.drop_duplicates(subset=['municipio', 'departamento'])
        return df_clean
    
    def _enhance_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Añade campos adicionales para mejorar la búsqueda y análisis"""
        df_enhanced = df.copy()
        
        # Crear ID único
        df_enhanced['id'] = range(1, len(df_enhanced) + 1)
        
        # Reordenar columnas
        base_columns = ['id', 'departamento', 'municipio', 'no_psico', 
                       'psico', 'semillas', 'total']
        
        # Solo incluir columnas que existan
        final_columns = [col for col in base_columns if col in df_enhanced.columns]
        
        return df_enhanced[final_columns]

def test_transformation():
    
    extractor = CannabisDataExtractor()
    raw_data = extractor.extract_data()
    
    print(f"Columnas en raw_data: {list(raw_data[0].keys()) if raw_data else 'No data'}")
    
    transformer = CannabisDataTransformer()
    transformed_data = transformer.transform_data(raw_data)
    
    print(f"Datos transformados: {len(transformed_data)} registros")
    if transformed_data:
        print(f"Primer registro transformado: {transformed_data[0]}")
    return transformed_data

if __name__ == "__main__":
    test_transformation()