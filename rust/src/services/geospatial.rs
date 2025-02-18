use std::collections::HashMap;
use geo::Contains;
use geo::{GeometryCollection, Point};

fn find_bbox(point: Point, grid_size: f64) -> String {
    // finds the bbox size and returns it as the string required for the hashmap lookup
    let tmp_x = point.x() / grid_size;
    let tmp_y = point.y() / grid_size;

    let lat_min = tmp_x.floor() * grid_size;
    let lng_min = tmp_y.floor() * grid_size;

    let lat_max = lat_min + grid_size;
    let lng_max = lng_min + grid_size;
    // let xMin =

    return format!(
        "{:.1}:{:.1}:{:.1}:{:.1}",
        lat_min, lng_min, lat_max, lng_max
    );
}

pub fn check_point(
    // map: &RwLockReadGuard<'_, HashMap<String, GeometryCollection>>,
    map: &HashMap<String, GeometryCollection>,
    point: Point,
) -> bool {
    let bbox = find_bbox(point, 5.0); // need a way to set the grid size better

    match map.get(&bbox) {
        Some(grid) => {
            if grid.contains(&point) {
                return true;
            } else {
                return false;
            }
        }
        None => return false,
    }
}
