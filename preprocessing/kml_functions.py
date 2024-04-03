from enum import Enum
import json
from typing import List, Union
from shapely import affinity
from shapely.geometry import GeometryCollection, Polygon, mapping, LineString
import copy
from functools import reduce
import math
import sys
from shapely.ops import split
import pandas as pd
import geopandas as gpd
from geopandas.tools import overlay
from shapely import wkt


class OutputFormat(Enum):
    Geojson = "geojson"
    Polygons = "polygons"
    GeometryCollection = "geometrycollection"


def check_crossing(
    lon1: float, lon2: float, validate: bool = True, dlon_threshold: float = 180.0
):
    """
    Assuming a minimum travel distance between two provided longitude coordinates,
    checks if the 180th meridian (antimeridian) is crossed.
    """
    if validate and (any(abs(x) > dlon_threshold) for x in [lon1, lon2]):
        raise ValueError("longitudes must be in degrees [-180.0, 180.0]")
    return abs(lon2 - lon1) > dlon_threshold


def translate_polygons(
    geometry_collection: GeometryCollection,
    output_format: OutputFormat = OutputFormat.Geojson,
) -> Union[List[dict], List[Polygon], GeometryCollection]:
    geo_polygons = []
    for polygon in geometry_collection.geoms:
        (minx, _, maxx, _) = polygon.bounds
        if minx < -180:
            geo_polygon = affinity.translate(polygon, xoff=360)
        elif maxx > 180:
            geo_polygon = affinity.translate(polygon, xoff=-360)
        else:
            geo_polygon = polygon

        geo_polygons.append(geo_polygon)

    if output_format == OutputFormat.Polygons:
        result = geo_polygons
    if output_format == OutputFormat.Geojson:
        result = [json.dumps(mapping(p)) for p in geo_polygons]
    elif output_format == OutputFormat.GeometryCollection:
        result = GeometryCollection(geo_polygons)

    return result


class AcceptedGeojsonTypes(Enum):
    Polygon = "Polygon"
    MultiPolygon = "MultiPolygon"


def split_coords(src_coords: List[List[List[float]]]) -> GeometryCollection:
    coords_shift = copy.deepcopy(src_coords)
    shell_minx = sys.float_info.max
    shell_maxx = sys.float_info.min

    # it is possible that the shape provided may be defined as more than 360
    #   degrees in either direction. Under these circumstances the shifted polygon
    #   would cross both the 180 and the -180 degree representation of the same
    #   meridian. This is not allowed, but checked for using the len(split_meriditans)
    split_meridians = set()

    for ring_index, ring in enumerate(coords_shift):
        if len(ring) < 1:
            continue
        else:
            ring_minx = ring_maxx = ring[0][0]
            crossings = 0

        for coord_index, (lon, _) in enumerate(ring[1:], start=1):
            lon_prev = ring[coord_index - 1][
                0
            ]  # [0] corresponds to longitude coordinate
            if check_crossing(lon, lon_prev, validate=False):
                direction = math.copysign(1, lon - lon_prev)
                coords_shift[ring_index][coord_index][0] = lon - (direction * 360.0)
                crossings += 1

            x_shift = coords_shift[ring_index][coord_index][0]
            if x_shift < ring_minx:
                ring_minx = x_shift
            if x_shift > ring_maxx:
                ring_maxx = x_shift

        # Ensure that any holes remain contained within the (translated) outer shell
        if ring_index == 0:  # by GeoJSON definition, first ring is the outer shell
            shell_minx, shell_maxx = (ring_minx, ring_maxx)
        elif ring_minx < shell_minx:
            ring_shift = [[x + 360, y] for (x, y) in coords_shift[ring_index]]
            coords_shift[ring_index] = ring_shift
            ring_minx, ring_maxx = (x + 360 for x in (ring_minx, ring_maxx))
        elif ring_maxx > shell_maxx:
            ring_shift = [[x - 360, y] for (x, y) in coords_shift[ring_index]]
            coords_shift[ring_index] = ring_shift
            ring_minx, ring_maxx = (x - 360 for x in (ring_minx, ring_maxx))

        if crossings:  # keep track of meridians to split on
            if ring_minx < -180:
                split_meridians.add(-180)
            if ring_maxx > 180:
                split_meridians.add(180)

    n_splits = len(split_meridians)
    if n_splits == 0:
        shell, *holes = src_coords
        split_polygons = GeometryCollection([Polygon(shell, holes)])
    elif n_splits == 1:
        split_lon = split_meridians.pop()
        meridian = [[split_lon, -90.0], [split_lon, 90.0]]
        splitter = LineString(meridian)

        shell, *holes = coords_shift
        split_polygons = split(Polygon(shell, holes), splitter)
    else:
        raise NotImplementedError(
            """Splitting a Polygon by multiple meridians (MultiLineString) 
               not supported by Shapely"""
        )
    return split_polygons


def split_polygon(
    geojson: dict, output_format: OutputFormat = OutputFormat.Geojson
) -> Union[List[dict], List[Polygon], GeometryCollection]:
    """
    Given a GeoJSON representation of a Polygon, returns a collection of
    'antimeridian-safe' constituent polygons split at the 180th meridian,
    ensuring compliance with GeoJSON standards (https://tools.ietf.org/html/rfc7946#section-3.1.9)

    Assumptions:
      - Any two consecutive points with over 180 degrees difference in
        longitude are assumed to cross the antimeridian
      - The polygon spans less than 360 degrees in longitude (i.e. does not wrap around the globe)
      - However, the polygon may cross the antimeridian on multiple occasions

    Parameters:
        geojson (dict): GeoJSON of input polygon to be split. For example:
                {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [179.0, 0.0], [-179.0, 0.0], [-179.0, 1.0],
                            [179.0, 1.0], [179.0, 0.0]
                        ]
                    ]
                }
        output_format (str): Available options: "geojson", "polygons", "geometrycollection"
                             If "geometrycollection" returns a Shapely GeometryCollection.
                             Otherwise, returns a list of either GeoJSONs or Shapely Polygons

    Returns:
        List[dict]/List[Polygon]/GeometryCollection: antimeridian-safe polygon(s)
    """
    geotype = AcceptedGeojsonTypes(geojson["type"])
    if geotype is AcceptedGeojsonTypes.Polygon:
        split_polygons = split_coords(geojson["coordinates"])
    elif geotype is AcceptedGeojsonTypes.MultiPolygon:
        split_polygons = reduce(
            GeometryCollection.union,
            (split_coords(coords) for coords in geojson["coordinates"]),
        )
    return translate_polygons(split_polygons, output_format)


