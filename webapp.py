#!/usr/bin/env python
# Encoding: utf-8
# -----------------------------------------------------------------------------
# Project : Docker
# -----------------------------------------------------------------------------
# Author : Edouard Richard                                  <edou4rd@gmail.com>
# -----------------------------------------------------------------------------
# License : GNU Lesser General Public License
# -----------------------------------------------------------------------------
# Creation : 25-Feb-2013
# Last mod : 25-Feb-2013
# -----------------------------------------------------------------------------
	# TODO: Handle branches

from flask import Flask, render_template, request, send_file, Response, abort, session, redirect, url_for
import json, urllib, os, git, subprocess, sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APP      = Flask(__name__)

# -----------------------------------------------------------------------------
#
# API
#
# -----------------------------------------------------------------------------

@APP.route('/hook/', methods=('POST', 'GET'))
def hook():
	repo_url    = request.args.get('repo_url')
	project_dir = os.path.join(ROOT_DIR, 'repos', urllib.quote_plus(repo_url))
	repo_dir    = os.path.join(project_dir, 'repo')
	if not os.path.exists(project_dir):
		abort(404)
	# make a pull
	git.Repo(repo_dir).remotes.origin.pull()
	conf       = json.load(file(os.path.join(project_dir, 'config.json')))
	deploy_cmd = conf.get('deploy_cmd')
	# launch command
	response   = subprocess.call(['fab', 'dev'], stdout=subprocess.PIPE, shell=False, cwd=repo_dir)
	return json.dumps({'status':response == 0})

# -----------------------------------------------------------------------------
#
# Main
#
# -----------------------------------------------------------------------------

if __name__ == '__main__':
	""" syntax:
	./webapp add <git_url> <"deployment command">
	"""
	if len(sys.argv) >= 4 and sys.argv[1] == "add":
		repo_url    = sys.argv[2]
		deploy_cmd  = sys.argv[3]
		project_dir = os.path.join(ROOT_DIR, 'repos', urllib.quote_plus(repo_url))
		repo_dir    = os.path.join(project_dir, 'repo')
		if not os.path.exists(os.path.join(ROOT_DIR, 'repos')):
			os.makedirs(s.path.join(ROOT_DIR, 'repos'))
		if not os.path.exists(project_dir):
			os.makedirs(project_dir)
			# create repo
			os.makedirs(repo_dir)
			git.Git().clone(repo_url, repo_dir)
			# create config file
			with open(os.path.join(project_dir, 'config.json'), 'w') as f:
				f.write(json.dumps({"repo_url":repo_url, "deploy_cmd":deploy_cmd}, indent=4))
		sys.exit()
	APP.debug = True
	# run application
	APP.run()
# EOF