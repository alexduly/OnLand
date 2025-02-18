use actix_web::{web::{self, Path}, HttpResponse};
use geo::point;
use crate::{services::geospatial::check_point, AppState};


pub async fn info() -> HttpResponse {
    return HttpResponse::Ok().body("Coming soon...");
}

pub async fn healthcheck() -> HttpResponse {
    return HttpResponse::Ok().finish();
}

pub async fn coord_check(path: Path<(f64, f64)>, state: web::Data<AppState>) -> HttpResponse {
    let (lat, lng) = path.into_inner();
    // get bounds from shape file ( maybe put in as separate layer so deosnt get saved to grids by itself )
    // default to this if not good
    if lat >= 90.00 || lat <= -90.00 || lng >= 180.0 || lng <= -180.0 {
        return HttpResponse::BadRequest().body("Coordinates out of bounds\n");
    }
    println!("lat: {lat}, lng: {lng}");

    let point: geo::Point = point!([lng, lat]);

    let mut found: bool = false;
    if let Ok(read_guard) = &state.shapes.read(){
        found = check_point(read_guard, point);
    }

    if found {
        return HttpResponse::Ok().finish();
    } else {
        return HttpResponse::NotFound().finish();
    }
    
}
