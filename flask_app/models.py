from typing import List

from flask_app.firestore_ci import FirestoreDocument


class Game(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.name = str()


Game.init()


class Player(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.name: str = str()
        self.game: str = str()
        self.won: List[str] = list()
        self.lost: List[str] = list()
        self.points: int = 0
        self.tie_break: int = 0
        self.lives: int = 3
        self.byes: List[int] = list()
        self.last_round: int = 0
        self.rank: int = 0

    @property
    def image(self) -> str:
        return f"{self.game}/{self.name}.jpg"

    @property
    def byes_count(self) -> int:
        return len(self.byes)

    @property
    def played_count(self) -> int:
        return len(self.won) + len(self.lost)

    def __eq__(self, other: 'Player') -> bool:
        return self.name == other.name

    def played(self, other: 'Player') -> bool:
        return other.name in self.won or other.name in self.lost


Player.init()


class Schedule(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.game: str = str()
        self.player1: str = str()
        self.player2: str = str()
        self.winner: str = str()
        self.round: int = 0
        self.match: int = 0


Schedule.init()
