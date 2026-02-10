import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime


# Load club data from JSON file
def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


# Load competition data from JSON file
def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

# Initialize data sets
competitions = loadCompetitions()
clubs = loadClubs()


# Display the login page
@app.route('/')
def index():
    return render_template('index.html')


# Authenticate user by email and show dashboard
@app.route('/showSummary', methods=['POST'])
def showSummary():
    # Attempt to find the club matching the provided email
    try:
        club = [club for club in clubs if club['email'] == request.form['email']][0]
        return render_template('welcome.html', club=club, competitions=competitions)
    except IndexError:
        # Replaced login_message variable with flash()
        flash("Sorry, that email was not found.")
        return render_template('index.html')


# Display the booking form for a specific competition
@app.route('/book/<competition>/<club>')
def book(competition, club):
    # Retrieve specific club and competition objects
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]

    # Check if competition is in the past
    if foundCompetition['date'] < datetime.now().strftime("%Y-%m-%d %H:%M:%S"):
        flash("This competition is over.")
        return render_template('welcome.html', club=foundClub, competitions=competitions)

    if foundClub and foundCompetition:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    else:
        # Error handling if data is missing
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


# Process the place purchase and update inventory
@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    # Identify the competition and club from form data
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])

    # Double check if competition is in the past during purchase
    if competition['date'] < datetime.now().strftime("%Y-%m-%d %H:%M:%S"):
        flash("This competition is over.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Check if the competition has enough places
    if placesRequired > int(competition['numberOfPlaces']):
        flash("Not enough places")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Limit booking to 12 places per transaction
    if placesRequired > 12:
        flash("You cannot book more than 12 places")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Check if the club has enough points
    if placesRequired > int(club['points']):
        flash("Not enough points")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Deduct requested places from competition capacity
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    club['points'] = int(club['points'])-placesRequired
    # Save updated data to JSON files
    with open('clubs.json', 'w') as c:
        json.dump({'clubs': clubs}, c)
    with open('competitions.json', 'w') as comps:
        json.dump({'competitions': competitions}, comps)
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)

# TODO: Add route for points display


# Log out the user and return to index
@app.route('/logout')
def logout():
    return redirect(url_for('index'))