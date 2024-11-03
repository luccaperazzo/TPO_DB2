from py2neo import Graph, Node
from funciones_gestion import *
from pymongo import MongoClient
from funciones_hotel import *
from funciones_amenity import *
from datetime import datetime
from funciones_hotel import *
from funciones_hotel import listar_hoteles_con_validacion

client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_db']
reservas_collection = db['reservas']

graph = Graph("bolt://neo4j:12345678@localhost:7687")

def alta_habitacion():
    try:
        # Paso 1: Mostrar lista de hoteles y seleccionar hotel
        id_hotel = listar_hoteles_con_validacion()
        if not id_hotel:
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
        query_nombre= """
            MATCH (h:Hotel {id_hotel: $id_hotel})
            RETURN h.nombre AS nombre
        """
        nombre_hotel = graph.run(query_nombre, id_hotel=id_hotel).data()[0]["nombre"].replace(" ", "_")

        #nombre_hotel = id_hotel["nombre"].replace(" ", "_")
        id_habitacion = f"{nombre_hotel}_{nuevo_id}"

        # Paso 3: Ingresar tipo de habitación
        tipo_habitacion = input("Ingrese el tipo de habitación (ej. 'Suite', 'Doble', 'Individual'): ")

        # Crear la habitación y relacionarla con el hotel
        query = """
            MATCH (h:Hotel {id_hotel: $id_hotel})
            CREATE (h)-[:TIENE]->(:Habitacion {id_habitacion: $id_habitacion, tipo_habitacion: $tipo_habitacion})
        """
        graph.run(query, id_hotel=id_hotel, id_habitacion=id_habitacion, tipo_habitacion=tipo_habitacion)
        print(f"Habitación '{id_habitacion}' de tipo '{tipo_habitacion}' creada exitosamente en el hotel '{nombre_hotel}'.")

        # Paso 4: Mostrar amenities disponibles y permitir la selección
        amenitys = traer_amenitys()
        if not amenitys:
            crear_nuevo = input("No hay amenities disponibles. ¿Desea crear uno nuevo? (s/n): ")
            if crear_nuevo.lower() == 's':
                nombre_amenity = input("Ingrese el nombre del nuevo amenity: ")
                resultado = alta_amenity(nombre_amenity)
                print(resultado)
                # Volver a cargar los amenities después de crear uno nuevo
                amenitys = traer_amenitys()
            else:
                print("No se asignarán amenities a la habitación.")
                return

        print("Amenidades disponibles:")
        for idx, amenity in enumerate(amenitys, start=1):
            print(f"{idx}. {amenity['nombre']} ")
        
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

        print(f"Creación completa de la habitación '{id_habitacion}' en el hotel '{id_hotel}'.")

    except Exception as e:
        print(f"Error al crear la habitación: {e}")


   
def baja_habitacion():
    try:
        # Paso 1 y 2: Mostrar lista de hoteles y seleccionar hotel
        id_hotel = listar_hoteles_con_validacion()
        if not id_hotel:
            return
        # Paso 4: Seleccionar una habitación
        id_habitacion= listar_habitaciones_con_validacion(id_hotel)
        if not id_habitacion:
            return
       
        # Paso 5: Mostrar detalles de la habitación
        query_habitacion = """
        MATCH (h:Habitacion {id_habitacion: $id_habitacion})
        RETURN h.tipo_habitacion AS tipo_habitacion, h.id_habitacion AS nombre
        """
        habitacion_actual = graph.run(query_habitacion, id_habitacion=id_habitacion).data()
        tipo_actual = habitacion_actual [0]["tipo_habitacion"]
        print(f"Detalles de la habitación seleccionada:")
        print(f"ID: {id_habitacion}, Tipo: {tipo_actual}")

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
        # Paso 4: Seleccionar una habitación
        id_habitacion= listar_habitaciones_con_validacion(id_hotel)
        if not id_habitacion:
            return
        
        query_habitacion = """
        MATCH (h:Habitacion {id_habitacion: $id_habitacion})
        RETURN h.tipo_habitacion AS tipo_habitacion, h.id_habitacion AS nombre
        """
        habitacion_actual = graph.run(query_habitacion, id_habitacion=id_habitacion).data()
        
        # Obtener detalles actuales de la habitación
        tipo_actual = habitacion_actual [0]["tipo_habitacion"]
        print(f"Tipo actual de habitación: {tipo_actual}")

        # Obtener amenities actuales
        query_amenities = """
            MATCH (h:Habitacion {id_habitacion: $id_habitacion})-[:INCLUYE]->(a:Amenity)
            RETURN a.id_amenity AS id_amenity, a.nombre AS nombre
        """
        amenities_actuales = graph.run(query_amenities, id_habitacion=id_habitacion).data()
        print("Amenities actuales:")
        traer_amenitys()

        # Paso 5: Modificar tipo de habitación o amenities
        modificar_tipo = input("¿Desea modificar el tipo de habitación? (s/n): ").lower()
        if modificar_tipo == 's':
            tipos_habitacion = ["Suite", "Doble", "Individual"]
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
            amenitys_disponibles = traer_amenitys()
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
        id_hotel = listar_hoteles_con_validacion()
        if not id_hotel:
            print("No hay hoteles disponibles.")
            return
        id_habitacion= listar_habitaciones_con_validacion(id_hotel)
        if not id_habitacion:
            return       
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

