# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    jsonify,
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from sqlalchemy.sql.sqltypes import ARRAY
from forms import *
from flask_migrate import Migrate

from datetime import datetime
import sys

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:123@localhost:5434/fyyur"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True  # to supress the notification
# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking_for = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())

    artists = db.relationship("Artist", secondary="Show")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking_for_venues = db.Column(db.Boolean())
    seeking_description = db.Column(db.String())
    venues = db.relationship("Venue", secondary="Show")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = "Show"
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"))
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"))
    start_time = db.Column(db.String, nullable=False)

    artist = db.relationship("Artist", backref=db.backref("artist_associations"))
    venue = db.relationship("Venue", backref=db.backref("venue_associations"))


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


today = str(datetime.now())


@app.route("/venues")
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    for city, state in db.session.query(Venue.city, Venue.state):
        tmp = {}
        tmp["city"] = city
        tmp["state"] = state
        query = db.session.query(Venue.id, Venue.name).filter(
            Venue.city == city and Venue.state == state
        )
        venues = []
        for id, name in query:
            venues.append(
                {
                    "id": id,
                    "name": name,
                    "num_upcoming_shows": db.session.query(Venue)
                    .join(Show)
                    .filter(Venue.id == id == Show.venue_id and today < Show.start_time)
                    .count(),
                }
            )
        tmp["venues"] = venues
        data.append(tmp)
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    res = db.session.query(Venue.id,Venue.name).filter(Venue.name.ilike('%'+request.form.get('search_term')+'%')).all()
    data = [row._asdict() for row in res]
    response = {
        "count": len(res),
        "data":data,
    }
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    ven = Venue.query.get(venue_id)
    query1 = (
        db.session.query(Artist.id, Artist.name, Artist.image_link, Show.start_time)
        .join(Show)
        .filter(Artist.id == Show.artist_id and today > Show.start_time)
        .all()
    )
    query2 = (
        db.session.query(Artist.id, Artist.name, Artist.image_link, Show.start_time)
        .join(Show)
        .filter(Artist.id == Show.artist_id and today < Show.start_time)
        .all()
    )

    past_shows = [row._asdict() for row in query1]
    upcoming_shows = [row._asdict() for row in query2]
    data = {
        "id": ven.id,
        "name": ven.name,
        "genres": ven.genres,
        "address": ven.address,
        "city": ven.city,
        "state": ven.state,
        "phone": ven.phone,
        "website": ven.website_link,
        "facebook_link": ven.facebook_link,
        "seeking_talent": ven.looking_for,
        "seeking_description": ven.seeking_description,
        "image_link": ven.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    flag = False
    try:
        res = request.form
        venue = Venue(
            name=res["name"],
            city=res["city"],
            state=res["state"],
            address=res["address"],
            phone=res["phone"],
            genres=res.getlist("genres"),
            facebook_link=res["facebook_link"],
            image_link=res["image_link"],
            website_link=res["website_link"],
            seeking_description=res["seeking_description"],
        )
        try:
            venue.looking_for = bool(res["seeking_talent"])
        except:
            venue.looking_for = False
        db.session.add(venue)
        db.session.commit()
    except:
        flag = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        if not flag:
            flash("Venue " + request.form["name"] + " was successfully listed!")
        else:
            flash(
                "An error occurred. "
                + request.form["name"]
                + " Venue could not be listed."
            )
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.filter(Venue.id == venue_id).delete()
        db.session.commit()
        flash(f"Venue with {venue_id=} has been deleted successfully")
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash(f"Venue with {venue_id=} has not been deleted")
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return jsonify(dict(redirect=url_for("index")))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database
    query = db.session.query(Artist.id,Artist.name).all()
    data = [row._asdict() for row in query]
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {
        "count": 1,
        "data": [
            {
                "id": 4,
                "name": "Guns N Petals",
                "num_upcoming_shows": 0,
            }
        ],
    }
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    art = Artist.query.get(artist_id)
    query1 = (
        db.session.query(Artist.id, Artist.name, Artist.image_link, Show.start_time)
        .join(Show)
        .filter(Artist.id == Show.artist_id and today > Show.start_time)
        .all()
    )
    query2 = (
        db.session.query(Artist.id, Artist.name, Artist.image_link, Show.start_time)
        .join(Show)
        .filter(Artist.id == Show.artist_id and today < Show.start_time)
        .all()
    )

    past_shows = [row._asdict() for row in query1]
    upcoming_shows = [row._asdict() for row in query2]
    data = {
        "id": art.id,
        "name": art.name,
        "genres": art.genres,
        "city": art.city,
        "state": art.state,
        "phone": art.phone,
        "website": art.website_link,
        "facebook_link": art.facebook_link,
        "seeking_venue": art.looking_for_venues,
        "seeking_description": art.seeking_description,
        "image_link": art.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id).__dict__
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = db.session.query(Venue).filter(Venue.id==venue_id).first().__dict__
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    flag = False
    try:
        res = request.form
        print(res)
        artist = Artist(
            name=res["name"],
            city=res["city"],
            state=res["state"],
            phone=res["phone"],
            genres=res.getlist("genres"),
            facebook_link=res["facebook_link"],
            image_link=res["image_link"],
            website_link=res["website_link"],
            seeking_description=res["seeking_description"],
        )
        try:
            print(bool(res["seeking_venue"]))
            artist.looking_for_venues = bool(res["seeking_venue"])
        except:
            artist.looking_for_venues = False
        db.session.add(artist)
        db.session.commit()
    except:
        flag = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        if not flag:
            flash("Artist " + request.form["name"] + " was successfully listed!")
        else:
            flash(
                "An error occurred. Artist "
                + request.form["name"]
                + " could not be listed."
            )

    # on successful db insert, flash success
    # flash("Artist " + request.form["name"] + " was successfully listed!")
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = [
        {
            "venue_id": 1,
            "venue_name": "The Musical Hop",
            "artist_id": 4,
            "artist_name": "Guns N Petals",
            "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
            "start_time": "2019-05-21T21:30:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 5,
            "artist_name": "Matt Quevedo",
            "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
            "start_time": "2019-06-15T23:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-01T20:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-08T20:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-15T20:00:00.000Z",
        },
    ]
    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash("Show was successfully listed!")
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
