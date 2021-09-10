from enum import Enum

import requests

ROOT = "https://sugoku.herokuapp.com/board?difficulty="


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    RANDOM = "random"


def getUrl(diff: Difficulty) -> str:
    return f"{ROOT}{diff.value}"


def getEasyUrl() -> str:
    return f"{ROOT}{Difficulty.EASY}"


def getMediumUrl() -> str:
    return f"{ROOT}{Difficulty.MEDIUM}"


def getHardUrl() -> str:
    return f"{ROOT}{Difficulty.HARD}"


def getRandomUrl() -> str:
    return f"{ROOT}{Difficulty.RANDOM}"


if __name__ == '__main__':
    print()
