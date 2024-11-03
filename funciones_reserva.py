from py2neo import Graph, Node
from funciones_gestion import *
from pymongo import MongoClient
from funciones_hotel import *
from funciones_hotel import * 
from funciones_habitacion import *

graph = Graph("bolt://neo4j:12345678@localhost:7687")
client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_db']
reservas_collection = db['reservas']


def crear_reserva():
    try:
        id_hotel = listar_hoteles_con_validacion()

        if not id_hotel:
            return

        # Solicitar fechas de entrada y salida
        fecha_entrada = input("Ingrese la fecha de entrada (YYYY-MM-DD): ")
        fecha_salida = input("Ingrese la fecha de salida (YYYY-MM-DD): ")

        # Obtener todos los huéspedes
        huespedes = graph.run("MATCH (h:Huesped) RETURN h.id_huesped AS id_huesped, h.nombre AS nombre, h.apellido AS apellido").data()

        # Comprobar si hay huéspedes y mostrar el conteo
        num_huespedes = len(huespedes)

        if num_huespedes > 0:
            print("\nLista de huéspedes:")
            for huesped in huespedes:
                print(f"ID: {huesped['id_huesped']}, Nombre: {huesped['nombre']}, Apellido: {huesped['apellido']}")
        else:
            print("No hay huéspedes registrados en el sistema.")
            return  # Salir si no hay huéspedes

        id_huesped = input("Ingrese el ID del huésped: ")

        # Llamar a la función de habitaciones disponibles
        habitaciones_disponibles = habitaciones_disponibles_en_hotel(id_hotel, fecha_entrada, fecha_salida)
        
        if habitaciones_disponibles:
            print(f"\nHabitaciones disponibles en el hotel con ID {id_hotel}:")
            for habitacion_id in habitaciones_disponibles:
                print(f"Habitación disponible ID: {habitacion_id}")

            # Solicitar el ID de la habitación a reservar
            id_habitacion = input("Ingrese el ID de la habitación que desea reservar: ")
            precio = input("Ingrese el precio de la reserva: ")
            print(crear_reserva_si_disponible(id_habitacion, id_huesped, fecha_entrada, fecha_salida, precio))
        else:
            print(f"No hay habitaciones disponibles en el hotel con ID {id_hotel} para las fechas especificadas.")

    except Exception as e:
        print(f"Error al crear la reserva: {e}")


def baja_reserva():
    reservas = listar_reservas()
    
    if not reservas:
        return "No hay reservas disponibles para eliminar."

    print("Reservas disponibles:")
    for reserva in reservas:
        print(f"ID: {reserva['id_reserva']}, Habitación ID: {reserva['id_habitacion']}, "
              f"Huésped ID: {reserva['id_huesped']}, Fecha Entrada: {reserva['fecha_entrada']}, "
              f"Fecha Salida: {reserva['fecha_salida']}, Precio: {reserva['precio']}")

    id_reserva = input("Ingrese el ID de la reserva a eliminar: ")
    
    # Validar que la reserva exista
    reserva_existente = next((reserva for reserva in reservas if reserva["id_reserva"] == id_reserva), None)

    if not reserva_existente:
        return f"No se encontró la reserva con ID: {id_reserva}"

    # Confirmar eliminación
    confirmacion = input(f"¿Está seguro de que desea eliminar la reserva con ID {id_reserva}? (s/n): ")
    
    if confirmacion.lower() == 's':
        # Eliminar la reserva de MongoDB
        reservas_collection.delete_one({"_id": ObjectId(id_reserva)})
        return f"Reserva con ID {id_reserva} eliminada exitosamente."
    else:
        return "Eliminación cancelada."
    

def listar_reservas():
    # Obtener todas las reservas
    reservas = reservas_collection.find()
    lista_reservas = []

    for reserva in reservas:
        lista_reservas.append({
            "id_reserva": str(reserva["_id"]),
            "id_habitacion": reserva["id_habitacion"],
            "id_huesped": reserva["id_huesped"],
            "fecha_entrada": reserva["fecha_entrada"],
            "fecha_salida": reserva["fecha_salida"],
            "precio": reserva["precio"]
        })

    return lista_reservas


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
    
