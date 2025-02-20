from qgis.core import *
import pandas as pd
from tqdm import tqdm
from qgis.PyQt.QtCore import QMetaType

# add in a function to load test data via a file that runs if the proj is empty. will save me having to regernate grids every time


def loadLayer():
    output_layer = QgsVectorLayer(
        "/workspaces/data/output/shapes/world.shp", baseName="output_layer", providerLib="ogr")
    if not output_layer.isValid():
        print("Layer failed to load. Exiting...")
        exit(1)
    else:
        print("Output shapefile loaded")
    return output_layer


def create_test_points(proj: QgsProject, points_count: int):
    '''
    Passing project reference, instead of reading in file as in prod this will run as a oner and should save resource reading in data?
    but open to changing/ playing around with
    '''
    import processing
    from processing.core.Processing import Processing
    Processing.initialize()

    output = proj.mapLayersByName("Output")

    if output == []:
        print("Unable to get layer, trying direct from file.")
        output_layer = loadLayer()
    else:
        output_layer = output[0]


    points_layer: QgsVectorLayer = processing.run(algOrName="native:randompointsinextent",
                                                 parameters={"EXTENT": output_layer.extent(),
                                                             "POINTS_NUMBER": points_count,
                                                             "MIN_DISTANCE": 0,
                                                             "TARGET_CRS": output_layer.crs(),
                                                             "MAX_ATTEMPTS": 200,
                                                             "OUTPUT": "TEMPORARY_OUTPUT"})["OUTPUT"]
    if not points_layer.isValid():
        print("Invalid points layer generated. Exiting...")
        exit(1)
    else:
        print("Points generated")
    rows = []
    # do not want the extent in this or eveyrthing will be considered on land
    request = QgsFeatureRequest().setSubsetOfAttributes(
        ['Grid'], output_layer.fields()).setFilterExpression('"Grid"!=\'Extent\'')
    ids = [f.id() for f in output_layer.getFeatures(request)]
    output_layer.selectByIds(ids)

    filtered_output_layer = QgsVectorLayer(
        "Polygon?crs=" + output_layer.crs().authid(), baseName="FilteredOutput", providerLib="memory")
    filtered_output_layer_data = filtered_output_layer.dataProvider()

    # Add selected features to the new layer
    filtered_output_layer_data.addFeatures(output_layer.selectedFeatures())

    filtered_output_layer.updateExtents()

    if not output_layer.featureCount() - filtered_output_layer.featureCount() == 1:
        print("Removing extent polygon failed... will not be able to classify points. Exiting...")
        exit(1)

    processing.run("native:selectbylocation",
                   {"INPUT": points_layer,
                    # the within ( figure out if you can get this via enum)
                    "PREDICATE": [6],
                    # QgsProcessingFeatureSourceDefinition(output_layer, selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                    "INTERSECT":  filtered_output_layer,
                    "METHOD": 1  # create new selection
                    })

    land_field = QgsField(name="Land", type=QMetaType.Bool)

    points_layer.startEditing()
    
    points_layer.addAttribute(land_field)

    points_layer.updateFields()
    
  
    
    rows = []
    for points_feature in tqdm(points_layer.selectedFeatures(), total=points_layer.selectedFeatureCount(), desc="Processing Land points", leave=True):
        pointsFtr: QgsFeature
        point: QgsPointXY = points_feature.geometry().asPoint()
        points_feature["Land"] = True

        if not output_layer.extent().contains(point):
            print(f'point out of extent??{point}')

        rows.append({
            "Lat": point.y(),
            "Lng": point.x(),
            "Land": True,
        })
        points_layer.updateFeature(points_feature)

    points_layer.invertSelection()
    for points_feature in tqdm(points_layer.selectedFeatures(), total=points_layer.selectedFeatureCount(), desc="Processing Water points", leave=True):
        pointsFtr: QgsFeature
        point: QgsPointXY = points_feature.geometry().asPoint()
        if not output_layer.extent().contains(point):
            print(f'point out of extent??{point}')
        points_feature["Land"] = False

        rows.append({
            "Lat": point.y(),
            "Lng": point.x(),
            "Land": False,
        })
        points_layer.updateFeature(points_feature)


    points_layer.commitChanges()
    df = pd.DataFrame(rows, columns=["Lat", "Lng", "Land"])
    # df = df.sample(frac = 1).round(5) # shuffle the rows so that the land/water points are mixed up

    df.to_csv("/workspaces/data/output/test_data/test_points.csv", index=False)

    # points.
    # debug write to shape file
    

    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "ESRI Shapefile"
    outputFile = "/workspaces/data/output/test_data/points.shp"
    QgsVectorFileWriter.writeAsVectorFormatV3(
        layer=points_layer, fileName=outputFile, transformContext=QgsCoordinateTransformContext(), options=options)

    print(f"Processed points created and written to {outputFile}")
