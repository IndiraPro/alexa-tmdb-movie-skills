from src import app
from flask_ask import Ask, statement, question, session
from flask_ask import request as flask_ask_request
from random import randint
import json
import requests
import time
import unidecode
import logging
import os
from flask import render_template, make_response, request, url_for, jsonify

@app.route('/')
@app.route('/index')
def home():
    return 'Alexa TMDB Movies is running now.'

ask = Ask(app, "/")
def movieOverview():
    url = "https://data.backlash10.hasura-app.io/v1/query"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 702b9fc35664b4a2f408cf49fc57a8f0ec051f2ad1459287"
    }

    body = {
        "type": "run_sql",
        "args": {
            "sql": "SELECT id, budget, homepage, original_title, release_date, revenue, overview FROM tmdb_movies ORDER BY RANDOM() LIMIT 1"
        }
    }
    response = requests.request("POST", url, data=json.dumps(body), headers=headers)
    json_response = response.json()

    if 'result' in json_response:
        if len(json_response['result']) > 1:
            query_text = 'Movie ID ' + json_response['result'][1][0]
            tmdb_id = json_response['result'][1][0]
            query_response = json_response['result'][1][3] + ' Movie overview played from data store'
            response_time = str(response.elapsed.total_seconds())
            is_error_occured = 'False'
            query_overview = query_response + json_response['result'][1][6]
        else:
            query_text = 'Movie ID '
            tmdb_id = 0
            query_response = 'Sorry, Movie details are NOT available'
            response_time = str(response.elapsed.total_seconds())
            is_error_occured = 'False'
            query_overview = 'Sorry, Movie details are NOT available'
    else:
        query_text = 'Movie ID '
        tmdb_id = 0
        query_response = 'Sorry, Movie details are NOT available'
        response_time = str(response.elapsed.total_seconds())
        is_error_occured = 'True'
        query_overview = 'Sorry, Movie details are NOT available'
    body1 = {
        'type': 'insert',
        'args': {
            'table': 'query_logs',
            'objects': [
                {
                    'query_text': query_text,
                    'tmdb_id': tmdb_id,
                    'query_response': query_response,
                    'response_time': response_time,
                    'is_error_occured': is_error_occured
                }
            ]
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 702b9fc35664b4a2f408cf49fc57a8f0ec051f2ad1459287"
    }
    requests.post(url, data=json.dumps(body1), headers=headers)
    return ('You are listening to Overview of Movie' + json_response['result'][1][3] + json_response['result'][1][6])

@ask.launch
def start_skill():
    voverview = movieOverview()
    speech_text = voverview + ' ... mmmmmmm ... Do you want to hear about more movies'
    return question(speech_text)

@ask.intent("YesIntent")
def shareQuote():
    voverview = movieOverview()
    speech_text = voverview + ' ... mmmmmmm ... Do you want to hear about more movies'
    return question(speech_text)

@ask.intent("NoIntent")
def noIntent():
    byeText = 'OK... Bye'
    return statement(byeText)

@ask.session_ended
def session_ended():
    return "{}", 200

# Show Random Quotes upon Reload
@app.route("/myquotes")
def myquotes():
    url = "https://data.backlash10.hasura-app.io/v1/query"
    requestPayload = {
        "type": "run_sql",
        "args": {"sql": "SELECT id, quote FROM yoda_quotes ;"}
    }
    headers = {
        "Content-Type": "application/json",
        "hasura-id": "1",
        "hasura-roles": "admin",
        "Authorization" : "Bearer 702b9fc35664b4a2f408cf49fc57a8f0ec051f2ad1459287"
        }

    response = requests.request("POST", url, data=json.dumps(requestPayload), headers=headers)
    respObj = response.json()
    print (respObj)
    return render_template('QuoteTemplate.html', respObj=respObj)


# Show Random Quotes upon Reload
@app.route("/movienames")
def movienames():
    url = "https://data.backlash10.hasura-app.io/v1/query"
    requestPayload = {
        "type": "run_sql",
        "args": {"sql": "SELECT id, budget, homepage, original_title, release_date, revenue, overview FROM tmdb_movies order by revenue desc ;"}
    }
    headers = {
        "Content-Type": "application/json",
        "hasura-id": "1",
        "hasura-roles": "admin",
        "Authorization" : "Bearer 702b9fc35664b4a2f408cf49fc57a8f0ec051f2ad1459287"
        }

    response = requests.request("POST", url, data=json.dumps(requestPayload), headers=headers)
    respObj = response.json()
    print (respObj)
    return render_template('TMDB_Movies.html', respObj=respObj)

@app.route("/Getmovies/<pmoviename>")
def get_movie_with_logs(pmoviename):
    '''Responds with the Movie details for the given movie name'''
    url = "https://data.backlash10.hasura-app.io/v1/query"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 702b9fc35664b4a2f408cf49fc57a8f0ec051f2ad1459287"
    }
    body = {
        "type": "run_sql",
        "args": {
            "sql": "SELECT id, budget, homepage, original_title, release_date, revenue, overview FROM tmdb_movies where original_title = \'" + pmoviename + "\' order by revenue desc"
        }
    }
    response = requests.request("POST", url, data=json.dumps(body), headers=headers)
    json_response = response.json()
    print (json_response)
    print (json_response['result'][1][6])
    if 'result' in json_response:
        if len(json_response['result']) > 1:
            query_text = 'Movie ID ' + json_response['result'][1][0]
            tmdb_id = json_response['result'][1][0]
            query_response = 'Movie ' + pmoviename + ' is available in data store'
            response_time = str(response.elapsed.total_seconds())
            is_error_occured = 'False'
        else:
            query_text = 'Movie ID '
            tmdb_id = 0
            query_response = 'Sorry, Movie ' + pmoviename + ' is NOT available'
            response_time = str(response.elapsed.total_seconds())
            is_error_occured = 'False'
    else:
        query_text = 'Movie ID '
        tmdb_id = 0
        query_response = 'Sorry, Movie ' + pmoviename + ' is NOT available'
        response_time = str(response.elapsed.total_seconds())
        is_error_occured = 'True'

    body1 = {
        'type': 'insert',
        'args': {
            'table': 'query_logs',
            'objects': [
                {
                    'query_text': query_text,
                    'tmdb_id': tmdb_id,
                    'query_response': query_response,
                    'response_time': response_time,
                    'is_error_occured': is_error_occured
                }
            ]
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 702b9fc35664b4a2f408cf49fc57a8f0ec051f2ad1459287"
    }
    requests.post(url, data=json.dumps(body1), headers=headers)
    resp = make_response(render_template('TMDB_Movies.html', respObj=json_response))
    return resp
