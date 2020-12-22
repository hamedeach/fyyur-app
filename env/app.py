#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Show(db.Model):
  __tablename__='show'
  
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime , nullable=False, default =datetime.utcnow)
  venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'),nullable=False)
  artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'),nullable=False)
  
  def __repr__(self):
    return '<Show artist id :{}, venue id : {}, start time : {}>'.format(self.artist_id, self.venue_id,self.start_time)

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)
    
    def __repr__(self):
      return f'id: {self.id},name: {self.name}'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate -done

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_shows = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)
    
    def __repr__(self):
      return f'id: {self.id},name: {self.name}'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. -done

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue. - Done
  data=Venue.query.all()
  print(data)
  data=[]
  states =  db.session.query(Venue.state,Venue.city).group_by(Venue.state,Venue.city).all()
  print(states)
  for state in states:
    data.append({
      "city" : state[1],
      "state": state[0]
    })
    venueslst =  Venue.query.filter(Venue.city==state[1] and Venue.state ==state[0]).all()
    for ven in venueslst:
      data.append({
        "venues" : venueslst
      })

  
 
  """ data=[]
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    data.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time)
      })
     """
  
  """ data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }] """
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term')
  print(search_term)
  data = Venue.query.filter(Venue.name.like('%'+search_term+'%')).all()
  count = Venue.query.filter(Venue.name.like('%'+search_term+'%')).count()
  print(data)
  print(count)
  response={
    "count" :str( count),
    "data":  data
    }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.get(venue_id)
 
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead - Done
  # TODO: modify data to be the data object returned from db insertion -Done
  
  error =False
  try:
    #get form data
    venue_name = request.form.get('name')
    venue_city = request.form.get('city')
    venue_state = request.form.get('state')
    venue_address = request.form.get('address')
    venue_phone = request.form.get('phone')
    venue_genres = request.form.get('genres')
    venue_image_link = request.form.get('image_link')
    venue_facebook_link = request.form.get('facebook_link')
    #create new model object
    newVenue  = Venue(name=venue_name,city=venue_city,state=venue_state,address=venue_address,genres=venue_genres,phone=venue_phone,image_link=venue_image_link,facebook_link=venue_facebook_link)
    #add model to session and commit
    db.session.add(newVenue)
    db.session.commit()
    error=False
  except():
   error=True
   print(sys.exc_info())
   db.session.rollback()
  finally:
    db.session.close()
      
  if error:
    flash('An error occurred. Venue ' + venue_name + ' could not be listed.')
   
  else:
    flash('Venue ' + venue_name + ' was successfully listed!')
     
   
  
    

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
   # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # return None
  error = False
  tempname=''
  try:
    venue = Venue.query.get(venue_id)
    tempname=venue.name
    db.session.delete(venue)
    db.session.commit()
    error = False
  except():
     db.session.rollback()
     error = True
     print(sys.exc_info())
  finally:
     db.session.close()
     
     
  if error:
    print('error exist')
    flash('An error occurred. Venue ' + tempname + ' could not be deleted.')
  else:
    print('no error exist')
    flash('Venue ' + tempname + ' was successfully deleted!')
    
  return render_template('pages/home.html')
  
  

 

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database -done
  data=Artist.query.all()
  print(data)
  
    
   
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term')
  data = Artist.query.filter(Artist.name.like('%'+search_term+'%')).all()
  count = Artist.query.filter(Artist.name.like('%'+search_term+'%')).count()
  print(data)
  print(count)
  response={
    "count" :str( count),
    "data":  data
    }
 
 
  """ response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }] 
  }
  """
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Artist.query.get(artist_id)
 
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error =False
  artist=''
  tempname=''
 
  try:
    artist = Artist.query.get(artist_id)
    tempname=artist.name
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.get('genres')
    #artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    
    db.session.commit()
    error=False
  except :
   error=True
   print(sys.exc_info())
   db.session.rollback()
  finally:
    db.session.close()
  
  if error:
    flash('An error occurred. Artist ' + tempname + ' could not be updated.')
  else:
    flash('Artist ' + tempname + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue=Venue.query.get(venue_id)
  print(venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error =False
  tempname=''
  venue=''
  try:
    venue = Venue.query.get(venue_id)
    tempname=venue.name
    venue.name = request.form.get('name')
    venue.address = request.form.get('address')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.get('genres')
    #venue.image_link = request.form.get('image_link')
    venue.facebook_link = request.form.get('facebook_link')
    
    db.session.commit()
    error=False
  except :
   error=True
   print(sys.exc_info())
   db.session.rollback()
  finally:
    db.session.close()
  
  if error:
    flash('An error occurred. venue ' +tempname + ' could not be updated.')
  else:
    flash('venue ' + tempname + ' was successfully updated!')
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead  - Done
  # TODO: modify data to be the data object returned from db insertion - Done
  error =False
  try:
    #get form data
    artist_name = request.form.get('name')
    artist_city = request.form.get('city')
    artist_state = request.form.get('state')
    artist_phone = request.form.get('phone')
    artist_genres = request.form.get('genres')
    artist_image_link = request.form.get('image_link')
    artist_facebook_link = request.form.get('facebook_link')
    #create new model object
    newartist  = Artist(name=artist_name,city=artist_city,state=artist_state,genres=artist_genres,phone=artist_phone,image_link=artist_image_link,facebook_link=artist_facebook_link)
    #add model to session and commit
    db.session.add(newartist)
    db.session.commit()
    error=False
  except():
   error=True
   print(sys.exc_info())
   db.session.rollback()
  finally:
    db.session.close()
      
  if error:
    flash('An error occurred. artist ' + artist_name + ' could not be listed.')
   
  else:
    flash('Artist ' + artist_name + ' was successfully listed!')
     
  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead. - Done
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  shows=Show.query.all()
 
  data=[]
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    data.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time)
      })
  
  """ data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }] """
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error =False
  try:
    #get form data
   show_venueid = request.form.get('venue_id')
   show_datetime = request.form.get('start_time')
   show_artistid = request.form.get('artist_id')
   #create new model object
   newshow  = Show(start_time=show_datetime,venue_id =show_venueid,artist_id=show_artistid)
   #add model to session and commit
   db.session.add(newshow)
   db.session.commit()
   error=False
  except():
   error=True
   print(sys.exc_info())
   db.session.rollback()
  finally:
    db.session.close()
      
  if error:
    flash('failed to create show')
   
  else:
    flash('Show was successfully listed!')
     
  

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
