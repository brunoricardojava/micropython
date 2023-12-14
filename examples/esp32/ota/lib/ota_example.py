import machine
import uos as os
import ujson as json
import urequests as requests


class OTAUpdater:
    def __init__(
        self,
        repo_url: str,
        filenames: list = None,
        timeout:int = 5,
        soft_reset: bool = False,
        hard_reset: bool = False
        ) -> None:

        self._version_file_name = "version.json"
        self._repo_url = self._repo_url_parser(repo_url)
        self._filenames = filenames
        self._version_url = self._version_url_parser()
        self._current_version = None
        self._timeout = timeout
        self._soft_reset = soft_reset
        self._hard_reset = hard_reset
        
        self._load_version_file()

    def _repo_url_parser(self, repo_url) -> str:
        repo_url = repo_url.strip("/")
        repo_url = self._change_domain_url(repo_url)
        repo_url = self._remove_tree_url(repo_url)
        return repo_url
    
    @staticmethod
    def _change_domain_url(repo_url: str) -> str:
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

    def check_for_updates(self) -> bool:
        new_version_available = False
        headers = {"accept": "application/json"}

        try:
            response = requests.get(self._version_url, headers=headers, timeout=self._timeout)
            if response.status_code < 200 or response.status_code >= 300:
                print(f"Falha na requisição, status_code: {response.status_code}")
                return False

            version_json = response.json()
            remote_version = version_json.get("version")

            if self._current_version != remote_version:
                print(f"Versão do dispositivo: {self._current_version}")
                print(f"Versão da atualização: {remote_version}")
                new_version_available = True
                self._filenames = version_json.get("filenames")
        except Exception as e:
            print(f"Request Exception: {e}")

        return new_version_available

    @staticmethod
    def _make_dirs_recursive(file_path) -> None:
        file_path = file_path.strip("/")
        if len(file_path.split("/")) > 1:
            directory, filename = file_path.rsplit('/', 1)
            try:
                os.stat(directory)
            except OSError:
                directory_parts = directory.split("/")

                for i in range(1, len(directory_parts) +1):
                    sub_dir = "/".join(directory_parts[:i])
                    try:
                        os.mkdir(sub_dir)
                    except:
                        pass
            except Exception as e:
                print(f"Erro ao criar diretorios: {e}")
    
    def _make_dir_structure(self):
        for file in self._filenames:
            self._make_dirs_recursive(file)

    @staticmethod
    def _remove_directory_recursive(directory):
        def recursive_remove(current_directory):
            try:
                items = os.listdir(current_directory)
                for item in items:
                    item_path = current_directory + "/" + item
                    try:
                        if os.stat(item_path)[0] & 0o040000:  # Verifica se é um diretório
                            recursive_remove(item_path)  # Chama recursivamente para o diretório encontrado
                        else:
                            os.remove(item_path)  # Remove o arquivo
                    except OSError as e:
                        print(f"Erro ao remover item: {e}")
                
                os.rmdir(current_directory)  # Remove o diretório vazio
            except OSError as e:
                print(f"Erro ao acessar diretório: {e}")

        recursive_remove(directory)

    @classmethod
    def _delete_tmp_dir(cls) -> None:
        try:
            cls._remove_directory_recursive("tmp")
        except:
            pass

    def _download_code(self) -> bool:
        all_files_found = True
        
        self._make_dir_structure()
        
        try:
            try:
                os.mkdir("tmp")
            except:
                pass
            
            for file in self._filenames:
                tmp_path = f"tmp{file}"
                url_request = self._repo_url + file
                print(f"Baixando arquivo: {url_request}")
                response = requests.get(url_request, timeout=self._timeout)

                response_status_code = response.status_code
                response_text = response.text
                response.close()

                if response_status_code < 200 or response_status_code >= 300:
                    print(f"Arquivo não encontrado: {url_request}")
                    all_files_found = False
                    break

                self._make_dirs_recursive(tmp_path)

                with open(tmp_path, "w") as update_file:
                    update_file.write(response_text)

            if all_files_found:
                print("Download concluido. Instalando atualização...")
                for file in self._filenames:
                    print(file)
                    tmp_path = f"tmp{file}" 
                    with open(tmp_path, "r") as new_file, open(file, "w") as code_file:
                        code_file.write(new_file.read())
                    os.remove(tmp_path)
                    
                print("Instalação concluida!")

                self._delete_tmp_dir()

                return True
            else:
                print("Erro na atualização de um arquivo. Encerrando atualização.")
                return False

        except Exception as e:
            print(f"Alguma coisa deu errado: {e}")
            return False

    def update(self):
        if self.check_for_updates():
            print("Atualização encontrada, seguindo com o download...")
            if self._download_code():
                if self._soft_reset:
                    machine.soft_reset()
                if self._hard_reset:
                    machine.reset()
        else:
            print(f"Dispositivo atualizado. Versão: {self._current_version}")
