import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google-cloud.json'

from flask_app.models import Game, Player, Schedule
from flask_app.drive import Drive, STATIC_FOLDER
from flask_app import routes

def delete_all(game_id: str):
    print(Schedule.objects.filter_by(game=game_id).delete())
    print(Player.objects.filter_by(game=game_id).delete())
    print(Game.objects.filter_by(name=game_id).delete())


def delete(game_id: str):
    print(Game.objects.filter_by(name=game_id).delete())


def add(game_id: str):
    if Game.objects.filter_by(name=game_id).first():
        print('Game already exists')
        return
    game = Game()
    game.name = game_id
    game.set_id(game_id)
    game.save()
    print('Game created')
    return


def name_error(game_id: str):
    players = Player.objects.filter_by(game=game_id).get()
    errors = [player for player in players if len(player.name) != 5 or not player.name[:2].isalpha() or
              not player.name[2:5].isdigit()]
    for error in errors:
        print(error.name)
    return


def name_replace(game_id: str, old_name: str, new_name: str):
    player = Player.objects.filter_by(game=game_id, name=old_name).first()
    if not player:
        print("Player not found")
        return
    if player.name not in Drive.get_files(game_id):
        print("File not found")
        return
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), STATIC_FOLDER, game_id)
    old_file = os.path.join(f"{path}/{old_name}.jpg")
    new_file = os.path.join(f"{path}/{new_name}.jpg")
    os.rename(old_file, new_file)
    player.name = new_name
    player.save()
    name_replace_schedule(game_id, old_name, new_name)
    name_replace_result(game_id, old_name, new_name)
    print("Player name updated")


def name_replace_schedule(game_id: str, old_name: str, new_name: str):
    schedules = Schedule.objects.filter_by(game=game_id, player1=old_name).get()
    for schedule in schedules:
        schedule.player1 = new_name
        schedule.save()
    print(f"{len(schedules)} player1 in schedules updated")
    schedules = Schedule.objects.filter_by(game=game_id, player2=old_name).get()
    for schedule in schedules:
        schedule.player2 = new_name
        schedule.save()
    print(f"{len(schedules)} player2 in  schedules updated")
    return


def name_replace_result(game_id: str, old_name: str, new_name: str):
    schedules = Schedule.objects.filter_by(game=game_id, winner=old_name).get()
    for schedule in schedules:
        schedule.winner = new_name
        schedule.save()
    print(f"{len(schedules)} winners in schedules updated")
    players = Player.objects.filter_by(game=game_id).get()
    won_count = lost_count = 0
    for player in players:
        if old_name in player.won:
            player.won = [new_name if name == old_name else name for name in player.won]
            won_count += 1
            player.save()
            continue
        if old_name in player.lost:
            player.lost = [new_name if name == old_name else name for name in player.lost]
            lost_count += 1
            player.save()
    print(f"{won_count} won_players and {lost_count} lost_players updated")


def sync_points(game_id: str):
    players = Player.objects.filter_by(game=game_id).get()
    routes.sync_points(players)
    for player in players:
        player.save()
    print(f"{len(players)} synced")
