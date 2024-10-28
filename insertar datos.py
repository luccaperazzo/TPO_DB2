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

graph.run("MATCH (n) DETACH DELETE n")


# --- Hoteles ---
graph.run("CREATE (:Hotel {id_hotel: '1', nombre: 'Hotel A', direccion: 'Calle 123', telefono: '123-456-7890', email: 'hotel_a@example.com', coordenadas: '12.34,56.78'})")
graph.run("CREATE (:Hotel {id_hotel: '2', nombre: 'Hotel B', direccion: 'Calle 456', telefono: '987-654-3210', email: 'hotel_b@example.com', coordenadas: '34.56,78.90'})")

# --- Habitaciones ---
graph.run("CREATE (:Habitacion {id_habitacion: '101', tipo_habitacion: 'Simple', hotel_id: '1'})")
graph.run("CREATE (:Habitacion {id_habitacion: '102', tipo_habitacion: 'Doble', hotel_id: '1'})")
graph.run("CREATE (:Habitacion {id_habitacion: '201', tipo_habitacion: 'Suite', hotel_id: '2'})")

# --- Huespedes ---
graph.run("CREATE (:Huesped {id_huesped: '1', nombre: 'Juan', apellido: 'Pérez', direccion: 'Calle X 789', telefono: '111-222-3333', email: 'juan.perez@example.com'})")
graph.run("CREATE (:Huesped {id_huesped: '2', nombre: 'Ana', apellido: 'Gomez', direccion: 'Calle Y 987', telefono: '444-555-6666', email: 'ana.gomez@example.com'})")



# --- Amenities ---
graph.run("CREATE (:Amenity {id_amenity: '1', nombre: 'WiFi'})")
graph.run("CREATE (:Amenity {id_amenity: '2', nombre: 'Desayuno'})")
graph.run("CREATE (:Amenity {id_amenity: '3', nombre: 'Piscina'})")


# --- POIs ---
graph.run("CREATE (:POI {id_poi: '1', nombre: 'Museo X', detalle: 'Museo de arte moderno', coordenadas: '12.35, 56.79', tipo: 'museo'})")
graph.run("CREATE (:POI {id_poi: '2', nombre: 'Parque Y', detalle: 'Parque con senderos', coordenadas: '34.57, 78.91', tipo: 'parque'})")


# --- Relaciones ---

# Hotel - Habitacion
graph.run("MATCH (h:Hotel {id_hotel: '1'}), (hab:Habitacion {id_habitacion: '101'}) CREATE (h)-[:TIENE]->(hab)")
graph.run("MATCH (h:Hotel {id_hotel: '1'}), (hab:Habitacion {id_habitacion: '102'}) CREATE (h)-[:TIENE]->(hab)")
graph.run("MATCH (h:Hotel {id_hotel: '2'}), (hab:Habitacion {id_habitacion: '201'}) CREATE (h)-[:TIENE]->(hab)")


# Habitacion - Amenity (Relación N:M a través de un nodo intermedio)
graph.run("MATCH (hab:Habitacion {id_habitacion: '101'}), (amenity:Amenity {id_amenity: '1'}) CREATE (hab)-[:TIENE_AMENITY]->(amenity)")
graph.run("MATCH (hab:Habitacion {id_habitacion: '101'}), (amenity:Amenity {id_amenity: '2'}) CREATE (hab)-[:TIENE_AMENITY]->(amenity)")
graph.run("MATCH (hab:Habitacion {id_habitacion: '201'}), (amenity:Amenity {id_amenity: '3'}) CREATE (hab)-[:TIENE_AMENITY]->(amenity)")



# Hotel - POI
graph.run("MATCH (h:Hotel {id_hotel: '1'}), (poi:POI {id_poi: '1'}) CREATE (h)-[:CERCA_DE {distancia: 0.5}]->(poi)")
graph.run("MATCH (h:Hotel {id_hotel: '2'}), (poi:POI {id_poi: '2'}) CREATE (h)-[:CERCA_DE {distancia: 0.2}]->(poi)")


# --- Datos en MongoDB (pymongo) ---

from pymongo import MongoClient

client_mongo = MongoClient('mongodb://localhost:27017/')
db_mongo = client_mongo['hotel_db']
reservas_collection = db_mongo['reservas']

reservas_collection.insert_many([
    {"id_habitacion": "101", "id_huesped": "1", "fecha_entrada": "2024-05-10", "fecha_salida": "2024-05-15", "precio": 120.0},
    {"id_habitacion": "201", "id_huesped": "2", "fecha_entrada": "2024-06-01", "fecha_salida": "2024-06-05", "precio": 200.0}
])


print("Datos cargados en Neo4j y MongoDB.")