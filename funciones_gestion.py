from py2neo import Graph
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from funciones_huesped import *

# --- Conexiones ---
graph = Graph("bolt://neo4j:12345678@localhost:7687")
client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_db']
reservas_collection = db['reservas']

def alta_habitacion(id_habitacion, tipo_habitacion, id_hotel):
    try:
        query = """
            MATCH (h:Hotel {id_hotel: $id_hotel})
            CREATE (h)-[:TIENE]->(:Habitacion {id_habitacion: $id_habitacion, tipo_habitacion: $tipo_habitacion})
        """
        graph.run(query, id_habitacion=id_habitacion, tipo_habitacion=tipo_habitacion, id_hotel=id_hotel)
        return f"Habitación '{id_habitacion}' creada exitosamente en el hotel {id_hotel}."
    except Exception as e:
        return f"Error al crear la habitación: {e}"
    
def baja_habitacion(id_habitacion):
    try:
        query = """
            MATCH (hab:Habitacion {id_habitacion: $id_habitacion})
            DETACH DELETE hab
        """
        graph.run(query, id_habitacion=id_habitacion)
        return f"Habitación con ID {id_habitacion} eliminada exitosamente."
    except Exception as e:
        return f"Error al eliminar la habitación: {e}"
    
    
def modificar_habitacion(id_habitacion, tipo_habitacion=None, id_hotel=None):
    try:
        # Actualizar solo los campos que no son None
        update_fields = []
        
        if tipo_habitacion:
            update_fields.append(f"hab.tipo_habitacion = '{tipo_habitacion}'")
        
        # Verificar si se debe cambiar el id_hotel
        if id_hotel:
            # Eliminar la relación existente con el hotel
            query_unlink = "MATCH (h)-[r:TIENE]->(hab:Habitacion {id_habitacion: $id_habitacion}) DELETE r"
            graph.run(query_unlink, id_habitacion=id_habitacion)

            # Crear la nueva relación con el nuevo hotel
            query_link = "MATCH (h:Hotel {id_hotel: $id_hotel}), (hab:Habitacion {id_habitacion: $id_habitacion}) CREATE (h)-[:TIENE]->(hab)"
            graph.run(query_link, id_hotel=id_hotel, id_habitacion=id_habitacion)

        # Si hay campos para actualizar, construir y ejecutar la consulta de actualización
        if update_fields:
            query = f"""
                MATCH (hab:Habitacion {{id_habitacion: $id_habitacion}})
                SET {', '.join(update_fields)}
            """
            graph.run(query, id_habitacion=id_habitacion)
        
        return f"Habitación con ID {id_habitacion} modificada exitosamente."
    
    except Exception as e:
        return f"Error al modificar la habitación: {e}"
    
def crear_relacion_hotel_habitacion(id_hotel, id_habitacion):
    query = f"MATCH (h:Hotel {{id_hotel: '{id_hotel}'}}), (hab:Habitacion {{id_habitacion: '{id_habitacion}'}}) CREATE (h)-[:TIENE]->(hab)"
    graph.run(query)
    return f"Relación TIENE creada entre Hotel {id_hotel} y Habitación {id_habitacion}."

def crear_relacion_habitacion_amenity(id_habitacion, id_amenity):
    query = f"MATCH (hab:Habitacion {{id_habitacion: '{id_habitacion}'}}), (a:Amenity {{id_amenity: '{id_amenity}'}}) CREATE (hab)-[:TIENE_AMENITY]->(a)"
    graph.run(query)
    return f"Relación TIENE_AMENITY creada entre Habitación {id_habitacion} y Amenity {id_amenity}."

def crear_relacion_hotel_poi(id_hotel, id_poi, distancia):
    query = f"MATCH (h:Hotel {{id_hotel: '{id_hotel}'}}), (p:POI {{id_poi: '{id_poi}'}}) CREATE (h)-[:CERCA_DE {{distancia: {distancia}}}]->(p)"
    graph.run(query)
    return f"Relación CERCA_DE creada entre Hotel {id_hotel} y POI {id_poi} con distancia {distancia}."

