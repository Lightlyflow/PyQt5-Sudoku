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


if __name__ == '__main__':
    print()
