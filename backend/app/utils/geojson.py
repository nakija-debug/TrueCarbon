"""GeoJSON utility functions for spatial operations."""

from typing import Optional
from sqlalchemy import text
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping, shape
import json


def geometry_to_geojson(geometry) -> dict:
    """
    Convert GeoAlchemy2 Geometry to GeoJSON dict.

    Args:
        geometry: GeoAlchemy2 Geometry object

    Returns:
        GeoJSON geometry dict with type and coordinates
    """
    if geometry is None:
        return None

    # Convert to Shapely shape
    shapely_shape = to_shape(geometry)

    # Convert to GeoJSON
    return mapping(shapely_shape)


def geojson_to_wkt(geojson: dict) -> str:
    """
    Convert GeoJSON to WKT format for database insertion.

    Args:
        geojson: GeoJSON geometry dict

    Returns:
        WKT string representation
    """
    if not geojson or "type" not in geojson:
        raise ValueError("Invalid GeoJSON format")

    # Convert GeoJSON to Shapely
    shapely_shape = shape(geojson)

    # Return WKT
    return shapely_shape.wkt


def geojson_to_postgis_sql(geojson: dict, srid: int = 4326) -> str:
    """
    Convert GeoJSON to PostGIS SQL format.

    Args:
        geojson: GeoJSON geometry dict
        srid: Spatial Reference System ID (default 4326 for WGS84)

    Returns:
        SQL ST_GeomFromText() expression
    """
    wkt = geojson_to_wkt(geojson)
    return f"ST_GeomFromText('{wkt}', {srid})"


def calculate_area_hectares_sql(geometry_col: str, table: str = None) -> str:
    """
    Generate SQL to calculate area in hectares using PostGIS.

    Uses ST_Area with geography cast to get accurate area in square meters,
    then converts to hectares (1 ha = 10,000 m²).

    Args:
        geometry_col: Name of geometry column
        table: Optional table name for context

    Returns:
        SQL expression for area calculation
    """
    if table:
        col = f"{table}.{geometry_col}"
    else:
        col = geometry_col

    return f"ST_Area({col}::geography) / 10000.0"
