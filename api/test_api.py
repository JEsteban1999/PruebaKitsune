# api/test_api.py (corregido)
import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "cannabis-key-2025"

headers = {
    "X-API-Key": API_KEY
}

def test_endpoints():
    """Prueba todos los endpoints de la API"""
    
    print("🧪 Probando API de Licencias de Cannabis...\n")
    
    try:
        # 1. Test root endpoint
        print("1. Probando endpoint raíz...")
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}\n")
        
        # 2. Test listar licencias
        print("2. Probando listado de licencias...")
        response = requests.get(f"{BASE_URL}/licencias?limit=5")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Total registros: {data['total']}")
        print(f"   Registros retornados: {len(data['resultados'])}\n")
        
        # 3. Test obtener licencia específica
        print("3. Probando obtener licencia por ID...")
        if data['resultados']:
            first_id = data['resultados'][0]['id']
            response = requests.get(f"{BASE_URL}/licencias/{first_id}")
            print(f"   Status: {response.status_code}")
            licencia = response.json()
            print(f"   Licencia: {licencia['municipio']}, {licencia['departamento']} - Total: {licencia['total']}\n")
        
        # 4. Test búsqueda
        print("4. Probando búsqueda...")
        response = requests.get(f"{BASE_URL}/licencias/buscar/?q=Antioquia&limit=3")
        print(f"   Status: {response.status_code}")
        search_data = response.json()
        print(f"   Resultados búsqueda: {search_data['total']}")
        if search_data['resultados']:
            for resultado in search_data['resultados']:
                print(f"     - {resultado['municipio']}: {resultado['total']} licencias")
        print()
        
        # 5. Test estadísticas
        print("5. Probando estadísticas...")
        response = requests.get(f"{BASE_URL}/estadisticas")
        print(f"   Status: {response.status_code}")
        stats = response.json()
        print(f"   Total municipios: {stats['totales']['total_municipios']}")
        print(f"   Total licencias: {stats['totales']['total_licencias']}")
        print(f"   Promedio por municipio: {stats['totales']['promedio_por_municipio']:.1f}")
        print(f"   Top departamento: {stats['top_departamentos'][0]['departamento']} - {stats['top_departamentos'][0]['total_licencias']} licencias\n")
        
        # 6. Test actualización (protegido) - CORREGIDO
        print("6. Probando actualización de datos (endpoint protegido)...")
        response = requests.post(
            f"{BASE_URL}/actualizar-datos",
            headers={"X-API-Key": API_KEY}  # Header corregido
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}\n")
        else:
            print(f"   Error: {response.text}\n")
            
        # 7. Test sin API key (debe fallar)
        print("7. Probando sin API key (debe fallar)...")
        response = requests.post(f"{BASE_URL}/actualizar-datos")
        print(f"   Status: {response.status_code} (esperado: 403)")
        print(f"   Response: {response.json()}\n")
            
        print("✅ Todas las pruebas completadas!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar a la API. Asegúrate de que el servidor esté ejecutándose.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_endpoints()