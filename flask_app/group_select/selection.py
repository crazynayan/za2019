import datetime as dt
from typing import List

import pytz
from firestore_ci import FirestoreDocument
from wtforms import SelectMultipleField, widgets, SubmitField, ValidationError

from config import BaseMap
from flask_app import FSForm
from flask_app.legacy.models import Player


class PlayerMap(BaseMap):

    def __init__(self, name: str = None):
        self.name: str = name if name else str()
        self.rank: int = 0
        self.selected: bool = False
        self.league: int = 0
        self.league_rank: int = 0
        self.url: str = str()
        self.url_expiration: dt.datetime = dt.datetime.utcnow().replace(tzinfo=pytz.UTC)


class AdjustRank:
    def __init__(self, league: int, rank: int, adjustment: int):
        self.league: int = league
        self.rank: int = rank
        self.adjustment: int = adjustment


class Group(FirestoreDocument):
    ADJUST_RANKS = [
        AdjustRank(1, 192, 0),
        AdjustRank(1, 224, 128),
        AdjustRank(1, 1000, 384),
        AdjustRank(2, 61, 192),
        AdjustRank(2, 125, 195),
        AdjustRank(2, 235, 274),
        AdjustRank(2, 1000, 452),
        AdjustRank(3, 3, 253),
        AdjustRank(3, 50, 349),
        AdjustRank(3, 146, 462),
        AdjustRank(3, 1000, 565),
        AdjustRank(4, 3, 509),
        AdjustRank(4, 50, 637),
        AdjustRank(4, 126, 771),
        AdjustRank(4, 1000, 838),
        AdjustRank(5, 3, 708),
        AdjustRank(5, 70, 898),
        AdjustRank(5, 1000, 1095),
    ]

    def __init__(self):
        super().__init__()
        self.name: str = str()
        self.player_maps: List[dict] = list()
        self.player_count: int = 0
        self.group_rank: int = 0
        self.selection: bool = False

    def __repr__(self) -> str:
        return f"{self.name}:{self.player_count}:{self.group_rank}"

    def update_player_map(self, players: List[Player]) -> None:
        for player in players:
            player_map = next((player_map for player_map in self.player_maps if player_map["name"] == player.name),
                              None)
            if not player_map:
                player_map = PlayerMap(player.name).to_dict()
                self.player_maps.append(player_map)
            player_map["url"] = player.url
            player_map["url_expiration"] = player.url_expiration
            player_map["league_rank"] = player.rank
            player_league = int(player.game[-1:])
            player_map["rank"] = next(rank.adjustment + player.rank for rank in self.ADJUST_RANKS
                                      if rank.league == player_league and player.rank <= rank.rank)
            player_map["league"] = player_league
        return


Group.init()


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SelectionForm(FSForm):
    player_options = MultiCheckboxField("Players")
    submit = SubmitField("Finalize Selection")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        query = Group.objects.filter_by(selection=False).filter("player_count", ">", 9)
        self.group: Group = query.order_by("player_count", Group.objects.ORDER_DESCENDING).first()
        if not self.group:
            return
        self.player_options.choices = [(player_map["name"], player_map["name"])
                                       for player_map in self.group.player_maps]

    @staticmethod
    def validate_player_options(_, player_options):
        if len(player_options.data) != 9:
            raise ValidationError("You need to select 9 players")

    def update(self):
        for name in self.player_options.data:
            player_map = next(player_map for player_map in self.group.player_maps if player_map["name"] == name)
            player_map["selected"] = True
        self.group.selection = True
        self.group.save()
