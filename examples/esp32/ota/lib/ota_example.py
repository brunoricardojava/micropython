import uos as os
import ujson as json
import urequests as requests


class OTAUpdater:
    def __init__(self, repo_url: str, filenames: list = None) -> None:
        self._version_file_name = "version.json"
        self._repo_url = self._repo_url_parser(repo_url)
        self._filenames = filenames
        self._version_url = self._version_url_parser()
        self._current_version = None
        
        self._load_version_file()

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

    def _load_version_file(self) -> None:
        if self._version_file_name in os.listdir():
            with open(self._version_file_name, "r+") as version_file:
                try:
                    version_json = json.load(version_file)
                    self._current_version = version_json.get("version")
                    self._filenames = self._filenames if self._filenames else version_json.get("filenames")
                except json.JSONDecodeError:
                    print(f"Erro ao abrir o arquivo {self._version_file_name}")
        else:
            self._current_version = "0"
            self._filenames = self._listdir()
            self._filenames.append("/" + self._version_file_name)
            version_content = {
                "version": self._current_version,
                "filenames": self._filenames
            }
            with open(self._version_file_name, "w") as version_file:
                json.dump(version_content, version_file)
    
    @staticmethod
    def _listdir(root_dir: str = "") -> list:
        """Retornar a lista de arquivos do dispositivo """
        file_list = []

        def recursive_search(directory):
            items = os.listdir(directory)
            for item in items:
                item_path = directory + '/' + item  # Concatena o diretório com o nome do item
                try:
                    if os.stat(item_path)[0] & 0o100000:  # Verifica se é um arquivo (usando máscara de bits)
                        file_list.append(item_path)
                    elif os.stat(item_path)[0] & 0o040000:  # Verifica se é um diretório (usando máscara de bits)
                        recursive_search(item_path)  # Chama recursivamente para o diretório encontrado
                except:
                    pass  # Ignora erros de permissão ou acesso a itens

        recursive_search(root_dir)
        return file_list

    def check_for_updates(self, timeout=5) -> bool:
        new_version_available = False
        headers = {"accept": "application/json"}

        try:
            response = requests.get(self._version_url, headers=headers, timeout=timeout)
            if response.status_code < 200 or response.status_code >= 300:
                print(f"Falha na requisição, status_code: {response.status_code}")
                return False

            version_json = response.json()
            remote_version = version_json.get("version")

            if remote_version:
                new_version_available = True if self._current_version != remote_version else False
        except Exception as e:
            print(f"Request Exception: {e}")

        return new_version_available
