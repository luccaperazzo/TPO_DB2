from py2neo import Graph, Node
from funciones_gestion import *
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# Conexion BD Neo4J
graph = Graph("bolt://neo4j:12345678@localhost:7687")
client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_db']
reservas_collection = db['reservas']

def mostrar_reservas_con_numero_confirmacion():
    try:
        # Obtener todas las reservas y su número de confirmación
        reservas = list(reservas_collection.find({}, {"_id": 1, "id_huesped": 1, "fecha_entrada": 1, "fecha_salida": 1, "id_habitacion": 1}))

        # Verificar si existen reservas
        if not reservas:
            print("No hay reservas disponibles.")
            return

        # Mostrar la información de cada reserva
        print("Lista de reservas y sus números de confirmación:")
        for reserva in reservas:
            numero_confirmacion = reserva["_id"]
            id_huesped = reserva["id_huesped"]
            print(f"Reserva ID (Número de confirmación): {numero_confirmacion}, Huésped ID: {id_huesped}")
            print("-----------------------------------------------------")

    except Exception as e:
        print(f"Error al obtener las reservas con número de confirmación: {e}")




# Funciones Huesped
def alta_huesped(nombre, apellido, direccion, telefono, email):
    try:
        # Encuentra el ID más alto de los huéspedes actuales
        query = "MATCH (h:Huesped) RETURN coalesce(max(toInteger(h.id_huesped)), 0) AS max_id"
        result = graph.run(query).data()
        
        # Obtener el ID más alto
        max_id = result[0]["max_id"] if result else 0
        nuevo_id = max_id + 1

        # Crear el nuevo huésped con el nuevo ID
        graph.create(Node("Huesped", id_huesped=str(nuevo_id), nombre=nombre, apellido=apellido, direccion=direccion, telefono=telefono, email=email))
        print( f"Huésped creado exitosamente con ID: {nuevo_id}")

    except Exception as e:
        return f"Error al crear el huésped: {e}"
    
def modificar_huesped():
    try:
        get_huespedes()
        # Pedir el ID del huésped por input
        id_huesped = input("Ingrese el ID del huésped que desea modificar: ")
        
        # Verificar si el ID del huésped existe
        query_verificar = "MATCH (h:Huesped {id_huesped: $id_huesped}) RETURN h"
        resultado = graph.run(query_verificar, id_huesped=id_huesped).data()
        
        if not resultado:
            print(f"Error: No se encontró ningún huésped con el ID {id_huesped}.")
            return
        
        # Solicitar los campos a modificar
        nombre = input("Ingrese el nuevo nombre (deje vacío si no desea cambiarlo): ") or None
        apellido = input("Ingrese el nuevo apellido (deje vacío si no desea cambiarlo): ") or None
        direccion = input("Ingrese la nueva dirección (deje vacío si no desea cambiarla): ") or None
        telefono = input("Ingrese el nuevo teléfono (deje vacío si no desea cambiarlo): ") or None
        email = input("Ingrese el nuevo email (deje vacío si no desea cambiarlo): ") or None

        # Actualizar solo los campos que no son None
        update_fields = []
        if nombre:
            update_fields.append(f"h.nombre = '{nombre}'")
        if apellido:
            update_fields.append(f"h.apellido = '{apellido}'")
        if direccion:
            update_fields.append(f"h.direccion = '{direccion}'")
        if telefono:
            update_fields.append(f"h.telefono = '{telefono}'")
        if email:
            update_fields.append(f"h.email = '{email}'")
        
        if not update_fields:
            print("No se proporcionó ningún campo para modificar.")
            return
        
        query_modificar = f"""
            MATCH (h:Huesped {{id_huesped: $id_huesped}})
            SET {', '.join(update_fields)}
        """
        graph.run(query_modificar, id_huesped=id_huesped)
        print(f"Huésped con ID {id_huesped} modificado exitosamente.")
    
    except Exception as e:
        print(f"Error al modificar el huésped: {e}")


## Consultas 
def ver_detalles_huesped():
    try:
        # Mostrar la lista de huéspedes disponibles
        print("Lista de huéspedes disponibles:")
        get_huespedes()

        # Solicitar el ID del huésped
        id_huesped = input("Introduce el ID del huésped que deseas ver: ")

        # Consulta para buscar el huésped por ID
        query = """
        MATCH (huesped:Huesped {id_huesped: $id_huesped})
        RETURN huesped
        """
        result = graph.run(query, parameters={"id_huesped": id_huesped}).data()

        # Mostrar los detalles del huésped si se encuentra
        if result:
            for record in result:
                huesped = record['huesped']
                print("-----------------------------------------------------")
                print(f"Detalles del huésped:\nID: {huesped['id_huesped']}\nNombre: {huesped['nombre']}\nApellido: {huesped['apellido']}\nDirección: {huesped['direccion']}\nTeléfono: {huesped['telefono']}\nEmail: {huesped['email']}")
                print("-----------------------------------------------------")
        else:
            print(f"No se encontraron huéspedes con el ID '{id_huesped}'.")

    except Exception as e:
        print(f"Error al obtener los detalles del huésped: {e}")


def reservas_por_huesped():
    # Listar todos los huéspedes
    print("Lista de huéspedes disponibles:")
    get_huespedes()  # Asegúrate de que esta función imprima los huéspedes y sus IDs

    # Solicitar al usuario que ingrese el ID del huésped
    id_huesped = input("Introduce el ID del huésped para ver sus reservas: ")

    # Consultar reservas para el huésped específico
    reservas = list(reservas_collection.find({"id_huesped": id_huesped}))

    if reservas:
        for reserva in reservas:
            print("-----------------------------------------------------")
            print(f"Reserva ID: {reserva['_id']}\nFecha de entrada: {reserva['fecha_entrada']}\nFecha de salida: {reserva['fecha_salida']}\nID de habitación: {reserva['id_habitacion']}")
            print("-----------------------------------------------------")
    else:
        print("No se encontraron reservas para este huésped.")


def get_huespedes():
    try:
        # Consulta para obtener los nombres y apellidos de todos los huéspedes
        query = """
        MATCH (h:Huesped)
        RETURN h.nombre AS nombre, h.apellido AS apellido,h.id_huesped as id_huesped
        """
        result = graph.run(query).data()

        # Mostrar los nombres y apellidos
        if result:
            for record in result:
                nombre = record['nombre']
                apellido = record['apellido']
                id_huesped = record['id_huesped']
                print(f"Nombre: {nombre}, Apellido: {apellido}, ID : {id_huesped}")
        else:
            print("No se encontraron huéspedes en la base de datos.")

    except Exception as e:
        print(f"Error al obtener los huéspedes: {e}")
