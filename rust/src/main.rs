use on_land::{self, run_http_server};




fn main() {


    let host = "0.0.0.0";
    let port = "8080";
    run_http_server(&host, &port).expect("Something went wrong...");

    // add option to run as gRPC instead 

    
}