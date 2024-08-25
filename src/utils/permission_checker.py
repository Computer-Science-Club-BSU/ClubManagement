from logging import Logger
from src.utils.db_utilities import connect
from flask import abort, Request
from typing import NoReturn


def check_perms(request:Request,
                user_seq: int,
                logger: Logger) -> None | NoReturn:
    with connect() as conn:
        if request.endpoint is None:
            abort(404)
        if conn.can_user_access_endpoint(user_seq, request.endpoint):
            return
        else:
            print(request.endpoint)
            if not conn.does_endpoint_exist(request.endpoint):
                raise Exception(f"Endpoint {request.endpoint} is not set up with valid permissions.")
            raise abort(401)
        