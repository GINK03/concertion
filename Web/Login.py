
from urllib.parse import parse_qsl
from requests_oauthlib import OAuth1Session
from flask import Flask, session, make_response
from flask import jsonify, request, redirect, url_for
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask import Flask, request, jsonify
from flask import render_template, redirect

def login():
    return redirect(url_for('twitter.login'))
