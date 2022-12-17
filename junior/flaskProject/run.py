import os
from application import create_app

env = os.getenv("env", "dev")
app = create_app(env)


if __name__ == '__main__':
    app.run()
