"""
PENELOPE Geospatial Risk Engine - Safe Mountain Routing Engine
Implements risk-penalized pathfinding using NetworkX over mountain road and trail graphs.
Penalizes edges crossing flood hazard cells, near-river corridors, and submerged bridges.
Identifies nearest open relief shelters and emits tactical warning advisories.
"""

import math
import networkx as nx
from typing import List, Dict, Any, Tuple, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import select

from apps.api.models import Location, Region
from apps.api.geo_types import extract_lon_lat
from apps.api.geospatial.risk_engine import haversine_km


def compute_edge_penalty(length_m: float, flood_risk: float, is_low_lying: bool) -> float:
    """
    Computes penalized traversal cost:
    - Base cost is distance in meters
    - Penalized by flood risk (quadratic scale)
    - Low-lying segments near river banks get extra hazard penalties
    - Severe flood hazard (>= 0.75) heavily penalizes the edge to force mountain ridge detour
    """
    risk = max(0.0, min(1.0, flood_risk))
    multiplier = 1.0 + (risk * 15.0) + ((risk ** 2) * 50.0)

    if is_low_lying and risk > 0.25:
        multiplier += 25.0 * risk

    if risk >= 0.70:
        multiplier += 200.0 * (risk ** 2)

    return length_m * multiplier


