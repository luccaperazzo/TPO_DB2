from py2neo import Graph, Node
from funciones_gestion import *
from pymongo import MongoClient
from funciones_hotel import *
from funciones_amenity import *

graph = Graph("bolt://neo4j:12345678@localhost:7687")

def alta_habitacion():
    try:
        # Paso 1 y 2: Mostrar lista de hoteles y seleccionar hotel
        hoteles = mostrar_hoteles()
        if not hoteles:
            print("No hay hoteles disponibles para asignar una habitación.")
            return
        
        id_hotel = input("Ingrese el ID del hotel para asignar la habitación: ")
        hotel_seleccionado = next((hotel for hotel in hoteles if hotel["id"] == id_hotel), None)
        
        if not hotel_seleccionado:
            print("ID de hotel no válido. Por favor, seleccione un hotel de la lista.")
            return

        # Paso 2: Obtener el máximo ID de habitación asociado al hotel seleccionado y generar uno nuevo
        query = """
            MATCH (:Hotel {id_hotel: $id_hotel})-[:TIENE]->(h:Habitacion)
            RETURN coalesce(max(toInteger(split(h.id_habitacion, "_")[-1])), 0) AS max_id
        """
        result = graph.run(query, id_hotel=id_hotel).data()
        max_id = result[0]["max_id"] if result else 0
        nuevo_id = max_id + 1

        # Generar nombre para la habitación basado en el hotel
        nombre_hotel = hotel_seleccionado["nombre"].replace(" ", "_")
        id_habitacion = f"{nombre_hotel}_{nuevo_id}"

        # Paso 3: Ingresar tipo de habitación
        tipo_habitacion = input("Ingrese el tipo de habitación (ej. 'Suite', 'Doble', 'Individual'): ")

        # Crear la habitación y relacionarla con el hotel
        query = """
            MATCH (h:Hotel {id_hotel: $id_hotel})
            CREATE (h)-[:TIENE]->(:Habitacion {id_habitacion: $id_habitacion, tipo_habitacion: $tipo_habitacion})
        """
        graph.run(query, id_hotel=id_hotel, id_habitacion=id_habitacion, tipo_habitacion=tipo_habitacion)
        print(f"Habitación '{id_habitacion}' de tipo '{tipo_habitacion}' creada exitosamente en el hotel '{hotel_seleccionado['nombre']}'.")

        # Paso 4: Mostrar amenities disponibles y permitir la selección
        amenitys = mostrar_amenitys()
        if not amenitys:
            crear_nuevo = input("No hay amenities disponibles. ¿Desea crear uno nuevo? (s/n): ")
            if crear_nuevo.lower() == 's':
                nombre_amenity = input("Ingrese el nombre del nuevo amenity: ")
                resultado = alta_amenity(nombre_amenity)
                print(resultado)
                # Volver a cargar los amenities después de crear uno nuevo
                amenitys = mostrar_amenitys()
            else:
                print("No se asignarán amenities a la habitación.")
                return

        print("Amenidades disponibles:")
        for amenity in amenitys:
            print(f"ID: {amenity['id']}, Nombre: {amenity['nombre']}")
        
        # Seleccionar amenities para la habitación
        ids_amenities = input("Ingrese los IDs de los amenities que desea asignar a la habitación, separados por comas (o presione Enter para omitir): ")
        if ids_amenities.strip():  # Solo proceder si el usuario ingresó algo
            ids_amenities = ids_amenities.split(",")
            for id_amenity in ids_amenities:
                id_amenity = id_amenity.strip()
                # Verificar si el ID del amenity es válido
                if not any(amenity["id"] == id_amenity for amenity in amenitys):
                    print(f"El ID {id_amenity} no es válido o no existe en la lista de amenities.")
                    continue
                
                # Crear la relación entre la habitación y el amenity
                query = """
                    MATCH (a:Amenity {id_amenity: $id_amenity})
                    MATCH (h:Habitacion {id_habitacion: $id_habitacion})
                    CREATE (h)-[:INCLUYE]->(a)
                """
                graph.run(query, id_habitacion=id_habitacion, id_amenity=id_amenity)
                print(f"Amenity con ID {id_amenity} asignado a la habitación {id_habitacion} exitosamente.")

        print(f"Creación completa de la habitación '{id_habitacion}' en el hotel '{hotel_seleccionado['nombre']}'.")

    except Exception as e:
        print(f"Error al crear la habitación: {e}")


   
