from py2neo import Graph
from pymongo import MongoClient
from funciones_gestion import *
from crear_entidades import *
from funciones_gestion import *


# --- Conexiones --- #
# 
#TEST ILAN CONTRA LUCCA
#TEST SUBIDA FACU
#TEST MILI
# test

graph = Graph("bolt://neo4j:12345678@localhost:7687")
client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_db']
reservas_collection = db['reservas']


def gestionar_entidad():
    while True:
        print("Seleccione la operación que desea realizar:")
        print("1. Crear")
        print("2. Modificar")
        print("3. Eliminar")
        print("4. Crear Relación")
        print("5. Consultas")
        print("6. Crear Datos Iniciales")
        print("7. Salir")
        opcion = input("Ingrese el número de la operación (1-7): ")

        # Para todas las opciones menos consultas, se selecciona la entidad
        if opcion in ['1', '2', '3', '4']:
            print("Seleccione la entidad:")
            print("1. Hotel")
            print("2. Habitación")
            print("3. Amenity")
            print("4. POI")
            print("5. Huésped")
            print("6. Reserva")
            entidad = input("Ingrese el número de la entidad (1-6): ")

        if opcion == '1':  # Crear
            if entidad == '1':  # Hotel
                nombre = input("Ingrese el nombre del hotel: ")
                direccion = input("Ingrese la dirección del hotel: ")
                telefono = input("Ingrese el teléfono del hotel: ")
                email = input("Ingrese el email del hotel: ")
                print(alta_hotel(nombre, direccion, telefono, email))
            
            elif entidad == '2':  # Habitación
                id_habitacion = input("Ingrese el ID de la habitación: ")
                tipo_habitacion = input("Ingrese el tipo de habitación: ")
                id_hotel = input("Ingrese el ID del hotel: ")
                print(alta_habitacion(id_habitacion, tipo_habitacion, id_hotel))
            
            elif entidad == '3':  # Amenity
                id_amenity = input("Ingrese el ID del amenity: ")
                nombre = input("Ingrese el nombre del amenity: ")
                print(alta_amenity(id_amenity, nombre))
            
            elif entidad == '4':  # POI
                id_poi = input("Ingrese el ID del POI: ")
                nombre = input("Ingrese el nombre del POI: ")
                detalle = input("Ingrese el detalle del POI: ")
                direccion = input("Ingrese la direccion del POI: ")
                tipo = input("Ingrese el tipo del POI: ")
                print(alta_poi(id_poi, nombre, detalle, direccion, tipo))
                
            elif entidad == '5':  # Huésped
                nombre = input("Ingrese el nombre del huésped: ")
                apellido = input("Ingrese el apellido del huésped: ")
                direccion = input("Ingrese la dirección del huésped: ")
                telefono = input("Ingrese el teléfono del huésped: ")
                email = input("Ingrese el email del huésped: ")
                print(alta_huesped(nombre, apellido, direccion, telefono, email))
            
            elif entidad == '6':  # Reserva
                id_habitacion = input("Ingrese el ID de la habitación: ")
                id_huesped = input("Ingrese el ID del huésped: ")
                fecha_entrada = input("Ingrese la fecha de entrada (YYYY-MM-DD): ")
                fecha_salida = input("Ingrese la fecha de salida (YYYY-MM-DD): ")
                precio = input("Ingrese el precio de la reserva: ")
                print(crear_reserva_si_disponible(id_habitacion, id_huesped, fecha_entrada, fecha_salida, precio))

        elif opcion == '2':  # Modificar
            if entidad == '1':  # Hotel
                id_hotel = input("Ingrese el ID del hotel a modificar: ")
                nombre = input("Ingrese el nuevo nombre del hotel (o presione Enter para omitir): ")
                direccion = input("Ingrese la nueva dirección del hotel (o presione Enter para omitir): ")
                telefono = input("Ingrese el nuevo teléfono del hotel (o presione Enter para omitir): ")
                email = input("Ingrese el nuevo email del hotel (o presione Enter para omitir): ")
                coordenadas = input("Ingrese las nuevas coordenadas del hotel (o presione Enter para omitir): ")
                print(modificar_hotel(id_hotel, nombre if nombre else None, direccion if direccion else None,
                                    telefono if telefono else None, email if email else None,
                                    coordenadas if coordenadas else None))
            
            elif entidad == '2':  # Habitación
                id_habitacion = input("Ingrese el ID de la habitación a modificar: ")
                tipo_habitacion = input("Ingrese el nuevo tipo de habitación (o presione Enter para omitir): ")
                id_hotel = input("Ingrese el nuevo ID de hotel (o presione Enter para omitir): ")
                print(modificar_habitacion(id_habitacion, tipo_habitacion if tipo_habitacion else None, 
                                            id_hotel if id_hotel else None))
            
            elif entidad == '3':  # Amenity
                id_amenity = input("Ingrese el ID del amenity a modificar: ")
                nombre = input("Ingrese el nuevo nombre del amenity (o presione Enter para omitir): ")
                print(modificar_amenity(id_amenity, nombre if nombre else None))
            
            elif entidad == '4':  # POI
                id_poi = input("Ingrese el ID del POI a modificar: ")
                nombre = input("Ingrese el nuevo nombre del POI (o presione Enter para omitir): ")
                detalle = input("Ingrese el nuevo detalle del POI (o presione Enter para omitir): ")
                coordenadas = input("Ingrese las nuevas coordenadas del POI (o presione Enter para omitir): ")
                tipo = input("Ingrese el nuevo tipo del POI (o presione Enter para omitir): ")
                print(modificar_poi(id_poi, nombre if nombre else None, detalle if detalle else None, 
                                    coordenadas if coordenadas else None, tipo if tipo else None))

        elif opcion == '3':  # Eliminar
            if entidad == '1':  # Hotel
                id_hotel = input("Ingrese el ID del hotel a eliminar: ")
                print(baja_hotel(id_hotel))
            
            elif entidad == '2':  # Habitación
                id_habitacion = input("Ingrese el ID de la habitación a eliminar: ")
                print(baja_habitacion(id_habitacion))
            
            elif entidad == '3':  # Amenity
                id_amenity = input("Ingrese el ID del amenity a eliminar: ")
                print(baja_amenity(id_amenity))
            
            elif entidad == '4':  # POI
                id_poi = input("Ingrese el ID del POI a eliminar: ")
                print(baja_poi(id_poi))

        elif opcion == '4':  # Crear Relación
            print("Seleccione la relación que desea crear:")
            print("1. Hotel - TIENE -> Habitación")
            print("2. Habitación - TIENE_AMENITY -> Amenity")
            print("3. Hotel - CERCA_DE -> POI")
            relacion = input("Ingrese el número de la relación (1-3): ")

            if relacion == '1':  # Hotel - Habitación
                id_hotel = input("Ingrese el ID del hotel: ")
                id_habitacion = input("Ingrese el ID de la habitación: ")

                # Verificar que la habitación no esté asignada a otro hotel
                if verificar_habitacion_en_hotel(id_habitacion):
                    print(f"La habitación {id_habitacion} ya está asignada a otro hotel.")
                else:
                    print(crear_relacion_hotel_habitacion(id_hotel, id_habitacion))
            
            elif relacion == '2':  # Habitación - Amenity
                id_habitacion = input("Ingrese el ID de la habitación: ")
                id_amenity = input("Ingrese el ID del amenity: ")
                print(crear_relacion_habitacion_amenity(id_habitacion, id_amenity))
            
            elif relacion == '3':  # Hotel - POI
                id_hotel = input("Ingrese el ID del hotel: ")
                id_poi = input("Ingrese el ID del POI: ")
                distancia = input("Ingrese la distancia entre el hotel y el POI: ")
                print(crear_relacion_hotel_poi(id_hotel, id_poi, distancia))
        
        elif opcion == '5':  # Consultas
            print("Seleccione la consulta que desea realizar:")
            print("1. Hoteles cerca de un POI")
            print("2. Información de un hotel")
            print("3. POIs cerca de un hotel")
            print("4. Habitaciones disponibles")
            print("5. Amenities de una habitación")
            print("6. Reservas por número de confirmación")
            print("7. Reservas de un huésped")
            print("8. Reservas por fecha en el hotel")
            print("9. Ver detalles del huésped")
            consulta = input("Ingrese el número de la consulta (1-9): ")

            # Lógica para cada consulta
            if consulta == '1':
                poi_nombre = input("Ingrese el nombre del POI: ")
                print(hoteles_cerca_de_poi(poi_nombre))
            elif consulta == '2':
                hotel_nombre = input("Ingrese el nombre del hotel: ")
                print(informacion_hotel(hotel_nombre))
            elif consulta == '3':
                id_hotel = input("Ingrese el ID del hotel: ")
                print(pois_cerca_de_hotel(id_hotel))
            elif consulta == '4':  # Habitaciones disponibles
                    id_hotel = input("Ingrese el ID del hotel: ")
                    fecha_entrada = input("Ingrese la fecha de entrada (YYYY-MM-DD): ")
                    fecha_salida = input("Ingrese la fecha de salida (YYYY-MM-DD): ")
                    # Llama a la función y filtra las habitaciones por hotel
                    habitaciones_disponibles_hotel = habitaciones_disponibles(fecha_entrada, fecha_salida, id_hotel)
                    
                    if habitaciones_disponibles_hotel:
                        for hotel, habitacion in habitaciones_disponibles_hotel:
                            print(f"Hotel: {hotel}, Habitación: {habitacion}")
                    else:
                        print("No hay habitaciones disponibles para este hotel en las fechas especificadas.")


            elif consulta == '5':
                id_habitacion = input("Ingrese el ID de la habitación: ")
                print(amenities_habitacion(id_habitacion))
            elif consulta == '6':
                numero_confirmacion = input("Ingrese el número de confirmación: ")
                print(reservas_por_numero_confirmacion(numero_confirmacion))
            elif consulta == '7':
                id_huesped = input("Ingrese el ID del huésped: ")
                print(reservas_por_huesped(id_huesped))
            elif consulta == '8':
                id_hotel = input("Ingrese el ID del hotel: ")
                fecha = input("Ingrese la fecha (YYYY-MM-DD): ")
                print(reservas_por_fecha_en_hotel(id_hotel, fecha))
            elif consulta == '9':
                ver_detalles_huesped()
        
        elif opcion == '6':
            crear_huespedes()
            crear_hoteles()
            crear_pois()
            

        elif opcion == '7':  # Salir
            print("Salir del sistema") 
            break

        else:
            print("Opción no válida.")

gestionar_entidad()