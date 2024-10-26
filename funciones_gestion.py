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

    
def alta_amenity(id_amenity, nombre):
    try:
        query = """
            CREATE (:Amenity {id_amenity: $id_amenity, nombre: $nombre})
        """
        graph.run(query, id_amenity=id_amenity, nombre=nombre)
        return f"Amenity '{nombre}' creado exitosamente."
    except Exception as e:
        return f"Error al crear el amenity: {e}"

def baja_amenity(id_amenity):
    try:
        query = """
            MATCH (a:Amenity {id_amenity: $id_amenity})
            DETACH DELETE a
        """
        graph.run(query, id_amenity=id_amenity)
        return f"Amenity con ID {id_amenity} eliminado exitosamente."
    except Exception as e:
        return f"Error al eliminar el amenity: {e}"
    
def modificar_amenity(id_amenity, nombre=None):
    try:
        if nombre:
            query = """
                MATCH (a:Amenity {id_amenity: $id_amenity})
                SET a.nombre = $nombre
            """
            graph.run(query, id_amenity=id_amenity, nombre=nombre)
        return f"Amenity con ID {id_amenity} modificado exitosamente."
    except Exception as e:
        return f"Error al modificar el amenity: {e}"
    
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
def hoteles_cerca_de_poi(poi_nombre):
    query = """
    MATCH (poi:POI {nombre: $poi_nombre})<-[:CERCA_DE]-(hotel:Hotel)
    RETURN hotel.nombre, hotel.direccion
    """
    result = graph.run(query, parameters={"poi_nombre": poi_nombre})
    return result.data()


# 4. Información de un hotel
def informacion_hotel(hotel_nombre):
    query = """
    MATCH (hotel:Hotel {nombre: $hotel_nombre})
    RETURN hotel.nombre, hotel.direccion, hotel.telefono, hotel.email, hotel.coordenadas
    """
    result = graph.run(query, parameters={"hotel_nombre": hotel_nombre})
    return result.data()


# 5. POIs cerca de un hotel
def pois_cerca_de_hotel(hotel_nombre):
    query = """
    MATCH (hotel:Hotel {nombre: $hotel_nombre})-[:CERCA_DE]->(poi:POI)
    RETURN poi.nombre, poi.detalle, poi.tipo
    """
    result = graph.run(query, parameters={"hotel_nombre": hotel_nombre})
    return result.data()


# 6. Habitaciones disponibles en un rango de fechas
def habitaciones_disponibles(fecha_inicio, fecha_fin, id_hotel):
    # Convertir fechas a objetos datetime
    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

    # Obtener reservas que interfieren con el rango de fechas solicitado
    reservas = reservas_collection.find({
        "$or": [
            {"fecha_entrada": {"$gte": fecha_inicio.strftime("%Y-%m-%d"), "$lte": fecha_fin.strftime("%Y-%m-%d")}},
            {"fecha_salida": {"$gte": fecha_inicio.strftime("%Y-%m-%d"), "$lte": fecha_fin.strftime("%Y-%m-%d")}},
            {"$and": [
                {"fecha_entrada": {"$lte": fecha_inicio.strftime("%Y-%m-%d")}},
                {"fecha_salida": {"$gte": fecha_fin.strftime("%Y-%m-%d")}}
            ]}
        ]
    })

    # Obtener IDs de habitaciones ocupadas
    habitaciones_ocupadas = {reserva["id_habitacion"] for reserva in reservas}
    
    # Consultar habitaciones disponibles junto con sus hoteles
    query = """
        MATCH (h:Hotel)-[:TIENE]->(hab:Habitacion) 
        WHERE NOT hab.id_habitacion IN $habitaciones_ocupadas AND h.id_hotel = $id_hotel
        RETURN h.nombre AS hotel, hab.id_habitacion AS habitacion
    """
    
    # Ejecutar la consulta
    result = graph.run(query, habitaciones_ocupadas=list(habitaciones_ocupadas), id_hotel=id_hotel)

    # Retornar los resultados como una lista de tuplas
    return [(record["hotel"], record["habitacion"]) for record in result.data()]




# 7. Amenities de una habitación
def amenities_habitacion(id_habitacion):
    query = """
    MATCH (habitacion:Habitacion {id_habitacion: $id_habitacion})-[:TIENE_AMENITY]->(amenity:Amenity)
    RETURN amenity.nombre
    """
    result = graph.run(query, parameters={"id_habitacion": id_habitacion})
    return result.data()


# 8. Reservas por número de confirmación (ID en MongoDB)
def reservas_por_numero_confirmacion(reserva_id):
    reserva = reservas_collection.find_one({"_id": ObjectId(reserva_id)})
    return reserva if reserva else None





# 10. Traer las reservas por fecha de reserva en el hotel.
def reservas_por_fecha_en_hotel(hotel_id, fecha_inicio, fecha_fin):
    try:
       fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
       fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")

       query = """
       MATCH (hotel:Hotel {id_hotel: $hotel_id})-[:TIENE]->(habitacion:Habitacion)
       WITH habitacion
       MATCH (reserva:Reserva)
       WHERE reserva.id_habitacion = habitacion.id_habitacion AND reserva.fecha_reserva >= $fecha_inicio AND reserva.fecha_reserva <= $fecha_fin

       RETURN reserva
       """


       reservas = graph.run(query, hotel_id=hotel_id, fecha_inicio=fecha_inicio, fecha_fin = fecha_fin).data()
       return reservas


    except Exception as e:
      return f"Error al obtener las reservas por fecha en el hotel: {e}"


   
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


