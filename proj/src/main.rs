use geo::{point, Area, Contains};
fn main() {

    let filename = "WestCoatUSAGridDiff/WestCoatUSAGridDiff.shp";
    let shapes = shapefile::read_as::<_, shapefile::Polygon, shapefile::dbase::Record>(
        filename,
    )
    .expect("Could not open polygon-shapefile");
    // 34.297°, -116.246°

    let test_point = point!([-118.245, 35.297]);

    use std::time::Instant;

    for (shape, _) in shapes {
        let geo_polygon: geo::MultiPolygon<f64> = shape.into();
        if geo_polygon.unsigned_area() == 0.0 {
            println!("skipping");
            continue;
        }

        for poly in geo_polygon {
            let now = Instant::now();

            if poly.contains(&test_point) {
                println!("Point found");
                let elapsed = now.elapsed();
                println!("Elapsed: {:.2?}", elapsed);
                break;
            }
        }
        
    }
    return;
}