def verificar_habitacion_en_hotel(id_habitacion):
    query = f"MATCH (h:Hotel)-[:TIENE]->(hab:Habitacion {{id_habitacion: '{id_habitacion}'}}) RETURN h"
    resultado = graph.run(query).data()
    return len(resultado) > 0  # Si ya está asignada, devuelve True

# 3. Hoteles cerca de un POI
def hoteles_cerca_de_poi():
    # Consulta para obtener todos los POIs disponibles
    query_pois = """
    MATCH (poi:POI)
    RETURN poi.nombre AS nombre, poi.detalle AS detalle
    """
    pois_result = graph.run(query_pois)

    # Listar los POIs disponibles
    print("Lista de POIs disponibles:")
    pois_disponibles = []
    for record in pois_result:
        poi_nombre = record['nombre']
        poi_detalle = record['detalle']
        pois_disponibles.append(poi_nombre)
        print(f"POI: {poi_nombre}, Detalle: {poi_detalle}")
    
    # Solicitar al usuario que elija un POI
    poi_nombre = input("Ingrese el nombre de un POI para ver los hoteles cercanos: ")
    
    if poi_nombre not in pois_disponibles:
        print("El POI ingresado no está en la lista de POIs disponibles.")
        return
    
    # Consulta para obtener hoteles cercanos al POI seleccionado
    query_hoteles = """
    MATCH (poi:POI {nombre: $poi_nombre})<-[:CERCA_DE]-(hotel:Hotel)
    RETURN hotel.nombre AS nombre, hotel.direccion AS direccion
    """
    result = graph.run(query_hoteles, parameters={"poi_nombre": poi_nombre})

    # Mostrar los hoteles cercanos al POI seleccionado
    hoteles_cercanos = []
    for record in result:
        hotel_nombre = record['nombre']
        hotel_direccion = record['direccion']
        hoteles_cercanos.append((hotel_nombre, hotel_direccion))
    
    if hoteles_cercanos:
        for hotel in hoteles_cercanos:
            print("-----------------------------------------------------")
            print(f"Hotel: {hotel[0]}\nDirección: {hotel[1]}")
            print("-----------------------------------------------------")
    else:
        print("No se encontraron hoteles cercanos a ese POI.")

        
# 4. Información de un hotel
def informacion_hotel():
    # Consulta para obtener todos los hoteles disponibles
    query_hoteles = """
    MATCH (hotel:Hotel)
    RETURN hotel.nombre AS nombre, hotel.direccion AS direccion
    """
    hoteles_result = graph.run(query_hoteles)

    # Listar los hoteles disponibles
    print("Lista de hoteles disponibles:")
    hoteles_disponibles = []
    for record in hoteles_result:
        hotel_nombre = record['nombre']
        hotel_direccion = record['direccion']
        hoteles_disponibles.append(hotel_nombre)
        print(f"Hotel: {hotel_nombre}, Dirección: {hotel_direccion}")
    
    # Solicitar al usuario que elija un hotel
    hotel_nombre = input("Ingrese el nombre de un hotel para ver sus detalles: ")
    
    if hotel_nombre not in hoteles_disponibles:
        print("El hotel ingresado no está en la lista de hoteles disponibles.")
        return
    
    # Consulta para obtener la información detallada del hotel seleccionado
    query = """
    MATCH (hotel:Hotel {nombre: $hotel_nombre})
    RETURN hotel.nombre AS nombre, hotel.direccion AS direccion, 
           hotel.telefono AS telefono, hotel.email AS email, 
           hotel.coordenadas AS coordenadas
    """
    result = graph.run(query, parameters={"hotel_nombre": hotel_nombre})

    # Mostrar la información detallada del hotel
    for record in result:
        hotel_nombre = record['nombre']
        hotel_direccion = record['direccion']
        hotel_telefono = record['telefono']
        hotel_email = record['email']
        hotel_coordenadas = record['coordenadas']

        print("-----------------------------------------------------")
        print(f"Detalles del hotel:\nNombre: {hotel_nombre}\nDirección: {hotel_direccion}")
        print(f"Teléfono: {hotel_telefono}\nEmail: {hotel_email}\nCoordenadas: {hotel_coordenadas}")
        print("-----------------------------------------------------")




