# Module Imports
import mariadb
import bleach
import sys
import logging
import traceback
from typing import Callable
import bcrypt
from mariadb import InterfaceError, Cursor
from mariadb.connections import Connection
from src.utils.cfg_utils import get_cfg
import base64
from typing import List, Dict, Optional, Type, Sequence, Any
from types import TracebackType
from conf import LOG_DIR

# Create a new logger
handler = logging.FileHandler(f'{LOG_DIR}sql.log')
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

# Call it "SQL Log, set the default level to INFO, and add the log location 'sql.log'"
sqllogger = logging.getLogger("SQL Log")
sqllogger.setLevel(logging.DEBUG)
sqllogger.addHandler(handler)

logger = logging.getLogger('DatabaseManager')

class connect:
    def __init__(self):

        # Connect to MariaDB Platform
        conf = get_cfg()['DATA']
        try:
            self.conn: Connection = mariadb.connect(
                user=conf['USER'],
                password=conf['PASS'],
                host=conf['HOST'],
                port=conf['PORT'],
                database=conf['NAME']

            )
            self.cur: Cursor = self.conn.cursor()

        except mariadb.Error as e:
            logger.error(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

    def _exec_safe(func: Callable):
        def wrapper(self, *args, **kwargs):
            try:
                results = func(self, *args, **kwargs)
                self.conn.commit()
                return (True, results)
            except Exception as e:
                self.conn.rollback()
                logger.error(f"DB Exception Occured {traceback.format_exc()}")
                return (False, None)
        return wrapper

    def _convert_to_dict(func: Callable):
        def wrapper(self, *args, **kwargs):
            # Execute the function (Performs the SQL Query)
            res = func(self, *args, **kwargs)
            if res is not None:
                return None
            # Assemble a dictionary based off the cursor description.
            field_names = [bleach.clean(i[0]) for i in self.cur.description]
            data = self.cur.fetchall()
            row_data = []
            for row in data:

                row_data.append(
                    {key: bleach.clean(val) if isinstance(val, str) else val
                        for key, val in zip(field_names, row)
                    }
                )
            return row_data
        return wrapper

    def _convert_to_dict_single(func: Callable):
        def wrapper(self, *args, **kwargs):
            # Execute the function (Performs the SQL Query)
            func(self, *args, **kwargs)
            # Assemble a dictionary based off the cursor description.
            field_names = [bleach.clean(i[0]) for i in self.cur.description]
            data = self.cur.fetchone()

            return {key: bleach.clean(val) if isinstance(val, str) else val
                        for key, val in zip(field_names, data)
                    }
        return wrapper
    
    # All statements should call `run_statements` to ensure proper logging.
    def run_statement(self, statement: str, data: Sequence = (), buffered: Any|None = None):
        log_str = f'SQL Statement: {statement}'
        log_str += f'\n\tArgs:{data}' if len(data) > 0 else ''
        try:
            self.cur.execute(statement, data,buffered)
            sqllogger.info(log_str)
        except Exception as e:
            sqllogger.error(log_str)
            raise e
    
    def get_user_by_seq(self, user_seq):
        """Get a user by their seq

        Args:
            user_seq (int): User Sequence Number (Unique Identifier)
        """

        logger.debug(f"Getting User for User Seq {user_seq}")
        user_data = self.get_user_data_by_seq(user_seq)
        class_data = self.get_user_classes_by_user_seq(user_seq)
        permissions = self.get_user_perms_by_user_seq(user_seq)
        fin_dash = self.get_user_finance_dashboards_by_user_seq(user_seq)
        doc_dash = self.get_user_docket_dashboards_by_user_seq(user_seq)
        return user_data, permissions, class_data, fin_dash, doc_dash

    @_convert_to_dict_single
    def get_user_data_by_seq(self, user_seq) -> dict:
        # Select User from SQL Table
        logger.debug(f"Getting User Data for User Seq {user_seq}")
        SQL = "SELECT * FROM users WHERE seq = %s"
        self.run_statement(SQL, (user_seq,))

    @_convert_to_dict
    def get_user_classes_by_user_seq(self, user_seq) -> List[Dict[str,str]]:
        logger.debug(f"Getting User Classes for User Seq {user_seq}")

        SQL = """SELECT a.position_name FROM class a, class_assignments b
        WHERE a.seq = b.class_seq AND b.user_seq = %s"""
        self.run_statement(SQL, (user_seq,))


    def get_user_perms_by_user_seq(self, user_seq):
        logger.debug(f"Getting User Permissions for User Seq {user_seq}")

        SQL = """SELECT a.seq, d.perm_desc, a.granted FROM
        perms a, class_assignments c, perm_types d, terms ea, terms eb
        WHERE a.class_seq = c.class_seq
        AND d.seq = a.perm_seq
        AND c.user_seq = %s AND ea.seq = c.start_term AND eb.seq = c.end_term
        AND ea.start_date <= current_timestamp
        AND eb.end_date >= current_timestamp;"""

        self.run_statement(SQL, (user_seq,))
        field_names = [i[0] for i in self.cur.description]
        data = self.cur.fetchall()
        raw_perms = []
        for row in data:
            raw_perms.append(
                {key: val for key,val in zip(field_names, row)}
                )

        perm_data = {}
        for row in raw_perms:
            perm_data[row['perm_desc']] \
                = row['granted'] | perm_data.get(row['perm_desc'], 0)
        return perm_data

    def get_user_finance_dashboards_by_user_seq(self, user_seq) -> List[Dict[str,str]]:
        return [{"1": "test"}]

    @_convert_to_dict
    def get_user_docket_dashboards_by_user_seq(self, user_seq) -> List[Dict[str,str]]:
        SQL = """SELECT dash.* FROM dashboards dash, dash_assign da,
        class_assignments ca WHERE da.dash_seq = dash.seq
        AND da.class_seq = ca.seq AND ca.user_seq = %s;"""
        self.run_statement(SQL, (user_seq,))

    
    def authorize_user(self, username: str, password: str) -> int:
        user_data = self.get_user_by_username(username)
        if user_data is None:
            return -1
        classes = self.get_user_classes_by_user_seq(user_data.get('seq'))
        for class_ in classes:
            if class_.get('position_name') == 'locked':
                return -1
        hashed_pw = user_data.get("hash_pass").encode()
        password = password.encode()
        if bcrypt.checkpw(password, hashed_pw):
            return user_data.get('seq')

        return -1



    def get_user_by_username(self, username: str):
        sql = "SELECT seq FROM users WHERE user_name = %s"
        self.run_statement(sql, (username,))
        if self.cur.rowcount < 1:
            return None
        elif self.cur.rowcount > 1:
            self.cur.fetchall()
            return None
        seq = self.cur.fetchone()[0]
        return self.get_user_data_by_seq(seq)

    
    def get_finances_total(self) -> int:
        finances = self.get_finances()
        total = 0
        for finance in finances:
            total += finance['tax'] + finance['fees']
            for line in finance['lines']:
                total += (line['price'] * line['qty'])
        return total

    @_convert_to_dict
    def get_finance_headers(self) -> List[Dict[str,str]]:
        SQL = """SELECT * FROM finance_hdr"""
        self.run_statement(SQL)

    @_convert_to_dict
    def get_finance_lines_by_hdr(self, hdr_seq: int) -> List[Dict[str,str]]:
        SQL = """SELECT A.seq, A.finance_seq, A.line_id, B.price, A.qty,
        A.added_by, A.updated_by, A.added_dt, A.update_dt FROM
        finance_line A, item_cost B WHERE A.item_id = B.seq AND
        A.finance_seq=%s"""
        self.run_statement(SQL, (hdr_seq,))

    def get_finances(self) -> List[Dict[str,str]]:
        # Get the header data
        headers = self.get_finance_headers()
        for item in headers:
            hdr_seq = item['seq']
            lines = self.get_finance_lines_by_hdr(hdr_seq)
            item['lines'] = lines

        return headers

    @_convert_to_dict
    def get_finance_statuses(self) -> List[Dict[str,str]]:
        SQL = "SELECT * from finance_status"
        self.run_statement(SQL)

    @_convert_to_dict
    def get_finance_hdr_by_status(self, stat_desc: str) -> List[Dict[str,str]]:
        SQL = """SELECT a.* from finance_hdr a,
        finance_status b where a.stat_seq = b.seq AND b.stat_desc = %s"""
        self.run_statement(SQL, (stat_desc,))


    @_convert_to_dict
    def get_docket_statuses(self) -> List[Dict[str,str]]:
        SQL = "SELECT * from docket_status"
        self.run_statement(SQL)

    @_convert_to_dict
    def get_docket_hdr_by_status(self, stat_desc: str) -> List[Dict[str,str]]:
        SQL = """SELECT a.* from docket_hdr a,
        docket_status b where a.stat_seq = b.seq AND b.stat_desc = %s"""
        self.run_statement(SQL, (stat_desc,))


    @_convert_to_dict_single
    def get_docket_by_seq(self, seq: int) -> Dict[str,str]:
        SQL = """SELECT hdr.seq as 'seq', hdr.docket_title, hdr.docket_desc,
        stat.stat_desc as 'status', vote.vote_desc,
        hdr.added_by as 'creator_seq',
        DATE_FORMAT(hdr.added_dt, '%W, %M %D, %Y') as 'added_dt',
        concat(u.first_name, ' ', u.last_name) as 'creator'
        FROM docket_hdr hdr, docket_status stat, vote_types vote, users u
        WHERE hdr.vote_type = vote.seq AND hdr.stat_seq = stat.seq
        AND hdr.added_by = u.seq AND hdr.seq = %s;"""
        self.run_statement(SQL, (seq,))

    @_convert_to_dict
    def get_docket_conversations(self, seq):
        SQL = """SELECT conv.seq, concat(usr.first_name, ' ', usr.last_name)
        AS 'name', conv.creator, conv.body
        FROM docket_conversations conv, users usr
        WHERE conv.creator = usr.seq
        AND conv.docket_seq = %s
        ORDER BY dt_added;"""
        self.run_statement(SQL, (seq,))

    @_convert_to_dict
    def get_docket_assignees(self, seq) -> dict:
        SQL = """SELECT assn.seq, concat(usr.first_name, ' ', usr.last_name)
        AS 'name', assn.user_seq
        FROM docket_assignees assn, users usr
        WHERE assn.user_seq = usr.seq AND
        assn.docket_seq = %s ORDER BY assn.added_dt;"""
        self.run_statement(SQL, (seq,))


    def get_all_docket_data_by_seq(self, seq):
        seq = int(seq)
        docket_data = self.get_docket_by_seq(seq)
        conversations = self.get_docket_conversations(seq)
        assignees = self.get_docket_assignees(seq)
        return {
            "docket": docket_data,
            "conv": conversations,
            "assign": assignees
        }

    def get_finance_summary(self):
        # Get finance statuses
        summary = {}
        for status in self.get_finance_statuses():
            stat = status['stat_desc']
            summary[stat] = len(self.get_finance_hdr_by_status(stat))
        return summary

    @_convert_to_dict
    def get_about_page_assignments(self) -> List[Dict[str,str]]:
        SQL = """SELECT e.title_desc as 'title',
        CONCAT(a.first_name, ' ', a.last_name) AS 'name',
        c.position_name FROM users a, class_assignments b, class c,
        terms d_a, terms d_b, titles e WHERE
        b.user_seq = a.seq AND b.class_seq = c.seq AND c.displayed = 1
        AND a.is_active = 1 AND b.start_term = d_a.seq AND b.end_term = d_b.seq
        AND d_a.start_date <= current_timestamp AND
        d_b.end_date >= current_timestamp and e.seq = a.title
        ORDER BY c.ranking ASC;"""
        self.run_statement(SQL)

    @_convert_to_dict
    def get_about_former_officers(self) -> List[Dict[str,str]]:
        SQL = """SELECT e.title_desc as 'title', concat(A.first_name, ' ', A.last_name) as
        'name', C.position_name, Da.term_desc as 'start', Db.term_desc as 'end'
        FROM users A, class_assignments B, class C, terms Da, terms Db,
        titles e WHERE B.user_seq = A.seq AND B.class_seq = C.seq AND
        B.start_term = Da.seq AND B.end_term = Db.seq AND C.displayed = 1
        AND Db.end_date < current_date and e.seq = A.title
        ORDER BY Db.end_date DESC, A.last_name DESC"""
        self.run_statement(SQL)


    def get_docket_summary(self):
        summary = {}
        for status in self.get_docket_statuses():
            stat = status['stat_desc']
            summary[stat] = len(self.get_docket_hdr_by_status(stat))
        return summary

    @_convert_to_dict
    def get_all_non_archived_docket(self) -> List[Dict[str,str]]:
        SQL = """SELECT hdr.seq, hdr.docket_title, hdr.docket_desc,
        stat.stat_desc as 'status', vote.vote_desc,
        hdr.added_by as 'creator_seq',
        DATE_FORMAT(hdr.added_dt, '%W, %M %D, %Y') as 'added_dt',
        concat(u.first_name, ' ', u.last_name) as 'creator'
        FROM docket_hdr hdr, docket_status stat, vote_types vote, users u
        WHERE hdr.vote_type = vote.seq AND hdr.stat_seq = stat.seq AND
        LOWER(stat.stat_desc) != 'archived' AND hdr.added_by = u.seq;"""
        self.run_statement(SQL)

    def can_user_edit_docket(self, user_seq, docket_seq) -> bool:
        user_perms = self.get_user_perms_by_user_seq(user_seq)
        if user_perms.get('doc_admin') == 1:
            return True

        docket_data = self.get_all_docket_data_by_seq(docket_seq)
        for assignee in docket_data.get('assign', []):
            if user_seq == assignee.get('user_seq'):
                return True

        if docket_data.get('docket',{}).get("creator_seq") == user_seq:
            return True

        return False

    @_convert_to_dict
    def get_docket_users(self):
        SQL = "SELECT * FROM docket_users"
        self.run_statement(SQL)

    @_exec_safe
    def create_docket_conversation(self,
                                   doc_seq: int,
                                   user_seq: int,
                                   conv_data: str) -> tuple[bool, any]:
        SQL = """INSERT INTO docket_conversations
        (docket_seq, creator, body) VALUES (%s,%s,%s)"""
        self.run_statement(SQL, (doc_seq,user_seq,conv_data))


    def create_docket_item(self,
                           doc_title: str,
                           doc_body: str,
                           user_seq: int,
                           status:int=1,
                           vote_type:int=1):
        SQL = """INSERT INTO docket_hdr (docket_title, docket_desc, added_by,
        updated_by, stat_seq, vote_type) VALUES (%s,%s,%s,%s,%s,%s)"""
        self.cur.execute(SQL, (
            doc_title,
            doc_body,
            user_seq,
            user_seq,
            status,
            vote_type))
        return self.cur.lastrowid

    def add_docket_assignee(self, doc_seq: int, assignee: int, user_seq: int):
        SQL = """INSERT INTO docket_assignees (docket_seq, user_seq,
        added_by, updated_by) VALUES (%s,%s,%s,%s)"""
        self.run_statement(SQL, (doc_seq, assignee, user_seq, user_seq))

    @_exec_safe
    def create_docket_and_assign(self,
                                 doc_title: str,
                                 doc_body: str,
                                 user_seq: int,
                                 status:int=1,
                                 vote_type:int=1,
                                 assignees:List[int]=[]):
        doc_seq = self.create_docket_item(doc_title,
                                          doc_body,
                                          user_seq,
                                          status,
                                          vote_type)
        for assignee in assignees:
            self.add_docket_assignee(doc_seq, assignee, user_seq)
        return doc_seq

    @_convert_to_dict
    def get_docket_dash_data(self, dash_seq: int, user_seq: int) -> List[Dict[str,str]]:
        SQL = """SELECT dash.sp_name FROM dashboards dash,
        dash_assign da, class_assignments ca WHERE da.dash_seq = dash.seq AND
        ca.user_seq = %s AND da.class_seq = ca.class_seq AND dash.seq = %s;"""
        self.run_statement(SQL, (user_seq, dash_seq))
        if self.cur.rowcount != 1:
            return False
        sp_name = self.cur.fetchone()[0]

        self.cur.callproc(sp_name)

    @_convert_to_dict
    def get_docket_vote_types(self):
        SQL = "SELECT * FROM vote_types"
        self.run_statement(SQL)

    @_exec_safe
    def update_docket(self,
                      doc_seq: int,
                      title: str,
                      body: str,
                      user_seq: int,
                      stat: int|None=None,
                      vote: int|None=None
                      ):
        SQL = """UPDATE docket_hdr
        SET docket_title = %s, docket_desc = %s, updated_by = %s"""
        vals = [title, body, user_seq]

        if stat is not None:
            SQL += ", stat_seq = %s"
            vals.append(stat)

        if vote is not None:
            SQL += ", vote_type = %s"
            vals.append(vote)

        SQL += " WHERE seq = %s"
        vals.append(doc_seq)
        self.run_statement(SQL, vals)

    @_convert_to_dict
    def get_permission_data(self) -> List[Dict[str,str]]:
        SQL = """SELECT * FROM perm_types WHERE grantable=1;"""
        self.run_statement(SQL)

    @_convert_to_dict
    def get_all_db_perms(self) -> List[Dict[str,str]]:
        SQL = "SELECT * FROM perms"
        self.run_statement(SQL)

    @_convert_to_dict
    def get_user_classes(self) -> List[Dict[str,str]]:
        SQL = """SELECT * FROM class"""
        self.run_statement(SQL)

    def get_class_perms(self) -> dict[dict]:
        SQL = """SELECT perms.seq, perms.granted, c.position_name,
        p.name_short, p.perm_desc from perms LEFT JOIN (class c, perm_types p)
        ON (perms.class_seq = c.seq AND perms.perm_seq = p.seq
        AND p.grantable = 1);"""
        self.run_statement(SQL)
        perms = {}
        for row in self.cur.fetchall():
            class_dict = perms.get(row[2], {})
            class_dict[row[4]] = (row[0], (row[1] == 1))
            perms[row[2]] = class_dict

        return perms

        
    @_exec_safe
    def create_class(self, class_name, user_seq):
        SQL = """INSERT INTO class (position_name, added_by, updated_by,
        displayed) VALUES (%s, %s, %s, 0)"""
        self.run_statement(SQL, (class_name, user_seq, user_seq))
        class_seq = self.cur.lastrowid
        perm_sql = """INSERT INTO perms (class_seq, perm_seq,
        added_by, updated_by) VALUES (%s, %s, %s, %s)"""
        for row in self.get_permission_data():
            self.cur.execute(perm_sql, (
                class_seq,
                row['seq'],
                user_seq,
                user_seq))

    @_exec_safe
    def create_email(self,
                     subject: str,
                     body: str,
                     user_seq: int,
                     to: list,
                     cc: list,
                     bcc: list) -> tuple[bool, int]:
        SQL = """INSERT INTO emails (email_subject, email_body, added_by,
        state) VALUES (%s,%s,%s, 'd')"""
        self.run_statement(SQL, (subject,body,user_seq))
        email_seq = self.cur.lastrowid
        recp_sql = """INSERT INTO email_recp (email_seq, email_id, recp_type)
        VALUES (%s,%s,%s)"""
        for email in to:
            if email == "":
                continue
            self.run_statement(recp_sql, (email_seq, email, 't'))
        for email in cc:
            if email == "":
                continue
            self.run_statement(recp_sql, (email_seq, email, 'c'))
        for email in bcc:
            if email == "":
                continue
            self.run_statement(recp_sql, (email_seq, email, 'b'))

        return email_seq

    def get_nav_pages(self):
        self.run_statement("SELECT menu_path FROM plugin_defn WHERE is_active=1")
        return [str(x[0]) for x in self.cur.fetchall()]

    @_convert_to_dict_single
    def get_email_header(self, email_seq: int) -> dict:
        SQL = "SELECT * FROM emails WHERE seq = %s"
        self.run_statement(SQL, (email_seq,))

    @_convert_to_dict
    def get_email_to(self, email_seq) -> List[Dict[str,str]]:
        SQL = "SELECT * FROM email_recp WHERE email_seq=%s AND recp_type = 't'"
        self.run_statement(SQL, (email_seq,))

    @_convert_to_dict
    def get_email_cc(self, email_seq) -> List[Dict[str,str]]:
        SQL = "SELECT * FROM email_recp WHERE email_seq=%s AND recp_type = 'c'"
        self.run_statement(SQL, (email_seq,))

    @_convert_to_dict
    def get_email_bcc(self, email_seq) -> List[Dict[str,str]]:
        SQL = "SELECT * FROM email_recp WHERE email_seq=%s AND recp_type = 'b'"
        self.run_statement(SQL, (email_seq,))

    def get_email_data(self, email_seq):
        email_hdr = self.get_email_header(email_seq)
        to = self.get_email_to(email_seq)
        cc = self.get_email_cc(email_seq)
        bcc = self.get_email_bcc(email_seq)
        return email_hdr, to, cc, bcc

    @_exec_safe
    def mark_email_for_sending(self, email_seq, user_seq):
        sql = "UPDATE emails SET state='p' WHERE seq=%s AND added_by=%s"
        self.run_statement(sql, (email_seq, user_seq))

    def get_queued_emails(self):
        sql = "SELECT seq FROM emails WHERE state = 'p'"
        self.run_statement(sql)
        emails = []
        for row in self.cur.fetchall():
            seq = row[0]
            emails.append(self.get_email_data(seq))
        return emails

    @_exec_safe
    def mark_email_as_sent(self, email_seq):
        sql = "UPDATE emails SET state='s' WHERE seq=%s"
        self.run_statement(sql, (email_seq,))

    @_exec_safe
    def mark_email_as_failed(self, email_seq):
        sql = "UPDATE emails SET state='x' WHERE seq=%s"
        self.run_statement(sql, (email_seq,))

    
    @_exec_safe
    def clear_exp_password_reset(self):
        sql = """DELETE FROM password_reset WHERE
        TIMESTAMPDIFF(DAY, created_dt, current_timestamp) >= 1;"""
        self.run_statement(sql)

    @_exec_safe
    def reset_failed_emails(self):
        sql = """UPDATE emails SET state='p' WHERE state='x'"""
        self.run_statement(sql)

    @_convert_to_dict 
    def get_finance_headers_summary(self) -> List[Dict[str,str]]:
        SQL = "SELECT * FROM finance_hdr_summary"
        self.run_statement(SQL)

    @_convert_to_dict
    def get_finance_users(self):
        SQL = """SELECT DISTINCT
                    A.* FROM users A, class_assignments B, class C, perms D,
                    perm_types E, terms tA, terms tB WHERE B.user_seq = A.seq AND
                    B.class_seq = C.seq AND D.class_seq = C.seq
                    AND D.perm_seq = E.seq AND E.perm_desc = 'fin_add'
                    AND D.granted = 1 AND A.is_active = 1 AND B.start_term = tA.seq AND
                    B.end_term = tB.seq AND tA.start_date <= current_timestamp
                AND current_timestamp <= tB.end_date"""
        self.run_statement(SQL)

    @_convert_to_dict
    def get_finance_approvers(self):
        SQL = """SELECT DISTINCT A.* FROM users A, class_assignments B,
                    class C, perms D, perm_types E, terms tA, terms tB WHERE B.user_seq = A.seq
                AND B.class_seq = C.seq AND D.class_seq = C.seq
                AND D.perm_seq = E.seq AND E.perm_desc = 'fin_approve'
                AND D.granted = 1 AND A.is_active = 1 AND B.start_term = tA.seq AND
                    B.end_term = tB.seq AND tA.start_date <= current_timestamp
                AND current_timestamp <= tB.end_date"""
        self.run_statement(SQL)

    @_convert_to_dict
    def get_finance_types(self):
        SQL = """SELECT * FROM finance_type"""
        self.run_statement(SQL)

    @_convert_to_dict
    def search_items(self, date):
        SQL = """SELECT items.item_name, items.item_vendor,
        item_cost.price, date_format(item_cost.eff_date, '%M %D, %Y') "eff_date",item_cost.seq FROM items,item_cost WHERE
        items.seq = item_cost.item_seq AND items.displayed = 1 AND
    eff_date = (
        SELECT MAX(eff_date) FROM item_cost B
        WHERE B.item_seq = items.seq AND B.eff_date <= %s )"""
        self.run_statement(SQL, (date,))

    @_convert_to_dict_single
    def get_finance_status_by_seq(self, seq):
        SQL = """SELECT * FROM finance_status WHERE seq = %s"""
        self.run_statement(SQL, (seq,))

    @_convert_to_dict_single
    def get_finance_type_by_seq(self, seq) -> dict:
        SQL = """SELECT * FROM finance_type WHERE seq = %s"""
        self.run_statement(SQL, (seq,))

    @_exec_safe
    def add_docket_attachment(self, seq, file_json, user):
        SQL = """INSERT INTO docket_attachments
        (docket_seq, file_name, file_data, added_by, updated_by) VALUES
        (%s,%s,%s,%s,%s)"""
        self.cur.execute(SQL, (seq, file_json['file_name'],
                               base64.b64encode(file_json['file_data'].encode()),
                               user, user))

    @_convert_to_dict
    def get_docket_attachments_summary(self, seq):
        SQL = """SELECT seq, file_name as name FROM docket_attachments WHERE
        docket_seq = %s"""
        self.run_statement(SQL, (seq,))

    def get_docket_attachment(self, attach_seq) -> tuple[str,bytes]:
        SQL = """SELECT file_name ,file_data FROM docket_attachments WHERE
        seq = %s"""
        self.run_statement(SQL, (attach_seq,))
        result = self.cur.fetchone()
        name = result[0]
        data = base64.b64decode(result[1])
        return name, data

    @_convert_to_dict
    def get_users(self):
        SQL = """SELECT * FROM users WHERE is_active = 1"""
        self.run_statement(SQL)

    def get_assignments(self):
        SQL = """SELECT assignment_seq, user_seq, first_name, last_name,
        email, title, position_name, start_date, end_date
        FROM officer_lookup"""
        # SQL = """SELECT ca.seq, c.position_name,
        # concat(u.first_name, ' ', u.last_name) FROM
        # class_assignments ca, class c, users u
        # WHERE ca.class_seq = c.seq AND ca.user_seq = u.seq AND u.is_active=1"""
        assignments = {}
        self.run_statement(SQL)
        data = self.cur.fetchall()
        for row in data:
            class_row = assignments.get(row[6], [])
            class_row.append(row)
            assignments[row[6]] = class_row
        return assignments

    def can_user_access_endpoint(self, user_seq: str | int, endpoint: str) -> bool:
        SQL = """SELECT * FROM plugin_permissions WHERE path_func_name = %s
        AND (perm_seq in (SELECT B.perm_seq FROM perms B, class_assignments C
        WHERE B.class_seq = C.class_seq AND C.user_seq = %s AND B.granted = 1)
        OR perm_seq = (SELECT seq FROM perm_types
        WHERE perm_desc = 'guest'))"""
        logger.debug(SQL % (endpoint, user_seq))
        self.run_statement(SQL, (endpoint, user_seq))
        return self.cur.rowcount > 0

    @_exec_safe
    def update_docket_assignmees(self, docket_seq, data, user_seq):
        assignees = [x['seq'] for x in self.get_docket_assignees(docket_seq)]
        for user in data:
            print(f"{user=}, {user not in assignees}")
            if user not in assignees:
                # INSERT
                SQL = """INSERT INTO docket_assignees 
                (docket_seq, user_seq, added_by, updated_by)
                VALUES (%s,%s,%s,%s)"""
                self.run_statement(SQL, (docket_seq, user, user_seq, user_seq))

        for user in assignees:
            print(f"{user=}, {user not in data}")
            if user not in data:
                #DELETE
                SQL = """DELETE FROM docket_assignees WHERE
                docket_seq = %s AND user_seq = %s"""
                self.run_statement(SQL, (docket_seq, user))

    @_exec_safe
    def add_requested_user(self, data: dict) -> tuple[bool, any]:
        # Insert into our email record in the contacts table
        SQL = """INSERT INTO contacts
            (email_address, first_name, last_name, is_active)
            VALUES (%s,%s,%s,1)"""
        self.run_statement(SQL, (data.get('email'),
                               data.get('fName'),
                               data.get('lName')))
        # Insert into our pending_users table
        SQL = """INSERT INTO pending_users
        (user_name, first_name, last_name, email, title, process_flag)
        VALUES
        (%s,%s,%s,%s,%s, 'S')"""
        self.run_statement(SQL, (data.get('uName'),
                               data.get('fName'),
                               data.get('lName'),
                               data.get('email'),
                               data.get('title')))

    @_convert_to_dict_single
    def get_class_assignment_by_seq(self, seq):
        SQL = """SELECT * FROM officer_lookup WHERE assignment_seq = %s"""
        self.run_statement(SQL, (seq,))

    @_convert_to_dict
    def get_terms(self):
        SQL = """SELECT * FROM terms ORDER BY end_date DESC"""
        self.run_statement(SQL)

    @_exec_safe
    def update_class_assignment(self,
                                seq: int,
                                _class: int,
                                start: int,
                                end: int,
                                user_seq: int) -> tuple[bool, any]:
        SQL = """UPDATE class_assignments SET class_seq=%s,start_term=%s,
        end_term=%s,updated_by=%s WHERE seq=%s"""
        self.run_statement(SQL, (_class, start, end, user_seq, seq))

    @_convert_to_dict
    def get_all_path_rules(self) -> List[Dict[str,str]]:
        SQL = """SELECT A.seq, B.plugin_name, A.path_func_name, C.name_short
        as 'pathperm', D.name_short as 'adminperm'
        FROM plugin_permissions A, plugin_defn B, perm_types C, perm_types D
        WHERE A.plugin_seq = B.seq AND A.perm_seq = C.seq AND
        B.admin_perm = D.seq"""
        self.run_statement(SQL)

    def get_dev_email_addr(self):
        SQL = "SELECT * FROM developer_emails"
        self.run_statement(SQL)
        return [x[0] for x in self.cur.fetchall()]

    @_exec_safe
    def update_permissions(self,
                           perm_seq: int,
                           grant_status: bool, user_seq: int):
        SQL = """SELECT granted FROM perms WHERE seq=%s"""
        self.run_statement(SQL, (perm_seq,))
        granted = self.cur.fetchone()[0]
        if (granted == 1) == grant_status:
            logger.debug(f'Req. Grant and DB Grant are the same. Skipping {perm_seq=}')
            return

        check_sql = """SELECT a.granted FROM perms a, class_assignments b
        WHERE b.user_seq = %s
        AND a.perm_seq = (SELECT b.perm_seq FROM perms b WHERE b.seq = %s);"""
        self.run_statement(check_sql, (user_seq, perm_seq))
        rows = self.cur.fetchall()
        if not any([x[0] == 1 for x in rows]):
            raise Exception(f'User cannot alter perm seq {perm_seq}')

        logger.debug(f"Updating {perm_seq=}, {grant_status=}, {user_seq=}")
        update_sql = """UPDATE perms SET granted = %s, updated_by = %s
        WHERE seq=%s"""
        self.run_statement(update_sql, (grant_status, user_seq, perm_seq))

    @_convert_to_dict_single
    def get_home_widgets(self, user_seq) -> dict:
        SQL = """SELECT
    (SELECT widget_path FROM home_widgets C
    WHERE A.top_left_widget = C.seq) as 'top_left',
    (SELECT widget_path FROM home_widgets C
    WHERE A.top_rght_widget = C.seq) as 'top_right',
    (SELECT widget_path FROM home_widgets C
    WHERE A.bot_left_widget = C.seq) as 'bot_left',
    (SELECT widget_path FROM home_widgets C
    WHERE A.bot_rght_widget = C.seq) as 'bot_right'
    FROM home_page_defn A,
     users B
    WHERE
    B.home_page_seq = A.seq AND B.seq = %s"""
        self.run_statement(SQL, (user_seq,))

    @_exec_safe
    def create_class_assignment(self, user: str, _class: str, start: str,
                                end: str, user_seq: str):
        SQL = """INSERT INTO class_assignments (
            user_seq, class_seq, start_term, end_term, added_by, updated_by
        )
        VALUES (%s,%s,%s,%s,%s,%s)"""
        self.run_statement(SQL, (user, _class, start, end, user_seq, user_seq))

    @_exec_safe
    def delete_class_assignment(self, assignment_seq, user_seq):
        SQL = """
        INSERT INTO del_class_assignments (
            user_seq, class_seq, start_term, end_term, added_by, updated_by,
            added_dt, update_dt)
            SELECT user_seq, class_seq, start_term, end_term, added_by, %s,
            added_dt, current_timestamp FROM class_assignments WHERE seq = %s;
        """
        self.run_statement(SQL, (user_seq, assignment_seq))
        SQL = """DELETE FROM class_assignments WHERE seq = %s"""
        self.run_statement(SQL, (assignment_seq,))
    
    @_exec_safe
    def create_fin_item(self, vendor, name, price, date, visible, user):
        SQL = """INSERT INTO items (item_vendor, item_name, displayed,
        added_by, updated_by) VALUES (%s,%s,%s,%s,%s)"""
        self.run_statement(SQL, (vendor, name, visible, user, user))
        seq = self.cur.lastrowid
        SQL = """INSERT INTO item_cost (item_seq, eff_date, price, added_by,
        updated_by) VALUES (%s,%s,%s,%s,%s)"""
        self.run_statement(SQL, (seq, date, price, user, user))
    
    @_exec_safe
    def update_fin_item(self, vendor, name, price, date, visible, user):
        SQL = """UPDATE items SET displayed = %s WHERE item_name = %s AND
        item_vendor = %s"""
        self.run_statement(SQL, (visible, vendor, name))
        SQL = "SELECT seq FROM items WHERE item_vendor = %s AND item_name = %s"
        self.run_statement(SQL, (vendor, name))
        seq = self.cur.fetchone()[0]
        SQL = """INSERT INTO item_cost (item_seq, eff_date, price, added_by,
        updated_by) VALUES (%s,%s,%s,%s,%s)"""
        self.run_statement(SQL, (seq, date, price, user, user))

    @_convert_to_dict
    def fetch_pending_user_requests(self) -> list[dict]:
        SQL = """SELECT * FROM pending_users WHERE process_flag = 'S'"""
        self.run_statement(SQL)

    @_convert_to_dict
    def get_non_approval_titles(self):
        SQL = """SELECT * FROM titles WHERE approval_req = 0"""
        self.run_statement(SQL)
    
    def get_user_admin_emails(self):
        SQL = """SELECT usr.email FROM users usr, class_assignments cls,
        terms tA, terms tB, perms p, perm_types pt WHERE cls.user_seq = usr.seq
        AND cls.start_term = tA.seq AND cls.end_term = tB.seq AND
        p.class_seq = cls.class_seq AND p.granted = 1 AND p.perm_seq = pt.seq
        and pt.perm_desc = 'user_admin' and tA.start_date <= current_timestamp
        AND current_timestamp <= tB.end_date AND email is not null and
        email != ''"""
        self.run_statement(SQL)
        return [x[0] for x in self.cur.fetchall()]
    
    @_exec_safe
    def update_pending_user_flag(self, request_seq, flag):
        SQL = """UPDATE pending_users SET process_flag=%s WHERE seq=%s"""
        self.run_statement(SQL, (flag, request_seq))
    
    @_exec_safe
    def introspect_database(self):
        self.update_introspection_flag()
        # Get a list of all tables
        self.run_statement('SHOW FULL TABLES')
        db_show_tables = list(self.cur.fetchall())
        for table in db_show_tables:
            select_table = '''SELECT seq, self_introspect FROM db_tables
            WHERE name = %s'''
            self.run_statement(select_table, (table[0],))
            if self.cur.rowcount == 0:
                t_seq = self.create_db_introspection_table(table)
                introspect = 1
            else:
                t_seq, introspect = self.cur.fetchone()
                self.update_db_introspection_table(t_seq)
            if introspect == 1:
                self.update_table_introspection(table[0], t_seq)
                self.conn.commit()
        for table in db_show_tables:
            self.introspect_keys(table[0])
            self.conn.commit()
        self.purge_non_introspected_records()
    
    
    def update_db_introspection_table(self, t_seq):
        sql = "UPDATE db_tables SET maintained=1 WHERE seq=%s"
        self.run_statement(sql, (t_seq,))
    
    def introspect_keys(self, t_name):
        key_sql = """SELECT
    TABLE_NAME,COLUMN_NAME,CONSTRAINT_NAME, REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE REFERENCED_TABLE_SCHEMA = 'management' AND
    REFERENCED_TABLE_NAME = %s"""
        self.run_statement(key_sql, (t_name,))
        results = list(self.cur.fetchall())
        for key in results:
            # Check if key exists.
            search_sql = """SELECT b.seq FROM db_tables a, db_cols b
            WHERE a.seq = b.table_seq AND a.name = %s and b.name = %s"""
            self.run_statement(search_sql, (key[0], key[1]))
            print(search_sql, (key[0], key[1]))
            source = self.cur.fetchone()[0]
            self.run_statement(search_sql, (key[3], key[4]))
            dest = self.cur.fetchone()[0]
            
            rel_search = """SELECT * FROM db_rels WHERE col=%s AND
            target_col=%s"""
            self.run_statement(rel_search, (source, dest))
            if self.cur.rowcount == 0:
                self.insert_row_ref(source, dest)
            else:
                seq = self.cur.fetchone()[0]
                self.update_row_ref(seq, source, dest)
    
    def insert_row_ref(self, source, dest):
        SQL = """INSERT INTO db_rels (col, target_col) VALUES (%s,%s)"""
        self.run_statement(SQL, (source, dest))
    
    def update_row_ref(self, seq, source, dest):
        SQL = """UPDATE db_rels SET maintained = 1 WHERE seq = %s"""
        self.run_statement(SQL, (seq,))
    
    def create_db_introspection_table(self, table: tuple[str,str]):
        table_sql = "INSERT INTO db_tables (name, type) VALUES (%s,%s)"
        table_type = "view" if table[1] == 'VIEW' else 'table' 
        self.run_statement(table_sql, (table[0], table_type))
        return self.cur.lastrowid

    def update_table_introspection(self, t_name, t_seq):
        self.run_statement(f'DESCRIBE {t_name}')
        results = list(self.cur.fetchall())
        for rowdata in results:
            # Check if row exists
            check_sql = """SELECT seq FROM db_cols WHERE table_seq = %s AND
            name=%s"""
            self.run_statement(check_sql, (t_seq,rowdata[0]))
            if self.cur.rowcount == 0:
                self.create_row_introspection(t_seq,rowdata)
            else:
                r_seq = self.cur.fetchone()[0]
                self.update_row_introspection(r_seq, rowdata)
            

    def update_introspection_flag(self):
        
        sql = "UPDATE db_tables SET maintained = 0 WHERE self_introspect = 1"
        self.run_statement(sql)
        
        # Iterate through cols
        sql = """SELECT A.seq from db_cols A, db_tables B WHERE
        A.table_seq = B.seq AND B.self_introspect = 1"""
        self.run_statement(sql)
        cols = self.cur.fetchall()
        for col in cols:
            sql = "UPDATE db_cols SET maintained = 0 WHERE seq = %s"
            self.run_statement(sql, (col[0],))
        
        # Iterate through refs
        # Iterate through cols
        sql = """SELECT UNIQUE A.seq FROM db_rels A, db_cols B, db_tables C
        WHERE (A.col = B.seq OR A.target_col = B.seq) AND B.table_seq = C.seq
        AND C.self_introspect = 1"""
        self.run_statement(sql)
        cols = self.cur.fetchall()
        for col in cols:
            sql = "UPDATE db_rels SET maintained = 0 WHERE seq = %s"
            self.run_statement(sql, (col[0],))

    def purge_non_introspected_records(self):
        sql = """DELETE FROM db_rels WHERE maintained = 0"""
        self.run_statement(sql)
        sql = """DELETE FROM db_cols WHERE maintained = 0"""
        self.run_statement(sql)
        sql = """DELETE FROM db_tables WHERE maintained = 0"""
        self.run_statement(sql)
        
    def create_row_introspection(self, t_seq:int, rowdata:tuple):
        row_sql = """INSERT INTO db_cols (table_seq, name, type)
            VALUES (%s,%s,%s)"""
        self.run_statement(row_sql, (t_seq, rowdata[0], rowdata[1]))
    
    def update_row_introspection(self, r_seq, rowdata):
        update_sql = """UPDATE db_cols SET name=%s, type=%s, maintained=1
        WHERE seq=%s"""
        self.run_statement(update_sql, (rowdata[0], rowdata[1], r_seq))
    
    @_exec_safe
    def create_finance_record(self, data: Dict[str,Any], user: int):
        """{
  "header": {
    "id": "123465",
    "creator": "1",
    "approver": "",
    "status": "5",
    "inv_date": "2024-07-13",
    "type": "1",
    "tax": "0.00",
    "fees": "0.00",
    "total": "78.00"
  },
  "lines": [
    {
      "line_id": 1,
      "item_seq": '1',
      "item_desc": "Pizza, Cheese",
      "item_price": "15.7900",
      "qty": "5",
      "total": "78.950"
    }
  ]
}"""
        header_seq = self.create_finance_header(data['header'], user)
        for line in data['lines']:
            self.create_finance_line(line, header_seq, user)
    
    def create_finance_header(self, data: dict, user: int):
        sql = """INSERT INTO finance_hdr (id, created_by, approved_by,
        inv_date, stat_seq, type_seq, tax, fees, added_by, updated_by) VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        self.run_statement(sql, (
            data['id'],
            data['creator'],
            data['approver'] if data['approver'] != '' else None,
            data['inv_date'],
            data['status'],
            data['type'],
            data['tax'],
            data['fees'],
            user,user
        ))
        
        return self.cur.lastrowid
    
    def create_finance_line(self, line: dict, header_seq:int, user:int):
        """"lines": [
    {
      "line_id": 1,
      "item_seq": '1',
      "item_desc": "Pizza, Cheese",
      "item_price": "15.7900",
      "qty": "5",
      "total": "78.950"
    }
  ]"""
        sql = """INSERT INTO finance_line (finance_seq, line_id, item_id, qty,
        added_by, updated_by) VALUES (%s,%s,%s,%s,%s,%s)"""
        self.cur.execute(sql, (header_seq,
                               line['line_id'],
                               line['item_seq'],
                               line['qty'],
                               user,
                               user))
    
    # __methods__
    def __enter__(self):
        logger.debug("DB Opened in Context Manager")
        return self

    def __exit__(self, exctype: Optional[Type[BaseException]],
             excinst: Optional[BaseException],
             exctb: Optional[TracebackType]):
        try:
            self.conn.rollback()
        except InterfaceError:
            # If we fail to rollback, log it in the log file
            logger.warning('Database failed to roll back')
        self.conn.close()
        logger.debug("DB Instance Closed")
        if exctype is not None:
            logger.critical(f"DB Closed with errors!")
            error_str = f"""Exception: {exctype.__class__}
            {excinst}
            Traceback:\n {'\n'.join(traceback.format_tb(exctb))}"""
            logger.critical(error_str)

    