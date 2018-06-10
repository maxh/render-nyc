docker cp ./render_nyc.py render_nyc:/
docker cp ./outline.geojson render_nyc:/
docker exec render_nyc python2 /render_nyc.py --format svg
docker cp render_nyc:/nyc.svg ./