def baja_habitacion():
    try:
        # Paso 1: Mostrar lista de hoteles
        id_hotel = listar_hoteles_con_validacion()
        if not id_hotel:
            return

        # Paso 3: Mostrar habitaciones del hotel seleccionado
        query_habitaciones = """
            MATCH (h:Hotel {id_hotel: $id_hotel})-[:TIENE]->(hab:Habitacion)
            RETURN hab.id_habitacion AS id_habitacion, hab.tipo_habitacion AS tipo_habitacion
        """
        habitaciones = graph.run(query_habitaciones, id_hotel=id_hotel).data()

        if not habitaciones:
            print("No hay habitaciones disponibles en el hotel seleccionado.")
            return

        print("Habitaciones disponibles:")
        for hab in habitaciones:
            print(f"ID: {hab['id_habitacion']}, Tipo: {hab['tipo_habitacion']}")

        # Paso 4: Seleccionar una habitación para eliminar
        id_habitacion = input("Ingrese el ID de la habitación que desea eliminar: ")
        habitacion_seleccionada = next((hab for hab in habitaciones if hab["id_habitacion"] == id_habitacion), None)

        if not habitacion_seleccionada:
            print("ID de habitación no válido. Por favor, seleccione una habitación de la lista.")
            return

        # Paso 5: Mostrar detalles de la habitación
        print(f"Detalles de la habitación seleccionada:")
        print(f"ID: {habitacion_seleccionada['id_habitacion']}, Tipo: {habitacion_seleccionada['tipo_habitacion']}")

        # Paso 6: Confirmar la operación
        confirmar = input("¿Está seguro de que desea eliminar esta habitación? (s/n): ").lower()
        if confirmar != 's':
            print("Operación cancelada.")
            return

        # Paso 7: Eliminar relaciones y la habitación
        try:
            # Eliminar las relaciones con amenities
            query_delete_amenities = """
                MATCH (h:Habitacion {id_habitacion: $id_habitacion})-[r:INCLUYE]->(a:Amenity)
                DELETE r
            """
            graph.run(query_delete_amenities, id_habitacion=id_habitacion)

            # Eliminar la relación entre el hotel y la habitación
            query_delete_hotel_relation = """
                MATCH (h:Hotel)-[r:TIENE]->(hab:Habitacion {id_habitacion: $id_habitacion})
                DELETE r
            """
            graph.run(query_delete_hotel_relation, id_habitacion=id_habitacion)

            # Eliminar el nodo de la habitación
            query_delete_habitacion = """
                MATCH (h:Habitacion {id_habitacion: $id_habitacion})
                DELETE h
            """
            graph.run(query_delete_habitacion, id_habitacion=id_habitacion)

            print(f"La habitación con ID {id_habitacion} ha sido eliminada exitosamente.")
        except Exception as e:
            print(f"Error al eliminar la habitación o sus relaciones: {e}")

    except Exception as e:
        print(f"Error al procesar la baja de la habitación: {e}")

    
def modificar_habitacion():
    try:
        # Paso 1: Mostrar lista de hoteles y seleccionar hotel
        id_hotel = listar_hoteles_con_validacion()
        if not id_hotel:
            return        

        # Paso 3: Mostrar habitaciones del hotel seleccionado
        query_habitaciones = """
            MATCH (h:Hotel {id_hotel: $id_hotel})-[:TIENE]->(hab:Habitacion)
            RETURN hab.id_habitacion AS id_habitacion, hab.tipo_habitacion AS tipo_habitacion
        """
        habitaciones = graph.run(query_habitaciones, id_hotel=id_hotel).data()

        if not habitaciones:
            print("No hay habitaciones disponibles en el hotel seleccionado.")
            return

        print("Habitaciones disponibles:")
        for hab in habitaciones:
            print(f"ID: {hab['id_habitacion']}, Tipo: {hab['tipo_habitacion']}")

        # Paso 4: Seleccionar una habitación
        id_habitacion = input("Ingrese el ID de la habitación que desea modificar: ")
        habitacion_seleccionada = next((hab for hab in habitaciones if hab["id_habitacion"] == id_habitacion), None)

        if not habitacion_seleccionada:
            print("ID de habitación no válido. Por favor, seleccione una habitación de la lista.")
            return

        # Obtener detalles actuales de la habitación
        tipo_actual = habitacion_seleccionada["tipo_habitacion"]
        print(f"Tipo actual de habitación: {tipo_actual}")

        # Obtener amenities actuales
        query_amenities = """
            MATCH (h:Habitacion {id_habitacion: $id_habitacion})-[:INCLUYE]->(a:Amenity)
            RETURN a.id_amenity AS id_amenity, a.nombre AS nombre
        """
        amenities_actuales = graph.run(query_amenities, id_habitacion=id_habitacion).data()

        print("Amenities actuales:")
        for amenity in amenities_actuales:
            print(f"ID: {amenity['id_amenity']}, Nombre: {amenity['nombre']}")

        # Paso 5: Modificar tipo de habitación o amenities
        modificar_tipo = input("¿Desea modificar el tipo de habitación? (s/n): ").lower()
        if modificar_tipo == 's':
            tipos_habitacion = ["Suite", "Doble", "Simple"]
            print("Tipos de habitación disponibles:")
            for i, tipo in enumerate(tipos_habitacion, 1):
                print(f"{i}. {tipo}")
            nuevo_tipo = input("Ingrese el nuevo tipo de habitación: ")
            if nuevo_tipo in tipos_habitacion:
                # Actualizar tipo de habitación
                query_update_tipo = """
                    MATCH (h:Habitacion {id_habitacion: $id_habitacion})
                    SET h.tipo_habitacion = $nuevo_tipo
                """
                graph.run(query_update_tipo, id_habitacion=id_habitacion, nuevo_tipo=nuevo_tipo)
                print(f"Tipo de habitación actualizado a '{nuevo_tipo}'.")  # Mensaje de éxito

        modificar_amenities = input("¿Desea modificar los amenities? (s/n): ").lower()
        if modificar_amenities == 's':
            # Mostrar amenities disponibles
            amenitys_disponibles = mostrar_amenitys()
            if not amenitys_disponibles:
                print("No hay amenities disponibles para asignar.")
                return
            
            # Aquí ahora no se imprimirá 'None' si no hay amenities
            ids_amenities_input = input("Ingrese los IDs de los amenities que desea asignar, separados por comas (o presione Enter para eliminar todos): ")
            if ids_amenities_input.strip():  # Si el usuario ingresó algo
                ids_amenities = [id.strip() for id in ids_amenities_input.split(",")]
                
                # Eliminar las relaciones actuales
                query_delete_current = """
                    MATCH (h:Habitacion {id_habitacion: $id_habitacion})-[r:INCLUYE]->(a:Amenity)
                    DELETE r
                """
                graph.run(query_delete_current, id_habitacion=id_habitacion)

                # Crear nuevas relaciones con los amenities seleccionados
                for id_amenity in ids_amenities:
                    # Verificar si el ID del amenity es válido
                    if not any(amenity["id"] == id_amenity for amenity in amenitys_disponibles):
                        print(f"El ID {id_amenity} no es válido o no existe en la lista de amenities.")
                        continue
                    
                    # Crear la relación entre la habitación y el amenity
                    query_add_amenity = """
                        MATCH (a:Amenity {id_amenity: $id_amenity})
                        MATCH (h:Habitacion {id_habitacion: $id_habitacion})
                        CREATE (h)-[:INCLUYE]->(a)
                    """
                    graph.run(query_add_amenity, id_habitacion=id_habitacion, id_amenity=id_amenity)
                    print(f"Amenity con ID {id_amenity} asignado a la habitación {id_habitacion} exitosamente.")
                
                print("Modificación de amenities completada.")  # Mensaje de éxito
            else:
                # Eliminar todas las relaciones de amenities
                query_delete_all = """
                    MATCH (h:Habitacion {id_habitacion: $id_habitacion})-[r:INCLUYE]->(a:Amenity)
                    DELETE r
                """
                graph.run(query_delete_all, id_habitacion=id_habitacion)
                print(f"Todas las relaciones de amenities han sido eliminadas de la habitación {id_habitacion}.")  # Mensaje de éxito

    except Exception as e:
        print(f"Error al modificar la habitación: {e}")



