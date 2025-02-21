use std::collections::HashMap;

use actix_web::{http::header::ContentType, test, web, App};
use geo::{BoundingRect, GeometryCollection};
use land_or_water::{services::{
    coord_check, get_info, healthcheck, CoordCheckBadRes, CoordCheckRes,
}, AppState, data};
mod utils;

#[actix_web::test]
async fn test_index_get() {
    let app = test::init_service(App::new().service(get_info)).await;
    let req = test::TestRequest::default().to_request();
    let resp = test::call_service(&app, req).await;
    assert!(resp.status().is_success());
}
#[actix_web::test]
async fn test_healthcheck() {
    // Expand to do further checks of guards once / if that is implemented and if possible
    let app = test::init_service(App::new().service(healthcheck)).await;
    let req = test::TestRequest::get().uri("/healthcheck").to_request();
    let resp = test::call_service(&app, req).await;
    assert!(resp.status().is_success());
}

#[actix_web::test]
async fn test_check_coords_accuracy() {
    // this tests accuracy. add in other tests that dont care about land/water but test other cases e.g. no numbers, non floats etc ?
    let points = utils::read_test_points();
    let mut count = 0;
    match points {
        Ok(points_vec) => {
            // let app = test::init_service(App::new().service(coord_check)).await;
            let state_polys: HashMap<String, GeometryCollection> = data::load_polys("/data/shapes/world.shp");
            let extent = state_polys["Extent"].bounding_rect().expect("Failed to load extent");
        
            let app = test::init_service(App::new().service(coord_check).app_data(web::Data::new(
                AppState {
                    shapes: state_polys.clone(),
                    extent: extent.clone(),
                },
            )))
            .await;

            for point in points_vec {
                let path = format!("/api/{:5}/{:5}", point.lat, point.lng);

                let req = test::TestRequest::get().uri(&path).to_request();
                let resp = test::call_service(&app, req).await;
                assert!(resp.status().is_success());
                let check_res: CoordCheckRes = test::read_body_json(resp).await;
                assert_eq!(check_res.land, point.land);
                count +=1;

            }
        }
        Err(e) => {
            println!("failed to get points: {}", e);
            assert!(false)
        }
    }
}
