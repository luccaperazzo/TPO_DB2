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
        return f"Huésped creado exitosamente con ID: {nuevo_id}"

    except Exception as e:
        return f"Error al crear el huésped: {e}"
    
def modificar_huesped():
    try:
        id_huesped= listar_huespedes_con_validacion()
        if not id_huesped:
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

#Baja huesped
def baja_huesped():
    try:
        id_huesped = listar_huespedes_con_validacion()
        if id_huesped:
            query = """
                MATCH (h:Huesped {id_huesped: $id_huesped}) 
                DETACH DELETE h
            """
            graph.run(query, id_huesped=id_huesped)
            print ( f"Huesped con ID {id_huesped} eliminado exitosamente.")
    except Exception as e:
        print('Error al eliminar el huesped')
        return f"Error al eliminar el huesped: {e}"

## Consultas 
def ver_detalles_huesped():
    try:
        id_huesped= listar_huespedes_con_validacion()
        if not id_huesped:
            return
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
    id_huesped= int(listar_huespedes_con_validacion())
    print(id_huesped)
    if not id_huesped:
        return
    # Consultar reservas para el huésped específico
    reservas = list(reservas_collection.find({"id_huesped": id_huesped}))

    if reservas:
        for reserva in reservas:
            print("-----------------------------------------------------")
            print(f"Reserva ID: {reserva['_id']}\nFecha de entrada: {reserva['fecha_entrada']}\nFecha de salida: {reserva['fecha_salida']}\nID de habitación: {reserva['id_habitacion']}")
            print("-----------------------------------------------------")
    else:
        print("No se encontraron reservas para este huésped.")



def listar_huespedes_con_validacion():
    try:
        query = "MATCH (h:Huesped) RETURN h.id_huesped, h.nombre ORDER BY h.nombre"
        result = graph.run(query)
        huespedes = result.data()  # Devuelve una lista de diccionarios con los huespedes
        
        if not huespedes:
            print("No hay huespedes disponibles.")
            return None
        intentos= 0
        while intentos<2:
            print("Seleccione el huesped:")
            for idx, huesped in enumerate(huespedes, start=1):
                print(f"{idx}. {huesped['h.nombre']} ")
        
            seleccion = int(input("Ingrese el número del huesped: "))
            if 1 <= seleccion <= len(huespedes):
                return huespedes[seleccion - 1]['h.id_huesped']  # Retorna el id del huesped seleccionado
            else:
                print("Selección inválida.Intente nuevamente.")
                intentos +=1
        if intentos ==2:
            print("Demasiados intentos fallidos. Volviendo al menú principal.")
            return None
    except Exception as e:
        print(f"Error al listar los huespedes: {e}")
        return None
