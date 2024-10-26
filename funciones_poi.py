from py2neo import Graph, Node
from funciones_gestion import *
#cambio lucca
# Conexion BD Neo4J
graph = Graph("bolt://neo4j:12345678@localhost:7687")

def alta_poi(id_poi, nombre, detalle, coordenadas, tipo):
    try:
        query = """
            CREATE (:POI {id_poi: $id_poi, nombre: $nombre, detalle: $detalle, 
            coordenadas: $coordenadas, tipo: $tipo})
        """
        graph.run(query, id_poi=id_poi, nombre=nombre, detalle=detalle, coordenadas=coordenadas, tipo=tipo)
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
    
def modificar_poi(id_poi, nombre=None, detalle=None, coordenadas=None, tipo=None):
    try:
        # Actualizar solo los campos que no son None
        update_fields = []
        if nombre:
            update_fields.append(f"poi.nombre = '{nombre}'")
        if detalle:
            update_fields.append(f"poi.detalle = '{detalle}'")
        if coordenadas:
            update_fields.append(f"poi.coordenadas = '{coordenadas}'")
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