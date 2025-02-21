use csv::Reader;
use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct TestPoint {
   pub lat: f64,
   pub lng: f64,
   pub land: bool,
}

pub fn read_test_points() -> Result<Vec<TestPoint>, csv::Error> {
    /* Reads in test points from csv */
    let mut reader = Reader::from_path("/data/test_data/test_points.csv")?; 
    let records = reader
        .deserialize::<TestPoint>()
        .collect::<Result<Vec<TestPoint>, csv::Error>>()?;

    Ok(records)
}
