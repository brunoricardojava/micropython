import os
import json
import urequests as requests


class OTAUpdater:
    def __init__(self, repo_url: str, filenames: list) -> None:
        self._version_file_name = "version.json"
        self._repo_url = self._repo_url_parser(repo_url)
        self._filenames = filenames
        self._version_url = self._version_url_parser()
        self._current_version = self._get_current_version()
        
    def _repo_url_parser(self, repo_url) -> str:
        repo_url = self._change_domain_url(repo_url)
        repo_url = self._remove_tree_url(repo_url)
        return repo_url
    
    @staticmethod
    def _change_domain_url(repo_url: str) -> str:
        repo_url = repo_url.strip("/")
        domain_to_replace = "https://github.com/"
        domain_to_use = "https://raw.githubusercontent.com/"
        return repo_url.replace(domain_to_replace, domain_to_use)
    
    @staticmethod
    def _remove_tree_url(repo_url: str) -> str:
        term_to_remove = "/tree"
        return repo_url.replace(term_to_remove, "")

    def _version_url_parser(self) -> str:
        return self._repo_url + "/" + self._version_file_name

    def _get_current_version(self) -> str:
        if self._version_file_name in os.listdir():
            with open(self._version_file_name, "r+") as version_file:
                try:
                    version_json = json.load(version_file)
                    current_version = version_json.get("version")
                except json.JSONDecodeError:
                    print(f"Erro ao abrir o arquivo {self._version_file_name}")
        else:
            current_version = "0"
            with open(self._version_file_name, "w") as version_file:
                json.dump({"version": current_version}, version_file)

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
