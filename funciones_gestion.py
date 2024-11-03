from py2neo import Graph
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from funciones_huesped import *
from funciones_hotel import *
from funciones_reserva import *
from funciones_habitacion import *

# --- Conexiones ---
graph = Graph("bolt://neo4j:12345678@localhost:7687")
client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_db']
reservas_collection = db['reservas']

def borrar_bd_reservas ():
    resultado = reservas_collection.delete_many({})
    print(f"Documentos eliminados: {resultado.deleted_count}")

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

# 1. Hoteles cerca de un POI
def hoteles_cerca_de_poi():
    # Consulta para obtener todos los POIs con al menos un hotel cercano y el conteo de hoteles cercanos
    query_pois = """
    MATCH (poi:POI)<-[:CERCA_DE]-(hotel:Hotel)
    RETURN poi.nombre AS poi_nombre, poi.detalle AS poi_detalle, COUNT(hotel) AS cantidad_hoteles
    """
    pois_result = graph.run(query_pois).data()

    # Listar los POIs disponibles y su cantidad de hoteles cercanos
    print("Lista de POIs disponibles con hoteles cercanos:")
    pois_disponibles = []
    for idx, record in enumerate (pois_result, start=1):
        poi_nombre = record['poi_nombre']
        poi_detalle = record['poi_detalle']
        cantidad_hoteles = record['cantidad_hoteles']
        pois_disponibles.append(poi_nombre)
        print(f"{idx}. {poi_nombre}, Detalle: {poi_detalle} --> Hoteles cercanos: {cantidad_hoteles}")

    # Solicitar al usuario que elija un POI por índice
    try:
        seleccion_idx = int(input("\nIngrese el número del POI para ver los hoteles cercanos: ")) - 1
        if seleccion_idx < 0 or seleccion_idx >= len(pois_disponibles):
            print("El número ingresado no es válido. Debe estar entre 1 y", len(pois_disponibles))
            return
        poi_nombre = pois_disponibles[seleccion_idx]  # Obtener el nombre del POI usando el índice
    except ValueError:
        print("Entrada inválida. Por favor, ingrese un número.")
        return
    
    # Consulta para obtener detalles de hoteles cercanos al POI seleccionado
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
        print(f"\nHoteles cercanos al POI '{poi_nombre}':")
        for hotel in hoteles_cercanos:
            print("-----------------------------------------------------")
            print(f"Hotel: {hotel[0]}\nDirección: {hotel[1]}")
            print("-----------------------------------------------------")
    else:
        print("No se encontraron hoteles cercanos a ese POI.")

# 4. Información de un hotel
def informacion_hotel():
    id_hotel = listar_hoteles_con_validacion()

    if not id_hotel:
        return
    # Consulta para obtener la información detallada del hotel seleccionado
    query = """
    MATCH (hotel:Hotel {id_hotel: $id_hotel})
    RETURN hotel.nombre AS nombre, hotel.direccion AS direccion, 
           hotel.telefono AS telefono, hotel.email AS email, 
           hotel.coordenadas AS coordenadas
    """
    result = graph.run(query, parameters={"id_hotel": id_hotel})

    # Mostrar la información detallada del hotel
    for record in result:
        hotel_nombre = record['nombre']
        hotel_direccion = record['direccion']
        hotel_telefono = record['telefono']
        hotel_email = record['email']
        hotel_coordenadas = record['coordenadas']

        print("-----------------------------------------------------")
        print(f"Detalles del hotel\nNombre: {hotel_nombre}\nDirección: {hotel_direccion}")
        print(f"Teléfono: {hotel_telefono}\nEmail: {hotel_email}\nCoordenadas: {hotel_coordenadas}")
        print("-----------------------------------------------------")


