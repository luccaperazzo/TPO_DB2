from py2neo import Graph, Node
from funciones_gestion import *
from geopy.geocoders import Nominatim

#cambio lucca
# Conexion BD Neo4J
graph = Graph("bolt://neo4j:12345678@localhost:7687")
geolocator = Nominatim(user_agent="geoapi")

def obtener_coordenadas(direccion):
    # Agrega "Capital Federal, Argentina" a la dirección
    direccion_completa = f"{direccion}, Capital Federal, Argentina"
    try:
        location = geolocator.geocode(direccion_completa)
        if location:
            return (location.latitude, location.longitude)
        else:
            print("No se encontraron coordenadas para la dirección proporcionada.")
            return None
    except Exception as e:
        print(f"Error al obtener coordenadas: {e}")
        return None

def alta_poi(nombre, detalle, direccion, tipo):
    try:
        # Encuentra el ID más alto de los POI actuales
        query = "MATCH (p:POI) RETURN coalesce(max(toInteger(p.id_poi)), 0) AS max_id"
        result = graph.run(query).data()
        
        # Obtener el ID más alto
        max_id = result[0]["max_id"] if result else 0
        nuevo_id = max_id + 1

        id_poi= nuevo_id

        latitude, longitude = obtener_coordenadas(direccion)
        if latitude is None or longitude is None:
            return f"No se pudieron obtener las coordenadas para la dirección: {direccion}"
        
        query = """
            CREATE (:POI {id_poi: $id_poi, nombre: $nombre, direccion: $direccion, detalle: $detalle, 
            latitude: $latitude, longitude: $longitude , tipo: $tipo})
        """
        graph.run(query, id_poi=id_poi, nombre=nombre, direccion=direccion, detalle=detalle, latitude=latitude, longitude=longitude, tipo=tipo)
       
        subquery="""
        MATCH (p:POI{id_poi: $id_poi}), (h:Hotel)
        WHERE point.distance(point({latitude: p.latitude, longitude: p.longitude}), point({latitude: h.latitude, longitude: h.longitude})) < 1000
        CREATE (h) - [:CERCA_DE {distancia: point.distance(point({latitude: p.latitude, longitude: p.longitude}),
        point({latitude: h.latitude, longitude: h.longitude})) }] -> (p)"""

        graph.run(subquery, id_poi=id_poi)

        return f"POI '{nombre}' creado exitosamente."
    except Exception as e:
        return f"Error al crear el POI: {e}"
    
def baja_poi(id_poi):
    try:
        query = """
            MATCH (poi:POI {id_poi: $id_poi})
            DETACH DELETE poi
        """
        graph.run(query, id_poi=id_poi)
        return f"POI con ID {id_poi} eliminado exitosamente."
    except Exception as e:
        return f"Error al eliminar el POI: {e}"
    
def modificar_poi(id_poi, nombre=None, detalle=None, direccion=None, tipo=None):
    try:
        # Actualizar solo los campos que no son None
        update_fields = []
        if nombre:
            update_fields.append(f"poi.nombre = '{nombre}'")
        if detalle:
            update_fields.append(f"poi.detalle = '{detalle}'")
        if direccion:
            update_fields.append(f"poi.direccion = '{direccion}'")
            latitude,longitude = obtener_coordenadas(direccion)
            update_fields.append(f"poi.latitude = {latitude}")
            update_fields.append(f"poi.longitude = {longitude}")
            
        if tipo:
            update_fields.append(f"poi.tipo = '{tipo}'")
        
        if not update_fields:
            return "No se proporcionó ningún campo para modificar."
        
        query = f"""
            MATCH (poi:POI {{id_poi: $id_poi}})
            SET {', '.join(update_fields)}
        """
        graph.run(query, id_poi=id_poi)

        if direccion:
            delete_query = """
                MATCH (h:Hotel)-[r:CERCA_DE]->(p:POI {id_poi: $id_poi})
                DELETE r
            """
            graph.run(delete_query, id_poi=id_poi)

            create_query = """
                MATCH (h:Hotel), (p:POI{id_poi: $id_poi})
                WHERE point.distance(point({latitude: h.latitude, longitude: h.longitude}), point({latitude: p.latitude, longitude: p.longitude})) < 1000
                CREATE (h)-[:CERCA_DE {distancia: point.distance(point({latitude: h.latitude, longitude: h.longitude}), point({latitude: p.latitude, longitude: p.longitude}))}]->(p)
            """
            graph.run(create_query, id_poi=id_poi)

        return f"POI con ID {id_poi} modificado exitosamente."
    except Exception as e:
        return f"Error al modificar el POI: {e}"
    

def listar_pois():
    try:
        query = "MATCH (p:POI) RETURN p.id_poi, p.nombre ORDER BY p.nombre"
        result = graph.run(query)
        pois = result.data()  # Devuelve una lista de diccionarios con los hoteles
        if not pois:
            print("No hay pois disponibles para modificar.")
            return None
        
        print("Seleccione el punto de interes a modificar:")
        for idx, poi in enumerate (pois, start=1):
            print(f"{idx}. {poi['p.nombre']} ")
        
        seleccion = int(input("Ingrese el número del punto de interes que desea modificar: "))
        if 1 <= seleccion <= len(pois):
            return pois[seleccion - 1]['p.id_poi']  # Retorna el id del hotel seleccionado
        else:
            print("Selección inválida.")
            return None
    except Exception as e:
        print(f"Error al listar los hoteles: {e}")
        return None
    