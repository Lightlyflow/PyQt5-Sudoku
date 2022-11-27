import pprint
import os


PATH = "../Puzzles/"
REQUIRED_FIELDS = [("fileName", "example"),
                   ("time", 0),
                   ("board", [["" for _ in range(9)] for _ in range(9)]),
                   ("frozen", [["" for _ in range(9)] for _ in range(9)])]


class SavesManager:
    """Manages the Sudoku saves."""
    def __init__(self):
        self.data = {}
        self._setMissingReqs()

    def load_data(self, fileName: str) -> None:
        """Loads all data from the file [name]."""
        try:
            with open(f"{PATH + fileName}") as f:
                self.__init__()
                for line in f.readlines():
                    key, val = line.strip().split(": ")
                    if key in ["board", "frozen"]:
                        self.data[key] = eval(val)
                    else:
                        self.data[key] = val
            print(f"Loaded data from {fileName}.")
        except Exception as e:
            print(f"Could not load data: \n{e}")

    def save(self, fileName: str) -> None:
        """Saves data from kwargs to [filename]. WARNING: SAVES THE REPR OF OBJECT!"""
        try:
            self.data['fileName'] = fileName
            with open(f"{PATH + fileName}", "w") as f:
                for key in self.data.keys():
                    lineWrite = f"{key}: {self.data[key]}\n"
                    f.write(lineWrite)
            print(f"Saved data to {fileName}.")
        except Exception as e:
            print(f"Could not save data: \n{e}")

    @staticmethod
    def delete(fileName: str):
        try:
            os.remove(PATH + fileName)
            print(f"Removed {fileName}.")
        except Exception as e:
            print(f"Error removing file: \n{e}")

    def printData(self) -> None:
        pprint.pprint(self.data, indent=1)

    def _setMissingReqs(self) -> None:
        """If any keys are missing, they are added to the data and set to the default values"""
        for req_key, req_value in REQUIRED_FIELDS:
            if req_key not in self.data:
                self.data[req_key] = req_value
