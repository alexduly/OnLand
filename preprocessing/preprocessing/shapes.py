from qgis.core import *
from qgis.PyQt.QtCore import QMetaType
from tqdm import tqdm
import math


def round_nearest_base(num, base=5, up=True):
    # used for generating grid squares
    if up:
        return math.ceil(num / base) * base
    else:
        return math.floor(num / base) * base




def process_polygons(filepath: str, Prj: QgsProject):
    import processing
    from processing.core.Processing import Processing
    Processing.initialize()

    input_layer = QgsVectorLayer(
        filepath, baseName="InputLayer", providerLib="ogr")
    if not input_layer.isValid():
        print("Layer failed to load!")
        exit(1)
    init_extent = input_layer.extent()

    # print(f"xMax: {extent.xMaximum()}, xmin: {extent.xMinimum()}, ymax: {extent.yMaximum()}, ymin: {extent.yMinimum()}")
    # exit(1)
    # x == lng , y == lat!
    new_xmin = round_nearest_base(init_extent.xMinimum(), up=False)
    new_xmax = round_nearest_base(init_extent.xMaximum(), up=True)
    new_ymin = round_nearest_base(init_extent.yMinimum(), up=False)
    new_ymax = round_nearest_base(init_extent.yMaximum(), up=True)

    # add in checks to make sure they are not out of bounds of the world. ie -/+90, -/+180

    if new_xmin < -180.0:
        print(f"changing xmin {new_xmin}" )
        new_xmin = -180.0
    if new_xmax > 180.0:
        print(f"changing xmin {new_xmax}" )

        new_xmax = 180.0
    if new_ymin < -90.0:
        print(f"changing xmin {new_ymin}" )

        new_ymin = -90.0
    if new_ymax > 90.0:
        print(f"changing xmin {new_ymax}" )
        new_ymax = 90.0

    rounded_extent: QgsRectangle = QgsRectangle(
        new_xmin, new_ymin, new_xmax, new_ymax)

    grid_layer: QgsVectorLayer = processing.run("native:creategrid",
                                                {'TYPE': 2,
                                                 'EXTENT': rounded_extent,
                                                 'HSPACING': 5,
                                                 'VSPACING': 5,
                                                 'HOVERLAY': 0,
                                                 'VOVERLAY': 0,
                                                 'CRS': input_layer.crs(),
                                                 'OUTPUT': 'TEMPORARY_OUTPUT'})["OUTPUT"]
    grid_layer.startEditing()

    grid_field_name = "Grid"
    grid_field = QgsField("Grid", QMetaType.QString)

    grid_layer.addAttribute(grid_field)

    output_layer = QgsVectorLayer(
        "Polygon?crs=" + input_layer.crs().authid(), "Clipped Results", "memory")

    Prj.addMapLayers([grid_layer, input_layer, output_layer])

    provider: QgsVectorDataProvider | None = output_layer.dataProvider()
    provider.addAttributes(grid_layer.fields())
    output_layer.updateFields()

    # add bounding box to the output feature for ease of access for the rust server 
    boundingBox = QgsFeature()
    boundingBox.setGeometry(rounded_extent)
    boundingBox.setAttribute(grid_field_name, "Extent")
    provider.addFeature(boundingBox)
    
    
    
    count = 0 

    for feature in tqdm(grid_layer.getFeatures(), total=grid_layer.featureCount(), desc="Processing Features", leave=True):
        feature: QgsFeature
        grid_bbox = feature.geometry().boundingBox()

        # feature["GridBBox"] = f"{boundingBox}"
        overlay_single = QgsVectorLayer(
            "Polygon?crs=" + grid_layer.crs().authid(), "temp", "memory")
        provider_single = overlay_single.dataProvider()
        provider_single.addFeatures([feature])

        result_layer = processing.run("native:clip", {
            "INPUT": input_layer,
            "OVERLAY": overlay_single,
            "OUTPUT": "memory:",
        })["OUTPUT"]
        result_layer.startEditing()
        result_layer.addAttribute(grid_field)
        result_layer.updateFields()

        for clipped_feature in result_layer.getFeatures():
            clipped_feature: QgsFeature
            # pyqgis reverse lat an dlong. x == long y == lat in pyqgis
            clipped_feature[grid_field_name] = f"{grid_bbox.xMinimum()}:{grid_bbox.yMinimum()}:{grid_bbox.xMaximum()}:{grid_bbox.yMaximum()}"
            provider.addFeature(clipped_feature)

        count +=1
        if count == 5:
            break
   

    output_layer.updateExtents()
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "ESRI Shapefile"

    QgsVectorFileWriter.writeAsVectorFormatV3(
        output_layer, 'data/output/world.shp', QgsCoordinateTransformContext(), options)
