from time import sleep
import sys  # noqa these have to imported in this order
sys.path.append('/usr/share/qgis/python/plugins')  # noqa these have to imported in this order
from generation import shapes
from testgen import testgen
from qgis.core import *
import os
import multiprocessing as mp

def clean_output():
    print("Deleting all output files... you have 5 seconds to cancel")

    for i in range(5, 1, -1):
        print(f"Countdown: {i}", end="\r", flush=True)
        sleep(1)

    for dirpath, _, filenames in os.walk("/workspaces/data/output"):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

    return


def main():

    # if os.getenv("mode", default="prod") == "DEV":
    #     clean_output()
    QgsApplication.setPrefixPath("/usr/share/qgis", True)

    qgis = QgsApplication([], GUIenabled=False)
    qgis.initQgis()
    Prj: QgsProject | None = QgsProject.instance()
    if Prj == None:
        print('Project didnt load, exiting')
        exit(1)

    # means if someone uploads a polygon of land, it wont get reversed
    input_biome = os.getenv("INPUT_BIOME", default="water")
    # ogr2ogr -f "ESRI Shapefile" data/input/shapes/  data/input/hydropolys.gdb  - just run processing cmd if gdb
    mp.set_start_method('spawn')

    shapes.process_polygons(filepath="data/input/UK/", input_biome=input_biome, proj=Prj)
    # if os.getenv("mode", default="prod") == "DEV":  # dont need test points  for prod
        # set via env eventually
    testgen.create_test_points(proj=Prj, points_count=10000)
    qgis.exitQgis()
    return


if __name__ == "__main__":
    main()
