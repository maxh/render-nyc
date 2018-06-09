import math
import mapnik

manhattan_outline = """
{
  "type": "Polygon",
  "coordinates": [[
    [
      -73.93180847167969,
      40.88133311333721
    ],
    [
      -74.00115966796875,
      40.773261878622634
    ],
    [
      -74.02725219726562,
      40.714476284709335
    ],
    [
      -74.02725219726562,
      40.69521661351715
    ],
    [
      -73.99703979492188,
      40.704066343242474
    ],
    [
      -73.97575378417969,
      40.70875101828792
    ],
    [
      -73.96614074707031,
      40.72696606629052
    ],
    [
      -73.96751403808594,
      40.7451761300463
    ],
    [
      -73.93730163574219,
      40.77898159474759
    ],
    [
      -73.92494201660156,
      40.80133575979202
    ],
    [
      -73.92906188964844,
      40.83667117059108
    ],
    [
      -73.90159606933594,
      40.873545407754946
    ],
    [
      -73.93180847167969,
      40.88133311333721
    ]
  ]]
}

"""

# Helpers to convert from lat/lon to web mercator. From:
# https://wiki.openstreetmap.org/wiki/Mercator#Python_implementation
def merc_x(lon):
  r_major = 6378137.000
  return r_major * math.radians(lon)

def merc_y(lat):
  if lat > 89.5:
    lat = 89.5
  if lat < -89.5:
    lat = -89.5
  r_major = 6378137.000
  r_minor = 6356752.3142
  temp = r_minor / r_major
  eccent = math.sqrt(1 - temp ** 2)
  phi = math.radians(lat)
  sinphi = math.sin(phi)
  con = eccent * sinphi
  com = eccent / 2
  con = ((1.0 - con) / (1.0 + con)) ** com
  ts = math.tan((math.pi / 2 - phi) / 2) / con
  y = 0 - r_major*math.log(ts)
  return y

# Compute the bounds.
top_left_lon = -74.06
top_left_lat = 41.12
bottom_right_lon = -73.90
bottom_right_lat = 40.85
box_coords = [
  merc_x(bottom_right_lon),
  merc_y(bottom_right_lat),
  merc_x(top_left_lon),
  merc_y(top_left_lat),
]
bounds = mapnik.Box2d(*box_coords)

# Create the map.
factor = 4 # higher for higher res
m = mapnik.Map(1024*factor, 2048*factor)
m.background = mapnik.Color("#FFFFFF")
m.aspect_fix_mode = mapnik.aspect_fix_mode.ADJUST_BBOX_HEIGHT
m.zoom_to_box(bounds)

# Create the style.
s = mapnik.Style()
r = mapnik.Rule()
line_symbolizer = mapnik.LineSymbolizer()
line_symbolizer.stroke_width = 1.95
r.symbols.append(line_symbolizer)
s.rules.append(r)
m.append_style("basic_style", s)

# Create the layer.
layer = mapnik.Layer("osm_lines")
query = (
"""
(
  SELECT *
  FROM (
    (
      SELECT *
      FROM planet_osm_polygon
      WHERE waterway = 'riverbank'
        AND tunnel IS NULL
      ORDER BY z_order
    )
    UNION ALL
    (
      SELECT *
      FROM planet_osm_line
      WHERE tunnel IS NULL
        AND bridge IS NULL
        AND highway IS NOT NULL
      ORDER BY z_order
    )
  ) AS t
  WHERE ST_Intersects(
    t.way,
    ST_Transform(
      ST_SetSRID(
        ST_GeomFromGeoJSON('%s'),
        4326
      ),
      3857
    )
  )
)
AS shores_and_roads
"""
% manhattan_outline
)
layer.datasource = mapnik.PostGIS(
    host="docker.for.mac.localhost",
    user="postgres",
    password="",
    dbname="osm_nyc",
    table=query,
)
layer.srs = "+init=epsg:4326"
layer.styles.append("basic_style")
m.layers.append(layer)

# Render!
print("Rendering...")
mapnik.render_to_file(m, "nyc.png", "png")
print("Rendered to `nyc.png`.")
