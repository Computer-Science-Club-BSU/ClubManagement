import unittest
from src.utils.db_utilities import connect
from app import app



class TestDatabaseIntegrity(unittest.TestCase):    
    def test_route_perms(self):
        with connect() as conn:
            path_rules = conn.get_all_path_rules()
            path_rules = {x.get('path_func_name'): x for x in path_rules} # path_rules is executed with the convert_to_dict decorator. pylint: disable=not-an-iterable
            paths = list({x.endpoint for x in app.url_map.iter_rules()})
            for path in paths:
                self.assertNotEqual(path_rules.get(path), None,
                                    f"Endpoint \"{path}\" does not have valid"\
                                        " permission record in Database.")

class TestInterfaceIntegrity(unittest.TestCase):
    def test_route_log_in(self):
        pass


if __name__ == '__main__':
    unittest.main()