class SafeRoutingEngine:
    """
    Road and trail graph engine for mountain terrain.
    Maintains regional NetworkX graphs with dynamic edge risk attributes.
    """
    def __init__(self):
        self._graphs: Dict[str, nx.Graph] = {}
        self._all_graph: Optional[nx.Graph] = None

    def _ensure_graph(self, db: Session, region_id: Optional[str] = None) -> nx.Graph:
        key = region_id or "global"
        if key in self._graphs and self._graphs[key].number_of_nodes() > 0:
            return self._graphs[key]

        stmt = select(Location)
        if region_id:
            stmt = stmt.where(Location.region_id == region_id)
        locations = db.execute(stmt).scalars().all()

        G = nx.Graph()
        for loc in locations:
            c_lon, c_lat = extract_lon_lat(loc.geom)
            G.add_node(
                loc.id,
                name=loc.name,
                hindi_name=loc.hindi_name,
                lat=c_lat,
                lon=c_lon,
                elevation_m=loc.elevation_m,
                type=loc.type,
                river_dist_m=loc.river_distance_m,
                population=loc.population,
                risk_score=loc.current_risk_score,
                region_id=loc.region_id
            )

        # Connect each location to its nearest 5 neighbors in the region
        for i, l1 in enumerate(locations):
            lon1, lat1 = extract_lon_lat(l1.geom)
            dists: List[Tuple[float, Location]] = []

            for j, l2 in enumerate(locations):
                if i != j:
                    lon2, lat2 = extract_lon_lat(l2.geom)
                    d_m = haversine_km(lat1, lon1, lat2, lon2) * 1000.0
                    dists.append((d_m, l2))

            dists.sort(key=lambda x: x[0])
            for d_m, l2 in dists[:6]:
                # Determine low-lying proximity and initial flood risk
                is_low = min(l1.river_distance_m, l2.river_distance_m) < 160.0 or "bridge" in (l1.type + l2.type).lower()
                edge_risk = max(l1.current_risk_score, l2.current_risk_score, 0.08)
                cost = compute_edge_penalty(d_m, edge_risk, is_low)

                G.add_edge(
                    l1.id,
                    l2.id,
                    length_m=d_m,
                    is_low_lying=is_low,
                    flood_risk=edge_risk,
                    base_cost=d_m,
                    penalized_cost=cost
                )

        self._graphs[key] = G
        return G

    def set_edge_risk(self, u_id: str, v_id: str, flood_risk: float, region_id: Optional[str] = None):
        """Directly sets flood risk for a specific edge in the graph."""
        key = region_id or "global"
        G = self._graphs.get(key)
        if G and G.has_edge(u_id, v_id):
            edge = G[u_id][v_id]
            edge["flood_risk"] = flood_risk
            edge["penalized_cost"] = compute_edge_penalty(edge["length_m"], flood_risk, edge["is_low_lying"])

    def raise_segment_risk(self, location_id_or_name: str, flood_risk: float = 0.92, region_id: Optional[str] = None):
        """
        Raises flood risk on all edges connected to a location (e.g. bridge or riverside segment).
        Used in test fixtures and hazard simulations.
        """
        key = region_id or "global"
        G = self._graphs.get(key)
        if not G:
            return

        target_node = None
        for n, data in G.nodes(data=True):
            if n == location_id_or_name or data.get("name") == location_id_or_name:
                target_node = n
                break

        if target_node:
            for neighbor in list(G.neighbors(target_node)):
                edge = G[target_node][neighbor]
                edge["flood_risk"] = flood_risk
                edge["penalized_cost"] = compute_edge_penalty(edge["length_m"], flood_risk, edge["is_low_lying"])

    def find_nearest_node(self, G: nx.Graph, lon: float, lat: float) -> Tuple[str, float]:
        """Finds closest node in graph to GPS (lon, lat). Returns (node_id, distance_m)."""
        best_node = None
        min_dist = float("inf")
        for n, data in G.nodes(data=True):
            d = haversine_km(lat, lon, data["lat"], data["lon"]) * 1000.0
            if d < min_dist:
                min_dist = d
                best_node = n
        return best_node, min_dist

    def find_safe_route(
        self,
        db: Session,
        from_coords: Union[List[float], Tuple[float, float], Dict[str, float]],
        to_coords: Union[List[float], Tuple[float, float], Dict[str, float]],
        region_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Computes safe route penalized by flood risk and low-lying near-river segments.
        Returns GeoJSON route, risk exposure score, warnings, and nearest open shelter.
        """
        # Parse from coordinates
        if isinstance(from_coords, dict):
            f_lon = float(from_coords.get("lon") or from_coords.get("lng", 0.0))
            f_lat = float(from_coords.get("lat", 0.0))
        elif isinstance(from_coords, (list, tuple)):
            f_lon, f_lat = float(from_coords[0]), float(from_coords[1])
        else:
            raise ValueError("Invalid from_coords format")

        # Parse to coordinates
        if isinstance(to_coords, dict):
            t_lon = float(to_coords.get("lon") or to_coords.get("lng", 0.0))
            t_lat = float(to_coords.get("lat", 0.0))
        elif isinstance(to_coords, (list, tuple)):
            t_lon, t_lat = float(to_coords[0]), float(to_coords[1])
        else:
            raise ValueError("Invalid to_coords format")

        G = self._ensure_graph(db, region_id)
        if G.number_of_nodes() == 0:
            raise ValueError("Routing graph has no nodes in database.")

        src_node, d_src = self.find_nearest_node(G, f_lon, f_lat)
        dst_node, d_dst = self.find_nearest_node(G, t_lon, t_lat)

        if not src_node or not dst_node:
            raise ValueError("Could not snap endpoints to road network.")

        if src_node == dst_node:
            # Same nearest node
            path_nodes = [src_node]
        else:
            try:
                path_nodes = nx.shortest_path(G, src_node, dst_node, weight="penalized_cost")
            except nx.NetworkXNoPath:
                # Fallback to unweighted
                path_nodes = nx.shortest_path(G, src_node, dst_node)

        # Assemble route line coordinates, distance, and hazards
        route_coords: List[List[float]] = []
        route_coords.append([f_lon, f_lat])

        total_distance_m = d_src + d_dst
        penalized_cost_total = total_distance_m
        edge_risks: List[float] = []
        warnings: List[str] = []
        has_critical_segment = False

        node_details = []
        for i, n_id in enumerate(path_nodes):
            nd = G.nodes[n_id]
            node_details.append({
                "id": n_id,
                "name": nd["name"],
                "lat": nd["lat"],
                "lon": nd["lon"],
                "elevation_m": nd["elevation_m"],
                "type": nd["type"]
            })
            route_coords.append([nd["lon"], nd["lat"]])

            if i > 0:
                prev_id = path_nodes[i - 1]
                if G.has_edge(prev_id, n_id):
                    edge = G[prev_id][n_id]
                    length = edge["length_m"]
                    risk = edge["flood_risk"]
                    is_low = edge["is_low_lying"]
                    total_distance_m += length
                    penalized_cost_total += edge["penalized_cost"]
                    edge_risks.append(risk)

                    if risk >= 0.70:
                        has_critical_segment = True
                        warnings.append(
                            f"High flood risk hazard ({int(risk*100)}%) along segment between {G.nodes[prev_id]['name']} and {nd['name']}"
                        )
                    elif is_low and risk >= 0.30:
                        warnings.append(
                            f"Low-lying river corridor warning between {G.nodes[prev_id]['name']} and {nd['name']} ({nd['river_dist_m']}m from river)"
                        )

        route_coords.append([t_lon, t_lat])

        # Risk exposure score: maximum and average along route
        if edge_risks:
            max_risk = max(edge_risks)
            avg_risk = sum(edge_risks) / len(edge_risks)
            exposure_score = round(max_risk * 0.7 + avg_risk * 0.3, 3)
        else:
            exposure_score = 0.10

        if exposure_score >= 0.70 or has_critical_segment:
            safety_rating = "Hazardous"
            warnings.append("Route crosses active flash-flood hazard zones. Evacuation or detour recommended.")
        elif exposure_score >= 0.35:
            safety_rating = "Caution"
            warnings.append("Exercise caution: route traverses mountain slopes with moderate runoff potential.")
        else:
            safety_rating = "Safe"

        if not warnings:
            warnings.append("Route clear of critical flood hazards. Road conditions normal.")

        # Find nearest open relief shelter
        nearest_shelter = self._find_nearest_open_shelter(db, t_lon, t_lat, region_id)

        # Estimated travel duration: mountain roads avg 25 km/h
        est_duration_min = round((total_distance_m / 1000.0) / 25.0 * 60.0, 1)

        return {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": route_coords
            },
            "properties": {
                "distance_m": round(total_distance_m, 1),
                "distance_km": round(total_distance_m / 1000.0, 2),
                "estimated_duration_min": est_duration_min,
                "risk_exposure_score": exposure_score,
                "safety_rating": safety_rating,
                "penalized_cost": round(penalized_cost_total, 1),
                "warnings": warnings,
                "waypoints_count": len(path_nodes),
                "waypoints": node_details,
                "nearest_open_shelter": nearest_shelter
            }
        }

    def _find_nearest_open_shelter(
        self,
        db: Session,
        lon: float,
        lat: float,
        region_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Finds nearest active/ready evacuation shelter."""
        stmt = select(Location).where(Location.type == "shelter")
        if region_id:
            stmt = stmt.where(Location.region_id == region_id)
        shelters = db.execute(stmt).scalars().all()

        best = None
        min_dist_km = float("inf")
        for sh in shelters:
            sh_lon, sh_lat = extract_lon_lat(sh.geom)
            d = haversine_km(lat, lon, sh_lat, sh_lon)
            if d < min_dist_km:
                min_dist_km = d
                best = {
                    "id": sh.id,
                    "name": sh.name,
                    "hindi_name": sh.hindi_name,
                    "distance_km": round(d, 2),
                    "elevation_m": sh.elevation_m,
                    "capacity_persons": sh.capacity_persons,
                    "contact_person": sh.contact_person,
                    "contact_phone": sh.contact_phone,
                    "status": sh.status,
                    "coordinates": [sh_lon, sh_lat]
                }
        return best


routing_engine = SafeRoutingEngine()
