from logging import Logger
from src.utils.db_utilities import connect
from flask import abort, Request

from typing import NoReturn

perms = {
    # HTTP_method: {
    #  PATH: [<Perm1>, <Perm2>]   
    #}
    "GET": {
        "/": None,
        "/doc/create": ["doc_admin", "doc_add"],
        "/doc/create/": ["doc_admin", "doc_add"],
        "/doc/view": ["doc_admin", "doc_view"],
        "/doc/view/": ["doc_admin", "doc_view"],
        "/doc/edit": ["doc_admin", "doc_edit"],
        "/doc/edit/": ["doc_admin", "doc_edit"]
    },
    "POST": {
        "/doc/new": ["doc_admin", "doc_add"],
        "/doc/new/": ["doc_admin", "doc_add"],
        "/doc/edit": ["doc_admin", "doc_view"],
        "/doc/edit/": ["doc_admin", "doc_view"]
    },
    "PATCH":{
        
    },
    "PUT":{
        
    },
    "DELETE":{
        
    },
    "HEAD":{
        
    }

}


def check_perms(request:Request,
                user_seq: int,
                logger: Logger) -> None | NoReturn:
    method_rules = perms.get(request.method, {})
    path_rules = method_rules.get(request.path, [""])
    if path_rules is None:
        return
    if path_rules == [""]:
        logger.critical(
            f"[CRITICAL][500] Err: Path {request.path} has no rules set up!"
            )
        abort(500)
    if user_seq is None:
        logger.error(
            f"[401] {request.remote_addr} attempted to access {request.path}."
            "Access Denied."
        )
        abort(401)
    
    with connect() as conn:
        user_perms = conn.get_user_perms_by_user_seq(user_seq)
        for path_perm in path_rules:
            if user_perms.get(path_perm, 0) == 1:
                return
        user_data = conn.get_user_data_by_seq(user_seq)
        username = user_data['first_name'] + " " + user_data['last_name']
        logger.error(
            f"[403] User {username} attempted to access {request.path}."
            "Access Denied."
        )
        abort(403)