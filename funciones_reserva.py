from py2neo import Graph, Node
from funciones_gestion import *
from pymongo import MongoClient
from bson.objectid import ObjectId
from funciones_habitacion import *
from funciones_hotel import *


graph = Graph("bolt://neo4j:12345678@localhost:7687")
client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_db']
reservas_collection = db['reservas']


def crear_reserva():
    try:
        # Llamar a la nueva función para obtener un POI
        poi_seleccionado = hoteles_por_poi()
        if poi_seleccionado is None:
            return  # Salir si no se seleccionó un POI

        # Consulta para obtener detalles de hoteles cercanos al POI seleccionado
        query_hoteles = """
        MATCH (poi:POI {nombre: $poi_nombre})<-[:CERCA_DE]-(hotel:Hotel)
        RETURN hotel.id_hotel AS id_hotel, hotel.nombre AS nombre, hotel.direccion AS direccion
        """
        hoteles_result = graph.run(query_hoteles, parameters={"poi_nombre": poi_seleccionado}).data()

        if not hoteles_result:
            print("No se encontraron hoteles cercanos al POI seleccionado.")
            return

        # Mostrar los hoteles cercanos al POI seleccionado
        print(f"\nHoteles cercanos al POI '{poi_seleccionado}':")
        for idx, hotel in enumerate(hoteles_result, start=1):
            print(f"{idx}. ID: {hotel['id_hotel']}, Nombre: {hotel['nombre']}, Dirección: {hotel['direccion']}")

        # Solicitar al usuario que elija un hotel por índice
        try:
            seleccion_hotel_idx = int(input("\nIngrese el número del hotel que desea reservar: ")) - 1
            if seleccion_hotel_idx < 0 or seleccion_hotel_idx >= len(hoteles_result):
                print("El número ingresado no es válido. Debe estar entre 1 y", len(hoteles_result))
                return
            
            id_hotel = hoteles_result[seleccion_hotel_idx]['id_hotel']  # Obtener el ID del hotel seleccionado
        except ValueError:
            print("Entrada inválida. Por favor, ingrese un número.")
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
            for habitacion in habitaciones_disponibles:
                # Aquí se asume que 'habitacion' es un string que representa el ID de la habitación
                id_habitacion = habitacion  # No uses habitacion['id_habitacion'] porque es solo un string
                info_habitacion = obtener_informacion_habitacion(id_habitacion)

                if info_habitacion:
                    tipo_habitacion = info_habitacion['tipo_habitacion']
                    amenities = ', '.join(info_habitacion['amenities'])  # Convertir la lista de amenities a una cadena
                    print(f"Habitación disponible ID: {id_habitacion}, Tipo: {tipo_habitacion}, Amenities: {amenities}")
                else:
                    print(f"No se pudo obtener información para la habitación ID: {id_habitacion}")

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
    

def hoteles_por_poi():
    # Consulta para obtener todos los POIs con al menos un hotel cercano y el conteo de hoteles cercanos
    query_pois = """
    MATCH (poi:POI)<-[:CERCA_DE]-(hotel:Hotel)
    RETURN poi.nombre AS poi_nombre, poi.detalle AS poi_detalle, COUNT(hotel) AS cantidad_hoteles
    """
    pois_result = graph.run(query_pois).data()

    # Listar los POIs disponibles y su cantidad de hoteles cercanos
    print("Lista de POIs disponibles con hoteles cercanos:")
    pois_disponibles = []
    for idx, record in enumerate(pois_result, start=1):
        poi_nombre = record['poi_nombre']
        poi_detalle = record['poi_detalle']
        cantidad_hoteles = record['cantidad_hoteles']
        pois_disponibles.append(poi_nombre)
        print(f"{idx}. {poi_nombre}, Detalle: {poi_detalle} --> Hoteles cercanos: {cantidad_hoteles}")

    # Solicitar al usuario que elija un POI por índice
    try:
        seleccion_idx = int(input("\nIngrese el número del POI para ver los hoteles cercanos: ")) - 1
        if seleccion_idx < 0 or seleccion_idx >= len(pois_disponibles):
            print("El número ingresado no es válido. Debe estar entre 1 y", len(pois_disponibles))
            return None
        return pois_disponibles[seleccion_idx]  # Retorna el nombre del POI seleccionado
    except ValueError:
        print("Entrada inválida. Por favor, ingrese un número.")
        return None
