from funciones_gestion import *
from funciones_huesped import *
from funciones_hotel import *
from funciones_poi import *
from funciones_amenity import *
import random


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
        print(resultado)
def crear_pois():
    pois = [
        {"id_poi": 1, "nombre": "Obelisco", "detalle": "Monumento icónico en Buenos Aires", "direccion": "Av. 9 de Julio", "tipo": "Monumento"},
        {"id_poi": 2, "nombre": "Puente de la Mujer", "detalle": "Puente moderno en Puerto Madero", "direccion": "Aime Paine 500", "tipo": "Atracción"},
        {"id_poi": 3, "nombre": "Cementerio de la Recoleta", "detalle": "Cementerio histórico con arquitectura impresionante", "direccion": "Junín 1760", "tipo": "Histórico"},
        {"id_poi": 4, "nombre": "Plaza Serrano", "detalle": "Plaza popular en el barrio de Palermo", "direccion": "Armenia 5000", "tipo": "Espacio Público"},
        {"id_poi": 5, "nombre": "Mercado de San Telmo", "detalle": "Mercado tradicional en el barrio de San Telmo", "direccion": "Humberto Primo 831", "tipo": "Mercado"},
        {"id_poi": 6, "nombre": "Teatro Colón", "detalle": "Famoso teatro de ópera en el centro de Buenos Aires", "direccion": "Cerrito 628", "tipo": "Teatro"},
        {"id_poi": 7, "nombre": "Plaza de Mayo", "detalle": "Histórica plaza frente a la Casa Rosada", "direccion": "Av. Hipólito Yrigoyen s/n", "tipo": "Plaza"},
        {"id_poi": 8, "nombre": "Museo Nacional de Bellas Artes", "detalle": "Museo de arte con una amplia colección de obras", "direccion": "Libertador 1473", "tipo": "Museo"},
        {"id_poi": 9, "nombre": "Barrio Chino", "detalle": "Colorido barrio con tiendas y restaurantes chinos", "direccion": "Arribeños 2240", "tipo": "Barrio"},
        {"id_poi": 10, "nombre": "Jardín Botánico", "detalle": "Jardín botánico con variedad de plantas y esculturas", "direccion": "Av. Santa Fe 3870", "tipo": "Parque"},
        {"id_poi": 11, "nombre": "Planetario Galileo Galilei", "detalle": "Planetario con exhibiciones de astronomía", "direccion": "Sarmiento 3000", "tipo": "Ciencia"},
        {"id_poi": 12, "nombre": "Parque Centenario", "detalle": "Parque popular para eventos y ferias", "direccion": "Díaz Vélez 5000", "tipo": "Parque"},
        {"id_poi": 13, "nombre": "La Bombonera", "detalle": "Estadio de fútbol del club Boca Juniors", "direccion": "Brandsen 805", "tipo": "Estadio"},
        {"id_poi": 14, "nombre": "Palacio Barolo", "detalle": "Edificio histórico inspirado en la Divina Comedia", "direccion": "Av. de Mayo 1370", "tipo": "Arquitectura"},
        {"id_poi": 15, "nombre": "Bosques de Palermo", "detalle": "Parque grande con lagos y áreas recreativas", "direccion": "Av. Infanta Isabel 1500", "tipo": "Parque"}
    ]

    for poi in pois:
        resultado = alta_poi(
            poi["id_poi"], 
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

def crear_amenitys():
    amenitys = [
        "Sales de Baño",
        "Chocolates",
        "Copa de Bienvenida",
        "Mini Bar",
        "Toallas Extra",
        "Bata de Baño",
        "Desayuno en Habitación",
        "Almohadas Adicionales",
        "Wi-Fi Gratuito",
        "Café y Té"
    ]

    for nombre in amenitys:
        resultado = alta_amenity(nombre)
        print(resultado)


def crear_habitaciones():
    try:
        # Obtener la lista de hoteles
        hoteles = mostrar_hoteles()
        if not hoteles:
            print("No hay hoteles disponibles para crear habitaciones.")
            return

        # Obtener la lista de amenities
        amenitys = mostrar_amenitys()
        if not amenitys:
            print("No hay amenities disponibles para asignar a las habitaciones.")
            return
        
        tipos_habitacion = ["Suite", "Doble", "Simple"]  # Tipos de habitación disponibles

        for hotel in hoteles:
            id_hotel = hotel["id"]
            nombre_hotel = hotel["nombre"].replace(" ", "_")

            for i in range(5):  # Crear 5 habitaciones por hotel
                # Generar un nuevo ID de habitación
                nuevo_id = i + 1
                id_habitacion = f"{nombre_hotel}_{nuevo_id}"

                # Seleccionar un tipo de habitación aleatorio
                tipo_habitacion = random.choice(tipos_habitacion)

                # Crear la habitación y relacionarla con el hotel
                query = """
                    MATCH (h:Hotel {id_hotel: $id_hotel})
                    CREATE (h)-[:TIENE]->(:Habitacion {id_habitacion: $id_habitacion, tipo_habitacion: $tipo_habitacion})
                """
                graph.run(query, id_hotel=id_hotel, id_habitacion=id_habitacion, tipo_habitacion=tipo_habitacion)
                print(f"Habitación '{id_habitacion}' de tipo '{tipo_habitacion}' creada exitosamente en el hotel '{nombre_hotel}'.")

                # Asignar entre 0 y 4 amenities a la habitación
                num_amenities = random.randint(0, 4)  # Número aleatorio de amenities
                selected_amenities = random.sample(amenitys, num_amenities)  # Seleccionar amenities aleatorios

                for amenity in selected_amenities:
                    # Crear la relación entre la habitación y el amenity
                    query = """
                        MATCH (a:Amenity {id_amenity: $id_amenity})
                        MATCH (h:Habitacion {id_habitacion: $id_habitacion})
                        CREATE (h)-[:INCLUYE]->(a)
                    """
                    graph.run(query, id_habitacion=id_habitacion, id_amenity=amenity["id"])
                    print(f"Amenity con ID {amenity['id']} asignado a la habitación {id_habitacion} exitosamente.")

    except Exception as e:
        print(f"Error al crear las habitaciones: {e}")
