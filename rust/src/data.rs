use std::{collections::{hash_map::Entry, HashMap}, process::exit};

use geo::GeometryCollection;
use shapefile::dbase::FieldValue;



pub fn load_polys(filename: &str)->  HashMap<String, GeometryCollection >{
    println!("Loading shapefile now, please be patient...");
    let mut reader: shapefile::Reader<std::io::BufReader<std::fs::File>, std::io::BufReader<std::fs::File>> = shapefile::Reader::from_path(filename).expect("something went wrong");
    let mut map: HashMap<String, GeometryCollection > = HashMap::new();

    for result in reader.iter_shapes_and_records() {

        match result { 
            Ok((shape, record)) => {
                let grid_field_value = record.get("Grid").expect("Grid attribute must be set");
                let grid_str: &String; 
                match grid_field_value {
                    FieldValue::Character(Some(string)) => {
                        grid_str = string;}
                        ,
                    _ => {
                        println!("Grid attribute was not a string, exiting");
                        exit(1) // exit if not set / not a string?
                    }
                }

                let geo_polygon = geo::Geometry::<f64>::try_from(shape).expect("didnt work - change later");
                // note this geomtry new_from is soon going to be replaced by new?? but on next version

                match map.entry(grid_str.to_string()) {
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
    return map;
}