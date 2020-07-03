import random
from typing import List, Optional

from flask import render_template, flash, redirect, url_for, Response
from flask_login import login_required

from flask_app import za_app
from flask_app.forms import MatchForm
from flask_app.models import Game, Player, Schedule


@za_app.route('/')
@za_app.route('/index')
@za_app.route('/home')
@login_required
def home() -> Response:
    games = Game.objects.order_by('name', Game.objects.ORDER_DESCENDING).get()
    return render_template('home.html', games=games)


@za_app.route('/games/<string:game_id>/next_match_up', methods=['GET', 'POST'])
@login_required
def next_match_up(game_id: str) -> Response:
    game = Game.get_by_id(game_id)
    if not game or game.completed:
        flash("Game Over")
        return redirect(url_for('home'))
    match = Schedule.objects.filter_by(game=game_id, winner=str()).order_by('match').first()
    if match:
        return redirect(url_for('play_match', game_id=game_id, match_id=match.id))
    update_rank(game_id)
    if prepare_schedule(game_id):
        flash("A new round begins")
    else:
        flash("Game Over")
        game.completed = True
        game.save()
    return redirect(url_for('home'))


@za_app.route('/games/<string:game_id>/matches/<string:match_id>', methods=['GET', 'POST'])
@login_required
def play_match(game_id: str, match_id: str) -> Response:
    match = Schedule.get_by_id(match_id)
    if not match:
        flash('Error in retrieving match')
        return redirect(url_for('home'))
    player1: Player = Player.objects.filter_by(game=game_id, name=match.player1).first()
    player2: Player = Player.objects.filter_by(game=game_id, name=match.player2).first()
    form = MatchForm(player1.name, player2.name)
    if not form.validate_on_submit():
        return render_template('match_form.html', form=form, round=match.round, match=match.match,
                               player1=player1, player2=player2, game_id=game_id)
    if (form.player1.data and form.player2.data) or (not form.player1.data and not form.player2.data):
        flash("Invalid or No Choice made")
        return redirect(url_for('next_match_up', game_id=game_id))
    if player2.name in player1.won or player2.name in player1.lost:
        flash("The match has already been played.")
        return redirect(url_for('next_match_up', game_id=game_id))
    winner = player1 if form.player1.data else player2
    loser = player1 if form.player2.data else player2
    winner.won.append(loser.name)
    winner.points += 1
    winner.tie_break += loser.points
    winner.last_round = match.round
    winner.save()
    loser.lost.append(winner.name)
    loser.last_round = match.round
    loser.lives -= 1
    loser.save()
    match.winner = winner.name
    match.save()
    return redirect(url_for('next_match_up', game_id=game_id))


@za_app.route('/games/<string:game_id>/leaderboard')
@login_required
def leaderboard(game_id: str) -> Response:
    page_size = 50
    players = Player.objects.filter_by(game=game_id).order_by('points', Player.objects.ORDER_DESCENDING). \
        order_by('tie_break', Player.objects.ORDER_DESCENDING).order_by('rank').limit(page_size).get()
    return render_template('leaderboard.html', players=players, game_id=game_id, title=f'Top {page_size}')


@za_app.route('/games/<string:game_id>/leaderboard/leaderboard/all')
@login_required
def leaderboard_all(game_id: str) -> Response:
    players = Player.objects.filter_by(game=game_id).get()
    players.sort(key=lambda player: player.rank)
    return render_template('leaderboard.html', players=players, game_id=game_id, title='Leaderboard')


@za_app.route('/games/<string:game_id>/leaderboard/eliminated/all')
@login_required
def eliminated_all(game_id: str) -> Response:
    players = Player.objects.filter_by(game=game_id, lives=0).get()
    players.sort(key=lambda player: (-player.points, player.rank))
    return render_template('leaderboard.html', players=players, game_id=game_id, title='Eliminated')


@za_app.route('/games/<string:game_id>/playing/all')
@login_required
def playing_all(game_id: str) -> Response:
    players = Player.objects.filter_by(game=game_id).filter('lives', '>', 0).get()
    players.sort(key=lambda player: (-player.points, player.rank))
    return render_template('leaderboard.html', players=players, game_id=game_id, title='Playing')


@za_app.route('/games/<string:game_id>/rounds')
@login_required
def schedule_rounds(game_id: str) -> Response:
    last_match = Schedule.objects.filter_by(game=game_id).order_by('match', Schedule.objects.ORDER_DESCENDING).first()
    rounds = list(range(1, last_match.round + 1)) if last_match else list()
    return render_template('rounds.html', rounds=rounds, game_id=game_id)


