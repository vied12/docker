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
	# TODO: 
	# [ ] Dynamic command
	# [ ] Check commit messages for instructions (like HardRelease)
	# [ ] Handle branches
	# [ ] one by one

from flask import Flask, render_template, request, send_file, Response, abort, session, redirect, url_for
import json, urllib, os, subprocess, sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APP      = Flask(__name__)

# -----------------------------------------------------------------------------
#
# API
#
# -----------------------------------------------------------------------------

@APP.route('/hook/', methods=('POST', 'GET'))
def hook():
	if not request.method == 'POST':
		abort(404)
	repo_url    = request.args.get('repo_url')
	project_dir = os.path.join(ROOT_DIR, 'repos', urllib.quote_plus(repo_url))
	repo_dir    = os.path.join(project_dir, 'repo')
	if not os.path.exists(project_dir):
		abort(404)
	# make a pull
	response = subprocess.call(['git', 'pull', repo_url], shell=False, cwd=repo_dir)
	if response != 0:
		print "An error occured during pull of %s" % repo_url
	conf       = json.load(file(os.path.join(project_dir, 'config.json')))
	deploy_cmd = conf.get('deploy_cmd')
	# launch command
	response = subprocess.call(deploy_cmd.split(), shell=False, cwd=repo_dir)
	# search for key words in commit messages
	payload     = json.loads(request.form.values()[0])
	commit_msgs = [_.get("message", "") for _ in payload.get('commits')]
	commands_to_launch = dict()
	for msg in commit_msgs:
		for trigger, cmd in conf.get('triggers', dict()).items():
			if trigger in msg:
				commands_to_launch[trigger] = cmd
	for command in commands_to_launch.values():
		subprocess.call(command.split(), shell=False, cwd=repo_dir)
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
			os.makedirs(os.path.join(ROOT_DIR, 'repos'))
		if not os.path.exists(project_dir):
			os.makedirs(project_dir)
			# create repo
			subprocess.call(['git', 'clone', repo_url, repo_dir], stdout=subprocess.PIPE, shell=False)
			# create config file
			with open(os.path.join(project_dir, 'config.json'), 'w') as f:
				f.write(json.dumps({"repo_url":repo_url, "deploy_cmd":deploy_cmd}, indent=4))
		sys.exit()
	APP.debug = True
	# run application
	APP.run()
# EOF
