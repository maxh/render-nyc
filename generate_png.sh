docker cp ./render_nyc.py render_nyc:/
docker cp ./outline.geojson render_nyc:/
docker exec render_nyc python2 /render_nyc.py
docker cp render_nyc:/nyc.png ./
killall Preview 2>/dev/null
open -a Preview ./nyc.png
