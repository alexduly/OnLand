
use actix_web::http::StatusCode;
use actix_web::{
    get,
    web::{self, Path},
    HttpResponse, Responder,
};
use geo::point;
use log::debug;
use serde::{Deserialize, Serialize};

use crate::geospatial::check_point;
use crate::AppState;

#[derive(Serialize, Deserialize)]
pub struct CoordCheckRes {
    pub land: bool,
    pub lat: f64,
    pub lng: f64,
}
#[derive(Serialize, Deserialize)]
pub struct CoordCheckBadRes {
    pub message: String,
    pub status: u16,
    pub lat: f64,
    pub lng: f64,
}
#[get("/")]
pub async fn get_info() -> HttpResponse {
    return HttpResponse::Ok().body("Coming soon...\n");
}
#[get("/healthcheck")]
pub async fn healthcheck() -> HttpResponse {
    debug!("Healthcheck okay\n");
    return HttpResponse::Ok().finish();
}

#[get("/api/{lat}/{lng}")]
pub async fn coord_check(path: Path<(f64, f64)>, state: web::Data<AppState>) -> impl Responder {
    let (lat, lng) = path.into_inner();
    // get bounds from shape file ( maybe put in as separate layer so deosnt get saved to grids by itself )
    // default to this if not good
    if lat >= 90.00 || lat <= -90.00 || lng >= 180.0 || lng <= -180.0 {
        return HttpResponse::BadRequest().json(CoordCheckBadRes {
            message: "Invalid Coordinates".to_string(),
            status: StatusCode::BAD_REQUEST.as_u16(),
            lat: lat,
            lng: lng,
        });
    }

    debug!("Extent: {:?}", &state.extent);
    let point: geo::Point = point!([lng, lat]);
    let found: bool = check_point(&state.shapes, point);

    return HttpResponse::Ok().json(CoordCheckRes {
        land: found,
        lat: lat,
        lng: lng,
    });
}
