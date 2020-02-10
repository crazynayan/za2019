from typing import List

from firestore_ci import FirestoreDocument

from flask_app import za_app


class Game(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.name = str()
        self.player_count = str()


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
        self.tie_break2: int = 0
        self.tie_break3: int = 0
        self.lives: int = 3
        self.byes: List[int] = list()
        self.last_round: int = 0
        self.rank: int = 0

    @property
    def image(self) -> str:
        if not any(f"{self.name}{ext}" in za_app.config['IMAGES'] for ext in za_app.config['EXT']):
            return f"/images/SI001.jpg"
        file_name = next(iter(f"{self.name}{ext}" for ext in za_app.config['EXT']
                              if f"{self.name}{ext}" in za_app.config['IMAGES']))
        return f"images/{file_name}"

    @property
    def byes_count(self) -> int:
        return len(self.byes)

    @property
    def played_count(self) -> int:
        return len(self.won) + len(self.lost)

    @property
    def image_border_class(self) -> str:
        if self.lives >= 3:
            color = "border-success"
        elif self.lives == 2:
            color = "border-dark"
        elif self.lives == 1:
            color = "border-danger"
        else:
            color = "border-light"
        return f"img-fluid border border-strong {color}"

    @property
    def btn_class(self) -> str:
        if self.lives >= 3:
            color = "btn-success"
        elif self.lives == 2:
            color = "btn-dark"
        elif self.lives == 1:
            color = "btn-danger"
        else:
            color = "btn-light"
        return f"btn btn-block {color}"

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
        self.player1_rank: int = 0
        self.player2: str = str()
        self.player2_rank: int = 0
        self.winner: str = str()
        self.round: int = 0
        self.match: int = 0


Schedule.init()
