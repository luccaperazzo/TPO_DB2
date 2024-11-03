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
        print("Amenity creado en la base de datos.")
        return f"Amenity '{nombre}' creado exitosamente."
    except Exception as e:
        print(f"Excepción encontrada: {e}")
        return f"Error al crear el amenity: {e}"



def traer_amenitys():
    try:
        # Obtener todos los amenities con sus IDs
        query = "MATCH (a:Amenity) RETURN a.id_amenity AS id, a.nombre AS nombre"
        result = graph.run(query).data()

        # Mostrar los IDs y nombres de las amenidades
        if result:
            return result
        else:
            print("No hay amenitys disponibles en la base de datos.")
        
    except Exception as e:
        print(f"Error al obtener las amenidades: {e}")


def baja_amenity():
    try:
        id_amenity = listar_amenitys_con_validacion ()
        if not id_amenity:
            return
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
            
            
    except Exception as e:
        print(f"Error al intentar eliminar el amenity: {e}")

    
def modificar_amenity():
    try:

        id_amenity = listar_amenitys_con_validacion()
        if not id_amenity:
            return
        while True:  # Repetir hasta que se ingrese un nombre válido
            # Solicitar el nuevo nombre para la amenidad
            nuevo_nombre = input("Ingrese el nuevo nombre para la amenidad: ").strip()  # Strip para eliminar espacios

            # Validar que el nuevo nombre no esté vacío
            if not nuevo_nombre:
                print("El nombre de la amenidad no puede estar vacío. Intente nuevamente.")
            else:
                break  # Salir del bucle si se ingresó un nombre válido

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

    except Exception as e:
        print(f"Error al intentar modificar el amenity: {e}")


def listar_amenitys_con_validacion():
    try:
        query = "MATCH (a:Amenity) RETURN a.id_amenity, a.nombre ORDER BY a.nombre"
        result = graph.run(query)
        amenitys = result.data()  # Devuelve una lista de diccionarios con los Amenitys
        
        if not amenitys:
            print("No hay amenitys disponibles.")
            return None
        intentos= 0
        while intentos<2:
            print("Seleccione el amenity:")
            for idx, amenity in enumerate(amenitys, start=1):
                print(f"{idx}. {amenity['a.nombre']} ")
        
            seleccion = int(input("Ingrese el número del amenity: "))
            if 1 <= seleccion <= len(amenitys):
                return amenitys[seleccion - 1]['a.id_amenity']  # Retorna el id del amenity seleccionado
            else:
                print("Selección inválida.Intente nuevamente.")
                intentos +=1
        if intentos ==2:
            print("Demasiados intentos fallidos. Volviendo al menú principal.")
            return None
    except Exception as e:
        print(f"Error al listar los amenitys: {e}")
        return None