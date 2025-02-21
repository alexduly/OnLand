


use geo::Contains;
use geo::{GeometryCollection, Point};
use std::collections::HashMap;

fn find_bbox(point: Point, grid_size: f64) -> String {
    // finds the bbox size and returns it as the string required for the hashmap lookup
    // maybe add offset?
    // TODO: needs to be expanded to consider the dataset in terms of start end/point.
    let tmp_x = point.x() / grid_size;
    let tmp_y = point.y() / grid_size;

    let lng_min = tmp_x.floor() * grid_size;
    let lat_min = tmp_y.floor() * grid_size;

    let lng_max = lng_min + grid_size;
    let lat_max = lat_min + grid_size;
    // let xMin =

    return format!(
        "{:.1}:{:.1}:{:.1}:{:.1}",
        lng_min, lat_min, lng_max, lat_max
    );
}

pub fn check_point(map: &HashMap<String, GeometryCollection>, point: Point) -> bool {
    let bbox = find_bbox(point, 5.0); // need a way to set the grid size better

    log::info!("BBox of point {}", bbox);
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

#[cfg(test)]
mod tests {
    use super::*;
    use geo::{point, GeometryCollection, LineString, Polygon};

    #[test]
    fn test_good_bbox() {
        let grid_size = 5.0;
        let point1 = point!([3.4, 4.2]);
        let result1 = find_bbox(point1, grid_size);
        assert_eq!(result1, "0.0:0.0:5.0:5.0");

        // testing negative points too
        let point2 = point!([-4.9, 0.3]);
        let result2 = find_bbox(point2, grid_size);
        assert_eq!(result2, "-5.0:0.0:0.0:5.0");
       // testing negative points too
        let point3 = point!([0.4, -3.6]);
        let result3 = find_bbox(point3, grid_size);
        assert_eq!(result3, "0.0:-5.0:5.0:0.0");

        // edge
        let point4 = point!([0.0, 0.0]);
        let result4 = find_bbox(point4, grid_size);
        assert_eq!(result4, "0.0:0.0:5.0:5.0");
    }

    #[test]
    fn test_check_point() {
        let polygon1 = Polygon::new(
            LineString::from(vec![
                (-4.0, 1.0),
                (-3.0, 1.0),
                (-3.0, 2.0),
                (-4.0, 2.0),
                (-4.0, 1.0),
            ]),
            vec![],
        );
        let polygon2 = Polygon::new(
            LineString::from(vec![(-1.0, 3.0), (0.0, 4.0), (1.0, 3.0), (-1.0, 3.0)]),
            vec![],
        );

        let polygon3 = Polygon::new(
            LineString::from(vec![
                (-5.0, -1.0),
                (-4.0, -1.0),
                (-4.0, 0.0),
                (-5.0, 0.0),
                (-5.0, -1.0),
            ]),
            vec![],
        );

        let test_collection = GeometryCollection::from(vec![polygon1, polygon2, polygon3]);
        let mut grid_map: HashMap<String, GeometryCollection> = HashMap::new();
        grid_map.insert("-5.0:0.0:0.0:5.0".to_string(), test_collection.clone());

        let point1 = point!([-3.5, 1.5]); // returns true. inside grid  insdie poly
        let point2 = point!([-2.0, 4.0]); // retunrs false  inside grid, not inside poly
        let point3 = point!([6.0, 6.0]); // returns false  outside grid
        assert!(check_point(&grid_map, point1));
        assert!(!check_point(&grid_map, point2));
        assert!(!check_point(&grid_map, point3));
    }
}

