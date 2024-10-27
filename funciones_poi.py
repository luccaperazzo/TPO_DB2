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

def alta_poi(id_poi, nombre, detalle, direccion, tipo):
    try:

        latitude, longitude = obtener_coordenadas(direccion)
        if latitude is None or longitude is None:
            return f"No se pudieron obtener las coordenadas para la dirección: {direccion}"
        
        query = """
            CREATE (:POI {id_poi: $id_poi, nombre: $nombre, detalle: $detalle, 
            latitude: $latitude, longitude: $longitude , tipo: $tipo})
        """
        graph.run(query, id_poi=id_poi, nombre=nombre, detalle=detalle, latitude=latitude, longitude=longitude, tipo=tipo)
       
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
        if coordenadas:
            update_fields.append(f"poi.direccion = '{direccion}'")
        if tipo:
            update_fields.append(f"poi.tipo = '{tipo}'")
        
        if not update_fields:
            return "No se proporcionó ningún campo para modificar."
        
        query = f"""
            MATCH (poi:POI {{id_poi: $id_poi}})
            SET {', '.join(update_fields)}
        """
        graph.run(query, id_poi=id_poi)
        return f"POI con ID {id_poi} modificado exitosamente."
    except Exception as e:
        return f"Error al modificar el POI: {e}"