from funciones_gestion import *
from funciones_huesped import *
from funciones_hotel import *

# Lista de datos de los huéspedes a crear
def crear_huespedes():
    huespedes = [
        {"nombre": "Juan", "apellido": "Perez", "direccion": "Calle Falsa 123", "telefono": "123456789", "email": "juan.perez@example.com"},
        {"nombre": "Ana", "apellido": "Garcia", "direccion": "Avenida Siempre Viva 456", "telefono": "987654321", "email": "ana.garcia@example.com"},
        {"nombre": "Carlos", "apellido": "Lopez", "direccion": "Boulevard Principal 789", "telefono": "111222333", "email": "carlos.lopez@example.com"},
        {"nombre": "Marta", "apellido": "Martinez", "direccion": "Carrera 12 #34-56", "telefono": "444555666", "email": "marta.martinez@example.com"},
        {"nombre": "Luis", "apellido": "Gomez", "direccion": "Calle 7 #8-9", "telefono": "777888999", "email": "luis.gomez@example.com"}
    ]

    # Crear los huéspedes usando la función alta_huesped
    for huesped in huespedes:
        resultado = alta_huesped(
            huesped["nombre"], 
            huesped["apellido"], 
            huesped["direccion"], 
            huesped["telefono"], 
            huesped["email"]
        )

def crear_hoteles():
    hoteles = [
        {"nombre": "Hotel Obelisco", "direccion": "Av. 9 de Julio 123", "telefono": "123456789", "email": "obelisco@example.com", "coordenadas": "-34.603684, -58.381559"},
        {"nombre": "Hotel Puerto Madero", "direccion": "Dique 1, Puerto Madero", "telefono": "987654321", "email": "puertomadero@example.com", "coordenadas": "-34.6083, -58.3629"},
        {"nombre": "Hotel Recoleta", "direccion": "Av. Alvear 1891", "telefono": "111222333", "email": "recoleta@example.com", "coordenadas": "-34.5883, -58.3974"},
        {"nombre": "Hotel Palermo", "dire6ccion": "Calle Serrano 1425", "telefono": "444555666", "email": "palermo@example.com", "coordenadas": "-34.5888, -58.4304"},
        {"nombre": "Hotel San Telmo", "direccion": "Calle Defensa 1047", "telefono": "777888999", "email": "santelmo@example.com", "coordenadas": "-34.6215, -58.3731"}
    ]

    for hotel in hoteles:
        resultado = alta_hotel(
            hotel["nombre"], 
            hotel["direccion"], 
            hotel["telefono"], 
            hotel["email"], 
            hotel["coordenadas"]
        )
        print(resultado)   