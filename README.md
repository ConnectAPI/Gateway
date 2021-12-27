# Gateway
API gateway for the ConnectAPI system.


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


