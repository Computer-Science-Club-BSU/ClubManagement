from pymongo import MongoClient
from bson import ObjectId
from contextlib import contextmanager
from dotenv import load_dotenv
from os import environ
import time
import bcrypt
from typing import Tuple, List, Dict, Any
from uuid import uuid4
import pyotp
from cryptography.fernet import Fernet

class _connect:
    def __init__(self): 
        """Create a connection to the MongoDB specified in the .env file.<br>
        NOTE: This method does not support authentication methods."""
        # loads the environment variables from the .env file in the root 
        # directory
        load_dotenv()
        try:
            # Build a connection string to connect to Mongo
            host = environ['HOST']
            db = environ['DB']
            uri = f"mongodb://{host}:27017/"
            # Connect!
            self.conn = MongoClient(uri)
            self.db = self.conn[db]
        except Exception as e:
            # If we fail (Which is entirely possible), print the error and exit.
            print(e)    
            exit(1)

    def get_all_finances(self) -> list:
        """Searches the MongoDB for all finance records"""
        results = list(self.db['finances'].find())
        return results

    def save_user(self, user_dict: dict) -> ObjectId:
        """
        Saves the user from the dictionary provided. <br>
        Returns the object id of the new user. <br>
        This should only be called by the `config_app.py` file.
        """
        # Insert the user dictionary and store the result object
        result = self.db['users'].insert_one(user_dict | {
            "dt_added": int(time.time()),
            "dt_updated": int(time.time()),
            "is_active": True
        })
        # Get the ObjectId
        id = result.inserted_id
        # Set the created by to be the row that was inserted.
        self.db['users'].update_one({"_id": id},
                                    {"$set" :{"updated_by": id,
                                     "added_by": id}})
        self.db['users'].create_index("user_name", unique=True)
        return id

    def get_user_by_seq(self, user__id: str | ObjectId) -> Dict[str, Any]:
        """Search for a user by their _id value"""

        # Find a user whose _id value matches, and who is still listed as "active" in the system
        users = list(self.db['users'].find({"$and": [
            {"_id": ObjectId(user__id)},
            {"is_active": True}
            ]}))
        # If we matched (somehow) more than one then alert the user that their account isn't "unique"...
        # Sucks to not be unique, doesn't it...
        if len(users) > 1:
            return #TODO: Raise User _id Not Unique!

        # If we matched zero users, then alert the user that their account wasn't found!
        if len(users) == 0:
            return #TODO: Raise user Not Found!

        # If we matched one and only one user, then return that value.
        return users[0]
        
    
    def get_user_vote_perms(self, user__id) -> Dict[str, bool]:
        """
        Get the voting permissions of the user by their _id value
        """
        # Get the user's dictionary, and return the "voting" object from the "permissions" object.
        user = self.get_user_by_seq(user__id)
        
        return user.get("permissions", {}).get("voting", None)
    
    def get_user_by_user_name(self, user_name: str) -> Dict[str, Any]:

        users = list(self.db['users'].find({"user_name": user_name}))
        # If we matched (somehow) more than one then alert the user that their account isn't "unique"...
        # Sucks to not be unique, doesn't it...
        # THIS SHOULD NEVER BE RAISED! ALL USERNAMES SHOULD BE UNIQUE!
        if len(users) > 1:
            return  # TODO: Raise user_name Not Unique!

        # If we matched zero users, then alert the user that their account wasn't found!
        if len(users) == 0:
            return  # TODO: Raise user Not Found!
        
        return users[0]
    
    def check_user_valid(self,
                         username: str,
                         password: str,
                         OTP: str) -> Tuple[bool, str|None, str|None]:
        """Check if a user's provided password matches with their stored password

        :param username: The user's username
        :param password: The password provided by the user
        :param OTP: The OTP provided by the user
        :return: Tuple of (True, UserID, UserName) or (False, None, None)
        """
        # Get the user's information by their username
        user = self.get_user_by_user_name(username)

        # Get the stored password from the user's account
        stored_pw = user.get("password")
        if stored_pw is None: # If the password is not set, then do not allow the user to sign in.
            print("No password set")
            return False, None, None

        # If the password does not match, do not let the user log in.
        if not bcrypt.checkpw(password.encode("utf-8"),
                              stored_pw):
            print("Password Doesnt match")
            return False, None, None

        # Check OTP
        if not self.check_user_otp(user['_id'], OTP):
            print("OTP doesnt match")
            return False, None, None

        # Otherwise, return True, and the user data.
        return True, user.get("_id"), user.get("user_name")

    def is_user_admin(self, user__id: str) -> bool:
        """Check if the user is an administrator.

        :param user__id: The user's _id value
        :return: True if the user is an Administrator, otherwise False
        """
        user = self.get_user_by_seq(user__id)
        return user.get("permissions", {}).get("user_admin", False)

    
    def can_user_edit_finances(self, user__id: str) -> bool:
        user = self.get_user_by_seq(user__id)
        finance_edit = user.get("permissions", {}).get("inv_edit", False)
        finance_admin = user.get("permissions", {}).get("inv_admin", False)
        return finance_admin or finance_edit
    
    def get_all_finance_status_names(self) -> List[str]:
        return [ x['config_value']
                for x in self.db['config'].find(
                    {"config_type": "finance_status"},
                    {"_id": 0, "config_value": 1}
                )
            ]
    
    def get_all_fin_status_data(self) -> List[Dict[str, Any]]:
        return [ x['config_value']
                    for x in self.db['config'].find(
                        {"config_type": "finance_status"}
                    )
                ]

    def get_all_finance_types(self) -> List[str]:
        return [ x['config_value']
                for x in self.db['config'].find(
                    {"config_type": "finance_type"},
                    {"_id": 0, "config_value": 1}
                )
            ]

    def get_all_fin_types_data(self) -> List[Dict[str, Any]]:
        return [ x['config_value']
                for x in self.db['config'].find(
                    {"config_type": "finance_type"},
                )
            ]
        
    def filter_finances(self, filter_data: dict) -> Dict[str, Any]:
        print(filter_data.get("status",{}), filter_data.get("types", {}))
        return_list = []
        finances = self.get_all_finances()
        for finance in finances:
            status = finance['status']
            rec_type = finance['type']
            print(status, rec_type)
            print(filter_data.get("status",{}).get(status, False),
                  filter_data.get("types", {}).get(rec_type, False))
            if filter_data.get("status",{}).get(status, False) and \
                filter_data.get("types", {}).get(rec_type, False):
                return_list.append(finance)

        return return_list
    
    def get_record_by_seq(self, _id: str) -> dict:
        return self.db['finances'].find_one({"_id": ObjectId(_id)})
    
    def get_user_by_full_name(self, full_name: str) -> dict:
        users = self.db['users'].find({"is_active": True})
        for user in users:
            user_name = user['first_name'] + '' + user['last_name']
            if user_name == full_name:
                return user
    
    def get_type_seq(self, type_desc: str) -> str:
        return str(
            self.db['config'].find_one({'config_type': 'finance_type', 
                                        'config_value': type_desc}, 
                                        {
                                            '_id': 1
                                        })['_id']
                                    )
    
    def get_status_seq(self, stat_desc: str) -> str:
        return str(
            self.db['config'].find_one({'config_type': 'finance_status', 
                                        'config_value': stat_desc}, 
                                        {
                                            '_id': 1
                                        })['_id']
                                    )
    
    def create_record(self, record_data: dict, user: dict):
        result = self.db['finances'].insert_one(record_data)
        id = result.inserted_id
        current_time = int(time.time())
        self.db['users'].update_one({"_id": id}, 
                                    {"$set" :{"updated_by": id,
                                     "added_by": id,
                                     "dt_added": current_time,
                                     "dt_updated": current_time}})
        return id
    
    def check_invoice_info(self,
                           user_full_name: str,
                           user_pin: str) -> Tuple[bool, bool, bool]:
        user = self.get_user_by_full_name(user_full_name)
        if user is None:
            return (False, False, False)
        if user.get('finance_pin') != user_pin:
            return (False, False, False)
        perms = user.get("permissions", {})
        return (perms.get("inv_admin"),
                perms.get("inv_edit"),
                perms.get("approved_invoices"))
    
    def get_all_finance_users(self) -> list[dict]:
        return list(
            self.db['users'].find({
                "$and": [
                    {
                    "$or": [
                        {"permissions.inv_admin": True},
                        {"permissions.inv_edit": True},
                        {"permissions.approve_invoices": True}
                    ]},
                    {
                        "is_active": True
                    }
                ]
            })
        )
    
    def get_all_approvers(self):
        return list(
            self.db['users'].find({
                "$and": [
                    {
                    "$or": [
                        {"permissions.inv_admin": True},
                        {"permissions.approve_invoices": True}
                    ]},
                    {
                        "is_active": True
                    }
                ]
            })
        )
    
    def get_lines(self, _id):
        return self.db['finances'].find_one(
            {"_id": ObjectId(_id)}
        )['lines']
    
    def edit_record(self, _id: str, data: dict, current_user: dict):
        self.db['finances'].update_one(
            {"_id": ObjectId(id)},
            {
                "$set": data
            }
            )
        self.db['finances'].update_one(
            {"_id": ObjectId(_id)},
            {
                "$dt_updated": int(time.time()),
                "updated_by": current_user['_id'],
            }
        )

    def get_finance_dashboard_by_name(self, dashboard_name: str):
        results = self.db['config'].find_one({
            "config_type": 'finance_dashboard',
            "config_value.name": dashboard_name
        })
        return results
    
    def get_finance_dashboard_by_id(self, _id: str):
        results = self.db['config'].find_one({
            "config_type": 'finance_dashboard',
            "_id": ObjectId(_id)
        })
        return results
    
    def get_finance_dashboard_contents(self, dashboard_name: str, user: dict):
        dashboard = self.get_finance_dashboard_by_name(dashboard_name)
        if str(user['_id']) not in [str(x) for x in dashboard['config_value']['users']]:
            raise Exception #TODO: Implement Custom Exception
        return list(self.db['finances'].find(dashboard.get("config_value",{}).get('filter')))

    def change_preferences(self, target: dict, user: dict, prefs: dict):
        current_prefs = self.get_user_by_seq(target['_id'])
        update_dict = {"$set": current_prefs | prefs | {
            "updated_by": ObjectId(user['_id']),
            "updated_dt": int(time.time())
        }}
        self.db['users'].update_one({"_id": ObjectId(target["_id"])},
                                    update_dict)

    def request_reset_password(self, _id: str, requested_ip: str) \
            -> str:
        if self.get_user_by_seq(_id)['system_user']:
            raise Exception
        token = uuid4()
        self.db['users'].update_one({"_id": ObjectId(_id)},{
            "$set":{
                "reset_link": {
                    "token": token,
                    "requested_by": requested_ip
                }
            }
        })
        return token
    
    def get_user_by_reset_token(self, token_str):
        user = self.db['users'].find_one({
            "$and": [
                {"reset_link.token": token_str},
                {"is_active": True}
            ]
        })
        if user is None:
            raise Exception
        return user

    def get_docket_record(self, docket_id: str):
        return self.db['docket'].find_one({"_id": ObjectId(docket_id)})


    def can_user_edit_docket_record(self, user:dict, docket_id: str):
        doc_admin =  user['permissions'].get("doc_admin", False)
        doc_record = self.get_docket_record(docket_id)
        assignees = doc_record['assignees']
        creator = doc_record['created_by']
        user_id = ObjectId(user['_id'])
        return doc_admin or creator == user_id or user_id in assignees 

    def change_approver_pin(self, 
                            target_id: str,
                            current_user: dict,
                            new_pin: str) -> bool:
        if len(new_pin) != 4 and not new_pin.isdigit():
            return False
        self.db['users'].update_one({"_id": ObjectId(target_id)},
                            {
                                "$set": {
                                    "approver_pin": new_pin,
                                    "updated_by": ObjectId(current_user['id']),
                                    "updated_dt": int(time.time())
                                }
                            })
        return True

    def can_user_view_officer_docket(self, user:dict) -> bool:
        user = self.db['users'].find_one(
            {"$and": [
                {"_id": ObjectId(user['_id'])},
                {"is_active": True}
            ]}
            )
        permission = user['permissions']
        return permission['doc_view'] or permission["doc_admin"]
    
    def get_docket_viewers(self):
        return list(self.db['users'].find({"$and":[
        {"$or": [
            {"permissions.doc_view": True},
            {"permissions.doc_admin": True}
        ]},
        {"is_active": True}
        ]}))
    
    def reset_password(self,
                       user_id: str,
                       new_password: str,
                       old_password: str):
        otp = self.get_totp(user_id)
        fernet_key = self.get_secret()
        fernet = Fernet(fernet_key)
        hashed_otp = fernet.encrypt(otp)
        hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())

        self.db['users'].update_one({"$and":
                                     [
                                         {"_id": ObjectId(user_id)},
                                         {"is_active": True}
                                     ]}, {
                                         "$set": {
                                             "password": hashed.decode(),
                                             "reset_link": None,
                                             "otp_secret": hashed_otp
                                         }
                                     })
        # email_utils.send_password_updated_email(self.get_user_by_seq(user_id))

    def update_finance_status(self, _id: str, stat_desc: str, user: dict):
        self.db['config'].update_one({"_id": ObjectId(_id)}, {"$set":{
            "config_value": stat_desc,
            "updated_by": ObjectId(user['_id']),
            "dt_updated": int(time.time())
        }})
    
    def create_finance_status(self, stat_desc: str, user: dict):
        self.db['config'].insert_one(
            {
                "config_type": "finance_status",
                "config_value": stat_desc,
                "created_by": ObjectId(user['_id']),
                "updated_by": ObjectId(user['_id']),
                "dt_created": int(time.time()),
                "dt_updated": int(time.time())
            }
        )
    
    def update_docket_status(self, _id: str, stat_desc: str, user: dict):
        self.db['config'].update_one({"_id": ObjectId(_id)}, {
            "$set": {
                "config_value": stat_desc,
                "updated_by": ObjectId(user['_id']),
                "dt_updated": int(time.time())
            }
        })
    
    def create_docket_status(self, stat_desc: str, user: dict):
        self.db['config'].insert_one(
            {
                "config_type": "docket_status",
                "config_value": stat_desc,
                "created_by": ObjectId(user['_id']),
                "updated_by": ObjectId(user['_id']),
                "dt_created": int(time.time()),
                "dt_updated": int(time.time())
            }
        )
    

    def get_all_docket_statuses(self):
        return list(self.db['config'].find({"config_type": "docket_status"}))

    def get_all_docket_voting_types(self) -> List[str]:
        return list(
            self.db['config'].find({"config_type": "docket_vote"})
        )
    
    def get_officer_docket(self):
        docket = list(self.db['docket'].find())
        for item in docket:
            item['created_by'] = self.get_user_by_seq(item['created_by'])
            item['updated_by'] = self.get_user_by_seq(item['updated_by'])

    def get_docket_vote_email_users(self, vote_type):
        pass

    def get_config(self):
        return list(self.db['config'].find())
    
    def get_secret(self):
        secret = list(self.db['config'].find({"config_type": "secret"}))
        if len(secret) == 0:
            secret = Fernet.generate_key()
            self.db['config'].insert_one({
                "config_type": "secret",
                "config_value": secret
            })
            return secret
        else:
            return secret[0]['config_value']

    def generate_totp(self, user_email):
        secret = pyotp.random_base32()
        print(secret)
        fernet_key = self.get_secret()
        app_name = self.get_app_name()

        fernet = Fernet(fernet_key)
        return pyotp.totp.TOTP(secret).provisioning_uri(
                user_email, app_name
            ), fernet.encrypt(secret.encode())
    
    def get_totp(self, user_id: str | ObjectId):
        fernet_key = self.get_secret()
        fernet = Fernet(fernet_key)
        user = self.get_user_by_seq(user_id)
        otp_secret_encrypted = user['otp_secret']
        otp_secret = fernet.decrypt(otp_secret_encrypted)
        return pyotp.TOTP(otp_secret).provisioning_uri(
            user['email'], self.get_app_name()
        )


    

    def store_user(self, user_data: dict) -> None:
        otp, secret = self.generate_totp(user_data['emailID'])

        self.db['users'].insert_one({
            "email": user_data['emailID'],
            "system_user": True,
            "theme": 1,
            "is_active": True,
            "permissions": {},
            "added_by": None,
            "dt_added": int(time.time()),
            "dt_updated": int(time.time()),
            "first_name": user_data['fName'],
            "last_name": user_data['lName'],
            "password": bcrypt.hashpw(user_data['pass'].encode(), bcrypt.gensalt()),
            "user_name": user_data['emailID'].split("@")[0],
            "otp_secret": secret
        })

        return otp
    
    def get_app_name(self):
        for cfg in self.get_config():
            if cfg['config_type'] == 'app_name':
                return cfg['config_value']
                
                

    def check_user_otp(self, userID: str | ObjectId, OTP: str):
        fernet_key = self.get_secret()
        fernet = Fernet(fernet_key)
        user = self.get_user_by_seq(userID)
        otp_secret_encrypted = user['otp_secret']
        otp_secret = fernet.decrypt(otp_secret_encrypted)
        TOTP = pyotp.TOTP(otp_secret)
        print(TOTP.now())
        print(OTP)
        if TOTP.verify(OTP):
            self.db['users'].update_one({"_id": userID}, {"$set": {"lastOTP": OTP}})
            return True
        return False 

    def close(self):
        self.conn.close()


@contextmanager
def connect():
    x = _connect()
    try:
        yield x
    finally:
        x.close()
