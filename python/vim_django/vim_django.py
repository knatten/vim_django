"""vim_django.py see vim_django.vim"""
import fnmatch
import os
import sys
import time

# pylint: disable-msg=C0103
SKIP_ROOT_CHECK_FOR_TEST = False
SKIP_STOP_AT_CHECK_FOR_TEST = False
# pylint: enable-msg=C0103

def findfile_in_dir(name, path, time_limit=sys.maxint):
	"""Finds the first match of name in subdirectories of path"""
	for root, _, filenames in os.walk(path):
		if time.time() > time_limit:
			print "Timeout while searching for", name
			return None
		for filename in fnmatch.filter(filenames, name):
			return os.path.join(root, filename)
	return None


def findfile_outside(name, path, outside, time_limit=sys.maxint):
	"""Recursively finds a file in path, but skips "outside" """
	for fname in os.listdir(path):
		if os.path.isfile(os.path.join(path, fname)) and fname == name:
			return os.path.join(path, fname)
		if os.path.isdir(os.path.join(path, fname)) and fname != outside:
			match = findfile_in_dir(name, os.path.join(path, fname), time_limit)
			if match:
				return match

def path_is_root(path):
	return os.path.dirname(path) == path

def findfile(name, path, max_height=sys.maxint, stop_at=[], timeout=1):
	"""Finds a file in path, or subdir or subdir of a parent dir"""
	# pylint: disable-msg=W0102
	time_limit = time.time() + timeout
	if path.endswith(os.path.sep):
		path = path[:-len(os.path.sep)]
	level = 0
	previous_path = ''
	while True:
		if path == '' and not SKIP_ROOT_CHECK_FOR_TEST:
			return None
		if os.path.abspath(path) in [os.path.abspath(s) for s in stop_at]\
			and not SKIP_STOP_AT_CHECK_FOR_TEST:
			return None
		found = findfile_outside(name, path, previous_path, time_limit)
		if found:
			return found
		elif level == max_height or path_is_root(path):
			return None
		previous_path = os.path.basename(path)
		path = os.path.dirname(path)
		level += 1
	# pylint: enable-msg=W0102


def find_settings(for_file, settings='settings.py', max_height=sys.maxint, \
	stop_at=[], timeout=1):
	"""Find the settings-file for a django file

	This function searches for the the settings-file for the project that a
	file is part of.

	This is done by first searching the sub-directories of where the file is 
	located, and then recursively searching the sub-directories of all the
	parent directories of the file.
	
	Keyword arguments:
	for_file -- The file to use as a base when searching for the settings file
	settings -- The name of the settings-file (default 'settings.py')
	max_height -- The maximum number of levels of parent directories to search
	stop_at -- A list of directories to not search above. E.g. ['/home/me']
	timeout -- If the file is not found in <timeout> seconds, give up
	"""
	# pylint: disable-msg=W0102
	if not for_file:
		raise Exception("Could not find filename of current buffer. Are you in a buffer?")
	try:
		fname = findfile(settings, os.path.dirname(for_file), max_height, \
			stop_at, timeout)
	except OSError:
		raise Exception("Could not find " + settings)
	return fname
	# pylint: enable-msg=W0102

def absdirname(fname):
	"""Return full path of directory where fname is located"""
	return os.path.abspath(os.path.dirname(fname))

def get_setting(setting, settings):
	"""Get a value from django settings"""
	path = absdirname(settings)
	appended_path = False
	if not path in sys.path:
		sys.path.append(path)
		appended_path = True
	glbl = {}
	local = {'__file__': os.path.split(settings)[-1]}
	execfile(settings, glbl, local)
	if appended_path:
		sys.path.remove(path)
	return local[setting]

def get_template_dir(settings):
	"""Find the first element of TEMPLATE_DIRS"""
	setting = "TEMPLATE_DIRS"
	try:
		return get_setting(setting, settings)[0]
	except (KeyError, TypeError):
		raise Exception("Could not find " + setting + " in " + settings)

def get_app_name(for_file, settings, template_dir):
	"""Get the name of the app in which for_file belongs"""
	if os.path.abspath(template_dir) in os.path.abspath(for_file):
		subdir = os.path.abspath(for_file).replace(os.path.abspath(template_dir),'')
		return subdir.split(os.path.sep)[1]
	return for_file.replace(absdirname(settings), '').split(os.path.sep)[1].\
		strip(os.path.sep)

def get_app_dir(settings_dir, app_name):
	return os.path.join(absdirname(settings_dir), app_name)
