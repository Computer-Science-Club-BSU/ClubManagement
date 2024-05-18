# Module Imports
import mariadb
import sys
import logging
from typing import Callable

logger = logging.getLogger(__name__)


class connect:
    def __init__(self):

        # Connect to MariaDB Platform
        try:
            self.conn = mariadb.connect(
                user="admin",
                password="password",
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


    def get_user_data_by_seq(self, user_seq):
        # Select User from SQL Table
        logger.debug(f"Getting User Data for User Seq {user_seq}")
        SQL = "SELECT * FROM users WHERE seq = %s"
        self.cur.execute(SQL, (user_seq,))

        # If we did not get a user, return.
        if self.cur.rowcount != 1:
            return
        
        # Assemble a dictionary based off the cursor description.
        field_names = [i[0] for i in self.cur.description]
        data = self.cur.fetchone()
        user_data = { key: val for key, val in zip(field_names, data)}
        return user_data

    def get_user_classes_by_user_seq(self, user_seq):
        logger.debug(f"Getting User Classes for User Seq {user_seq}")
        
        SQL = """SELECT a.position_name FROM class a, class_assignments b
        WHERE a.seq = b.class_seq AND b.user_seq = %s"""
        self.cur.execute(SQL, (user_seq,))
        # Assemble a dictionary based off the cursor description.
        field_names = [i[0] for i in self.cur.description]
        data = self.cur.fetchone()
        class_data = { key: val for key, val in zip(field_names, data)}
        return class_data

    def get_user_perms_by_user_seq(self, user_seq):
        logger.debug(f"Getting User Permissions for User Seq {user_seq}")
        
        SQL = """SELECT a.* FROM perms a, class_assignments b WHERE 
        a.class = b.class_seq AND b.user_seq = 1;"""
        
        self.cur.execute(SQL, (user_seq,))
        field_names = [i[0] for i in self.cur.description]
        data = self.cur.fetchone()
        perm_data = { key: val for key, val in zip(field_names, data)}
        return perm_data
        
    def get_user_finance_dashboards_by_user_seq(self, user_seq):
        return []
    
    def get_user_docket_dashboards_by_user_seq(self, user_seq):
        return []
        
        
        
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


if __name__ == "__main__":
    with connect() as conn:
        print(conn.get_user_by_seq(1))
    