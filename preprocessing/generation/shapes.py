import os
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


def process_polygons(filepath: str, proj: QgsProject):
    import processing
    from processing.core.Processing import Processing
    Processing.initialize()

    input_layer = QgsVectorLayer(
        filepath, baseName="InputLayer", providerLib="ogr")
    if not input_layer.isValid():
        print("Layer failed to load. Exiting...")
        exit(1)
    else: 
        print("Input shapefile loaded")
    init_extent = input_layer.extent()

    # print(f"xMax: {extent.xMaximum()}, xmin: {extent.xMinimum()}, ymax: {extent.yMaximum()}, ymin: {extent.yMinimum()}")
    # exit(1)
    # x == lng , y == lat!

    x_step = int(os.getenv("X_STEP", default="5"))
    y_step = int(os.getenv("X_STEP", default="5"))

    new_xmin = round_nearest_base(
        init_extent.xMinimum(), base=x_step,  up=False)
    new_xmax = round_nearest_base(init_extent.xMaximum(), base=x_step, up=True)
    new_ymin = round_nearest_base(
        init_extent.yMinimum(), base=y_step, up=False)
    new_ymax = round_nearest_base(init_extent.yMaximum(), base=y_step, up=True)

    # add in checks to make sure they are not out of bounds of the world. ie -/+90, -/+180

    if new_xmin < -180.0:
        print(f"changing xmin {new_xmin}")
        new_xmin = -180.0
    if new_xmax > 180.0:
        print(f"changing xmin {new_xmax}")

        new_xmax = 180.0
    if new_ymin < -90.0:
        print(f"changing xmin {new_ymin}")

        new_ymin = -90.0
    if new_ymax > 90.0:
        print(f"changing xmin {new_ymax}")
        new_ymax = 90.0

    rounded_extent: QgsRectangle = QgsRectangle(
        new_xmin, new_ymin, new_xmax, new_ymax)

    grid_layer: QgsVectorLayer = processing.run("native:creategrid",
                                                {'TYPE': 2,
                                                 'EXTENT': rounded_extent,
                                                 'HSPACING': x_step,
                                                 'VSPACING': y_step,
                                                 'HOVERLAY': 0,
                                                 'VOVERLAY': 0,
                                                 'CRS': input_layer.crs(),
                                                 'OUTPUT': 'TEMPORARY_OUTPUT'})["OUTPUT"]

    if grid_layer.featureCount() == 0:
        print("No grids were generated, exiting...")
        exit(1)
    else:
        print("Grids created")

    grid_field_name = "Grid"
    grid_field = QgsField(name=grid_field_name, type=QMetaType.QString, len=254)
    x_step_field = QgsField(name="XStep", type=QMetaType.Int)
    y_step_field = QgsField(name="YStep", type=QMetaType.Int)
    fields = QgsFields()
    fields.append([grid_field, x_step_field, y_step_field])

    output_layer = QgsVectorLayer(
        "Polygon?crs=" + input_layer.crs().authid(), baseName="Output", providerLib="memory")

    proj.addMapLayers([grid_layer, input_layer, output_layer]) # so test poiints can read all of this wihtout having to re read in files

    provider: QgsVectorDataProvider | None = output_layer.dataProvider()
    output_layer.startEditing()
    provider.addAttributes(fields)
    output_layer.updateFields()

    # add bounding box to the output feature for ease of access for the rust server
    boundingBox = QgsFeature(fields)
    if not boundingBox:
        print("Unable to create bounding box")
        exit(1)

    boundingBox.setGeometry(QgsGeometry.fromRect(rounded_extent))
    boundingBox.setAttribute(grid_field_name, "Extent")
    boundingBox.setAttribute("XStep", value=x_step)
    boundingBox.setAttribute("YStep", value=y_step)

    provider.addFeature(boundingBox)


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

        
        
        

    output_layer.updateExtents()   
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "ESRI Shapefile"
    outputFile = "/workspaces/data/output/shapes/world.shp"
    QgsVectorFileWriter.writeAsVectorFormatV3(
        layer=output_layer, fileName=outputFile, transformContext=QgsCoordinateTransformContext(), options=options)
    
    print(f"Processed polygons created and written to {outputFile}")