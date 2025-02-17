use core::fmt;
use std::{collections::{hash_map::Entry, HashMap}, process::exit};

use geo::{point, Area, BoundingRect, Centroid, Contains, Geometry, GeometryCollection, MultiPolygon, Point, Rect};
use shapefile::{dbase::FieldValue, record};

// #[derive(Hash, Eq, PartialEq, Debug)]
// struct GridPolys {
//     bounds: str,
//     polys: MultiPolygon
// }


fn find_bbox(point: Point, grid_size: f64) -> String {
    // finds the bbox size and returns it as the string required for the hashmap lookup
    let tmp_x = point.x()/ grid_size;
    let tmp_y = point.y()/ grid_size;

    let lat_min = tmp_x.floor() * grid_size; 
    let lng_min =   tmp_y.floor() * grid_size;

    let lat_max = lat_min + grid_size;
    let lng_max = lng_min +  grid_size;
    // let xMin = 

    return format!("{:.1}:{:.1}:{:.1}:{:.1}", lat_min, lng_min, lat_max, lng_max);
}


fn main() {
    let filename = "/data/world.shp";

    // Open the shapefile for reading

    // let path = std::path::Path::new(filename);
    let mut reader: shapefile::Reader<std::io::BufReader<std::fs::File>, std::io::BufReader<std::fs::File>> = shapefile::Reader::from_path(filename).expect("something went wrong");
    let mut map: HashMap<String, GeometryCollection > = HashMap::new();

    // maybe take a step and try redoing the data gen stage if this doesnot work now 

    for result in reader.iter_shapes_and_records() {

        match result { 
            Ok((shape, record)) => {
                let gridbbox = record.get("GridBBox").expect("GridBox attribute must be set");
                let grid_box_str; 
                match gridbbox {
                    FieldValue::Character(Some(string)) => {
                        grid_box_str = string;}
                        ,
                    _ => {
                        exit(1) // exit if not set / not a string?
                    }
                }

                

                let geo_polygon = geo::Geometry::<f64>::try_from(shape).expect("didnt work - change later");
                // note this geomtry new_from is soon going to be replaced by new?? but on next version
                // map.entry(grid_box_str).and_modify(|field: &mut GeometryCollection| field[0] = geo_polygon).or_insert(GeometryCollection::new_from(vec![geo_polygon]));

                match map.entry(grid_box_str.to_string()) {
                    Entry::Vacant(e) => { 
                        e.insert(GeometryCollection::new_from(vec![geo_polygon])); 
                    
                    },
                        
                    Entry::Occupied(mut e) => {
                         e.get_mut().0.push(geo_polygon); 
                        }
                }
             
            

            },
            Err(e) => {
                    println!("Failed to unwrap shape {e}")
            }
        }


    }
    let lat =    38.07379014681535; 
    let lng = -121.4404606688909;
    let test_point = point!([lng,lat]);

    
    let bbox = find_bbox(test_point, 5.0);

    if map[&bbox].contains(&test_point){
        println!("point1 found");
    }
  
    println!("No point in polys");
    // // println!("Number of polygons: {}", shapefile.head);
    // // 34.297°, -116.246°

    // let test_point: Point = point!([0.00, 0.00]);

    // let found: bool = false;
    // // use std::time::Instant;
    // // let now = Instant::now();
    // println!("The useful size of `v` is {}", size_of_val(&*shapes));

    // for (shape, _) in shapes {
    //     let geo_polygon: geo::MultiPolygon<f64> = shape.into();
    //     if geo_polygon.unsigned_area() == 0.0 {
    //         println!("skipping");
    //         continue;
    //     }
    //     for poly in geo_polygon {
    //         if poly.contains(&test_point) {
    //             break;
    //         }
    //     }
    // }
    // if found {
    //     println!("Point found");
    // } else {
    //     println!("Not found");
    // }
    // // let elapsed = now.elapsed();
    // // println!("Elapsed: {:.2?}", elapsed);

    return;
}
