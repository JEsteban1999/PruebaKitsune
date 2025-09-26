import logging
import requests
import json
import time
from typing import Dict, List, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FastOllamaAgent:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.api_url = "http://localhost:8000"
        self.model = "gemma3:1b"
        self.conversation_history = []
        
        # Verificar conexiones rápidamente
        self._check_connections()
    
    def _check_connections(self):
        """Verificación rápida de conexiones"""
        logger.info("Verificando conexiones...")
        
        # Verificar Ollama rápidamente
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            if response.status_code == 200:
                logger.info("✅ Ollama conectado")
        except Exception as e:
            logger.error(f"❌ Ollama no disponible: {e}")
            raise ConnectionError("Ollama no está disponible")
        
        # Verificar API rápidamente
        try:
            response = requests.get(f"{self.api_url}/", timeout=3)
            if response.status_code == 200:
                logger.info("✅ API conectada")
        except Exception as e:
            logger.error(f"❌ API no disponible: {e}")
            raise ConnectionError("API no disponible")
    
    def call_ollama_fast(self, prompt: str, system_message: str = None) -> str:
        """Versión rápida de llamada a Ollama con timeout corto"""
        try:
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Más determinístico
                    "num_predict": 150,  # Menos tokens para respuesta más rápida
                    "num_thread": 4,     # Usar más threads si está disponible
                }
            }
            
            if system_message:
                data["system"] = system_message
            
            logger.debug(f"Prompt: {prompt[:80]}...")
            
            start_time = time.time()
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=data,
                timeout=15  # Timeout más corto
            )
            response.raise_for_status()
            
            result = response.json()
            respuesta = result.get("response", "").strip()
            elapsed = time.time() - start_time
            
            logger.debug(f"Ollama respondió en {elapsed:.2f}s: {respuesta[:80]}...")
            return respuesta
            
        except requests.exceptions.Timeout:
            logger.warning("⚠️ Ollama timeout - usando respuesta predefinida")
            return "Los datos están disponibles pero el modelo está tardando en responder. Aquí tienes la información directamente:"
        except Exception as e:
            logger.error(f"Error Ollama: {e}")
            return ""  # Cadena vacía para usar fallback
    
    def call_api(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Llama a la API REST rápidamente"""
        try:
            url = f"{self.api_url}{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error API {endpoint}: {e}")
            return None
    
    def interpretar_consulta_rapida(self, consulta: str) -> Dict:
        """Interpretación ultra rápida sin Ollama"""
        consulta_lower = consulta.lower()
        
        # Palabras clave más específicas
        estadisticas_keywords = ['cuántas', 'cuantos', 'total', 'número', 'numero', 'estadística', 'estadisticas', 'resumen']
        buscar_keywords = ['buscar', 'encontrar', 'municipio', 'departamento', 'ciudad', 'pueblo', 'localidad', 'departamentos']
        listar_keywords = ['listar', 'lista', 'todos', 'mostrar', 'ver todos', 'cuales', 'cuáles']
        
        # Buscar nombres de departamentos comunes
        departamentos = ['antioquia', 'bogotá', 'bogota', 'cundinamarca', 'valle', 'cauca', 'santander', 'boyacá', 'boyaca', 'huila', 'neiva', 'cali']
        
        # Verificar si menciona un departamento específico
        for depto in departamentos:
            if depto in consulta_lower:
                return {"accion": "buscar", "parametros": {"q": depto}}
        
        # Verificar por tipo de consulta
        if any(palabra in consulta_lower for palabra in estadisticas_keywords):
            return {"accion": "estadisticas", "parametros": {}}
        elif any(palabra in consulta_lower for palabra in buscar_keywords):
            # Extraer términos de búsqueda
            terminos = self._extraer_terminos_busqueda(consulta_lower)
            return {"accion": "buscar", "parametros": {"q": terminos}}
        elif any(palabra in consulta_lower for palabra in listar_keywords):
            return {"accion": "listar", "parametros": {"limit": 5}}
        else:
            # Por defecto, buscar
            return {"accion": "buscar", "parametros": {"q": consulta_lower}}
    
    def _extraer_terminos_busqueda(self, consulta: str) -> str:
        """Extrae términos de búsqueda relevantes"""
        # Palabras a eliminar
        stop_words = ['licencias', 'cannabis', 'de', 'en', 'por', 'para', 'con', 'las', 'los', 'qué', 'que']
        
        palabras = consulta.split()
        palabras_filtradas = [p for p in palabras if p not in stop_words and len(p) > 2]
        
        return ' '.join(palabras_filtradas) if palabras_filtradas else consulta
    
    def obtener_datos_formateados(self, accion: str, parametros: Dict) -> str:
        """Obtiene y formatea datos directamente sin Ollama"""
        datos = self.obtener_datos(accion, parametros)
        
        if not datos:
            return "No se pudieron obtener datos de la API."
        
        if accion == "estadisticas":
            return self._formatear_estadisticas_directo(datos)
        elif accion == "buscar":
            return self._formatear_busqueda_directo(datos)
        elif accion == "listar":
            return self._formatear_listado_directo(datos)
        else:
            return str(datos)
    
    def _formatear_estadisticas_directo(self, datos: Dict) -> str:
        """Formatea estadísticas directamente"""
        totals = datos.get('totales', {})
        response = "📊 **ESTADÍSTICAS DE LICENCIAS**\n\n"
        response += f"• Municipios con licencias: {totals.get('total_municipios', 'N/A')}\n"
        response += f"• Total licencias: {totals.get('total_licencias', 'N/A'):,}\n"
        response += f"• No psicoactivas: {totals.get('total_no_psico', 'N/A'):,}\n"
        response += f"• Psicoactivas: {totals.get('total_psico', 'N/A'):,}\n"
        response += f"• Semillas: {totals.get('total_semillas', 'N/A'):,}\n"
        response += f"• Promedio por municipio: {totals.get('promedio_por_municipio', 'N/A'):.1f}\n"
        return response
    
    def _formatear_busqueda_directo(self, datos: Dict) -> str:
        """Formatea búsqueda directamente"""
        if datos.get('total', 0) == 0:
            return "🔍 No se encontraron resultados para tu búsqueda."
        
        response = f"🔍 **ENCONTRADOS: {datos['total']} resultados**\n\n"
        for i, item in enumerate(datos.get('resultados', [])[:3], 1):
            response += f"{i}. **{item.get('municipio', 'N/A')}, {item.get('departamento', 'N/A')}**\n"
            response += f"   Total: {item.get('total', 0)} | "
            response += f"No psico: {item.get('no_psico', 0)} | "
            response += f"Psico: {item.get('psico', 0)} | "
            response += f"Semillas: {item.get('semillas', 0)}\n\n"
        return response
    
    def _formatear_listado_directo(self, datos: Dict) -> str:
        """Formatea listado directamente"""
        response = f"📋 **MUNICIPIOS CON LICENCIAS** ({datos.get('total', 0)} total)\n\n"
        for i, item in enumerate(datos.get('resultados', [])[:5], 1):
            response += f"{i}. {item.get('municipio', 'N/A')}, {item.get('departamento', 'N/A')} - {item.get('total', 0)} licencias\n"
        return response
    
    def obtener_datos(self, accion: str, parametros: Dict) -> Optional[Dict]:
        """Obtiene datos de la API"""
        try:
            if accion == "estadisticas":
                return self.call_api("/estadisticas")
            elif accion == "buscar":
                return self.call_api("/licencias/buscar/", parametros)
            elif accion == "listar":
                return self.call_api("/licencias", {"limit": parametros.get("limit", 5)})
            return None
        except Exception as e:
            logger.error(f"Error obteniendo datos: {e}")
            return None
    
    def procesar_consulta_hibrida(self, consulta: str) -> str:
        """Procesamiento híbrido: rápido con opción de mejora con Ollama"""
        start_time = time.time()
        
        try:
            # Paso 1: Interpretación rápida
            interpretacion = self.interpretar_consulta_rapida(consulta)
            logger.info(f"🔍 Acción: {interpretacion['accion']}")
            
            # Paso 2: Obtener datos rápidamente
            datos_brutos = self.obtener_datos_formateados(interpretacion["accion"], interpretacion["parametros"])
            
            # Paso 3: Intentar mejora con Ollama (pero con timeout corto)
            try:
                prompt_mejora = f"""
                El usuario preguntó: "{consulta}"
                Ya tengo esta respuesta basada en datos reales: "{datos_brutos}"
                
                Mejora esta respuesta haciéndola más natural y conversacional en español, 
                pero MANTÉN exactamente la misma información y números.
                Responde directamente con la versión mejorada, sin explicaciones adicionales.
                """
                
                respuesta_mejorada = self.call_ollama_fast(prompt_mejora, 
                    "Eres un asistente que mejora respuestas técnicas haciéndolas más naturales.")
                
                if respuesta_mejorada and len(respuesta_mejorada) > 10:
                    respuesta_final = respuesta_mejorada
                    metodo = "Ollama"
                else:
                    respuesta_final = datos_brutos
                    metodo = "Directo"
                    
            except Exception as e:
                respuesta_final = datos_brutos
                metodo = "Directo (fallback)"
                logger.warning(f"Ollama falló, usando directo: {e}")
            
            elapsed = time.time() - start_time
            logger.info(f"✅ Procesado en {elapsed:.2f}s usando {metodo}")
            
            return respuesta_final
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            logger.error(error_msg)
            return error_msg

# Interfaz optimizada
def main():
    print("⚡ ASISTENTE RÁPIDO DE LICENCIAS DE CANNABIS")
    print("=" * 45)
    
    try:
        agente = FastOllamaAgent()
        print("✅ Agente listo (usando Gemma 3 1B para mayor velocidad)")
        print("💡 Escribe tu consulta o 'salir' para terminar\n")
        
        while True:
            try:
                consulta = input("👤 Tú: ").strip()
                
                if consulta.lower() in ['salir', 'exit', 'quit', 'q']:
                    print("¡Hasta luego! 👋")
                    break
                
                if not consulta:
                    continue
                
                print("⚡ Procesando...", end="", flush=True)
                start_time = time.time()
                respuesta = agente.procesar_consulta_hibrida(consulta)
                elapsed = time.time() - start_time
                
                print(f"\r✅ Respondido en {elapsed:.1f}s")
                print(f"🤖 {respuesta}\n")
                
            except KeyboardInterrupt:
                print("\n\n¡Hasta luego! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()