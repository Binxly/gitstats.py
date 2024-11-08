from typing import List
import os
import pathlib

#TODO: test on windows , oops... small fix?

class GitRepositoryScanner:
    def __init__(self):
        self.dot_file = self._get_dot_file_path()

    def _get_dot_file_path(self) -> str:
        if os.name == 'nt':  # win
            cache_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'gitstats')
        else:  # unix
            cache_dir = os.path.join(str(pathlib.Path.home()), '.pygitlocalstats')
        
        os.makedirs(os.path.dirname(cache_dir), exist_ok=True)
        return cache_dir

    def _read_file_lines(self, file_path: str) -> List[str]:
        try:
            with open(file_path, "r") as f:
                return [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            open(file_path, "w").close()
            return []

    def _write_to_file(self, content: List[str], file_path: str) -> None:
        with open(file_path, "w") as f:
            f.write("\n".join(content))

    def _merge_unique(
        self, new_items: List[str], existing_items: List[str]
    ) -> List[str]:
        return list(set(existing_items + new_items))

    def scan_git_folders(self, folder: str) -> List[str]:
        repositories = []
        folder = folder.rstrip(os.path.sep)

        try:
            for root, dirs, _ in os.walk(folder, topdown=True):
                dirs[:] = [d for d in dirs if d not in ("vendor", "node_modules")]

                if ".git" in dirs:
                    repo_path = root
                    print(repo_path)
                    repositories.append(repo_path)
                    dirs.remove(".git")

        except PermissionError as e:
            print(f"Permission denied: {e}")
        except Exception as e:
            print(f"Error scanning folders: {e}")

        return repositories

    def scan(self, folder: str) -> None:
        print("Found folders:\n")
        repositories = self.scan_git_folders(folder)
        existing_repos = self._read_file_lines(self.dot_file)
        all_repos = self._merge_unique(repositories, existing_repos)
        self._write_to_file(all_repos, self.dot_file)
        print("\nSuccessfully added\n")
