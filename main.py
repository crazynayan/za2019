import datetime as dt
import os

import pytz

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google-cloud.json'

from flask_app.legacy.models import Player
from flask_app.file import Image


def update_url(_, __):
    print("Update URL function invoked")
    players = Player.objects.get()
    print(f"{len(players)} players read")
    url_expiration = dt.datetime.utcnow().replace(tzinfo=pytz.UTC)
    for player in players:
        player.url = Image.url(player.name)
        player.url_expiration = url_expiration
    print(f"All URL generated. Now saving all players.")
    print(f"URLs are valid till {url_expiration.isoformat()}")
    Player.save_all(players)
    print(f"{len(players)} player url updated. Function complete")