# 5. POIs cerca de un hotel
def pois_cerca_de_hotel():
    # Consulta para obtener todos los hoteles disponibles
    query_hoteles = """
    MATCH (hotel:Hotel)
    RETURN hotel.nombre AS nombre, hotel.direccion AS direccion
    """
    hoteles_result = graph.run(query_hoteles)

    # Listar los hoteles disponibles
    print("Lista de hoteles disponibles:")
    hoteles_disponibles = []
    for record in hoteles_result:
        hotel_nombre = record['nombre']
        hotel_direccion = record['direccion']
        hoteles_disponibles.append(hotel_nombre)
        print(f"Hotel: {hotel_nombre}, Dirección: {hotel_direccion}")
    
    # Solicitar al usuario que elija un hotel
    hotel_nombre = input("Ingrese el nombre de un hotel para ver los POIs cercanos: ")
    
    if hotel_nombre not in hoteles_disponibles:
        print("El hotel ingresado no está en la lista de hoteles disponibles.")
        return
    
    # Consulta para obtener los POIs cercanos al hotel seleccionado
    query = """
    MATCH (hotel:Hotel {nombre: $hotel_nombre})-[:CERCA_DE]->(poi:POI)
    RETURN poi.nombre AS nombre, poi.detalle AS detalle, poi.tipo AS tipo
    """
    result = graph.run(query, parameters={"hotel_nombre": hotel_nombre})

    # Mostrar la información de los POIs cercanos
    print(f"\nPOIs cercanos al hotel '{hotel_nombre}':")
    for record in result:
        poi_nombre = record['nombre']
        poi_detalle = record['detalle']
        poi_tipo = record['tipo']

        print("-----------------------------------------------------")
        print(f"Nombre: {poi_nombre}\nDetalle: {poi_detalle}\nTipo: {poi_tipo}")
        print("-----------------------------------------------------")



# 6. Habitaciones disponibles en un rango de fechas
def habitaciones_disponibles_en_hotel(fecha_inicio, fecha_fin):
    # Convertir fechas a objetos datetime
    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

    # Listar todos los hoteles
    query_hoteles = """
    MATCH (h:Hotel)
    RETURN h.id_hotel AS id, h.nombre AS nombre
    """
    result_hoteles = graph.run(query_hoteles)

    print("Lista de hoteles disponibles:")
    for record in result_hoteles:
        hotel_id = record['id']
        hotel_nombre = record['nombre']
        print(f"ID: {hotel_id}, Nombre: {hotel_nombre}")

    # Solicitar al usuario que ingrese el ID del hotel
    id_hotel = input("Introduce el ID del hotel para ver habitaciones disponibles: ")

    # Obtener reservas que interfieren con el rango de fechas solicitado
    reservas = reservas_collection.find({
        "$or": [
            {"fecha_entrada": {"$gte": fecha_inicio.strftime("%Y-%m-%d"), "$lte": fecha_fin.strftime("%Y-%m-%d")}},
            {"fecha_salida": {"$gte": fecha_inicio.strftime("%Y-%m-%d"), "$lte": fecha_fin.strftime("%Y-%m-%d")}},
            {
                "$and": [
                    {"fecha_entrada": {"$lte": fecha_inicio.strftime("%Y-%m-%d")}},
                    {"fecha_salida": {"$gte": fecha_fin.strftime("%Y-%m-%d")}}
                ]
            }
        ]
    })

    # Obtener IDs de habitaciones ocupadas
    habitaciones_ocupadas = {reserva["id_habitacion"] for reserva in reservas}
    
    # Consultar habitaciones disponibles en el hotel seleccionado
    query_habitaciones = """
        MATCH (h:Hotel {id_hotel: $id_hotel})-[:TIENE]->(hab:Habitacion) 
        WHERE NOT hab.id_habitacion IN $habitaciones_ocupadas
        RETURN hab.id_habitacion AS habitacion
    """
    
    # Ejecutar la consulta
    result_habitaciones = graph.run(query_habitaciones, habitaciones_ocupadas=list(habitaciones_ocupadas), id_hotel=id_hotel)

    # Comprobar si hay habitaciones disponibles
    habitaciones_disponibles = [record['habitacion'] for record in result_habitaciones]

    if habitaciones_disponibles:
        print(f"Habitaciones disponibles en el hotel con ID {id_hotel}:")
        for habitacion_id in habitaciones_disponibles:
            print("-----------------------------------------------------")
            print(f"Habitación disponible ID: {habitacion_id}")
            print("-----------------------------------------------------")
    else:
        print(f"No hay habitaciones disponibles en el hotel con ID {id_hotel} para las fechas especificadas.")



