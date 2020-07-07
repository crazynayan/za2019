import datetime as dt
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from operator import itemgetter
from typing import Tuple

import pytz

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google-cloud.json'

from flask_app.legacy.models import Player
from file import Image


def generate_url(player: Player) -> Tuple[str, str]:
    url = Image.url(player.name)
    return url, player.id


def update_url(_, __):
    print("Update URL function invoked")
    players = Player.objects.get()
    print(f"{len(players)} players read")
    url_expiration = dt.datetime.utcnow().replace(tzinfo=pytz.UTC)
    print(f"URLs are valid till {url_expiration.isoformat()}")
    players.sort(key=lambda item: item.id)
    print(f"Players sorted by ID. Now generating URL.")
    with ThreadPoolExecutor(max_workers=len(players)) as executor:
        threads = set()
        for player in players:
            threads.add(executor.submit(generate_url, player))
            print(f"{len(threads)} of {len(players)} threads created.")
        results = list()
        for future in as_completed(threads):
            results.append(future.result())
            print(f"{len(results)} of {len(players)} URL generated.")
    results.sort(key=itemgetter(1))
    print(f"URL Generated. Now updating players")
    for index, player in enumerate(players):
        player.url = results[index][0]
        player.url_expiration = url_expiration
    print(f"All Players updated. Now saving all players.")
    Player.save_all(players)
    print(f"{len(players)} player url updated. Function complete")
