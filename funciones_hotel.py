from py2neo import Graph, Node
from funciones_gestion import *
#cambio lucca
# Conexion BD Neo4J
graph = Graph("bolt://neo4j:12345678@localhost:7687")


def alta_hotel(nombre, direccion, telefono, email, coordenadas):
    try:
        # Encuentra el ID más alto de los huéspedes actuales
        query = "MATCH (h:Hotel) RETURN coalesce(max(toInteger(h.id_hotel)), 0) AS max_id"
        result = graph.run(query).data()
        
        # Obtener el ID más alto
        max_id = result[0]["max_id"] if result else 0
        nuevo_id = max_id + 1
        
        # Crear el nuevo hotel
        query = """
            CREATE (:Hotel {id_hotel: $id_hotel, nombre: $nombre, direccion: $direccion, 
            telefono: $telefono, email: $email, coordenadas: $coordenadas})
        """
        graph.run(query, id_hotel=nuevo_id, nombre=nombre, direccion=direccion, 
                  telefono=telefono, email=email, coordenadas=coordenadas)
        return f"Hotel '{nombre}' creado exitosamente."
    except Exception as e:
        return f"Error al crear el hotel: {e}"
    
    
def baja_hotel(id_hotel):
    try:
        # Eliminar el hotel y todas sus relaciones
        query = """
            MATCH (h:Hotel {id_hotel: $id_hotel}) 
            DETACH DELETE h
        """
        graph.run(query, id_hotel=id_hotel)
        return f"Hotel con ID {id_hotel} eliminado exitosamente."
    except Exception as e:
        return f"Error al eliminar el hotel: {e}"
    
    
    
def modificar_hotel(id_hotel, nombre=None, direccion=None, telefono=None, email=None, coordenadas=None):
    try:
        # Actualizar solo los campos que no son None
        update_fields = []
        if nombre:
            update_fields.append(f"h.nombre = '{nombre}'")
        if direccion:
            update_fields.append(f"h.direccion = '{direccion}'")
        if telefono:
            update_fields.append(f"h.telefono = '{telefono}'")
        if email:
            update_fields.append(f"h.email = '{email}'")
        if coordenadas:
            update_fields.append(f"h.coordenadas = '{coordenadas}'")
        
        if not update_fields:
            return "No se proporcionó ningún campo para modificar."
        
        query = f"""
            MATCH (h:Hotel {{id_hotel: $id_hotel}})
            SET {', '.join(update_fields)}
        """
        graph.run(query, id_hotel=id_hotel)
        return f"Hotel con ID {id_hotel} modificado exitosamente."
    except Exception as e:
        return f"Error al modificar el hotel: {e}"