@za_app.route('/games/<string:game_id>/rounds/<int:requested_round>', methods=['GET', 'POST'])
@login_required
def schedule_fixtures(game_id: str, requested_round: int) -> Response:
    schedules = Schedule.objects.filter_by(game=game_id, round=requested_round).order_by('match').get()
    players = Player.objects.filter_by(game=game_id).filter('byes', Player.objects.ARRAY_CONTAINS,
                                                            requested_round).get()
    return render_template('schedule.html', schedules=schedules, round=requested_round, players=players,
                           game_id=game_id)


@za_app.route('/games/<string:game_id>/players/<string:player_id>')
@login_required
def profile(game_id: str, player_id: str):
    player: Player = Player.objects.filter_by(game=game_id, name=player_id).first()
    player.won = [Player.objects.filter_by(game=game_id, name=player_name).first() for player_name in player.won]
    player.lost = [Player.objects.filter_by(game=game_id, name=player_name).first() for player_name in player.lost]
    return render_template('profile.html', player=player, game_id=game_id)


def get_match(player1: Player, players: List[Player], random_choice: bool) -> Optional[Player]:
    if not players:
        return None
    while players:
        player2 = random.choice(players) if random_choice else players[0]
        if not player1.played(player2):
            return player2
        players.remove(player2)
    return None


def prepare_schedule(game_id: str, random_choice: bool = False) -> bool:
    last_match = Schedule.objects.filter_by(game=game_id).order_by('match', Schedule.objects.ORDER_DESCENDING).first()
    next_round = last_match.round + 1 if last_match else 1
    next_match = last_match.match + 1 if last_match else 1
    match_players: List[Player] = Player.objects.filter_by(game=game_id).filter('lives', '>', 0).get()
    match_players.sort(key=lambda player: player.rank)
    schedule_prepared = False
    while match_players:
        if match_players[-1].byes:
            player1 = match_players[-1]
            player1_match_up = match_players[:-1] if len(match_players) > 1 else list()
            player1_match_up.reverse()
        else:
            player1 = match_players[0]
            player1_match_up = match_players[1:] if len(match_players) > 1 else list()
            if player1.lives == 1:
                player1_match_up.reverse()
        player2 = get_match(player1, player1_match_up, random_choice)
        if not player2:
            if next_round not in player1.byes:
                player1.byes.append(next_round)
                player1.save()
            match_players.remove(player1)
            continue
        Schedule.create_from_dict({'game': game_id, 'player1': player1.name, 'player2': player2.name,
                                   'match': next_match, 'round': next_round, 'player1_rank': player1.rank,
                                   'player2_rank': player2.rank})
        match_players.remove(player1)
        match_players.remove(player2)
        next_match += 1
        schedule_prepared = True
    if schedule_prepared:
        game = Game.get_by_id(game_id)
        game.round = next_round
        game.match = next_match - 1
        game.save()
    return schedule_prepared


def sync_points(players: List[Player]) -> None:
    for player in players:
        player.points = len(player.won)
    for player in players:
        player.tie_break = 0
        for won_name in player.won:
            won_player = next(player for player in players if player.name == won_name)
            player.tie_break += won_player.points
        player.tie_break3 = 0
        for lost_name in player.lost:
            lost_player = next(player for player in players if player.name == lost_name)
            player.tie_break3 += lost_player.points
    for player in players:
        player.tie_break2 = 0
        for won_name in player.won:
            won_player = next(player for player in players if player.name == won_name)
            player.tie_break2 += won_player.tie_break
    return


def update_rank(game_id: str) -> None:
    players = Player.objects.filter_by(game=game_id).get()
    sync_points(players)
    last_match = Schedule.objects.filter_by(game=game_id).order_by('match', Schedule.objects.ORDER_DESCENDING).first()
    life_increase = True if last_match and last_match.round % 3 == 0 else False
    players.sort(key=lambda player_sort: (-player_sort.points, -player_sort.tie_break, -player_sort.tie_break2,
                                          -player_sort.tie_break3))
    for player in players:
        rank_player = next(rank_player for rank_player in players if player.points == rank_player.points and
                           player.tie_break == rank_player.tie_break and player.tie_break2 == rank_player.tie_break2
                           and player.tie_break3 == rank_player.tie_break3)
        player.rank = players.index(rank_player) + 1
        if life_increase and player.lives > 0:
            player.lives += 1
    Player.save_all(players)
    return
