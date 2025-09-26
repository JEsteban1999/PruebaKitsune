from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

import sqlite3
import os
import sys
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from etl.main import run_etl_pipeline

# Configurar logging
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Licencias de Cannabis",
    description="API REST para consultar licencias de cannabis en Colombia",
    version="1.0.0"
)

# Configuración
DATABASE_URL = os.getenv("DATABASE_URL", "cannabis_licencias.db")
API_KEY = os.getenv("API_KEY", "cannabis-key-2025")
api_key_header = APIKeyHeader(name="X-API-Key")

# Dependencia para verificar API Key
def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="API key inválida"
        )
    return api_key

# Conexion a la base de datos
def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

# Modelos de datos
class LicenciaBase(BaseModel):
    id: int
    departamento: str
    municipio: str
    no_psico: int
    psico: int
    semillas: int
    total: int

class LicenciaResponse(LicenciaBase):
    class Config:
        from_attributes = True

class BusquedaResponse(BaseModel):
    resultados: List[LicenciaResponse]
    total: int
    pagina: int
    por_pagina: int

# Endpoints principales
@app.get("/")
async def root():
    return {
        "message": "API de Licencias de Cannabis",
        "version": "1.0.0",
        "endpoints": {
            "licencias": "/licencias",
            "licencia_por_id": "/licencias/{id}",
            "buscar": "/licencias/buscar/",
            "estadisticas": "/estadisticas",
            "actualizar-datos": "/actualizar-datos"
        }
    }

@app.get("/licencias", response_model=BusquedaResponse)
async def listar_licencias(
    skip: int = Query(0, ge=0, description="Numero de registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Numero de registros a retornar")
):
    """Lista todas las licencias con paginación"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obtener total de registros
        cursor.execute("SELECT COUNT(*) FROM licencias")
        total = cursor.fetchone()[0]

        # Obtener registros paginados
        cursor.execute("SELECT * FROM licencias ORDER BY total DESC LIMIT ? OFFSET ?", (limit, skip))

        resultados = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return BusquedaResponse(
            resultados=resultados,
            total=total,
            pagina=skip // limit + 1,
            por_pagina=limit
        )
    
    except Exception as e:
        logger.error(f"Error listando licencias: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/licencias/{licencia_id}", response_model=LicenciaResponse)
async def obtener_licencia(licencia_id: int):
    """Obtiene una licencia especifica por ID"""
    try:
        conn= get_db_connection()
        cursor=conn.cursor()

        cursor.execute("SELECT * FROM licencias WHERE id = ?", (licencia_id,))

        licencia = cursor.fetchone()
        conn.close()
    
        if not licencia:
            raise HTTPException(status_code=404, detail=f"Licencia con ID {licencia_id} no encontrada")
        
        return dict(licencia)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo licencia {licencia_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/licencias/buscar/", response_model=BusquedaResponse)
async def buscar_licencias(
    q: str = Query(..., description="Término de búsqueda"),
    departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    tipo: Optional[str] = Query(None, description="Tipo de licencia: no psico, psico, semillas, total"),
    min_total: Optional[int] = Query(None, ge=0, description="Minimo total de licencias"),
    max_total: Optional[int] = Query(None, ge=0, description="Máximo total de licencias"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """Busca licencias por termino y aplica filtros"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Construir query dinamica
        query = "SELECT * FROM licencias WHERE 1=1"
        params = []

        # Busqueda por término
        if q:
            query += " AND (departamento LIKE ? OR municipio LIKE ?)"
            params.extend([f"%{q}%", f"%{q}%"])
        
        # Filtros adicionales
        if departamento:
            query += " AND departamento = ?"
            params.append(departamento)
        
        if min_total is not None:
            query += " AND total >= ?"
            params.append(min_total)
        
        if max_total is not None:
            query += " AND total <= ?"
            params.append(max_total)
        
        # Ordernar por el tipo especificado o por total por defecto
        if tipo and tipo in ['no_psico', 'psico', 'semillas', 'total']:
            query += f" ORDER BY {tipo} DESC"
        else:
            query += f" ORDER BY total DESC"
        
        # Contar total de resultados
        count_query = f"SELECT COUNT(*) FROM ({query})"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

        # Aplicar paginacion
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        cursor.execute(query, params)
        resultados = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return BusquedaResponse(
            resultados=resultados,
            total=total,
            pagina=skip // limit + 1,
            por_pagina = limit
        )
    
    except Exception as e:
        logger.error(f"Error buscando licencias: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    
@app.get("/estadisticas")
async def obtener_estadisticas():
    """Obtiene estadisticas generales de las licencias"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        estadisticas = {}

        # Totales generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_municipios,
                SUM(total) as total_licencias,
                SUM(no_psico) as total_no_psico,
                SUM(psico) as total_psico,
                SUM(semillas) as total_semillas,
                AVG(total) as promedio_por_municipio
            FROM licencias
        """)
        
        stats = cursor.fetchone()
        estadisticas["totales"] = dict(stats)
        
        # Top 5 departamentos con más licencias
        cursor.execute("""
            SELECT departamento, SUM(total) as total_licencias
            FROM licencias 
            GROUP BY departamento 
            ORDER BY total_licencias DESC 
            LIMIT 5
        """)
        estadisticas["top_departamentos"] = [dict(row) for row in cursor.fetchall()]
        
        # Distribución por rangos
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN total = 0 THEN 'Sin licencias'
                    WHEN total BETWEEN 1 AND 5 THEN '1-5'
                    WHEN total BETWEEN 6 AND 20 THEN '6-20'
                    WHEN total > 20 THEN 'Más de 20'
                END as rango,
                COUNT(*) as cantidad_municipios
            FROM licencias
            GROUP BY rango
            ORDER BY cantidad_municipios DESC
        """)
        estadisticas["distribucion_rangos"] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return estadisticas
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/actualizar-datos")
async def actualizar_datos(api_key: str = Depends(get_api_key)):
    """Endpoint protegido para actualizar los datos desde el ETL"""
    try:
        # Importar y ejecutar el ETL
        logger.info("Solicitada actualización de datos via API")
        success = run_etl_pipeline()

        if success:
            return {
                "message": "Datos actualizados exitosamente", 
                "status": "success"
            }
        else:
            raise HTTPException(status_code=500, detail="Error al actualizar los datos")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando datos: {e}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar datos")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


