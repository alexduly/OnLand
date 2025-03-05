import os
from qgis.PyQt.QtCore import QMetaType
import numpy as np
from tqdm import tqdm
import math
from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsProject,
    QgsRectangle,
    QgsVectorDataProvider,
    QgsVectorFileWriter,
    QgsVectorLayer,
    edit,
    QgsCoordinateTransformContext,
    QgsApplication

)
from typing import Literal
import processing
from processing.core.Processing import Processing
import warnings
import multiprocessing as mp


from functools import partial



MAX_WORKERS = mp.cpu_count()


warnings.filterwarnings("ignore", category=UserWarning,
                        message=".*file size.*")


def round_nearest_base(num, base=5, up=True):
    # used for generating grid squares
    if up:
        return math.ceil(num / base) * base
    else:
        return math.floor(num / base) * base


def clip_poly(grids: QgsFeature, crs, input_layer, input_biome, fields, x_step, y_step):
    
    result = []

    for grid in grids.getFeatures():

        grid_bbox = grid.geometry().boundingBox()
        # feature["GridBBox"] = f"{boundingBox}"
        overlay_single = QgsVectorLayer(
            path="Polygon", crs=crs, baseName="temp", providerLib="memory")
        provider_single: QgsVectorDataProvider | None = overlay_single.dataProvider()
        provider_single.addFeatures([grid])

        result_layer = processing.run("native:clip", {
            "INPUT": input_layer,
            "OVERLAY": overlay_single,
            'CRS': crs,
            "OUTPUT": "memory:",
        })["OUTPUT"]

        if input_biome == "water":
            result_layer = processing.run("native:difference", {
                'INPUT': overlay_single,
                'OVERLAY': result_layer, 'OUTPUT': 'TEMPORARY_OUTPUT', 'GRID_SIZE': None})["OUTPUT"]
        with edit(result_layer):
            for field in fields:
                result_layer.addAttribute(field)

        for clipped_feature in result_layer.getFeatures():
            clipped_feature: QgsFeature
            # pyqgis reverse lat an dlong. x == long y == lat in pyqgis
            new = QgsFeature(fields)

            if not clipped_feature.isValid():
                try:
                    fixed_geometry = clipped_feature.makeValid()
                    new.setGeometry(fixed_geometry.geometry())

                except:
                    print("unable to repair invalid feature, skipping")
                    continue
            else:
                new.setGeometry(clipped_feature.geometry())
            if new.geometry().area() == 0:
                tqdm.write("skipping as area == 0")
                continue
            new.setAttribute(
                # lng  min               lat min                      lng max         lat max
                "Grid", f"{grid_bbox.xMinimum()}:{grid_bbox.yMinimum()}:{grid_bbox.xMaximum()}:{grid_bbox.yMaximum()}")
            new.setAttribute("XStep", value=x_step)
            new.setAttribute("YStep", value=y_step)
            result.append(new)
        # output_layer.commitChanges()
        # pbar.update(1)


