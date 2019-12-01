import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google-cloud.json'

from flask_app.models import Game, Player, Schedule


def delete_all(game_id: str):
    print(Schedule.objects.filter_by(game=game_id).delete())
    print(Player.objects.filter_by(game=game_id).delete())
    print(Game.objects.filter_by(name=game_id).delete())


def delete_game(game_id: str):
    print(Game.objects.filter_by(name=game_id).delete())


def add_game(game_id: str):
    if Game.objects.filter_by(name=game_id).first():
        print('Game already exists')
        return
    game = Game()
    game.name = game_id
    game.set_id(game_id)
    game.save()
    print('Game created')
    return
