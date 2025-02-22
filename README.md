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
OnLand is a Rust-based application that allows a user to determine if a point is on land or water, based on the ArcGIS World Water Dataset that can be found [here](https://www.arcgis.com/home/item.html?id=e750071279bf450cbd510454a80f2e63) . This repository serves as the main development hub for the project.

## Features
- [Feature 1]
- [Feature 2]
- [Feature 3]

## Installation
To set up the project locally, follow these steps:

### Prerequisites
- Rust 1.83.0 or later
- Docker (for development in a dev container)

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/alexduly/OnLand.git
   cd OnLand
   ```
2. Install dependencies:
   ```sh
   cargo build
   ```
3. Run the application:
   ```sh
   cargo run
   ```

## Usage
[Provide usage examples, CLI commands, or API usage depending on the project.]

## Development
This project is designed to run in a dev container:

```sh
devcontainer open
```

To manually build and run the container:

```sh
docker build -t onland .
docker run --rm -it onland
```

### Running Tests
Run unit tests using:
```sh
cargo test
```

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to your fork (`git push origin feature-branch`).
5. Open a pull request.

## License
This project is licensed under the [MIT License](LICENSE).


## Sources
 | **Map**           | **Attribution**                                                                                                                                   |
|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| World Water Bodies [Available at: https://www.arcgis.com/home/group.html?id=24838c2d95e14dd18c25e9bad55a7f82#overview] | ESRI, Garmin Available at: https://www.arcgis.com/home/group.html?id=24838c2d95e14dd18c25e9bad55a7f82#overview  |

---

For more information, visit the [repository](https://github.com/alexduly/OnLand).