def process_polygons(filepath: str, input_biome: Literal["land", "water"], proj: QgsProject):
    '''
    Reads in input polgyon, generates grids, then clips out and assigns and ID for the rust server to use as the lookup
    to narrow down which polygons to search through. 


    '''
    Processing.initialize()

    shp_files = [each for each in os.listdir(
        filepath) if each.endswith('.shp')]

    if len(shp_files) != 1:
        print(f"{len(shp_files)} shp files ({shp_files}) found, please ensure there is exactly one in data/input")
        exit(1)

    print(f"Found shp file: {shp_files[0]}")
    input_layer = QgsVectorLayer(
        path=filepath+shp_files[0], baseName="InputLayer", providerLib="ogr")

    if not input_layer.isValid():
        print("failed to open shapefile, trying to fix")
        tmp = processing.run("native:repairshapefile", {'INPUT': filepath})
        print(tmp)
        input_layer = QgsVectorLayer(
            path=filepath, baseName="InputLayer", providerLib="ogr")

        if not input_layer.isValid():
            print(
                f"Input Layer failed to load from {filepath} and could not repair. Exiting...")
            exit(1)
    else:
        print("Input shapefile loaded")
    fix_count = 0
    with edit(input_layer):
        # try and change this to only run if an error gets caught?
        print("Checking geometry validity, will repair if necessary")
        for feature in tqdm(input_layer.getFeatures(), total=input_layer.featureCount(), desc=f"Validating input geometry. Fixed: {fix_count}", leave=True):
            if not feature.geometry().isGeosValid():
                try:
                    fixed_geometry = feature.geometry().makeValid()

                    feature.setGeometry(fixed_geometry)
                    # Update the layer's feature in the data provider
                    input_layer.updateFeature(feature)
                    fix_count += 1
                    tqdm.write(
                        f"Feature {feature.id()} geometry was fixed. Total fixed == {fix_count}")
                except Exception as e:
                    tqdm.write(
                        f"Failed to fix feature {feature.id()}: {e}. Total fixed == {fix_count}")

    print("Checks complete")

    init_extent = input_layer.extent()

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
    output_layer = QgsVectorLayer(
        "MultiPolygon", crs=input_layer.crs(), baseName="Output", providerLib="memory")

    #  so test poiints can read all of this wihtout having to re read in files
    proj.addMapLayers([grid_layer, input_layer, output_layer])

    x_step_field = QgsField(name="XStep", type=QMetaType.Int)

    grid_field_name = "Grid"
    grid_field = QgsField(name=grid_field_name,
                          type=QMetaType.QString, len=254)
    y_step_field = QgsField(name="YStep", type=QMetaType.Int)
    fields = QgsFields()
    fields.append([grid_field, x_step_field, y_step_field])
    processed = []
    
    with mp.Pool(processes=MAX_WORKERS) as pool:
                # results_list = pool.map(foo, inputs)  # Collect results in a list
                clip_poly_partial = partial(clip_poly,  crs=grid_layer.crs(), input_layer=input_layer, input_biome=input_biome, fields=fields, x_step=x_step, y_step=y_step) #, pbar=pbar)
                print('here')
                # for grid in tqdm(grid_layer.getFeatures(), total=grid_layer.featureCount(), desc="Processing Features", leave=True):
                res =  pool.map(clip_poly_partial,grid_layer.getFeatures(), chunksize=(grid_layer.featureCount()/MAX_WORKERS))
        # clip_poly(grid=grid, crs=grid_layer.crs(), input_layer=input_layer, input_biome=input_biome, fields=fields, x_step=x_step,y_step=y_step )
                print("result appended")
                processed.append(list(np.concatenate(res).flat))

    print("Polygons clipped, now adding to layer and saving ")
    with edit(output_layer):
        for field in fields:
            output_layer.addAttribute(field)
        # add bounding box to the output feature for ease of access for the rust server
        boundingBox = QgsFeature(fields)
        if not boundingBox:
            print("Unable to create bounding box")
            exit(1)

        boundingBox.setGeometry(QgsGeometry.fromRect(rounded_extent))
        boundingBox.setAttribute(grid_field_name, "Extent")
        boundingBox.setAttribute("XStep", value=x_step)
        boundingBox.setAttribute("YStep", value=y_step)
        processed.append(boundingBox)
        for item in processed:
            res = output_layer.addFeature(feature=item)
            if not res:
                # not sure if this shoudl cause a panic or not
                print(f"Feature could not be added {item.geometry()}")
        output_layer.updateExtents()

    # print(output_layer.featureCount())
    print("All processed polygons added to layer")

    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "ESRI Shapefile"
    outputFile = "/workspaces/data/output/shapes/world.shp"
    QgsVectorFileWriter.writeAsVectorFormatV3(
        layer=output_layer, fileName=outputFile, transformContext=QgsCoordinateTransformContext(), options=options)

    print(f"Processed polygons created and written to {outputFile}")
