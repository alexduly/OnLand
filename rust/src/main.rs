use std::{collections::HashMap};

// 3rd partyy imports
use actix_web::{guard, middleware::Logger, web, App, HttpServer};
use env_logger;
use geo::{Geometry, GeometryCollection};
// env_logger::init_(env_logger::Env::new().default_filter_or("info"));

// local imports
mod data;
mod routes;
mod services;

struct AppState { 
    shapes: HashMap<String, GeometryCollection>,
}


#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));
    // app_data wraps variable in Arc, this is always read only ( For now! ) so do not need to wrap it in rwlock 
    let state_polys: HashMap<String, GeometryCollection> = data::load_polys("/data/world.shp");

    // to do add GNU Terry Pratchett X-Clacks-Overhead 
    HttpServer::new(move  ||{
        App::new()
            .route("/", web::get().to(routes::info))
            .route("/healthcheck", web::get().to(routes::healthcheck).guard(guard::Host("localhost"))) // only want localhost accessing healthcheck
            .route("/api/{lat}/{lng}", web::get().to(routes::coord_check)) // only want localhost accessing healthcheck
            .wrap(Logger::new("%a %s %U"))
            .app_data(web::Data::new(AppState {
                shapes: state_polys.clone()
            })
        )
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}