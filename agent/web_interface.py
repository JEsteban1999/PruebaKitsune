# agent/web_app.py
from flask import Flask, render_template, request, jsonify
import logging
import sys
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar el agente
try:
    from ollama import FastOllamaAgent
except ImportError:
    # Si hay error de importación, crear una versión mínima
    class FastOllamaAgent:
        def __init__(self):
            self.conversation_history = []
        
        def procesar_consulta_hibrida(self, consulta: str) -> str:
            return f"Agente temporal: Recibí tu consulta '{consulta}'. El agente principal está siendo cargado."

app = Flask(__name__)
app.secret_key = 'cannabis_agent_secret_2024'

# Instancia global del agente
agente = None

def inicializar_agente():
    """Inicializa el agente de manera segura"""
    global agente
    try:
        agente = FastOllamaAgent()
        logger.info("✅ Agente inicializado correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error inicializando agente: {e}")
        # Crear agente de respaldo
        agente = FastOllamaAgent()  # Usará la clase de respaldo si hay error
        return False

@app.route('/')
def index():
    """Página principal con el chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Endpoint para procesar mensajes del chat"""
    try:
        data = request.get_json()
        consulta = data.get('message', '').strip()
        
        if not consulta:
            return jsonify({
                'status': 'error',
                'error': 'La consulta no puede estar vacía'
            }), 400
        
        logger.info(f"📨 Consulta recibida: {consulta}")
        
        # Asegurarse de que el agente esté inicializado
        if agente is None:
            inicializar_agente()
        
        # Procesar la consulta
        respuesta = agente.procesar_consulta_hibrida(consulta)
        
        logger.info(f"✅ Respuesta generada: {len(respuesta)} caracteres")
        
        return jsonify({
            'status': 'success',
            'response': respuesta,
            'timestamp': os.times().elapsed  # Tiempo de procesamiento aproximado
        })
        
    except Exception as e:
        logger.error(f"❌ Error en chat endpoint: {e}")
        return jsonify({
            'status': 'error',
            'error': f'Error procesando la consulta: {str(e)}'
        }), 500

@app.route('/api/status', methods=['GET'])
def status_endpoint():
    """Endpoint para verificar el estado del servicio"""
    try:
        status_info = {
            'status': 'running',
            'agent_initialized': agente is not None,
            'ollama_available': False,
            'api_available': False
        }
        
        # Verificar Ollama
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=3)
            status_info['ollama_available'] = response.status_code == 200
        except:
            status_info['ollama_available'] = False
        
        # Verificar API
        try:
            import requests
            response = requests.get('http://localhost:8000/', timeout=3)
            status_info['api_available'] = response.status_code == 200
        except:
            status_info['api_available'] = False
        
        return jsonify(status_info)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_chat():
    """Endpoint para reiniciar el historial de conversación"""
    try:
        if agente and hasattr(agente, 'conversation_history'):
            agente.conversation_history = []
            logger.info("🔄 Historial de chat reiniciado")
        
        return jsonify({
            'status': 'success',
            'message': 'Historial reiniciado correctamente'
        })
        
    except Exception as e:
        logger.error(f"❌ Error reiniciando chat: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/models', methods=['GET'])
def list_models():
    """Endpoint para listar modelos disponibles de Ollama"""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return jsonify({
                'status': 'success',
                'models': [model['name'] for model in models]
            })
        else:
            return jsonify({
                'status': 'error',
                'error': 'No se pudieron obtener los modelos'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# Inicializar el agente al cargar la aplicación
@app.before_request
def initialize():
    inicializar_agente()

if __name__ == '__main__':
    # Inicializar el agente antes de ejecutar el servidor
    inicializar_agente()
    
    # Ejecutar la aplicación Flask
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True  # Para manejar múltiples solicitudes concurrentes
    )