# 3. POIs cerca de un hotel
def pois_cerca_de_hotel():
    # Consulta para obtener todos los hoteles con al menos un POI cercano y el conteo de POIs
    query_hoteles = """
    MATCH (hotel:Hotel)-[:CERCA_DE]->(poi:POI)
    RETURN hotel.nombre AS hotel_nombre, hotel.direccion AS hotel_direccion, COUNT(poi) AS cantidad_pois
    """
    hoteles_result = graph.run(query_hoteles).data()

    # Listar los hoteles disponibles con POIs cercanos y la cantidad de POIs
    print("Lista de hoteles con POIs cercanos:")
    hoteles_disponibles = []
    for idx, record in enumerate (hoteles_result, start=1):
        hotel_nombre = record['hotel_nombre']
        hotel_direccion = record['hotel_direccion']
        cantidad_pois = record['cantidad_pois']
        hoteles_disponibles.append(hotel_nombre)
        print(f"{idx}. {hotel_nombre}, Dirección: {hotel_direccion}, POIs cercanos: {cantidad_pois}")

    # Solicitar al usuario que elija un POI por índice
    try:
        seleccion_idx = int(input("\nIngrese el número del Hotel para ver los POI´s cercanos: ")) - 1
        if seleccion_idx < 0 or seleccion_idx >= len(hoteles_disponibles):
            print("El número ingresado no es válido. Debe estar entre 1 y", len(hoteles_disponibles))
            return
        hotel_nombre = hoteles_disponibles[seleccion_idx]  # Obtener el nombre del POI usando el índice
        print(hotel_nombre)
    except ValueError:
        print("Entrada inválida. Por favor, ingrese un número.")
        return

    # Consulta para obtener los detalles de los POIs cercanos al hotel seleccionado
    query_pois = """
    MATCH (hotel:Hotel {nombre: $hotel_nombre})-[:CERCA_DE]->(poi:POI)
    RETURN poi.nombre AS nombre, poi.detalle AS detalle, poi.tipo AS tipo
    """
    result = graph.run(query_pois, parameters={"hotel_nombre": hotel_nombre})

    # Mostrar la información de los POIs cercanos al hotel seleccionado
    print(f"\nPOIs cercanos al hotel '{hotel_nombre}':")
    for record in result:
        poi_nombre = record['nombre']
        poi_detalle = record['detalle']
        poi_tipo = record['tipo']

        print("-----------------------------------------------------")
        print(f"Nombre: {poi_nombre}\nDetalle: {poi_detalle}\nTipo: {poi_tipo}")
        print("-----------------------------------------------------")


# 6. Habitaciones disponibles en un rango de fechas
# Función para obtener habitaciones disponibles en un hotel para un rango de fechas

# 8. Reservas por número de confirmación (ID en MongoDB)

class ReservaIdError(Exception):
    """Excepción personalizada para errores en el ID de reserva."""
    pass

def validar_reserva_id(reserva_id):
    if len(reserva_id) != 24:
        raise ReservaIdError("El número de confirmación debe tener exactamente 24 caracteres.")

def reservas_por_numero_confirmacion():
    print("Lista de huéspedes disponibles:")
    mostrar_reservas_con_numero_confirmacion()

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
from datetime import datetime

def reservas_por_fecha_en_hotel(fecha_inicio, fecha_fin):
    try:
        hotel_id = listar_hoteles_con_validacion()

        if not hotel_id:
            return

        # Convertir fechas a formato de MongoDB
        fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")

        # Consultar reservas en MongoDB en el rango de fechas
        reservas = list(reservas_collection.find({
            "fecha_entrada": {"$gte": fecha_inicio},
            "fecha_salida": {"$lte": fecha_fin}
        }))

        # Filtrar reservas que pertenecen al hotel específico
        reservas_filtradas = []
        for reserva in reservas:
            id_habitacion = reserva["id_habitacion"]

            # Consultar en Neo4j para obtener el hotel de la habitación
            query_hotel_habitacion = """
            MATCH (hotel:Hotel)-[:TIENE]->(habitacion:Habitacion {id_habitacion: $id_habitacion})
            RETURN hotel.id_hotel AS id_hotel
            """
            resultado_hotel = graph.run(query_hotel_habitacion, id_habitacion=id_habitacion).data()

            # Verificar si el hotel coincide con el seleccionado
            if resultado_hotel and resultado_hotel[0].get("id_hotel") == hotel_id:
                reservas_filtradas.append(reserva)

        # Mostrar las reservas del hotel seleccionado en el rango de fechas
        if reservas_filtradas:
            print(f"\nReservas para el hotel ID {hotel_id} en el rango de fechas especificado:")
            for reserva in reservas_filtradas:
                print("-----------------------------------------------------")
                print(f"Reserva ID: {reserva['_id']}")
                print(f"Fecha de entrada: {reserva['fecha_entrada']}")
                print(f"Fecha de salida: {reserva['fecha_salida']}")
                print(f"Huésped ID: {reserva['id_huesped']}")
                print(f"ID de habitación: {reserva['id_habitacion']}")
                print(f"Precio : {reserva['precio']}")
                print("-----------------------------------------------------")
        else:
            print("No se encontraron reservas para ese rango de fechas y hotel.")

    except Exception as e:
        print(f"Error al obtener las reservas por fecha en el hotel: {e}")
   
 
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
    

def listar_hoteles():
    """Función para listar todos los hoteles disponibles con su ID y nombre."""
    query_hoteles = """
    MATCH (h:Hotel)
    RETURN h.id_hotel AS id_hotel, h.nombre AS nombre
    """
    return graph.run(query_hoteles).data()





