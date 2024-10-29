from py2neo import Graph, Node
from funciones_gestion import *
from pymongo import MongoClient

graph = Graph("bolt://neo4j:12345678@localhost:7687")

def alta_amenity(nombre):
    try:
        # Encuentra el ID más alto de los Amenity actuales
        query = "MATCH (a:Amenity) RETURN coalesce(max(toInteger(a.id_amenity)), 0) AS max_id"
        result = graph.run(query).data()
        
        # Obtener el ID más alto
        max_id = result[0]["max_id"] if result else 0
        nuevo_id = max_id + 1

        # Crear el nuevo Amenity con el ID correcto
        query = """
            CREATE (:Amenity {id_amenity: $id_amenity, nombre: $nombre})
        """
        graph.run(query, id_amenity=str(nuevo_id), nombre=nombre)
        return f"Amenity '{nombre}' creado exitosamente."
    except Exception as e:
        return f"Error al crear el amenity: {e}"



def mostrar_amenitys():
    # Obtener todos los amenities con sus IDs
    query = "MATCH (a:Amenity) RETURN a.id_amenity AS id, a.nombre AS nombre"
    result = graph.run(query).data()
    
    return result

def baja_amenity():
    try:
        while True:
            # Mostrar las amenidades actuales
            amenitys = mostrar_amenitys()
            if not amenitys:
                print("No hay amenidades disponibles para eliminar.")
                return
            
            # Solicitar el ID de la amenidad a eliminar
            id_amenity = input("Ingrese el ID de la amenidad que desea eliminar: ")
            
            # Verificar si el ID ingresado existe en la lista de amenidades
            if not any(amenity["id"] == id_amenity for amenity in amenitys):
                print(f"El ID {id_amenity} no existe. Por favor, seleccione un ID válido.")
                continue  # Repetir el bucle para solicitar un ID válido
            
            # Intentar eliminar la amenidad
            query = """
                MATCH (a:Amenity {id_amenity: $id_amenity})
                DETACH DELETE a
            """
            graph.run(query, id_amenity=id_amenity)
            
            # Verificar si la amenidad todavía existe
            verificar_query = """
                MATCH (a:Amenity {id_amenity: $id_amenity}) RETURN a
            """
            result = graph.run(verificar_query, id_amenity=id_amenity).data()
            
            # Confirmación o aviso según la existencia del nodo
            if result:
                print(f"No se puede eliminar el amenity con ID {id_amenity} porque está asociado a una habitación.")
            else:
                print(f"Amenity con ID {id_amenity} eliminado exitosamente.")
            break  # Salir del bucle después de una operación exitosa o fallida
            
    except Exception as e:
        print(f"Error al intentar eliminar el amenity: {e}")

    
def modificar_amenity():
    try:
        while True:
            # Mostrar las amenidades actuales
            amenitys = mostrar_amenitys()
            if not amenitys:
                print("No hay amenidades disponibles para modificar.")
                return
            
            # Solicitar el ID de la amenidad a modificar
            id_amenity = input("Ingrese el ID de la amenidad que desea modificar: ")

            # Verificar si el ID ingresado existe en la lista de amenidades
            if not any(amenity["id"] == id_amenity for amenity in amenitys):
                print(f"El ID {id_amenity} no existe. Por favor, seleccione un ID válido.")
                continue  # Repetir el bucle para solicitar un ID válido
            
            # Solicitar el nuevo nombre para la amenidad
            nuevo_nombre = input("Ingrese el nuevo nombre para la amenidad: ")

            # Modificar el nombre de la amenidad
            query = """
                MATCH (a:Amenity {id_amenity: $id_amenity})
                SET a.nombre = $nombre
            """
            graph.run(query, id_amenity=id_amenity, nombre=nuevo_nombre)
            
            # Verificar si la modificación se realizó correctamente
            verificar_query = """
                MATCH (a:Amenity {id_amenity: $id_amenity}) RETURN a.nombre AS nombre
            """
            result = graph.run(verificar_query, id_amenity=id_amenity).data()

            # Confirmación de modificación
            if result and result[0]["nombre"] == nuevo_nombre:
                print(f"Amenity con ID {id_amenity} modificado exitosamente. Nuevo nombre: {nuevo_nombre}")
            else:
                print(f"No se pudo modificar el amenity con ID {id_amenity}. Intente nuevamente.")
            break  # Salir del bucle después de una modificación exitosa o fallida

    except Exception as e:
        print(f"Error al intentar modificar el amenity: {e}")
