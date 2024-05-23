# Module Imports
import mariadb
import sys
import logging
from typing import Callable
import bcrypt

logger = logging.getLogger(__name__)


class connect:
    def __init__(self):

        # Connect to MariaDB Platform
        try:
            self.conn = mariadb.connect(
                user="admin",
                password="Password123",
                host="localhost",
                port=3306,
                database="management"

            )
            self.cur = self.conn.cursor()

        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)
    
    def _exec_safe(func: Callable):
        def wrapper(self, *args, **kwargs):
            try:
                results = func(self, *args, **kwargs)
                self.conn.commit()
                return results
            except Exception as e:
                self.conn.rollback()
                logger.error(f"Exception Occured {e}")
                return
        return wrapper

    def _convert_to_dict(func: Callable):
        def wrapper(self, *args, **kwargs):
            # Execute the function (Performs the SQL Query)
            func(self, *args, **kwargs)
            # Assemble a dictionary based off the cursor description.
            field_names = [i[0] for i in self.cur.description]
            data = self.cur.fetchall()
            row_data = []
            for row in data:

                row_data.append(
                    {key: val
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
            field_names = [i[0] for i in self.cur.description]
            data = self.cur.fetchone()
            return {key: val
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
    def get_user_data_by_seq(self, user_seq):
        # Select User from SQL Table
        logger.debug(f"Getting User Data for User Seq {user_seq}")
        SQL = "SELECT * FROM users WHERE seq = %s"
        self.cur.execute(SQL, (user_seq,))

    @_convert_to_dict
    def get_user_classes_by_user_seq(self, user_seq):
        logger.debug(f"Getting User Classes for User Seq {user_seq}")
        
        SQL = """SELECT a.position_name FROM class a, class_assignments b
        WHERE a.seq = b.class_seq AND b.user_seq = %s"""
        self.cur.execute(SQL, (user_seq,))
        

    def get_user_perms_by_user_seq(self, user_seq):
        logger.debug(f"Getting User Permissions for User Seq {user_seq}")
        
        SQL = """SELECT a.seq, d.perm_desc, a.granted FROM
        perms a, class_assignments c, perm_types d
        WHERE a.class_seq = c.class_seq
        AND c.seq = a.perm_seq
        AND c.user_seq = %s;"""
        
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
        
    def get_user_finance_dashboards_by_user_seq(self, user_seq):
        return []
    
    def get_user_docket_dashboards_by_user_seq(self, user_seq):
        return []
        
    
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
    def get_finance_headers(self) -> list[dict]:
        SQL = """SELECT * FROM finance_hdr"""
        self.cur.execute(SQL)
        
    @_convert_to_dict
    def get_finance_lines_by_hdr(self, hdr_seq: int) -> list[dict]:
        SQL = """SELECT * FROM finance_line WHERE finance_seq = %s"""
        self.cur.execute(SQL, (hdr_seq,))

    def get_finances(self) -> list[dict]:
        # Get the header data
        headers = self.get_finance_headers()
        for item in headers:
            hdr_seq = item['seq']
            lines = self.get_finance_lines_by_hdr(hdr_seq)
            item['lines'] = lines
        
        return headers
    
    @_convert_to_dict
    def get_finance_statuses(self) -> list[dict]:
        SQL = "SELECT * from finance_status"
        self.cur.execute(SQL)
    
    @_convert_to_dict
    def get_finance_hdr_by_status(self, stat_desc: str) -> list[dict]:
        SQL = """SELECT a.* from finance_hdr a,
        finance_status b where a.stat_seq = b.seq AND b.stat_desc = %s"""
        self.cur.execute(SQL, (stat_desc,))
    

    @_convert_to_dict
    def get_docket_statuses(self) -> list[dict]:
        SQL = "SELECT * from docket_status"
        self.cur.execute(SQL)
    
    @_convert_to_dict
    def get_docket_hdr_by_status(self, stat_desc: str) -> list[dict]:
        SQL = """SELECT a.* from docket_hdr a,
        docket_status b where a.stat_seq = b.seq AND b.stat_desc = %s"""
        self.cur.execute(SQL, (stat_desc,))


    @_convert_to_dict_single
    def get_docket_by_seq(self, seq: int) -> dict:
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
        SQL = """SELECT conv.seq, concat(u.first_name, ' ', u.last_name)"""


    def get_all_docket_data_by_seq(self, seq):
        seq = int(seq)
        docket_data = self.get_docket_by_seq(seq)
        conversations = self.get_docket_conversations(seq)
        return {
            "docket": docket_data
        }

    def get_finance_summary(self):
        # Get finance statuses
        summary = {}
        for status in self.get_finance_statuses():
            stat = status['stat_desc']
            summary[stat] = len(self.get_finance_hdr_by_status(stat))
        return summary
    
    @_convert_to_dict
    def get_about_page_assignments(self) -> list[dict]:
        SQL = """SELECT CONCAT(a.first_name, ' ', a.last_name) AS 'name',
        c.position_name FROM users a, class_assignments b, class c WHERE
        b.user_seq = a.seq AND b.class_seq = c.seq AND c.displayed = 1
        AND a.is_active = 1 ORDER BY c.ranking ASC;"""
        self.cur.execute(SQL)
        

    def get_docket_summary(self):
        summary = {}
        for status in self.get_docket_statuses():
            stat = status['stat_desc']
            summary[stat] = len(self.get_docket_hdr_by_status(stat))
        return summary
    
    @_convert_to_dict
    def get_all_non_archived_docket(self) -> list[dict]:
        SQL = """SELECT hdr.seq, hdr.docket_title, hdr.docket_desc,
        stat.stat_desc as 'status', vote.vote_desc,
        hdr.added_by as 'creator_seq',
        DATE_FORMAT(hdr.added_dt, '%W, %M %D, %Y') as 'added_dt',
        concat(u.first_name, ' ', u.last_name) as 'creator'
        FROM docket_hdr hdr, docket_status stat, vote_types vote, users u
        WHERE hdr.vote_type = vote.seq AND hdr.stat_seq = stat.seq AND
        LOWER(stat.stat_desc) != 'archived' AND hdr.added_by = u.seq;"""
        self.cur.execute(SQL)

    # __methods__
    def __enter__(self):
        logger.info("DB Opened in Context Manager")
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.conn.rollback()
        self.conn.close()
        logger.info("DB Instance Closed")
        if exc_type is not None or exc_value is not None or exc_tb is not None:
            logger.error(f"DB Exited with errors!")
            logger.error(f"{exc_type=}")
            logger.error(f"{exc_value=}")
            logger.error(f"{exc_tb=}")

    