import logging
import json
from framework import GoITServer, GoITRequest, GoITResponse

logging.basicConfig(level="DEBUG")

api = GoITServer("0.0.0.0", 8080, static_folder="public")

# @api.err("404")
# def handler_404(req: GoITRequest) -> GoITResponse:
#     return GoITResponse()

# @api.post("/dima")
# def post_dima_handler(req: GoITRequest) -> GoITResponse:
#     req_json = json.loads(req.body)
#     return GoITResponse(
#         200,
#         {},
#         f"I know your name: {req_json["name"]}.".encode()
#     )

@api.post("/contact")
def post_contact_handler(req: GoITRequest) -> GoITResponse:
    logging.info(req.body)

    return GoITResponse(
        301,
        {"Location": "/public/index.html"},
        b""
    )

if __name__ == '__main__':
    api.serve_forever()
