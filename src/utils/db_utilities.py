# Module Imports
import mariadb
import sys
import logging

logger = logging.getLogger(__name__)


class connect:
    def __init__(self, isContext = False):
        if not isContext:
            logger.info("DB Instance Created (Non-Context Managered!)")

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
    
    def _exec_safe(func):
        def wrapper(self, *args, **kwargs):
            try:
                results = func(self, *args, **kwargs)
                self.conn.commit()
                return results
            except Exception as e:
                self.conn.rollback()
                print(e)
                return
        return wrapper
    
    @_exec_safe
    def get_user_by_seq(self, user_seq):
        """Get a user by their seq

        Args:
            user_seq (int): User Sequence Number (Unique Identifier)
        """
        # Select User from SQL Table
        logger.info("")
        SQL = "SELECT * FROM users WHERE seq = %s"
        self.cur.execute(SQL, (user_seq,))

        # If we did not get a user, return.
        if self.cur.rowcount != 1:
            return
        
        # Assemble a dictionary based off the cursor description.
        field_names = [i[0] for i in self.cur.description]
        data = self.cur.fetchone()
        return { key: val for key, val in zip(field_names, data)}



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

    