# Gateway
API gateway for the Box's system.


### Full system overview
| Service      | Description | repo       |
|--------------|:-------------|------------|
| **Marketplace**  | Provide api and website to upload, download and search services. | https://github.com/ConnectAPI/MarketPlace  |
| **Gateway**      | The only entry point to the system, responsible for auth, validation and rate limit's. | https://github.com/ConnectAPI/Gateway |
| **Dashboard**    | Provide easy interface for managing and monitoring the system. | https://github.com/ConnectAPI/Dashboard |


### What it does?
Gateway responsible for:
1. managing plugin services
2. authentication
3. validation (validating request against openapi spec)
4. rate limit


### How it works?
Every plugin service that added to the system must provide it's openapi spec,
The spec can contain extra information like rate limit and required permission scope,
With the openapi the service also contain link to a docker image.

The gateway is running the docker image on a virtual network and used as a proxy to it.


### File structure
```
├───core
│   └───models
├───external_api // API the application suposed to access
│   └───endpoints // routes
├───internal_api // API for the dashboard and server side
│   ├───auth // authentication service, handling permission tokens
│   │   ├───core 
│   │   │   ├───models
│   │   │   └───schemas // data models
│   │   └───endpoints // routes
│   ├───service_discovery // managing the plugin services
│   │   ├───core
│   │   │   ├───models
│   │   │   ├───schemas // data models
└───└───└───endpoints // routes
```