use std::io::{stdout, Write};

use actix_web::{web::{self, Path}, HttpResponse};
use geo::point;
use crate::{services::geospatial::check_point, AppState};
use log::{debug,info};


pub async fn info() -> HttpResponse {
    return HttpResponse::Ok().body("Coming soon...\n");
}

pub async fn healthcheck() -> HttpResponse {
    debug!("Healthcheck okay\n");
    println!("this");
    stdout().flush().unwrap();

    return HttpResponse::Ok().finish();
}

pub async fn coord_check(path: Path<(f64, f64)>, state: web::Data<AppState>) -> HttpResponse {
    let (lat, lng) = path.into_inner();
    // get bounds from shape file ( maybe put in as separate layer so deosnt get saved to grids by itself )
    // default to this if not good
    if lat >= 90.00 || lat <= -90.00 || lng >= 180.0 || lng <= -180.0 {
        return HttpResponse::BadRequest().body("Coordinates out of bounds\n");
    }
    let point: geo::Point = point!([lng, lat]);
    let found = check_point(&state.shapes, point);

    if found {
        return HttpResponse::Ok().finish();
    } else {
        return HttpResponse::NotFound().finish();
    }
    
}
