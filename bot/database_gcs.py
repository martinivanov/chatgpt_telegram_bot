from typing import Optional, Any

from google.cloud import storage
import uuid
from datetime import datetime
import json

import config


class GCSDatabase:
    def __init__(self):
        if config.gcs_project is None:
            self.client = storage.Client()
        else:
            self.client = storage.Client(project=config.gcs_project)
        self.bucket = storage.Bucket(self.client, name=config.gcs_bucket)

    def check_if_user_exists(self, user_id: int, raise_exception: bool = False):
        # check if the user exists in the bucket
        blob = storage.Blob(f"users/{user_id}.json", self.bucket)
        user_exists = blob.exists()

        if raise_exception and not user_exists:
            raise ValueError(f"User {user_id} does not exist in the database")

        return user_exists

        
    def add_new_user(
        self,
        user_id: int,
        chat_id: int,
        username: str = "",
        first_name: str = "",
        last_name: str = "",
    ):
        user_dict = {
            "_id": user_id,
            "chat_id": chat_id,

            "username": username,
            "first_name": first_name,
            "last_name": last_name,

            "last_interaction": datetime.now(),
            "first_seen": datetime.now(),
            
            "current_dialog_id": None,
            "current_chat_mode": "assistant",

            "n_used_tokens": 0
        }

        if not self.check_if_user_exists(user_id):
            blob = storage.Blob(f"users/{user_id}.json", self.bucket)
            user_json = json.dumps(user_dict, indent=4, sort_keys=True, default=str)
            blob.upload_from_string(data=str(user_json), content_type="application/json")

    def start_new_dialog(self, user_id: int):
        self.check_if_user_exists(user_id, raise_exception=True)

        dialog_id = str(uuid.uuid4())
        dialog_dict = {
            "_id": dialog_id,
            "user_id": user_id,
            "chat_mode": self.get_user_attribute(user_id, "current_chat_mode"),
            "start_time": datetime.now(),
            "messages": []
        }

        # add new dialog
        blob = storage.Blob(f"dialogs/{user_id}/{dialog_id}.json", self.bucket)
        dialog_json = json.dumps(dialog_dict, indent=4, sort_keys=True, default=str)
        blob.upload_from_string(data=dialog_json, content_type="application/json")

        # update user's current dialog
        self.set_user_attribute(user_id, "current_dialog_id", dialog_id)

        return dialog_id

    def get_user_attribute(self, user_id: int, key: str):
        self.check_if_user_exists(user_id, raise_exception=True)

        # get user attribute from the bucket and put it in a python dict
        blob = storage.Blob(f"users/{user_id}.json", self.bucket)
        user_dict_str = blob.download_as_string()

        user_dict = json.loads(user_dict_str)

        if key not in user_dict:
            raise ValueError(f"User {user_id} does not have a value for {key}")

        return user_dict[key]

    def set_user_attribute(self, user_id: int, key: str, value: Any):
        self.check_if_user_exists(user_id, raise_exception=True)
        
        blob = storage.Blob(f"users/{user_id}.json", self.bucket)
        user_dict_str = blob.download_as_string()
        user_dict = json.loads(user_dict_str)
        user_dict[key] = value

        user_json = json.dumps(user_dict, indent=4, sort_keys=True, default=str)
        blob.upload_from_string(data=user_json, content_type="application/json")

    def get_dialog_messages(self, user_id: int, dialog_id: Optional[str] = None):
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        blob = storage.Blob(f"dialogs/{user_id}/{dialog_id}.json", self.bucket)
        dialog_dict_str = blob.download_as_string()
        dialog_dict = json.loads(dialog_dict_str)

        return dialog_dict["messages"]

    def set_dialog_messages(self, user_id: int, dialog_messages: list, dialog_id: Optional[str] = None):
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")
        
        blob = storage.Blob(f"dialogs/{user_id}/{dialog_id}.json", self.bucket)
        dialog_dict_str = blob.download_as_string()
        dialog_dict = json.loads(dialog_dict_str)
        dialog_dict["messages"] = dialog_messages

        dialog_json = json.dumps(dialog_dict, indent=4, sort_keys=True, default=str)
        blob.upload_from_string(data=dialog_json, content_type="application/json")