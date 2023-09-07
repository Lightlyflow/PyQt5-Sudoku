from enum import Enum

# GET
ROOT_GENERATE = "https://sugoku.herokuapp.com/board?difficulty="
# POST
ROOT_SOLVE = "https://sugoku.herokuapp.com/solve"


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    RANDOM = "random"


class path_gen:
    @staticmethod
    def getUrl(diff: Difficulty) -> str:
        return f"{ROOT_GENERATE}{diff.value}"

    @staticmethod
    def getEasyUrl() -> str:
        return f"{ROOT_GENERATE}{Difficulty.EASY}"

    @staticmethod
    def getMediumUrl() -> str:
        return f"{ROOT_GENERATE}{Difficulty.MEDIUM}"

    @staticmethod
    def getHardUrl() -> str:
        return f"{ROOT_GENERATE}{Difficulty.HARD}"

    @staticmethod
    def getRandomUrl() -> str:
        return f"{ROOT_GENERATE}{Difficulty.RANDOM}"
