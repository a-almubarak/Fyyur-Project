import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
#note: on my device the default port$ was '5434' the default port# for psql in general is '5432'
SQLALCHEMY_DATABASE_URI = "postgresql://postgres:123@localhost:5434/fyyur"
SQLALCHEMY_TRACK_MODIFICATIONS = False
