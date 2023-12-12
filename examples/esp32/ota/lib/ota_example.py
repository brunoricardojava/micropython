import os
import json
import urequests as requests


class OTAUpdater:
    def __init__(self, repo_url: str, filenames: list) -> None:
        self._version_file_name = "version.json"
        self._repo_url = repo_url.strip('/')
        self._filenames = filenames
        self._version_url = self._version_url_parser(self._repo_url, self._version_file_name)
        self._current_version = self._get_current_version(self._version_file_name)

    def _version_url_parser(self) -> str:
        return self._repo_url + "/" + self._version_file_name

    def _get_current_version(self) -> str:
        if self._version_file_name in os.listdir():
            with open(self._version_file_name) as version_file:
                current_version = json.load(version_file)
        else:
            current_version = "0"
            with open(self._version_file_name, "w") as version_file:
                json.dump({"version": current_version})

        return current_version

    def check_for_updates(self) -> bool:
        new_version_available = False
        headers = {"accept": "application/json"} 
        response = requests.get(self._version_url, headers=headers)
        version_json = json.load(response.text)
        remote_version = version_json.get("version")
        
        if remote_version:
            new_version_available = True if self._current_version != remote_version else False
        
        return new_version_available
