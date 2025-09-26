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
- Integración con LangChain y Ollama
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
