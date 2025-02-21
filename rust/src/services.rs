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

#[derive(Deserialize)]
struct CoordIn {
    lat: f64,
    lng: f64,
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
pub async fn coord_check(
    path: Option<Path<CoordIn>>,
    state: web::Data<AppState>,
) -> impl Responder {
    match path {
        Some(p) => {
            // get bounds from shape file ( maybe put in as separate layer so deosnt get saved to grids by itself )
            // default to this if not good
            if p.lat >= 90.00 || p.lat <= -90.00 || p.lng >= 180.0 || p.lng <= -180.0 {
                return HttpResponse::BadRequest().json(CoordCheckBadRes {
                    message: "Coordinates out of range".to_string(),
                    status: StatusCode::BAD_REQUEST.as_u16(),
                    lat: p.lat,
                    lng: p.lng,
                });
            }

            debug!("Extent: {:?}", &state.extent);
            let point: geo::Point = point!([p.lng, p.lat]);
            let found: bool = check_point(&state.shapes, point);

            return HttpResponse::Ok().json(CoordCheckRes {
                land: found,
                lat: p.lat,
                lng: p.lng,
            });
        }
        None => {
            return HttpResponse::BadRequest().json(CoordCheckBadRes {
                message: "Invalid Coordinates".to_string(),
                status: StatusCode::BAD_REQUEST.as_u16(),
                lat: 0.00,
                lng: 0.00,
            });
        }
    }
}
