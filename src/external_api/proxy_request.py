from fastapi import Request as FastAPIRequest
from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.request.datatypes import RequestParameters


class Headers(dict):
    pass


class ProxyRequest(OpenAPIRequest):
    def __init__(
            self,
            base_url,
            service_path,
            service_name,
            path,
            method: str,
            client,
            body: str,
            content_type,
            query_params,
            headers,
            cookies: dict,
    ):
                                                            # E.G: full url http://boxs.ml/users/user/{userId}
        self.base_url = base_url                            # E.G: http://boxs.ml/
        self.path = path                                    # E.G: users/user/{userId}
        self.service_path = service_path                    # E.G: user/{userId}
        self.service_name = service_name                    # E.G: users
        self.full_url_pattern = str(base_url) + str(path)   # E.G: http://boxs.ml/users/user/{userId}

        self.method = method.lower()
        self.mimetype = content_type
        self.client = client

        self.body = body
        self.cookies = cookies
        self.query_parameters = query_params
        self.headers = headers
        self.parameters = RequestParameters(query=query_params, header=headers, cookie=cookies, path={})

    @classmethod
    async def from_fastapi_request(cls, r: FastAPIRequest):
        request_path = r.path_params["p"]  # Example: "users/block/{userId}"
        service_path = request_path[request_path.find("/")+1:]  # Example: "block/{userId}"
        service_name = request_path.split("/")[0]

        query_params = {k: v for k, v in r.query_params.items()}
        full_content_type = r.headers.get("Content-Type")
        content_type = None if full_content_type is None else full_content_type.split(";")[0].lower()
        headers = Headers()
        headers.update({k: v for k, v in r.headers.items() if k != "authorization"})
        body = (await r.body()).decode()
        return cls(
            base_url=r.base_url,
            service_path=service_path,
            service_name=service_name,
            path=request_path,
            headers=headers,
            client=r.client,
            query_params=query_params,
            body=body,
            content_type=content_type,
            method=r.method.lower(),
            cookies=r.cookies,
        )
