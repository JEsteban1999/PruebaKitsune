# Análisis de Seguridad - Sistema de Licencias de Cannabis

## Descripción General
Este documento analiza los aspectos de seguridad y protección de datos del sistema de consulta de licencias de cannabis implementado.

## Datos Analizados

### Fuente de Datos
- **Dataset**: Distribución de licencias de cannabis vigentes por municipio
- **Origen**: datos.gov.co (portal oficial del gobierno colombiano)
- **Características**: Datos públicos y abiertos

### Campos del Dataset
- `departamento`: Nombre del departamento
- `municipio`: Nombre del municipio  
- `no_psico`: Número de licencias no psicoactivas
- `psico`: Número de licencias psicoactivas
- `semillas`: Número de licencias de semillas
- `total`: Total de licencias por municipio

## Análisis de Información Personal y Sensible

### ✅ Datos NO Considerados Sensibles
- **Nombres geográficos**: Departamentos y municipios son información pública
- **Estadísticas numéricas**: Cantidades de licencias son datos agregados
- **Información institucional**: Datos de licencias comerciales

### 🔍 Riesgos Identificados

#### 1. Riesgo de Agregación de Datos
**Riesgo**: Aunque los datos son públicos, la agregación podría revelar patrones comerciales sensibles
**Impacto**: Bajo - Información ya disponible públicamente

#### 2. Riesgo de Exposición de API
**Riesgo**: Endpoints públicos podrían ser objetivo de ataques
**Impacto**: Medio - Posible denegación de servicio

#### 3. Riesgo de Manipulación de Datos
**Riesgo**: Endpoint de actualización podría ser vulnerado
**Impacto**: Medio - Integridad de los datos

#### 4. Riesgo de Uso Malicioso del Agente de IA
**Riesgo**: El agente podría ser usado para extraer información de manera automatizada
**Impacto**: Bajo - Datos ya son públicos

## Medidas de Mitigación Implementadas

### 1. Protección de Endpoints
```python
# Endpoint protegido con API Key
@app.post("/actualizar-datos")
async def actualizar_datos(api_key: str = Depends(get_api_key)):
```

### 2. Validación de entradas
- **Paginación**: Límites de consultas (`limit` entre 1 - 100)
- **Validación de tipos**: Usando Pydantic models
- **Sanitización**: Filtrado de parámetros de búsqueda

### 3. Medidas de Seguridad en la API
```python
# Configuraciones de seguridad
API_KEY = os.getenv("API_KEY", "cannabis-key-2025")  # Key por environment
api_key_header = APIKeyHeader(name="X-API-Key")      # Header estándar
```

### 4. Seguridad en el Agente de IA
- **Rate limiting implícito**: Máximo de resultados por consulta
- **Validación de consultas**: Análisis de intención antes de ejecución
- **Logging**: Registro de actividades para auditoría

### 4. Seguridad de Datos
- **Backups automáticos**: De la base de datos SQLite
- **Encriptación**: De datos sensibles si se añaden en el futuro
- **Auditoría regular**: De logs y acceso

## Consideraciones Específicas del Dominio

### Contexto Legal del Cannabis en Colombia

- Los datos de licencias son información pública regulada
- No contienen información personal de titulares
- Cumplen con la ley de transparencia y acceso a la información
  
### Aspectos Éticos

- Los datos apoyan la transparencia en el emergente mercado del cannabis
- El sistema promueve acceso equitativo a información regulatoria
- No facilita usos indebidos de la información

## Plan de Respuesta a Incidentes

### Detección

- Monitoreo de logs de acceso
- Alertas por patrones
- Revisiones periódicas de seguridad

### Contención

- Bloqueo de IPs maliciosas
- Rotación de API keys comprometidas
- Restauración de backups si es necesario

## Conclusiones

### Nivel de Riesgo: BAJO

**Justificación**:

- Datos son inherentemente públicos y no sensibles
- Arquitectura incluye medidas básicas de protección
- No se maneja información personal identificable
