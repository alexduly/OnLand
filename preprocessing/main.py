from ast import Pass
from qgis.core import *
import sys
import os 
from preprocessing import shapes
from time import sleep

def clean_output():
    print("Deleting all output files... you have 5 seconds to cancel")

    for i in range(5,1, -1):
        print(f"Countdown: {i}", end="\r", flush=True)
        sleep(1)
        

    
    for dirpath, _, filenames in os.walk("data/output"):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")
    
    return


def main():

    if os.getenv("mode", default="prod") == "DEV":
        clean_output()
    # these i believe are required
    QgsApplication.setPrefixPath("/usr/share/qgis", True)
    sys.path.append('/usr/share/qgis/python/plugins')

    qgis = QgsApplication([], GUIenabled=False)
    Prj = QgsProject.instance()
    qgis.initQgis()

    Prj = QgsProject.instance()
    if Prj == None:
        print('Project didnt load, exiting')
        exit(1)

    #  TODO: fetch dataset via call, and invert using pyqgis ... 
    shapes.process_polygons(filepath="data/input/realworld.shp", Prj=Prj)
    qgis.exitQgis()
    return


if __name__ == "__main__":
    main()