def amenities_habitacion():
    # Consulta para obtener todas las habitaciones disponibles
    query_habitaciones = """
    MATCH (hotel:Hotel)-[:TIENE]->(habitacion:Habitacion)
    RETURN hotel.nombre AS hotel_nombre, habitacion.id_habitacion AS id_habitacion, habitacion.tipo_habitacion AS tipo_habitacion
    """
    habitaciones_result = graph.run(query_habitaciones)

    # Listar las habitaciones disponibles
    print("Lista de habitaciones disponibles:")
    habitaciones_disponibles = []
    for record in habitaciones_result:
        hotel_nombre = record['hotel_nombre']
        id_habitacion = record['id_habitacion']
        tipo_habitacion = record['tipo_habitacion']
        habitaciones_disponibles.append(id_habitacion)
        print(f"Hotel: {hotel_nombre}, Habitación ID: {id_habitacion}, Tipo: {tipo_habitacion}")

    # Solicitar al usuario que elija una habitación
    id_habitacion = input("Ingrese el ID de una habitación para ver sus amenities: ")

    if id_habitacion not in habitaciones_disponibles:
        print("El ID de habitación ingresado no está en la lista de habitaciones disponibles.")
        return

    # Consulta para obtener los amenities de la habitación seleccionada
    query = """
    MATCH (habitacion:Habitacion {id_habitacion: $id_habitacion})-[:TIENE_AMENITY]->(amenity:Amenity)
    RETURN amenity.nombre AS nombre
    """
    result = graph.run(query, parameters={"id_habitacion": id_habitacion})

    # Mostrar los amenities de la habitación seleccionada
    print(f"\nAmenities de la habitación ID {id_habitacion}:")
    for record in result:
        amenity_nombre = record['nombre']
        print("-----------------------------------------------------")
        print(f"Amenity: {amenity_nombre}")
        print("-----------------------------------------------------")



# 8. Reservas por número de confirmación (ID en MongoDB)

class ReservaIdError(Exception):
    """Excepción personalizada para errores en el ID de reserva."""
    pass

def validar_reserva_id(reserva_id):
    if len(reserva_id) != 24:
        raise ReservaIdError("El número de confirmación debe tener exactamente 24 caracteres.")


def reservas_por_numero_confirmacion():
    print("Lista de huéspedes disponibles:")
    get_huespedes()

    reserva_id = input("Ingrese el número de confirmación de un huésped para ver su reserva: ")
    
    try:
        validar_reserva_id(reserva_id)

        reserva = reservas_collection.find_one({"_id": ObjectId(reserva_id)})

        if reserva:
            print("-----------------------------------------------------")
            print(f"Reserva ID: {reserva['_id']}\nHuésped ID: {reserva['id_huesped']}\nFecha de entrada: {reserva['fecha_entrada']}\nFecha de salida: {reserva['fecha_salida']}\nID de habitación: {reserva['id_habitacion']}")
            print("-----------------------------------------------------")
        else:
            print("No se encontró ninguna reserva con ese ID.")

    except ReservaIdError as e:
        print(e)  # Imprimir el mensaje de error
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")






