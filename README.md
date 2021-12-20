# Gateway
API gateway for the ConnectAPI system.


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
3. validation (validating request against OpenAPI spec)
4. rate limit
5. monitoring


### How it works?
This service is used as a reversed proxy for the system, and provide the only entry point to the backend,
every request is validated on the OpenAPI spec, and authorized before forwarded to the destination service.


### File structure
```
├───core
│   └───models
├───external_api // API for the client side (application / website / game)
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
