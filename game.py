import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google-cloud.json'

# noinspection PyPep8
from flask_app.drive2 import Drive2
# noinspection PyPep8
from flask_app.models import Game, Player, Schedule
# noinspection PyPep8
from flask_app import routes, za_app


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
    # if player.name not in Drive.get_files(game_id):
    #     print("File not found")
    #     return
    # path = os.path.join(os.path.dirname(os.path.abspath(__file__)), STATIC_FOLDER, game_id)
    # old_file = os.path.join(f"{path}/{old_name}.jpg")
    # new_file = os.path.join(f"{path}/{new_name}.jpg")
    # os.rename(old_file, new_file)
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


def name_error_on_drive(folder_name: str):
    files = Drive2.get_files(folder_name)
    files.sort(key=lambda file_item: file_item['name'])
    invalid_files = [file for file in files if not file['name'].endswith('.jpg') or len(file['name']) != 9
                     or not file['name'][:2].isalpha() or not file['name'][2:5].isdigit()]
    for file in invalid_files:
        print(file['name'])
    return invalid_files


def name_error_replace(folder_name: str):
    invalid_files = name_error_on_drive(folder_name)
    for file in invalid_files:
        if len(file['name']) not in [8, 7]:
            print(f"Cannot replace {file['name']} - Not in format")
            continue
        old_number = file['name'][2:4] if len(file['name']) == 8 else file['name'][2]
        new_number = f"97{old_number}" if len(old_number) == 1 else f"9{old_number}"
        if not new_number.isdigit() or len(new_number) != 3:
            print(f"Cannot replace {file['name']} - Invalid number {new_number}")
            continue
        new_file_name = f"{file['name'][:2].upper()}{new_number}.jpg"
        if Drive2.file_exists('AFake', new_file_name) or Drive2.file_exists('wc2019', new_file_name):
            print(f"Cannot replace {file['name']} - File {new_file_name} already exists")
            continue
        Drive2.rename(file, new_file_name)
        print(f"File renamed to {new_file_name}")
    return


def name_change(folder_name: str, old_name: str, new_name: str):
    files = [file for file in Drive2.get_files(folder_name) if file['name'].startswith(old_name)]
    for file in files:
        new_file_name = file['name'].replace(old_name, new_name)
        if Drive2.file_exists('AFake', new_file_name) or Drive2.file_exists('wc2019', new_file_name):
            print(f"Cannot replace {file['name']} - File {new_file_name} already exists")
            continue
        Drive2.rename(file, new_file_name)
        print(f"File {file['name']} renamed to {new_file_name}")
    return


def duplicate_matches(game_id: str):
    players = Player.objects.filter_by(game=game_id).get()
    for player in players:
        if len(player.won) > len(set(player.won)):
            print(f"** {player.name} won against **")
            print(player.won)
        if len(player.lost) > len(set(player.lost)):
            print(f"** {player.name} lost against **")
            print(player.lost)


def rename_game(old_game_id: str, new_game_id: str):
    game = Game.get_by_id(old_game_id)
    if not game:
        print('Game not found.')
        return
    game.delete()
    game = Game()
    game.name = new_game_id
    game.set_id(new_game_id)
    game.save()
    print('Game ID updated. Starting Player update.')
    players = Player.objects.filter_by(game=old_game_id).get()
    for index, player in enumerate(players):
        player.game = new_game_id
        player.save()
        print(f'Player: {index + 1} of {len(players)} updated.')
    print('Starting Schedule update.')
    schedules = Schedule.objects.filter_by(game=old_game_id).get()
    for index, schedule in enumerate(schedules):
        schedule.game = new_game_id
        schedule.save()
        print(f'Schedule: {index + 1} of {len(schedules)} updated.')
    print('Game ID rename complete.')


def create_season(game_dict: dict) -> None:
    games = {game.id: dict() for game in Game.objects.get()}
    player_count_dict = {game_id: 0 for _, season in game_dict.items() for game_id in season}
    print('Starting validation')
    for _, season in game_dict.items():
        for game_id, player_count in season.items():
            player_count_dict[game_id] += player_count
    for _, season in game_dict.items():
        for game_id in season:
            if game_id not in games:
                print(f'Game {game_id}: Not found')
                return
            games[game_id] = Player.objects.filter_by(game=game_id).get()
            games[game_id].sort(key=lambda player_item: player_item.rank)
            if len(games[game_id]) != player_count_dict[game_id]:
                print(f'Game {game_id}: Count Mismatch. DB={len(games[game_id])}. Input={player_count_dict[game_id]}.')
                return
    print('Validation complete')
    for season_id, season in game_dict.items():
        game = Game()
        game.name = season_id
        game.player_count = sum(player_count for _, player_count in season.items())
        game.set_id(season_id)
        game.save()
        print(f'{season_id}: Game created. Starting player creation')
        for game_id, player_count in season.items():
            if player_count == 0:
                continue
            for index, player in enumerate(games[game_id][: player_count]):
                Player.create_from_dict({'name': player.name, 'game': season_id})
                print(f'{season_id}: {index + 1} of {player_count} players created from {game_id}')
            del games[game_id][: player_count]
            print(f'{season_id}: All players extracted from {game_id}')
        print(f'{season_id}: {game.player_count} players creation complete')
    return


def create_players(game_id: str, player_list: list):
    print('Starting Validation')
    games = {game.id: dict() for game in Game.objects.get()}
    if game_id not in games:
        print(f'Game {game_id}: Not found')
        return
    for player_name in player_list:
        if not any(f"{player_name}{ext}" in za_app.config['IMAGES'] for ext in za_app.config['EXT']):
            print(f'Player {player_name} does not have a image.')
            return
    print('Validation Complete')
    for index, player_name in enumerate(player_list):
        Player.create_from_dict({'name': player_name, 'game': game_id})
        print(f'{game_id}: {index + 1} of {len(player_list)} players created.')
    print('Player creation complete.')
    return


SEASON = {
    '2020-SA-LW1': {'2019-SO-LO1': 80, '2019-SO-LK2': 128, '2019-SO-LE3': 48},
    '2020-SA-LS2': {'2019-SO-LO1': 34, '2019-SO-LK2': 128, '2019-SO-LE3': 88},
    '2020-SA-LO3': {'2019-SO-LO1': 0, '2019-SO-LK2': 64, '2019-SO-LE3': 192},
    '2020-SA-LJ4': {'2019-SO-LO1': 0, '2019-SO-LK2': 32, '2019-SO-LE3': 224},
    '2020-SA-LE5': {'2019-SO-LO1': 0, '2019-SO-LK2': 32, '2019-SO-LE3': 319},
}
