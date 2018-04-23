import math
import mapnik

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
factor = 3 # higher for higher res
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
query = """(
SELECT *
FROM planet_osm_line
WHERE tunnel IS NULL
  AND (highway IS NOT NULL OR admin_level = '8')
  AND bridge IS NULL
ORDER BY z_order
) AS roads_and_admin_lines
"""
layer.datasource = mapnik.PostGIS(
    host="docker.for.mac.localhost",
    user="postgres",
    password="",
    dbname="gis",
    table=query,
)
layer.srs = "+init=epsg:4326"
layer.styles.append("basic_style")
m.layers.append(layer)

# Render!
print("Rendering...")
mapnik.render_to_file(m, "nyc.png", "png")
print("Rendered to `nyc.png`.")