# Function to convert GeoPandas geometry to GeoJSON
def geom_to_geojson(geometry):
    return geometry.__geo_interface__


### current approach for getting land area coverage ###
def get_all_land():
    # Read the data into GeoDataFrames
    minor_islands = gpd.read_file("../data/dump/naturalearth/ne_10m_minor_islands.shp")
    land = gpd.read_file("../data/dump/naturalearth/ne_10m_land.shp")

    # concat
    all_land = gpd.pd.concat([land, minor_islands], ignore_index=True)

    # 3. Standardize CRS and intersect with your regions
    return all_land.to_crs("EPSG:4326")  # Convert to WGS84 CRS


def grouped_area(gis_overlay, featurecla):
    gis_overlay = gis_overlay[gis_overlay["featurecla"] == featurecla]
    gis_overlay["region_area"] = gis_overlay.area / 1e6
    gis_overlay = (
        gis_overlay.groupby("region_id")["region_area"]
        .sum()
        .reset_index(name="region_area")
    )
    return gis_overlay


# Function to split polygons at the antimeridian
def split_antimeridian(gdf, geometry_column="polygon", id_column="region_id"):
    split_geometries = []
    for _, row in gdf.iterrows():
        geom = row[geometry_column]
        geojson_geom = geom_to_geojson(geom)
        if isinstance(geojson_geom["coordinates"], list):
            geojson_geom["coordinates"] = geojson_geom["coordinates"][0]
        converted_coordinates = [
            [list(point) for point in ring] for ring in geojson_geom["coordinates"]
        ]
        geojson_geom = {"type": "Polygon", "coordinates": converted_coordinates}
        split_geom = split_polygon(geojson_geom, OutputFormat.Polygons)
        df = gpd.GeoDataFrame(geometry=split_geom)
        df[id_column] = row[id_column]
        split_geometries.append(df)
    # concatenate
    return pd.concat(split_geometries)


def split_regions(gis_regions):
    """
    requires:
    completed,
    gis_region
    region_id

    returns:
    completed,
    geometry
    region_id
    """

    # start work on gis_regions
    gis_regions = gis_regions.rename(columns={"completed": "gis_completed"})
    gis_notnull = gis_regions[gis_regions["gis_region"].notnull()]

    # check whether null
    gis_notnull["gis_region"] = gis_notnull["gis_region"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(gis_notnull, geometry="gis_region")

    # Split antimeridian
    gdf = gdf.explode(index_parts=True)
    unique_regions = gdf[["region_id", "gis_region"]].drop_duplicates()
    gdf = split_antimeridian(unique_regions, geometry_column="gis_region")
    gdf.set_crs("EPSG:4326", inplace=True)
    gdf["gis_valid"] = gdf["geometry"].is_valid

    return gdf


def calculate_gis_area(gdf):
    """
    NB: not complete matching Rachel's numbers here.
    Would be good to trace back why exactly. However,
    1) for most regions the numbers are very close.
    2) for the regions where the numbers differ ours are correct, examples where we diverge:
    2.1.) Temple of the Jedi (entry_id: 812) we have basically all land on earth (which is correct)
    2.2.) Old Kingdom Religion at Abydos (entry_id: 1106) we have very small (which is correct)
    3) we are using "not completed" regions as well here, but we are flagging this.

    assumes that gdf is already split at antimeridian.
    """

    # Get all land
    all_land = get_all_land()

    # Intersecting with regions
    gis_overlay = overlay(all_land, gdf, how="intersection")

    # Figure out whether this is a good projection
    gis_overlay.to_crs("+proj=cea", inplace=True)

    # Take Land where applicable
    gis_land = grouped_area(gis_overlay, "Land")
    region_land = gis_land["region_id"].unique().tolist()

    # Take Minor islands where Land not applicable
    gis_islands = gis_overlay[~gis_overlay["region_id"].isin(region_land)]
    gis_islands = grouped_area(gis_islands, "Minor island")
    region_island = gis_islands["region_id"].unique().tolist()

    # Take base value when nothing applicable
    regions_completed = region_land + region_island
    gis_missing = gdf[~gdf["region_id"].isin(regions_completed)]
    gis_missing = gpd.GeoDataFrame(gis_missing, geometry="geometry")
    gis_missing.set_crs("EPSG:4326", inplace=True)
    gis_missing.to_crs("+proj=cea", inplace=True)
    gis_missing["region_area"] = gis_missing.area / 1e6
    gis_missing = gis_missing[["region_id", "region_area"]]

    # Flags
    gis_land["region_type"] = "Land"
    gis_islands["region_type"] = "Minor island"
    gis_missing["region_type"] = "No Match"

    # Concat
    gis_area = pd.concat([gis_land, gis_islands, gis_missing], ignore_index=True)

    # merge back with metadata
    gis_metadata = gis_area.merge(gdf, on="region_id", how="inner")

    return gis_metadata
