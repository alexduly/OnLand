# OnLand

![OnLand](https://img.shields.io/badge/Rust-1.83.0-orange?style=flat-square) ![License](https://img.shields.io/github/license/alexduly/OnLand)

A containerized Rust proejct that provides an API to determine if a given coordinate point (using EPSG:4326 - WGS 84 - Geographic), is in Land or in Water. 


## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Overview
OnLand is a Rust-based application that allows a user to determine if a point is on land or water. Requires input of shapefile data, for example: [here](https://www.arcgis.com/home/item.html?id=e750071279bf450cbd510454a80f2e63). This repository serves as the main development hub for the project. Developed and tested on ARM machine. 

With input of shapefiles that outline land, this program uses QGIS to prepocess the shapes and assign them a GridID in the format: "latmin:lngmin:latmax:lngmax", and then outputs a processed shapefile. Currently, data from example dataset must be manaually inverted and saved as shapefile to be read in, the automation of this process is in development now. 

A rust Actix http server is then created, that reads in the processed shapes and stores them in a hashmap using the referenced GridID. A coordinate is read in, and the gridID is calculated given the known grid size. Currenntly, it assumes the gridID is of size 5, and starts at a multiple of 5. Again, future releases will allow this to be set via the read in of the processed shapes. If the point is found in the polygons, then the api returns true, otherwise false is returned instead. 

The entire system is containerized for ease of deployment. 

```


```

## Info
**GET** `/`

### Description
Endpoint prints the usage of the server

### Request

- **Method**: `GET`
- **URL**: `/`

#### Query Parameters
There are no required query parameters for this endpoint.

### Response

- **Status Code**: `200 OK`


## Healthcheck
**GET** `/healthcheck`

### Description
Internal for docker healthcheck, returns 200 if server is running

### Request

- **Method**: `GET`
- **URL**: `/healthcheck`

#### Query Parameters
There are no required query parameters for this endpoint.

### Response

- **Status Code**: `200 OK`



## Coordinate Check
**GET** `/api/{lat}/{lng}`

### Description
The primary API. Coordinate submitted using the EPSG:4326 - WGS 84 coordinate reference system, will return if the point is on land or water

### Request

- **Method**: `GET`
- **URL**: `/api/{lat}/{lng}`

#### Path Parameters

| Parameter | Type   | Description                           |
|-----------|--------|---------------------------------------|
| `lat`   | f64 | the latitude of the point. Must be convertible to f64. |
| `lng`   | f64 | the longitude of the point. Must be convertible to f64. |

### Example Request

```http
GET /api/location/40.7128/-74.0060
```

### Response

#### Success Response:
- **Code**: 200 OK
- **Body**:
  ```json
  {
    "land": true,
    "lat": 45.0,
    "lng": -73.0
  }
  ```
#### Bad Request: Coordinates Out of Range
- **Code**: 400 Bad Request
- **Body**:
    ```json
  {
  "message": "Coordinates out of range",
  "status": 400,
  "lat": 95.0,
  "lng": -190.0
   }
    ```

#### Bad Request: Invalid Coordinates
- **Code**: 400 Bad Request
- **Body**:
 ```json
{
  "message": "Invalid Coordinates",
  "status": 400,
  "lat": 0.00,
  "lng": 0.00
} 
```

## Installation
To set up the project locally, follow these steps:

1. Install docker
2. Download shapefile
3. docker compose -f docker-compose-example.yaml up --build -d
4. Will be served on http://localhost:8080


### Prerequisites
- Docker for development and deployment

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/alexduly/OnLand.git
   cd OnLand
   ```
2.  Download chosen shapefile dataset:
   
3. Run the application:
   ```sh
   docker compose -f docker-compose-example.yaml up --build -d
   ```

## Development
This project has been developed in 2 dev containers, the configurations can be found in .devcontainer/




### Running Tests
Run unit and integration tests using:
```sh
cargo test
```

Accuracy has been assessed by the generation of random points using qgis in the preprocessing steps and are included in integration testing, which the service currently passes. Future testing will include using other datasets of known points on land and water. 

### Performance Metrics
TBD

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to your fork (`git push origin feature-branch`).
5. Open a pull request.

## License
This project is licensed under the [MIT License](LICENSE).

---

For more information, visit the [repository](https://github.com/alexduly/OnLand).
