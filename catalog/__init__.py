from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

app.secret_key = 'super_secret_key'

import catalog.views

print "The application should be serving on port 8090."

"""
if __name__ == '__main__':
	app.debug = True
	app.run(host= '0.0.0.0', port = 8090)

"""