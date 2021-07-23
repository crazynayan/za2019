import os

from flask_app import za_app

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-cloud.json"

from config import Config


@za_app.shell_context_processor
def make_shell_context():
    import main
    from flask_app.legacy.models import Game, Player, Schedule
    from flask_app.auth.auth import User
    return {
        "User": User,
        "Player": Player,
        "Config": Config,
        "Game": Game,
        "Schedule": Schedule,
        "main": main
    }


if __name__ == "__main__":
    za_app.run()
