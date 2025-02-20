Steps for processing: 


Import hydro dataset 
Create grid of decided size
Calculate difference per grid
vector-> geometry -> single to multi part to get list of polys again


TODO: run ^ in a docker container in build time
Use QGIS to generate datapoints ( possibly on pre split dataset of on land and on water points -> point generation) 

Source: https://www.arcgis.com/home/item.html?id=e750071279bf450cbd510454a80f2e63
https://www.arcgis.com/sharing/rest/content/items/e750071279bf450cbd510454a80f2e63/data ( is the actual dataset downnload link?)
Dataset is then inverted so there are land polygons not water polygons

To do: auto pull and automate the inversion 