def listar_habitaciones_con_validacion(id_hotel):
    try:
        query = """
        MATCH (hotel:Hotel {id_hotel: $id_hotel})-[:TIENE]->(h:Habitacion)
        RETURN h.id_habitacion, h.nombre
        ORDER BY h.nombre
        """
        result = graph.run(query,id_hotel=id_hotel )
        habitaciones = result.data()  # Devuelve una lista de diccionarios con los hoteles
        if not habitaciones:
            print("No hay habitaciones disponibles.")
            return None
        intentos= 0
        while intentos<2:
            print("Seleccione la habitacion:")
            for idx, habitacion in enumerate(habitaciones, start=1):
                print(f"{idx}. {habitacion ['h.id_habitacion']} ")
        
            seleccion = int (input("Ingrese el número del habitacion: "))
            if 1 <= seleccion <= len(habitaciones):
                return (habitaciones[seleccion - 1]['h.id_habitacion'])   
            else:
                print("Selección inválida.Intente nuevamente.")
                intentos +=1
        if intentos ==2:
            print("Demasiados intentos fallidos. Volviendo al menú principal.")
            return None
    except Exception as e:
        print(f"Error al listar los hoteles: {e}")
        return None
    
def habitaciones_disponibles1(fecha_inicio, fecha_fin):
    # Convertir fechas a objetos datetime
    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

    # Buscar reservas que coincidan o se solapen con el rango de fechas
    reservas = reservas_collection.find({
       "$or":[
            {"fecha_entrada": {"$gte": fecha_inicio, "$lte": fecha_fin}},
            {"fecha_salida": {"$gte": fecha_inicio, "$lte": fecha_fin}},
            {"$and":[
                {"fecha_entrada": {"$lte": fecha_inicio}},
                {"fecha_salida": {"$gte": fecha_fin}}
             ]}
        ]
    })

    # Extraer las habitaciones ocupadas de las reservas
    habitaciones_ocupadas = {reserva["id_habitacion"] for reserva in reservas}
    
    # Consultar en Neo4j las habitaciones que no están ocupadas
    query = """
        MATCH (h:Habitacion) 
        WHERE NOT h.id_habitacion IN $habitaciones_ocupadas
        RETURN h.id_habitacion AS id_habitacion
    """
    
    # Ejecutar la consulta y obtener las habitaciones disponibles
    result = graph.run(query, habitaciones_ocupadas=list(habitaciones_ocupadas))
    
    # Devolver las habitaciones disponibles como una lista de diccionarios
    return [record["id_habitacion"] for record in result]    
 
def obtener_informacion_habitacion(id_habitacion):
    try:
        query_habitacion = """
            MATCH (hab:Habitacion {id_habitacion: $id_habitacion})
            OPTIONAL MATCH (hab)-[:INCLUYE]->(amenity:Amenity)
            RETURN hab.tipo_habitacion AS tipo_habitacion, collect(amenity.nombre) AS amenities
        """
        result = graph.run(query_habitacion, id_habitacion=id_habitacion).data()
        
        if not result:
            return None

        habitacion_info = result[0]
        tipo_habitacion = habitacion_info['tipo_habitacion']
        amenities = habitacion_info['amenities'] if habitacion_info['amenities'] else []

        return {
            'tipo_habitacion': tipo_habitacion,
            'amenities': amenities
        }
    except Exception as e:
        print(f"Error al obtener la información de la habitación: {e}")
        return None
