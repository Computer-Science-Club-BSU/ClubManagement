from logging import Logger
from src.utils.db_utilities import connect
from flask import abort, Request
import re

from typing import NoReturn



def check_perms(request:Request,
                user_seq: int,
                logger: Logger) -> None | NoReturn:
    with connect() as conn:
        user_perms = conn.get_user_perms_by_user_seq(user_seq)
        print(user_perms)