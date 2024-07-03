from logging import Logger
from src.utils.db_utilities import connect
from flask import abort, Request
import re

from typing import NoReturn



def check_perms(request:Request,
                user_seq: int,
                logger: Logger) -> None | NoReturn:
    with connect() as conn:
        if request.endpoint is None:
            abort(404)
        if conn.can_user_access_endpoint(user_seq, request.endpoint)[0]:
            return
        else:
            print(request.endpoint)
            raise Exception
        