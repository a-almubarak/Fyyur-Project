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
from models import *
from flask_migrate import Migrate
from sqlalchemy.sql import text
from flask_wtf import CSRFProtect

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
csrf = CSRFProtect(app)

# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

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


# ----------------------------------------------------------------------------#
# Helper functions.
# ----------------------------------------------------------------------------#
#some dict. are key -> [value], this fucntion returns key -> value if [value] is of length of 1
def dictHelp(dict):
    for key in dict:
        if len(dict[key]) <= 1 and key.strip() != "genres":
            dict[key] = dict[key][0]
    return dict

#change the name of the keys.
def keyedDict(tuple, keys):
    return {keys[i]: tuple[i] for i in range(len(keys))}


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
                    .filter(Venue.id == id == Show.venue_id, today < Show.start_time)
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
    res = (
        db.session.query(Venue.id, Venue.name)
        .filter(Venue.name.ilike("%" + request.form.get("search_term") + "%"))
        .all()
    )
    data = [row._asdict() for row in res]
    response = {
        "count": len(res),
        "data": data,
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
        .filter(ven.id == Show.venue_id, today > Show.start_time)
        .all()
    )
    query2 = (
        db.session.query(Artist.id, Artist.name, Artist.image_link, Show.start_time)
        .join(Show)
        .filter(ven.id == Show.venue_id, today < Show.start_time)
        .all()
    )
    keys = ["artist_id", "artist_name", "artist_image_link", "start_time"]
    past_shows = [keyedDict(row, keys) for row in query1]
    upcoming_shows = [keyedDict(row, keys) for row in query2]
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
        "seeking_talent": ven.seeking_talent,
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
    form = VenueForm(request.form)
    if form.validate():
        try:
            res = dictHelp(request.form.to_dict(flat=False))
            res['seeking_talent'] = bool(res.get('seeking_talant'))
            res.pop('csrf_token')
            #unpack values of res
            venue = Venue(**res)
            db.session.add(venue)
            db.session.commit()
            flash("Venue " + res["name"] + " was successfully listed!")
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash(
                "An error occurred. "
                + res["name"]
                + " Venue could not be listed."
                ,'error'
            )
        finally:
            db.session.close()
    else:
        flash(f'Error {form.errors}')
        return render_template('forms/new_venue.html',form=form)
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    flag = False
    try:
        Venue.query.filter(Venue.id == venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        flag = True
    finally:
        if not flag:
            flash(f"Venue with {venue_id=} has been deleted successfully")
        else:
            flash(f"Venue with {venue_id=} has not been deleted")
            
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return jsonify(dict(redirect=url_for("index")))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database
    query = db.session.query(Artist.id, Artist.name).all()
    data = [row._asdict() for row in query]
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    query = db.session.query(Artist.id, Artist.name).filter(
        Artist.name.ilike("%" + request.form["search_term"] + "%")
    )
    data = [row._asdict() for row in query]

    response = {
        "count": len(data),
        "data": data,
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
        db.session.query(Venue.id, Venue.name, Venue.image_link, Show.start_time)
        .join(Show)
        .filter(art.id == Show.artist_id, today > Show.start_time)
        .all()
    )
    query2 = (
        db.session.query(Venue.id, Venue.name, Venue.image_link, Show.start_time)
        .join(Show)
        .filter(art.id == Show.artist_id, today < Show.start_time)
        .all()
    )
    keys = ["venue_id", "venue_name", "venue_image_link", "start_time"]
    past_shows = [keyedDict(row, keys) for row in query1]
    upcoming_shows = [keyedDict(row, keys) for row in query2]
    data = {
        "id": art.id,
        "name": art.name,
        "genres": art.genres,
        "city": art.city,
        "state": art.state,
        "phone": art.phone,
        "website": art.website_link,
        "facebook_link": art.facebook_link,
        "seeking_venue": art.seeking_venue,
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
    form = ArtistForm(request.form)
    if form.validate():
        try:
            new_info = dictHelp(request.form.to_dict(flat=False))
            new_info["seeking_venue"] = bool(new_info.get("seeking_venue"))
            new_info.pop('csrf_token')
            db.session.query(Artist).filter_by(id=artist_id).update(new_info)
            db.session.commit()
            flash(f"Artist with {artist_id=} has been edited successfully")
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash(f"ERROR. Artist with {artist_id=} has not been edited",'error')
        finally:
            db.session.close()
    else:
        flash(f"Error {form.errors}",'error')
        return render_template('forms/edit_artist.html',form=form,artist=Artist.query.get(artist_id))
    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first().__dict__
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    # to_dict() returns  key -> [value], so helping method makes it key -> value if the list of length 1
    form = VenueForm(request.form)
    if form.validate():
        try:
            new_info = dictHelp(request.form.to_dict(flat=False))
            new_info["seeking_talent"] = bool(new_info.get("seeking_talent"))
            new_info.pop('csrf_token')
            db.session.query(Venue).filter_by(id=venue_id).update(new_info)
            db.session.commit()
            flash(f"Venue with {venue_id=} has been edited successfully")
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash(f"ERROR. Venue with {venue_id=} has not been edited",'error')
        finally:
            db.session.close()
    else:
        flash(f'Errors {form.errors}','error')
        return render_template('forms/edit_venue.html',form=form,venue=Venue.query.get(venue_id))
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
    form = ArtistForm(request.form)
    if form.validate():
        try:
            res = dictHelp(request.form.to_dict(flat=False))
            res['seeking_venue'] = bool(res.get('seeking_venue'))    
            res.pop('csrf_token')
            #unpack result, this idea was found on stackoverflow
            artist = Artist(**res)
            db.session.add(artist)
            db.session.commit()
            flash("Artist " + request.form["name"] + " was successfully listed!")
        except:
            flag = True
            db.session.rollback()
            print(sys.exc_info())
            flash(
                "An error occurred. Artist "
                + request.form["name"]
                + " could not be listed."
            )
        finally:
            db.session.close()
    else:
        flash(f"Error {form.errors}",'error')
        return render_template('forms/new_artist.html',form=form)

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
    query = (
        db.session.query(
            Venue.id,
            Venue.name,
            Artist.id,
            Artist.name,
            Artist.image_link,
            Show.start_time,
        )
        .select_from(Venue)
        .join(Venue.artists)
        .join(Artist, Show.artist_id == Artist.id)
        .all()
    )
    keys = [
        "venue_id",
        "venue_name",
        "artist_id",
        "artist_name",
        "artist_image_link",
        "start_time",
    ]
    data = [keyedDict(row, keys) for row in query]
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
    res = dictHelp(request.form.to_dict(flat=False))
    try:
        venue = Venue.query.get(int(res["venue_id"]))
        show = Show(start_time=res["start_time"])
        show.artist = Artist.query.get(int(res["artist_id"]))
        venue.artists.append(show)
        db.session.commit()
        flash("Show was successfully listed!")
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash("An error occured. Show could not be listed.")
    finally:
        db.session.close()
    # on successful db insert, flash success
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
