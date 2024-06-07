from logging import Logger
from src.utils.db_utilities import connect
from flask import abort, Request
import re

from typing import NoReturn

perms = {
    # HTTP_method: {
    #  PATH: [<Perm1>, <Perm2>]   
    #}
    "GET": {
        "/?": "*",
        "/doc/create/?": ["doc_admin", "doc_add"],
        "/doc/view/?": ["doc_admin", "doc_view"],
        "/doc/edit/": ["doc_admin", "doc_edit"],
        '/auth/logout/?': "*",
        '/auth/login/?': "*",
        '/about/.*/?': "*"
    },
    "POST": {
        "/doc/create/?": ["doc_admin", "doc_add"],
        "/doc/edit/?": ["doc_admin", "doc_view"],
        "/doc/conv/add/?": ["doc_admin", "doc_view", "doc_add"],
        '/auth/login/?': "*",
        '/admin/permissions/edit': ["user_admin", "user_edit"]
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
    logger.info('Checking perms')
    method_rules = perms.get(request.method, {})
    path_rules = None
    for path in method_rules.items():
        logger.debug(f'{path[0]}, {request.path}')
        print(re.match(path[0], request.path) is not None)
        if re.match(path[0], request.path) is not None:
            path_rules = path[1]
            break
    logger.info('Loop done')
    print(path_rules)
    if path_rules is None:
        logger.info('Abort 500 None Path_Rules')
        
        abort(500)
    
    if request.path.startswith('/static/'):
        return
    if path_rules == '*':
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