# 10. Traer las reservas por fecha de reserva en el hotel.
def reservas_por_fecha_en_hotel(fecha_inicio, fecha_fin):
    try:
        # Mostrar lista de hoteles disponibles
        query_hoteles = """
        MATCH (hotel:Hotel)
        RETURN hotel.id_hotel AS id_hotel, hotel.nombre AS nombre
        """
        hoteles = graph.run(query_hoteles).data()

        print("Lista de hoteles disponibles:")
        for hotel in hoteles:
            print(f"Hotel ID: {hotel['id_hotel']}, Nombre: {hotel['nombre']}")

        # Solicitar al usuario que elija un hotel
        hotel_id = input("Ingrese el ID de un hotel para ver sus reservas: ")

        # Convertir fechas a formato de MongoDB
        fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")

        # Consultar reservas en MongoDB para el hotel seleccionado y el rango de fechas
        reservas = list(reservas_collection.find({
            "id_hotel": hotel_id,
            "fecha_reserva": {
                "$gte": fecha_inicio_obj,
                "$lte": fecha_fin_obj
            }
        }))

        # Mostrar las reservas si existen
        if reservas:
            print(f"\nReservas para el hotel ID {hotel_id} en el rango de fechas especificado:")
            for reserva in reservas:
                print("-----------------------------------------------------")
                print(f"Reserva ID: {reserva['_id']}")
                print(f"Fecha de reserva: {reserva['fecha_reserva']}")
                print(f"Huésped ID: {reserva['id_huesped']}")
                print(f"ID de habitación: {reserva['id_habitacion']}")
                print("-----------------------------------------------------")
        else:
            print("No se encontraron reservas para ese rango de fechas y hotel.")

    except Exception as e:
        print(f"Error al obtener las reservas por fecha en el hotel: {e}")



   
 #2 ALTA DE RESERVAS  
def habitaciones_disponibles1(fecha_inicio, fecha_fin):
    # Convertir fechas a objetos datetime
    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

    # Buscar reservas que coincidan o se solapen con el rango de fechas
    reservas = reservas_collection.find({
       "$or":[
            {"fecha_entrada": {"$gte": fecha_inicio, "$lte": fecha_fin}},
            {"fecha_salida": {"$gte": fecha_inicio, "$lte": fecha_fin}},
            {"$and":[
                {"fecha_entrada": {"$lte": fecha_inicio}},
                {"fecha_salida": {"$gte": fecha_fin}}
             ]}
        ]
    })

    # Extraer las habitaciones ocupadas de las reservas
    habitaciones_ocupadas = {reserva["id_habitacion"] for reserva in reservas}
    
    # Consultar en Neo4j las habitaciones que no están ocupadas
    query = """
        MATCH (h:Habitacion) 
        WHERE NOT h.id_habitacion IN $habitaciones_ocupadas
        RETURN h.id_habitacion AS id_habitacion
    """
    
    # Ejecutar la consulta y obtener las habitaciones disponibles
    result = graph.run(query, habitaciones_ocupadas=list(habitaciones_ocupadas))
    
    # Devolver las habitaciones disponibles como una lista de diccionarios
    return [record["id_habitacion"] for record in result]    
    
    
  

def crear_reserva_si_disponible(id_habitacion, id_huesped, fecha_entrada, fecha_salida, precio):
    try:
        # Verificar si la habitación está disponible en el rango de fechas
        habitaciones_libres = habitaciones_disponibles1(fecha_entrada, fecha_salida)

        # Comprobar si la habitación solicitada está en la lista de habitaciones disponibles
        if id_habitacion not in habitaciones_libres:
            return f"La habitación {id_habitacion} no está disponible entre {fecha_entrada} y {fecha_salida}."
        
        # Verificar si el huésped existe en Neo4j
        query_huesped = f"MATCH (h:Huesped {{id_huesped: '{id_huesped}'}}) RETURN h"
        result_huesped = graph.run(query_huesped).data()
        
        if not result_huesped:
            return f"No se encontró el huésped con ID: {id_huesped}"
        
        # Insertar la reserva en MongoDB si la habitación está disponible
        reserva = {
            "id_habitacion": id_habitacion,
            "id_huesped": id_huesped,
            "fecha_entrada": fecha_entrada,
            "fecha_salida": fecha_salida,
            "precio": precio
        }

        reservas_collection.insert_one(reserva)
        return f"Reserva creada exitosamente para la habitación {id_habitacion}."

    except Exception as e:
        return f"Error al crear la reserva: {e}"


