# Module Imports
import mariadb
import bleach
import sys
import logging
from typing import Callable
import bcrypt
from mariadb import InterfaceError
from src.utils.cfg_utils import get_cfg
import base64
from typing import List, Dict

logger = logging.getLogger("DatabaseManager")


class connect:
    def __init__(self):

        # Connect to MariaDB Platform
        conf = get_cfg()['DATA']
        try:
            self.conn = mariadb.connect(
                user=conf['USER'],
                password=conf['PASS'],
                host=conf['HOST'],
                port=conf['PORT'],
                database=conf['NAME']

            )
            self.cur = self.conn.cursor()

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
                logger.error(f"DB Exception Occured {e}")
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
                    {key: bleach.clean(val)
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

            return {key: bleach.clean(val)
                        for key, val in zip(field_names, data)
                    }
        return wrapper

    
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
        self.cur.execute(SQL, (user_seq,))

    @_convert_to_dict
    def get_user_classes_by_user_seq(self, user_seq) -> List[Dict[str,str]]:
        logger.debug(f"Getting User Classes for User Seq {user_seq}")

        SQL = """SELECT a.position_name FROM class a, class_assignments b
        WHERE a.seq = b.class_seq AND b.user_seq = %s"""
        self.cur.execute(SQL, (user_seq,))


    def get_user_perms_by_user_seq(self, user_seq):
        logger.debug(f"Getting User Permissions for User Seq {user_seq}")

        SQL = """SELECT a.seq, d.perm_desc, a.granted FROM
        perms a, class_assignments c, perm_types d, terms ea, terms eb
        WHERE a.class_seq = c.class_seq
        AND d.seq = a.perm_seq
        AND c.user_seq = %s AND ea.seq = c.start_term AND eb.seq = c.end_term
        AND ea.start_date <= current_timestamp
        AND eb.end_date >= current_timestamp;"""

        self.cur.execute(SQL, (user_seq,))
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
        self.cur.execute(SQL, (user_seq,))

    
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
        self.cur.execute(sql, (username,))
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
        self.cur.execute(SQL)

    @_convert_to_dict
    def get_finance_lines_by_hdr(self, hdr_seq: int) -> List[Dict[str,str]]:
        SQL = """SELECT * FROM finance_line WHERE finance_seq = %s"""
        self.cur.execute(SQL, (hdr_seq,))

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
        self.cur.execute(SQL)

    @_convert_to_dict
    def get_finance_hdr_by_status(self, stat_desc: str) -> List[Dict[str,str]]:
        SQL = """SELECT a.* from finance_hdr a,
        finance_status b where a.stat_seq = b.seq AND b.stat_desc = %s"""
        self.cur.execute(SQL, (stat_desc,))


    @_convert_to_dict
    def get_docket_statuses(self) -> List[Dict[str,str]]:
        SQL = "SELECT * from docket_status"
        self.cur.execute(SQL)

    @_convert_to_dict
    def get_docket_hdr_by_status(self, stat_desc: str) -> List[Dict[str,str]]:
        SQL = """SELECT a.* from docket_hdr a,
        docket_status b where a.stat_seq = b.seq AND b.stat_desc = %s"""
        self.cur.execute(SQL, (stat_desc,))


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
        self.cur.execute(SQL, (seq,))

    @_convert_to_dict
    def get_docket_conversations(self, seq):
        SQL = """SELECT conv.seq, concat(usr.first_name, ' ', usr.last_name)
        AS 'name', conv.creator, conv.body
        FROM docket_conversations conv, users usr
        WHERE conv.creator = usr.seq
        AND conv.docket_seq = %s
        ORDER BY dt_added;"""
        self.cur.execute(SQL, (seq,))

    @_convert_to_dict
    def get_docket_assignees(self, seq) -> dict:
        SQL = """SELECT assn.seq, concat(usr.first_name, ' ', usr.last_name)
        AS 'name', assn.user_seq
        FROM docket_assignees assn, users usr
        WHERE assn.user_seq = usr.seq AND
        assn.docket_seq = %s ORDER BY assn.added_dt;"""
        self.cur.execute(SQL, (seq,))


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
        SQL = """SELECT a.title, CONCAT(a.first_name, ' ', a.last_name) AS 'name',
        c.position_name FROM users a, class_assignments b, class c,
        terms d_a, terms d_b WHERE
        b.user_seq = a.seq AND b.class_seq = c.seq AND c.displayed = 1
        AND a.is_active = 1 AND b.start_term = d_a.seq AND b.end_term = d_b.seq
        AND d_a.start_date <= current_timestamp AND
        d_b.end_date >= current_timestamp ORDER BY c.ranking ASC;"""
        self.cur.execute(SQL)

    @_convert_to_dict
    def get_about_former_officers(self) -> List[Dict[str,str]]:
        SQL = """SELECT A.title, concat(A.first_name, ' ', A.last_name) as
        'name', C.position_name, Da.term_desc as 'start', Db.term_desc as 'end'
        FROM users A, class_assignments B, class C, terms Da, terms Db
        WHERE B.user_seq = A.seq AND B.class_seq = C.seq AND
        B.start_term = Da.seq AND B.end_term = Db.seq AND C.displayed = 1
        AND Db.end_date < current_date ORDER BY Db.end_date DESC"""
        self.cur.execute(SQL)


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
        self.cur.execute(SQL)

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
        self.cur.execute(SQL)

    @_exec_safe
    def create_docket_conversation(self,
                                   doc_seq: int,
                                   user_seq: int,
                                   conv_data: str) -> tuple[bool, any]:
        SQL = """INSERT INTO docket_conversations
        (docket_seq, creator, body) VALUES (%s,%s,%s)"""
        self.cur.execute(SQL, (doc_seq,user_seq,conv_data))


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
        self.cur.execute(SQL, (doc_seq, assignee, user_seq, user_seq))

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
        self.cur.execute(SQL, (user_seq, dash_seq))
        if self.cur.rowcount != 1:
            return False
        sp_name = self.cur.fetchone()[0]

        self.cur.callproc(sp_name)

    @_convert_to_dict
    def get_docket_vote_types(self):
        SQL = "SELECT * FROM vote_types"
        self.cur.execute(SQL)

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
        self.cur.execute(SQL, vals)

    @_convert_to_dict
    def get_permission_data(self) -> List[Dict[str,str]]:
        SQL = """SELECT * FROM perm_types WHERE grantable=1;"""
        self.cur.execute(SQL)

    @_convert_to_dict
    def get_all_db_perms(self) -> List[Dict[str,str]]:
        SQL = "SELECT * FROM perms"
        self.cur.execute(SQL)

    @_convert_to_dict
    def get_user_classes(self) -> List[Dict[str,str]]:
        SQL = """SELECT * FROM class"""
        self.cur.execute(SQL)

    def get_class_perms(self) -> dict[dict]:
        SQL = """SELECT perms.seq, perms.granted, c.position_name,
        p.name_short, p.perm_desc from perms LEFT JOIN (class c, perm_types p)
        ON (perms.class_seq = c.seq AND perms.perm_seq = p.seq
        AND p.grantable = 1);"""
        self.cur.execute(SQL)
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
        self.cur.execute(SQL, (class_name, user_seq, user_seq))
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
        self.cur.execute(SQL, (subject,body,user_seq))
        email_seq = self.cur.lastrowid
        recp_sql = """INSERT INTO email_recp (email_seq, email_id, recp_type)
        VALUES (%s,%s,%s)"""
        for email in to:
            if email == "":
                continue
            self.cur.execute(recp_sql, (email_seq, email, 't'))
        for email in cc:
            if email == "":
                continue
            self.cur.execute(recp_sql, (email_seq, email, 'c'))
        for email in bcc:
            if email == "":
                continue
            self.cur.execute(recp_sql, (email_seq, email, 'b'))

        return email_seq

    def get_nav_pages(self):
        self.cur.execute("SELECT menu_path FROM plugin_defn WHERE is_active=1")
        return [str(x[0]) for x in self.cur.fetchall()]

    @_convert_to_dict_single
    def get_email_header(self, email_seq: int) -> dict:
        SQL = "SELECT * FROM emails WHERE seq = %s"
        self.cur.execute(SQL, (email_seq,))

    @_convert_to_dict
    def get_email_to(self, email_seq) -> List[Dict[str,str]]:
        SQL = "SELECT * FROM email_recp WHERE email_seq=%s AND recp_type = 't'"
        self.cur.execute(SQL, (email_seq,))

    @_convert_to_dict
    def get_email_cc(self, email_seq) -> List[Dict[str,str]]:
        SQL = "SELECT * FROM email_recp WHERE email_seq=%s AND recp_type = 'c'"
        self.cur.execute(SQL, (email_seq,))

    @_convert_to_dict
    def get_email_bcc(self, email_seq) -> List[Dict[str,str]]:
        SQL = "SELECT * FROM email_recp WHERE email_seq=%s AND recp_type = 'b'"
        self.cur.execute(SQL, (email_seq,))

    def get_email_data(self, email_seq):
        email_hdr = self.get_email_header(email_seq)
        to = self.get_email_to(email_seq)
        cc = self.get_email_cc(email_seq)
        bcc = self.get_email_bcc(email_seq)
        return email_hdr, to, cc, bcc

    @_exec_safe
    def mark_email_for_sending(self, email_seq, user_seq):
        sql = "UPDATE emails SET state='p' WHERE seq=%s AND added_by=%s"
        self.cur.execute(sql, (email_seq, user_seq))

    def get_queued_emails(self):
        sql = "SELECT seq FROM emails WHERE state = 'p'"
        self.cur.execute(sql)
        emails = []
        for row in self.cur.fetchall():
            seq = row[0]
            emails.append(self.get_email_data(seq))
        return emails

    @_exec_safe
    def mark_email_as_sent(self, email_seq):
        sql = "UPDATE emails SET state='s' WHERE seq=%s"
        self.cur.execute(sql, (email_seq,))

    @_exec_safe
    def mark_email_as_failed(self, email_seq):
        sql = "UPDATE emails SET state='x' WHERE seq=%s"
        self.cur.execute(sql, (email_seq,))

    
    @_exec_safe
    def clear_exp_password_reset(self):
        sql = """DELETE FROM password_reset WHERE
        TIMESTAMPDIFF(DAY, created_dt, current_timestamp) >= 1;"""
        self.cur.execute(sql)

    @_exec_safe
    def reset_failed_emails(self):
        sql = """UPDATE emails SET state='p' WHERE state='x'"""
        self.cur.execute(sql)

    @_convert_to_dict 
    def get_finance_headers_summary(self) -> List[Dict[str,str]]:
        SQL = "SELECT * FROM finance_hdr_summary"
        self.cur.execute(SQL)

    @_convert_to_dict
    def get_finance_users(self):
        SQL = """SELECT DISTINCT
                    A.* FROM users A, class_assignments B, class C, perms D,
                    perm_types E WHERE B.user_seq = A.seq AND
                    B.class_seq = C.seq AND D.class_seq = C.seq
                    AND D.perm_seq = E.seq AND E.perm_desc = 'fin_add'
                    AND D.granted = 1 AND A.is_active = 1"""
        self.cur.execute(SQL)

    @_convert_to_dict
    def get_finance_approvers(self):
        SQL = """SELECT DISTINCT A.* FROM users A, class_assignments B,
                    class C, perms D, perm_types E WHERE B.user_seq = A.seq
                AND B.class_seq = C.seq AND D.class_seq = C.seq
                AND D.perm_seq = E.seq AND E.perm_desc = 'fin_approve'
                AND D.granted = 1 AND A.is_active = 1"""
        self.cur.execute(SQL)

    @_convert_to_dict
    def get_finance_types(self):
        SQL = """SELECT * FROM finance_type"""
        self.cur.execute(SQL)

    @_convert_to_dict
    def search_items(self, date):
        SQL = """SELECT items.item_name, items.item_vendor,
        item_cost.price, date_format(item_cost.eff_date, '%M %D, %Y') "eff_date",item_cost.seq FROM items,item_cost WHERE
        items.seq = item_cost.item_seq AND items.displayed = 1 AND
    eff_date = (
        SELECT MAX(eff_date) FROM item_cost B
        WHERE B.item_seq = items.seq AND B.eff_date <= %s )"""
        self.cur.execute(SQL, (date,))

    @_convert_to_dict_single
    def get_finance_status_by_seq(self, seq):
        SQL = """SELECT * FROM finance_status WHERE seq = %s"""
        self.cur.execute(SQL, (seq,))

    @_convert_to_dict_single
    def get_finance_type_by_seq(self, seq) -> dict:
        SQL = """SELECT * FROM finance_type WHERE seq = %s"""
        self.cur.execute(SQL, (seq,))

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
        self.cur.execute(SQL, (seq,))

    def get_docket_attachment(self, attach_seq) -> tuple[str,bytes]:
        SQL = """SELECT file_name ,file_data FROM docket_attachments WHERE
        seq = %s"""
        self.cur.execute(SQL, (attach_seq,))
        result = self.cur.fetchone()
        name = result[0]
        data = base64.b64decode(result[1])
        return name, data

    @_convert_to_dict
    def get_users(self):
        SQL = """SELECT * FROM users WHERE is_active = 1"""
        self.cur.execute(SQL)

    def get_assignments(self):
        SQL = """SELECT assignment_seq, user_seq, first_name, last_name,
        email, title, position_name, start_date, end_date
        FROM officer_lookup"""
        # SQL = """SELECT ca.seq, c.position_name,
        # concat(u.first_name, ' ', u.last_name) FROM
        # class_assignments ca, class c, users u
        # WHERE ca.class_seq = c.seq AND ca.user_seq = u.seq AND u.is_active=1"""
        assignments = {}
        self.cur.execute(SQL)
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
        WHERE perm_desc = 'Guest'))"""
        self.cur.execute(SQL, (endpoint, user_seq))
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
                self.cur.execute(SQL, (docket_seq, user, user_seq, user_seq))

        for user in assignees:
            print(f"{user=}, {user not in data}")
            if user not in data:
                #DELETE
                SQL = """DELETE FROM docket_assignees WHERE
                docket_seq = %s AND user_seq = %s"""
                self.cur.execute(SQL, (docket_seq, user))

    @_exec_safe
    def add_requested_user(self, data: dict) -> tuple[bool, any]:
        # Insert into our email record in the contacts table
        SQL = """INSERT INTO contacts
            (email_address, first_name, last_name, is_active)
            VALUES (%s,%s,%s,1)"""
        self.cur.execute(SQL, (data.get('email'),
                               data.get('fName'),
                               data.get('lName')))
        # Insert into our pending_users table
        SQL = """INSERT INTO pending_users
        (user_name, first_name, last_name, email, title, process_flag)
        VALUES
        (%s,%s,%s,%s,%s, 'S')"""
        self.cur.execute(SQL, (data.get('uName'),
                               data.get('fName'),
                               data.get('lName'),
                               data.get('email'),
                               data.get('title')))

    @_convert_to_dict_single
    def get_class_assignment_by_seq(self, seq):
        SQL = """SELECT * FROM officer_lookup WHERE assignment_seq = %s"""
        self.cur.execute(SQL, (seq,))

    @_convert_to_dict
    def get_terms(self):
        SQL = """SELECT * FROM terms ORDER BY end_date DESC"""
        self.cur.execute(SQL)

    @_exec_safe
    def update_class_assignment(self,
                                seq: int,
                                _class: int,
                                start: int,
                                end: int,
                                user_seq: int) -> tuple[bool, any]:
        SQL = """UPDATE class_assignments SET class_seq=%s,start_term=%s,
        end_term=%s,updated_by=%s WHERE seq=%s"""
        self.cur.execute(SQL, (_class, start, end, user_seq, seq))

    @_convert_to_dict
    def get_all_path_rules(self) -> List[Dict[str,str]]:
        SQL = """SELECT A.seq, B.plugin_name, A.path_func_name, C.name_short
        as 'pathperm', D.name_short as 'adminperm'
        FROM plugin_permissions A, plugin_defn B, perm_types C, perm_types D
        WHERE A.plugin_seq = B.seq AND A.perm_seq = C.seq AND
        B.admin_perm = D.seq"""
        self.cur.execute(SQL)

    def get_dev_email_addr(self):
        SQL = "SELECT * FROM developer_emails"
        self.cur.execute(SQL)
        return [x[0] for x in self.cur.fetchall()]

    @_exec_safe
    def update_permissions(self,
                           perm_seq: int,
                           grant_status: bool, user_seq: int):
        SQL = """SELECT granted FROM perms WHERE seq=%s"""
        self.cur.execute(SQL, (perm_seq,))
        granted = self.cur.fetchone()[0]
        if (granted == 1) == grant_status:
            logger.debug(f'Req. Grant and DB Grant are the same. Skipping {perm_seq=}')
            return

        check_sql = """SELECT a.granted FROM perms a, class_assignments b
        WHERE b.user_seq = %s
        AND a.perm_seq = (SELECT b.perm_seq FROM perms b WHERE b.seq = %s);"""
        self.cur.execute(check_sql, (user_seq, perm_seq))
        rows = self.cur.fetchall()
        if not any([x[0] == 1 for x in rows]):
            raise Exception(f'User cannot alter perm seq {perm_seq}')

        logger.debug(f"Updating {perm_seq=}, {grant_status=}, {user_seq=}")
        update_sql = """UPDATE perms SET granted = %s, updated_by = %s
        WHERE seq=%s"""
        self.cur.execute(update_sql, (grant_status, user_seq, perm_seq))

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
        self.cur.execute(SQL, (user_seq,))

    # __methods__
    def __enter__(self):
        logger.debug("DB Opened in Context Manager")
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        try:
            self.conn.rollback()
        except InterfaceError:
            # If we fail to rollback, log it in the log file
            logger.warning('Database failed to roll back')
        self.conn.close()
        logger.debug("DB Instance Closed")
        if exc_type is not None:
            logger.error(f"DB Exited with errors!")
            logger.error(f"{exc_type=}")
            logger.error(f"{exc_value=}")
            logger.error(f"{exc_tb=}")

    