def mostrar_amenities_habitacion():
    try:
        # Paso 1: Mostrar lista de hoteles
        hoteles = mostrar_hoteles()
        if not hoteles:
            print("No hay hoteles disponibles.")
            return

        # Paso 2: Seleccionar un hotel
        id_hotel = input("Ingrese el ID del hotel para ver los amenities de sus habitaciones: ")
        hotel_seleccionado = next((hotel for hotel in hoteles if hotel["id"] == id_hotel), None)

        if not hotel_seleccionado:
            print("ID de hotel no válido. Por favor, seleccione un hotel de la lista.")
            return

        # Paso 3: Mostrar habitaciones del hotel seleccionado
        query_habitaciones = """
            MATCH (h:Hotel {id_hotel: $id_hotel})-[:TIENE]->(hab:Habitacion)
            RETURN hab.id_habitacion AS id_habitacion, hab.tipo_habitacion AS tipo_habitacion
        """
        habitaciones = graph.run(query_habitaciones, id_hotel=id_hotel).data()

        if not habitaciones:
            print("No hay habitaciones disponibles en el hotel seleccionado.")
            return

        print("Habitaciones disponibles:")
        for hab in habitaciones:
            print(f"ID: {hab['id_habitacion']}, Tipo: {hab['tipo_habitacion']}")

        # Paso 4: Seleccionar una habitación para ver sus amenities
        id_habitacion = input("Ingrese el ID de la habitación para ver los amenities: ")
        habitacion_seleccionada = next((hab for hab in habitaciones if hab["id_habitacion"] == id_habitacion), None)

        if not habitacion_seleccionada:
            print("ID de habitación no válido. Por favor, seleccione una habitación de la lista.")
            return

        # Paso 5: Consultar amenities de la habitación seleccionada
        query_amenities = """
            MATCH (hab:Habitacion {id_habitacion: $id_habitacion})-[:INCLUYE]->(amenity:Amenity)
            RETURN amenity.nombre AS nombre
        """
        result = graph.run(query_amenities, id_habitacion=id_habitacion).data()

        # Mostrar los amenities de la habitación seleccionada
        print(f"\nAmenities de la habitación ID {id_habitacion}:")
        if not result:
            print("No hay amenities disponibles para esta habitación.")
        else:
            print("-----------------------------------------------------")
            for record in result:
                amenity_nombre = record['nombre']
                print(f"Amenity: {amenity_nombre}")
            print("-----------------------------------------------------")

    except Exception as e:
        print(f"Error al mostrar los amenities de la habitación: {e}")
