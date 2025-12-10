import requests
from geopy.distance import geodesic
from .models import Location, Edge
from math import sqrt
import numpy as np
import heapq

def get_lat_lon_from_pincode(pincode):
    url = f"https://nominatim.openstreetmap.org/search?postalcode={pincode}&country=India&format=json"
    
    headers = {
        "User-Agent": "PincodeRouteOptimizer/1.0"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon
    
    return None, None


def calculate_distance_km (lat1, lon1 , lat2 , lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km



def build_graph(k_neighbors=3):
    locations = list(Location.objects.all())

    if not locations:
        return "No locations found."

    
    latitudes = np.array([float(loc.latitude) for loc in locations])
    longitudes = np.array([float(loc.longitude) for loc in locations])

    
    lat_rad = np.radians(latitudes)
    lon_rad = np.radians(longitudes)

    n = len(locations)

    
    lat1 = lat_rad.reshape(n, 1)
    lat2 = lat_rad.reshape(1, n)
    lon1 = lon_rad.reshape(n, 1)
    lon2 = lon_rad.reshape(1, n)

    
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    R = 6371  

    distances = R * c  

    
    np.fill_diagonal(distances, 999999)

    
    for i, loc in enumerate(locations):
    
        k_idx = np.argsort(distances[i])[:k_neighbors]

        for idx in k_idx:
            other_loc = locations[idx]
            dist = float(distances[i][idx])

            
            Edge.objects.get_or_create(
                from_loc=loc,
                to_loc=other_loc,
                distance_km=dist,
                bidirectional=True
            )

    return "Graph built successfully using NumPy!"




def heuristic(loc1, loc2):
    return sqrt((loc1.latitude - loc2.latitude)**2 + (loc1.longitude - loc2.longitude)**2)

import heapq

def a_star(start_loc, end_loc):
    open_set = []
    heapq.heappush(open_set, (0, start_loc))

    came_from = {}
    g_score = {start_loc: 0}
    f_score = {start_loc: heuristic(start_loc, end_loc)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == end_loc:
            return reconstruct_path(came_from, current)

        # Get outgoing edges
        edges = Edge.objects.filter(from_loc=current)

        for edge in edges:
            neighbor = edge.to_loc
            tentative_g = g_score[current] + edge.distance_km

            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, end_loc)

                # FIXED: must be a tuple
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    # only called when no path exists
    return None


def reconstruct_path(came_from, current):
    total_path = [current]
    distance = 0

    while current in came_from:
        prev = came_from[current]

        edge = Edge.objects.get(from_loc = prev, to_loc = current)
        distance += edge.distance_km

        total_path.append(prev)
        current = prev

    total_path.reverse()


    return{"path": [loc.pincode for loc in total_path],
           "locations":total_path,
           "total_distance":round(distance,2)
           }


def dijkstra(start_loc, end_loc):
    distances = {start_loc: 0}
    priority_queue = [(0, start_loc)]
    came_from = {}


    while priority_queue:
        current_distance , current_loc = heapq.heappop(priority_queue)

        if current_loc == end_loc:
            return reconstruct_path(came_from , current_loc)
        
        edges = Edge.objects.filter(from_loc = current_loc)

        for edge in edges:
            neighbor = edge.to_loc
            new_distance = current_distance + edge.distance_km

            if new_distance < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_distance

                came_from[neighbor] = current_loc

    return None               
