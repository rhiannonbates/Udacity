#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import date
import sys
from models import app, db, Venue, Artist, Shows
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  """ Generates home page for venues which will group the venues with respect to their city and state. 

  Returns: 
    venue_data: generated array which includes all required data objects for the venue
  """
  # TODO: replace with real venues data.

  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  
  # Find the date today
  now = datetime.utcnow()

  # Get the initial data and use it to find the venues and the upcoming show models 
  intial_data = db.session.query(Venue)
  venues = intial_data.all()

  # Get the data for all distinct city, state combos
  list_of_places = Venue.query.distinct(Venue.city, Venue.state).all()

  # Create the data in the correct format by looping over the cities and venues
  venue_data = []
  for place in list_of_places:
    new_data = {
      "city": place.city,
      "state": place.state,
      "venues": []
    }
    venue_data.append(new_data)
    for venue in venues:
      upcoming_shows = intial_data.join(Shows).filter(Shows.start_time > now).filter(Shows.venue_id == venue.id)
      if venue.city == place.city:
        new_venue = {
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": upcoming_shows.count(),
        }
        new_data["venues"].append(new_venue)

  return render_template('pages/venues.html', areas=venue_data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  """
  Implements a case-insensitive search on venues 

  Args: 
    search_term: string with searched term

  Returns:
    on POST: Redirects customer to search_venue page which populates the venues that match the 
    searched string. The redirect passes in the url along with results and search term.
    results: object which contains the data containing the number of matched results 
             and corresponding data for the matched results
    search_term: string of the original searched term
  """
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

  search_term = request.form.get('search_term', '')
  search_result = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term)))
  # Write the data in the correct format
  response = {
    "count": search_result.count(),
    "data": search_result
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  """ 
  Displays the specific venue page

  Args: 
    venue_id: distinct integer to use to search the database for the correct venue

  Returns:
    Redirects to the venue's page using the venue_id. The redirect takes in the url 
    for the page along with the venue
    venue: object containing the specific data for the venue with venue_id including
           upcoming and past shows.
  """
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]

  # Find the date today
  now = datetime.utcnow()

  venue_data = Venue.query.get(venue_id)

  # Join the Shows and Artist table based on the venue ID to get the initial past and upcoming shows data
  past_shows_initial_data = db.session.query(Shows).join(Artist).filter(Shows.venue_id == venue_id).filter(Shows.start_time < now)
  upcoming_shows_initial_data = db.session.query(Shows).join(Artist).filter(Shows.venue_id == venue_id).filter(Shows.start_time > now)

  past_shows_count = past_shows_initial_data.count()
  upcoming_shows_count = upcoming_shows_initial_data.count()

  # Set up the data for the past shows in the correct format
  past_shows_data = past_shows_initial_data.all()
  past_shows = []
  for show in past_shows_data:
    past_shows_obj = {
        "artist_id": show.artist_id,
        "artist_name": show.Artist.name,
        "artist_image_link": show.Artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    past_shows.append(past_shows_obj)

  # Set up the data for the upcoming shows in the correct format
  upcoming_shows_data = upcoming_shows_initial_data.all()
  upcoming_shows = []
  for show in upcoming_shows_data:
    upcoming_shows_obj = {
        "artist_id": show.artist_id,
        "artist_name": Artist.query.get(show.artist_id).name,
        "artist_image_link": Artist.query.get(show.artist_id).image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    upcoming_shows.append(upcoming_shows_obj)

  # Format the data in the correct format
  data = {
    "id": venue_data.id,
    "name": venue_data.name,
    "genres": venue_data.genres,
    "address": venue_data.address,
    "city": venue_data.city,
    "state": venue_data.state,
    "phone": venue_data.phone,
    "website": venue_data.website,
    "facebook_link": venue_data.facebook_link,
    "seeking_talent": venue_data.seeking_talent,
    "seeking_description": venue_data.seeking_description,
    "image_link": venue_data.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
"""
  Creates a new venue in the Venue database 

  Returns: 
    on GET: Populates the venue form
  """
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  """
  Creates a new venue in the Venue database 

  Returns: 
    on POST: Redirects to the home page after the new venue has been added
             to the database.
  """
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)

  try:
    new_venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      facebook_link = form.facebook_link.data,
      genres = form.genres.data,
      image_link = form.image_link.data,
      website = form.website.data,
      seeking_talent = True if form.seeking_talent.data == "Yes" else False,
      seeking_description = form.seeking_description.data
    )
    db.session.add(new_venue)
    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + form.name.data + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except Exception as e:
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:  
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()

    flash('Venue was successfully deleted!')
  except Exception as e:
    db.session.rollback()
    flash('Venue was not deleted!')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  """
  Implements a case-insensitive search on artists

  Args: 
    search_term: string with searched term

  Returns:
    Redirects customer to search_artist page which populates the artists that match the 
    searched string. The redirect passes in the url along with results and search term.
    results: object which contains the data containing the number of matched results 
             and corresponding data for the matched results
    search_term: string of the original searched term
    """
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

  # Get the search term from the form
  search_term = request.form.get('search_term', '')
  search_result = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term)))

  # Write the data in the correct format
  response = {
    "count": search_result.count(),
    "data": search_result
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  """ 
  Displays the specific artist page

  Args: 
    artist_id: distinct integer to use to search the database for the correct artist

  Returns:
    Redirects to the atist's page using the artist_id. The redirect takes in the url 
    for the page along with the artist data
    artist: object containing the specific data for the artist with artist_id including
           upcoming and past shows.
  """
  # shows the artist page with the given artist_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  now = datetime.utcnow()

  artist_data = Artist.query.get(artist_id)

  # Join the Shows and Venue table based on the venue ID to get the initial past and upcoming shows data
  past_shows_initial_data = db.session.query(Shows).join(Venue).filter(Shows.artist_id == artist_id).filter(Shows.start_time < now)
  upcoming_shows_initial_data = db.session.query(Shows).join(Venue).filter(Shows.artist_id == artist_id).filter(Shows.start_time > now)

  past_shows_count = past_shows_initial_data.count()
  upcoming_shows_count = upcoming_shows_initial_data.count()

  # Set up the data for the past shows in the correct format
  past_shows_data = past_shows_initial_data.all()
  past_shows = []
  for show in past_shows_data:
    past_shows_obj = {
        "venue_id": show.venue_id,
        "venue_name": show.Venue.name,
        "venue_image_link": show.Venue.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    past_shows.append(past_shows_obj)

  # Set up the data for the upcoming shows in the correct format
  upcoming_shows_data = upcoming_shows_initial_data.all()
  upcoming_shows = []
  for show in upcoming_shows_data:
    upcoming_shows_obj = {
        "venue_id": show.venue_id,
        "venue_name": show.Venue.name,
        "venue_image_link": show.Venue.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    upcoming_shows.append(upcoming_shows_obj)

  # Format the data in the correct format
  data = {
    "id": artist_data.id,
    "name": artist_data.name,
    "genres": artist_data.genres,
    "city": artist_data.city,
    "state": artist_data.state,
    "phone": artist_data.phone,
    "website": artist_data.website,
    "facebook_link": artist_data.facebook_link,
    "seeking_venue": artist_data.seeking_venue,
    "seeking_description": artist_data.seeking_description,
    "image_link": artist_data.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  """
  Edits the artist with id artist_id in the database

  Args:
    artist_id: distinct integer which is the primary key for the artist

  Returns:
    on GET: populates the data in the form to being the current data for 
            artist with id artist_id
            Renders the form using the ArtistForm and specific details for artist
  """
  artist = Artist.query.get(artist_id)
  # Ensure that seeking venue has been converted to the values of the drop down
  artist.seeking_venue = "Yes" if artist.seeking_venue == True else "No"
  # Populate the entries in the form 
  form = ArtistForm(obj=artist)

  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  """
  Edits the artist with id artist_id in the database

  Args:
    artist_id: distinct integer which is the primary key for the artist

  Returns:
    on POST: Updates the entries for the artist with id artist_id in the 
             database
             Redirects the user to the show_artist page and passes in the 
             distinct integer for artist_id
  """
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  try:
    setattr(artist, "name", form.name.data)
    setattr(artist, "genres", form.genres.data)
    setattr(artist, "city", form.city.data)
    setattr(artist, "state", form.state.data)
    setattr(artist, "phone", form.phone.data)
    setattr(artist, "website", form.website.data)
    setattr(artist, "facebook_link", form.facebook_link.data)
    setattr(artist, "seeking_venue", True if form.seeking_venue.data == "Yes" else False)
    setattr(artist, "seeking_description", form.seeking_description.data)
    setattr(artist, "image_link", form.image_link.data)

    db.session.commit()

    flash('Venue ' + form.name.data + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('Venue ' + form.name.data + ' was not able to be updated!')
  finally:
    db.session.close()
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  """
  Edits the venue with id avenue_id in the database

  Args:
    venue_id: distinct integer which is the primary key for the venue

  Returns:
    on GET: populates the data in the form to being the current data for 
            venue with id venue_id
            Renders the form using the VenueForm and specific details for venue
  """
  venue = Venue.query.get(venue_id)
  # Ensure that seeking venue has been converted to the values of the drop down
  venue.seeking_talent = "Yes" if venue.seeking_talent == True else "No"
  # Populate the entries in the form 
  form = VenueForm(obj = venue)

  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  """
  Edits the venue with id venue_id in the database

  Args:
    venue_id: distinct integer which is the primary key for the venue

  Returns:
    on POST: Updates the entries for the venue with id venue_id in the 
             database
             Redirects the user to the show_venue page and passes in the 
             distinct integer for venue_id
  """
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)
  try:
    setattr(venue, "name", form.name.data)
    setattr(venue, "genres", form.genres.data)
    setattr(venue, "address", form.address.data)
    setattr(venue, "city", form.city.data)
    setattr(venue, "state", form.state.data)
    setattr(venue, "phone", form.phone.data)
    setattr(venue, "website", form.website.data)
    setattr(venue, "facebook_link", form.facebook_link.data)
    setattr(venue, "seeking_talent", True if form.seeking_talent.data == "Yes" else False)
    setattr(venue, "seeking_description", form.seeking_description.data)
    setattr(venue, "image_link", form.image_link.data)

    db.session.commit()

    flash('Venue ' + form.name.data + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('Venue ' + form.name.data + ' was not able to be updated!')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
 """
  Creates a new artist in the Artist database 

  Returns: 
    on GET: Populates artist form.
  """
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  """
  Creates a new artist in the Artist database 

  Returns: 
    on POST: Redirects to the home page after the new artist has been added
             to the database.
  """
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  try:
    new_artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      facebook_link = form.facebook_link.data,
      genres = form.genres.data,
      image_link = form.image_link.data,
      website = form.website.data,
      seeking_venue = True if form.seeking_venue.data == "Yes" else False,
      seeking_description = form.seeking_description.data
    )
    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + form.name.data + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except Exception as e:
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  """ Home page for shows which show all shows in the Shows database

  Returns: 
    shows: generated array which includes all required data objects for the shows
  """
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]

  # Join all models to get all required data
  shows = db.session.query(Shows).join(Venue).join(Artist).all()

  # set up the data to be in the correct format
  show_data = []
  for show in shows:
    show_obj = {
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    show_data.append(show_obj)

  return render_template('pages/shows.html', shows=show_data)

@app.route('/shows/create')
def create_shows():
  """
  Creates a new show in the Shows database 

  Returns: Populates the shows form.
  """
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  """
  Creates a new show in the Shows database 

  Returns: 
    on POST: Redirects to the home page after the new show has been added
             to the database.
  """
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)

  try:
    new_show = Shows(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )
    db.session.add(new_show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except Exception as e:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
