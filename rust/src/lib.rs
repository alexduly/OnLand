use std::{collections::HashMap};


// 3rd partyy imports
use actix_web::{middleware::Logger, web, App, HttpServer};
use env_logger;
use geo::{BoundingRect, GeometryCollection, Rect};
// env_logger::init_(env_logger::Env::new().default_filter_or("info"));

pub mod data;
mod geospatial;
pub mod services; 


pub struct AppState { 
    pub shapes: HashMap<String, GeometryCollection>,
    pub extent: Rect,
}


#[actix_web::main]
pub async fn run_http_server(host: &str, port: &str) -> std::io::Result<()> {
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("debug"));
    // app_data wraps variable in Arc, this is always read only ( For now! ) so do not need to wrap it in rwlock 
    let state_polys: HashMap<String, GeometryCollection> = data::load_polys("/data/shapes/world.shp");
    let extent = state_polys["Extent"].bounding_rect().expect("Failed to load extent");

    let addr = format!("{}:{}", host, port);

    // to do add GNU Terry Pratchett X-Clacks-Overhead 
    HttpServer::new(move  ||{
        App::new()
            .service(services::get_info)
             .service(services::healthcheck)
             .service(services::coord_check)
            // .route("/", web::get().to(routes::info))
            // .route("/healthcheck", web::get().to(routes::healthcheck).guard(guard::Host("localhost"))) // only want localhost accessing healthcheck
            // .route("/api/{lat}/{lng}", web::get().to(routes::coord_check)) // only want localhost accessing healthcheck
            .wrap(Logger::new("%a %s %U"))
            .app_data(web::Data::new(AppState {
                shapes: state_polys.clone(),
                extent: extent.clone()
            })
        )
    })
    .bind(addr)?
    .run()
    .await
}