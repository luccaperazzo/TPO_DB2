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
def crear_pois():
    pois = [
        {"nombre": "Obelisco", "detalle": "Monumento icónico en Buenos Aires", "direccion": "Av. 9 de Julio", "tipo": "Monumento"},
        {"nombre": "Puente de la Mujer", "detalle": "Puente moderno en Puerto Madero", "direccion": "Aime Paine 500", "tipo": "Atracción"},
        {"nombre": "Cementerio de la Recoleta", "detalle": "Cementerio histórico con arquitectura impresionante", "direccion": "Junín 1760", "tipo": "Histórico"},
        {"nombre": "Plaza Serrano", "detalle": "Plaza popular en el barrio de Palermo", "direccion": "Armenia 5000", "tipo": "Espacio Público"},
        {"nombre": "Mercado de San Telmo", "detalle": "Mercado tradicional en el barrio de San Telmo", "direccion": "Humberto Primo 831", "tipo": "Mercado"},
        {"nombre": "Teatro Colón", "detalle": "Famoso teatro de ópera en el centro de Buenos Aires", "direccion": "Cerrito 628", "tipo": "Teatro"},
        {"nombre": "Plaza de Mayo", "detalle": "Histórica plaza frente a la Casa Rosada", "direccion": "Av. Hipólito Yrigoyen s/n", "tipo": "Plaza"},
        {"nombre": "Museo Nacional de Bellas Artes", "detalle": "Museo de arte con una amplia colección de obras", "direccion": "Libertador 1473", "tipo": "Museo"},
        {"nombre": "Barrio Chino", "detalle": "Colorido barrio con tiendas y restaurantes chinos", "direccion": "Arribeños 2240", "tipo": "Barrio"},
        {"nombre": "Jardín Botánico", "detalle": "Jardín botánico con variedad de plantas y esculturas", "direccion": "Av. Santa Fe 3870", "tipo": "Parque"},
        {"nombre": "Planetario Galileo Galilei", "detalle": "Planetario con exhibiciones de astronomía", "direccion": "Sarmiento 3000", "tipo": "Ciencia"},
        {"nombre": "Parque Centenario", "detalle": "Parque popular para eventos y ferias", "direccion": "Díaz Vélez 5000", "tipo": "Parque"},
        {"nombre": "La Bombonera", "detalle": "Estadio de fútbol del club Boca Juniors", "direccion": "Brandsen 805", "tipo": "Estadio"},
        {"nombre": "Palacio Barolo", "detalle": "Edificio histórico inspirado en la Divina Comedia", "direccion": "Av. de Mayo 1370", "tipo": "Arquitectura"},
        {"nombre": "Bosques de Palermo", "detalle": "Parque grande con lagos y áreas recreativas", "direccion": "Av. Infanta Isabel 1500", "tipo": "Parque"}
    ]

    for poi in pois:
        resultado = alta_poi(
            poi["nombre"], 
            poi["detalle"], 
            poi["direccion"], 
            poi["tipo"]
        )
        print(resultado)
        
def crear_hoteles():
    hoteles = [
        {"nombre": "Hotel Puerto Madero", "direccion": "Dique 1, Puerto Madero", "telefono": "987654321", "email": "puertomadero@example.com"},
        {"nombre": "Hotel Obelisco", "direccion": "Cerrito 286", "telefono": "123456789", "email": "obelisco@example.com" },
        {"nombre": "Hotel Recoleta", "direccion": "Av. Alvear 1891", "telefono": "111222333", "email": "recoleta@example.com"},
        {"nombre": "Hotel Palermo", "direccion": "Honduras 4881", "telefono": "444555666", "email": "palermo@example.com"},
        {"nombre": "Hotel San Telmo", "direccion": "Defensa 1047", "telefono": "777888999", "email": "santelmo@example.com"}
    ]

    for hotel in hoteles:
        resultado = alta_hotel(
            hotel["nombre"], 
            hotel["direccion"], 
            hotel["telefono"], 
            hotel["email"], 
        )
        print(resultado)   


