from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField


class MatchForm(FlaskForm):
    player1 = BooleanField()
    player2 = BooleanField()
    submit = SubmitField("Next Match")

    def __init__(self, player1: str, player2: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['player1'].label = player1
        self['player2'].label = player2
