from funciones_gestion import *
from funciones_huesped import *
from funciones_hotel import *
from funciones_poi import *

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
        {"nombre": "Hotel Palermo", "direccion": "Calle Serrano 1425", "telefono": "444555666", "email": "palermo@example.com", "coordenadas": "-34.5888, -58.4304"},
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

def crear_pois():
    pois = [
        {"id_poi": 1, "nombre": "Obelisco", "detalle": "Monumento icónico en Buenos Aires", "coordenadas": "-34.603684, -58.381559", "tipo": "Monumento"},
        {"id_poi": 2, "nombre": "Puente de la Mujer", "detalle": "Puente moderno en Puerto Madero", "coordenadas": "-34.6083, -58.3629", "tipo": "Atracción"},
        {"id_poi": 3, "nombre": "Cementerio de la Recoleta", "detalle": "Cementerio histórico con arquitectura impresionante", "coordenadas": "-34.5883, -58.3974", "tipo": "Histórico"},
        {"id_poi": 4, "nombre": "Plaza Serrano", "detalle": "Plaza popular en el barrio de Palermo", "coordenadas": "-34.5888, -58.4304", "tipo": "Espacio Público"},
        {"id_poi": 5, "nombre": "Mercado de San Telmo", "detalle": "Mercado tradicional en el barrio de San Telmo", "coordenadas": "-34.6215, -58.3731", "tipo": "Mercado"},
        {"id_poi": 6, "nombre": "Teatro Colón", "detalle": "Famoso teatro de ópera en el centro de Buenos Aires", "coordenadas": "-34.601250, -58.383450", "tipo": "Teatro"},
        {"id_poi": 7, "nombre": "Plaza de Mayo", "detalle": "Histórica plaza frente a la Casa Rosada", "coordenadas": "-34.6081, -58.3703", "tipo": "Plaza"},
        {"id_poi": 8, "nombre": "Museo Nacional de Bellas Artes", "detalle": "Museo de arte con una amplia colección de obras", "coordenadas": "-34.5833, -58.3939", "tipo": "Museo"},
        {"id_poi": 9, "nombre": "Barrio Chino", "detalle": "Colorido barrio con tiendas y restaurantes chinos", "coordenadas": "-34.5635, -58.4416", "tipo": "Barrio"},
        {"id_poi": 10, "nombre": "Jardín Botánico", "detalle": "Jardín botánico con variedad de plantas y esculturas", "coordenadas": "-34.5803, -58.4231", "tipo": "Parque"},
        {"id_poi": 11, "nombre": "Planetario Galileo Galilei", "detalle": "Planetario con exhibiciones de astronomía", "coordenadas": "-34.5672, -58.4113", "tipo": "Ciencia"},
        {"id_poi": 12, "nombre": "Parque Centenario", "detalle": "Parque popular para eventos y ferias", "coordenadas": "-34.6061, -58.4335", "tipo": "Parque"},
        {"id_poi": 13, "nombre": "La Bombonera", "detalle": "Estadio de fútbol del club Boca Juniors", "coordenadas": "-34.6354, -58.3644", "tipo": "Estadio"},
        {"id_poi": 14, "nombre": "Palacio Barolo", "detalle": "Edificio histórico inspirado en la Divina Comedia", "coordenadas": "-34.6091, -58.3849", "tipo": "Arquitectura"},
        {"id_poi": 15, "nombre": "Bosques de Palermo", "detalle": "Parque grande con lagos y áreas recreativas", "coordenadas": "-34.5735, -58.4193", "tipo": "Parque"}
    ]

    for poi in pois:
        resultado = alta_poi(
            poi["id_poi"], 
            poi["nombre"], 
            poi["detalle"], 
            poi["coordenadas"], 
            poi["tipo"]
        )
        print(resultado)
