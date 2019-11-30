from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, ValidationError

from flask_app.drive import Drive
from flask_app.models import Game


class GameForm(FlaskForm):
    folder = StringField("Enter Game Folder Name - Game Folder must exists in Drive", validators=[DataRequired()])
    submit = SubmitField("Create Game")

    @staticmethod
    def validate_folder(_, folder) -> None:
        folder_name = folder.data
        if not Drive.folder_exists(folder_name):
            raise ValidationError('This folder does NOT exits.')
        if not Drive.get_files(folder_name):
            raise ValidationError('There are no jpg files in this folder')
        if folder_name in [game.name for game in Game.objects.get()]:
            raise ValidationError('The game is already started.')
        return


class MatchForm(FlaskForm):
    player1 = BooleanField()
    player2 = BooleanField()
    submit = SubmitField("Next Match")

    def __init__(self, player1: str, player2: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['player1'].label = player1
        self['player2'].label = player2
