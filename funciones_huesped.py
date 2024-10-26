from py2neo import Graph, Node
from funciones_gestion import *


# Conexion BD Neo4J
graph = Graph("bolt://neo4j:12345678@localhost:7687")

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
## Consultas 
def ver_detalles_huesped():
    try:
        # Mostrar los huéspedes disponibles
        print("Lista de huéspedes disponibles:")
        get_huespedes()

        # Solicitar el apellido del huésped
        apellido = input("Introduce el apellido del huésped que deseas ver: ")

        # Consulta para buscar el huésped por apellido
        query = """
        MATCH (huesped:Huesped {apellido: $apellido})
        RETURN huesped
        """
        result = graph.run(query, parameters={"apellido": apellido}).data()

        # Mostrar los detalles del huésped si se encuentra
        if result:
            for record in result:
                huesped = record['huesped']
                print("-----------------------------------------------------")
                print(f"Detalles del huésped:\nID: {huesped['id_huesped']}\nNombre: {huesped['nombre']}\nApellido: {huesped['apellido']}\nDirección: {huesped['direccion']}\nTeléfono: {huesped['telefono']}\nEmail: {huesped['email']}")
                print("-----------------------------------------------------")
        else:
            print(f"No se encontraron huéspedes con el apellido '{apellido}'.")

    except Exception as e:
        print(f"Error al obtener los detalles del huésped: {e}")

def reservas_por_huesped(id_huesped):
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
        RETURN h.nombre AS nombre, h.apellido AS apellido
        """
        result = graph.run(query).data()

        # Mostrar los nombres y apellidos
        if result:
            for record in result:
                nombre = record['nombre']
                apellido = record['apellido']
                print(f"Nombre: {nombre}, Apellido: {apellido}")
        else:
            print("No se encontraron huéspedes en la base de datos.")

    except Exception as e:
        print(f"Error al obtener los huéspedes: {e}")
