# 🌿 Sistema de consulta de licencias

## 📋 Descripción

Sistema completo de extremo a extremo para consultar licencias de cannabis en Colombia. Incluye ETL, API REST, y un agente de IA que permite consultas en lenguaje natural.

## 🚀 Características Principales

### ✅ ETL (Extract, Transform, Load)

- Extracción automática de datos oficiales
- Transformación y normalización de datos
- Carga en base de datos SQLite

### ✅ API REST

- Endpoints RESTful con FastAPI
- Búsqueda, filtros y paginación
- Documentación automática (Swagger)
- Autenticación por API Key

### ✅ Agente de IA

- Consultas en lenguaje natural
- Interpretación de intenciones del usuario
- Integración con Ollama
- Interfaz web

### ✅ Seguridad

- Análisis de riesgos completo
- Protección de endpoints críticos
- Validación y sanitización de datos

## 📁 Estructura del Proyecto

```text
pruebakitsune/
├── etl/                        # Pipeline de datos
│   ├── extractor.py            # Extracción de datos
│   ├── transformacion.py       # Transformación
│   ├── carga.py                # Carga a BD
│   └── main.py                 # Orquestación
├── api/                        # API REST
│   ├── main.py                 # Servidor FastAPI
│   ├── config.py               # Configuración
│   ├── server.py               # Configuración del servidor
│   └── test_api.py             # Pruebas de API
├── agent/                      # Agente de IA
│   ├── ollama.py               # Agente principal
│   ├── config.py               # Configuración IA
│   └── web_interface.py        # Interfaz web (opcional)
├── docs/                       # Documentación
│   └── security.md             # Análisis de seguridad
├── tests/                      # Tests unitarios
├── requirements.txt            # Dependencias
└── README.md                   # Este archivo
```

## 🛠️ Instalación y Configuración

### Prerrequisitos

- Python 3.8+
- pip (gestor de paquetes de Python)
- Acceso a internet (para descargar datos)

### 1. Clonar o Descargar el Proyecto

```bash
# Si tienes el código en un repositorio
git clone https://github.com/JEsteban1999/PruebaKitsune.git
cd PruebaKitsune

# O si tienes los archivos directamente
cd PruebaKitsune
```

### 2. Instalar las dependencias necesarias

### 3. Configurar Variables de Entorno

En el archivo ``env``:

```text
API_KEY=cannabis-key-2025
DATABASE_URL=sqlite:///cannabis_licencias.db
```

## 🎯 Ejecución Paso a Paso

### Paso 1: Ejecutar el ETL (Extracción de Datos)

```bash
python etl/main.py
```

#### ✅ Esperado:

```text
✅ ETL ejecutado exitosamente!
Base de datos creada con X registros
```

### Paso 2: Iniciar la API REST

```bash
# Terminal 2 - Iniciar el servidor de la API
python api/main.py
```

#### ✅ Esperado:

```text
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Paso 3: Probar la API (Opcional)

```bash
# Terminal 3 - Probar endpoints
python api/test_api.py
```

### Paso 4: Usar el agente de IA (Interfaz Web)

#### Opción A: Interfaz de Linea de Comandos (CLI)

```bash
# Terminal 4 - Interfaz conversacional
python agent/ollama.py
```

#### Opción B: Interfaz web

```bash
# Terminal 4 - Interfaz web
python agent/web_interface.py
# Abrir http://localhost:5000 en el navegador
```

## 🔧 Decisiones Técnicas

### 🗃️ Base de Datos: SQLite

**Decisión**: Usar SQLite en lugar de PostgreSQL

- **Razón**: Simplicidad para prueba técnica, cero configuración
- **Ventajas**:
    - No requiere servidor externo
    - Fácil portabilidad
    - Suficiente para volumen de datos (~100 registros)
- **Producción**: Migrar a PostgreSQL para concurrencia

### 🚀 API Framework: FastAPI

**Decisión**: FastAPI sobre Flask/Django REST

- **Razón**: Performance y experiencia de desarrollo
- **Ventajas**:
    - Tipado estático con Pydantic
    - Documentación automática (OpenAPI)
    - Soporte async nativo
    - Menos código boilerplate

### 🤖 Agente de IA: Gemma3:1b | Llama2

**Decisión**: Gemma3:1b | Llama2 sobre LangChain + OpenAI

- **Razón**: Rendimiento computacional y costos
- **Recomendaciones**: Migrar a LangChain + OpenAI para mejores resultados

### 🔐 Seguridad: API Key Simple

**Decisión**: Autenticación básica por API Key

- **Razón**: Suficiente para datos públicos
- **Producción**: Implementar JWT + OAuth2
- **Validación**: Sanitización de inputs y rate limiting básico

### 📊 Procesamiento de Datos: Pandas

**Decisión**: Pandas para transformación de datos

- **Razón**: Ecosistema robusto para ETL
- **Ventajas**:
    - Operaciones vectorizadas eficientes
    - Manejo fácil de datos faltantes
    - Integración con múltiples formatos

## 🧪 Testing

```bash
# Probar ETL
python -m etl.main

# Probar API
python api/test_api.py

# Probar Agente
python agent/ollama.py
```

## 📈 Monitoreo y Debug

### Logs de la API

```bash
# Los logs aparecen en la terminal donde ejecutas la API
INFO:     Started server process [1234]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## 🔄 Mantenimiento

### Actualizar datos

```bash
# Via API (requiere API key)
curl -X POST "http://localhost:8000/actualizar-datos" \
  -H "X-API-Key: cannabis-key-2025"

# Via ETL directo
python etl/main.py
```

## 🚀 Despliegue en Producción

### Recomendaciones para Producción

1. **Base de Datos**: Migrar a PostgreSQL
2. **Seguridad**: Implementar HTTPS, JWT, Rate Limiting
3. **Agente de IA**: Implementar LangChain y un modelo de IA más completo (OpenAI)
4. **Monitoring**: Agregar logs estructurados y métricas
5. **CI/CD**: Configurar pipelines de despliegue
6. **Escalabilidad**: Usar contenedores Docker