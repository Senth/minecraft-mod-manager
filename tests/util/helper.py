import sqlite3
from pathlib import Path
from subprocess import run
from typing import List, Optional


class Helper:
    def __init__(self) -> None:
        self.dir = Path("temp")
        self.dir.mkdir(exist_ok=True)

        self.cmd = ["python", "-m", "minecraft_mod_manager", "--dir", "temp"]

        self.db = sqlite3.connect(self.dir.joinpath(".minecraft-mod-manager.db"))
        self.cursor = self.db.cursor()

    def run(self, *args: str) -> int:
        cmd: List[str] = [*self.cmd, *args]
        output = run(cmd)
        return output.returncode

    def get_mod_in_dir_like(self, glob: str) -> Optional[Path]:
        for file in self.dir.glob(glob):
            return file
        return None

    def exists_in_db(self, id: str) -> bool:
        self.cursor.execute("SELECT * FROM mod WHERE id=?", [id])
        return self.cursor.fetchone() is not None

    def unstub(self) -> None:
        self.cursor.close()
        self.db.close()

        for file in self.dir.iterdir():
            file.unlink()

        self.dir.rmdir()
