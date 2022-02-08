from enum import Enum

import requests

# GET
ROOT_GENERATE = "https://sugoku.herokuapp.com/board?difficulty="
# POST
ROOT_SOLVE = "https://sugoku.herokuapp.com/solve"


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    RANDOM = "random"


def getUrl(diff: Difficulty) -> str:
    return f"{ROOT_GENERATE}{diff.value}"


def getEasyUrl() -> str:
    return f"{ROOT_GENERATE}{Difficulty.EASY}"


def getMediumUrl() -> str:
    return f"{ROOT_GENERATE}{Difficulty.MEDIUM}"


def getHardUrl() -> str:
    return f"{ROOT_GENERATE}{Difficulty.HARD}"


def getRandomUrl() -> str:
    return f"{ROOT_GENERATE}{Difficulty.RANDOM}"


if __name__ == '__main__':
    print()
