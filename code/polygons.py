"""Load the victim-location polygons and attach people to them geometrically.

The polygons live in data/coord_area.geojson. Each Feature carries:

    name_he       Hebrew area name, e.g. "בארי; אשלים"
    name_en       English name, taken from the database's "Event location"
    source_text   link text for a publication that already published the
                  addresses in this area
    source_url    the publication itself; an area that has one is treated as
                  already public
    public_exact  True when source_url is set -> its people may be shown as
                  exact markers on the public map. False -> the public map
                  shows the polygon only, and exact markers appear on the
                  private map alone.

Geometry may be null: some rows exist only to record that a place is public,
without anyone ever having drawn a ring for it.

People are never listed in the file. They are attached at build time by
testing their event coordinate against the rings, so an area holding forty
victims costs one ring rather than forty duplicated coordinates. That also
means renaming a place in the database cannot orphan its polygon, which is
what used to happen: "נתיבות; קריית משה" in the tsv never matched
"נתיבות; קרית משה" in the database, so three people the polygon existed to
blur were published as an exact marker instead.
"""
import json
import os

from shapely.geometry import Point, shape

GEOJSON = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       'data', 'coord_area.geojson')


def load_polygons(path=GEOJSON):
    """Return [(properties, shapely geometry or None), ...]."""
    with open(path, encoding='utf-8') as f:
        fc = json.load(f)
    out = []
    for feat in fc['features']:
        geom = shape(feat['geometry']) if feat['geometry'] else None
        out.append((feat['properties'], geom))
    return out


def assign(lat, lon, polygons=None):
    """Return the properties of the area containing (lat, lon), else None."""
    if polygons is None:
        polygons = load_polygons()
    pt = Point(lon, lat)
    for props, geom in polygons:
        if geom is not None and geom.contains(pt):
            return props
    return None


def area_for(place_name, coo=None, polygons=None):
    """The area a person belongs to, given their place name and coordinate.

    The recorded place name decides whenever it names a known area: one with a
    ring, or one whose addresses a publication already made public. Geometry is
    the fallback, and it is what catches people whose place name is spelled
    differently from the area's, or is coarser than it.
    """
    if polygons is None:
        polygons = load_polygons()
    for props, geom in polygons:
        if props['name_he'] == (place_name or '').strip():
            if props['public_exact'] or geom is not None:
                return props
            break
    return assign(coo[0], coo[1], polygons) if coo else None


def blurred(lat, lon, polygons=None):
    """The area whose polygon should replace this point on the public map.

    None means the point may be published as-is, either because it falls in no
    area or because the area's addresses were already published by the media.
    """
    props = assign(lat, lon, polygons)
    if props is None or props['public_exact']:
        return None
    return props