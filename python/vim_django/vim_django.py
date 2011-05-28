import fnmatch
import os
import sys
import time

SKIP_ROOT_CHECK_FOR_TEST = False
SKIP_STOP_AT_CHECK_FOR_TEST = False

def findfile_in_dir(name, path, time_limit=sys.maxint):
	for root, dirnames, filenames in os.walk(path):
		if time.time() > time_limit:
			print "Timeout while searching for", name
			return None
		for filename in fnmatch.filter(filenames, name):
			return os.path.join(root, filename)
	return None


def findfile_outside(name, path, outside, time_limit=sys.maxint):
	for f in os.listdir(path):
		if os.path.isfile(os.path.join(path,f)) and f == name:
			return os.path.join(path,f)
		if os.path.isdir(os.path.join(path, f)) and f != outside:
			match = findfile_in_dir(name, os.path.join(path, f), time_limit)
			if match:
				return match

def findfile(name, path, max_height=sys.maxint, stop_at=[], timeout=1):
	time_limit = time.time() + timeout
	if path.endswith(os.path.sep):
		path = path[:-len(os.path.sep)]
	level = 0
	previous_dir = ''
	while True:
		if path == '' and not SKIP_ROOT_CHECK_FOR_TEST:
			return None
		if os.path.abspath(path) in [os.path.abspath(s) for s in stop_at]\
			and not SKIP_STOP_AT_CHECK_FOR_TEST:
			return None
		found = findfile_outside(name, path, previous_dir, time_limit)
		if found:
			return found
		elif level == max_height:
			return None
		previous_dir = os.path.basename(path)
		path = os.path.dirname(path)
		level += 1


def get_setting(for_file, setting, settings='settings.py', max_height=sys.maxint, stop_at=[], timeout=1):
	"""Get a value from django settings

	This function searches for the the settings-file for the project that a
	file is part of and returns a specified setting.

	This is done by first searching the sub-directories of where the file is 
	located, and then recursively searching the sub-directories of all the
	parent directories of the file.
	
	Keyword arguments:
	for_file -- The file to use as a base when searching for the settings file
	setting -- The setting to search for
	settings -- The name of the settings-file (default 'settings.py')
	max_height -- The maximum number of levels of parent directories to search
	stop_at -- A list of directories to not search above. E.g. ['/home/me']
	"""
	try:
		fname = findfile(settings, os.path.dirname(for_file), max_height, stop_at, timeout=1)
	except OSError:
		return None
	if not fname:	
		return  None
	g = l = {}
	path = os.path.abspath(os.path.dirname(fname))
	appended_path = False
	if not path in sys.path:
		sys.path.append(path)
		appended_path = True
	execfile(fname, g, l)
	if appended_path:
		sys.path.remove(path)
	return l[setting]

def get_template_dir(for_file, settings='settings.py', max_height=sys.maxint, stop_at=[], timeout=1):
	"""Find the first element of TEMPLATE_DIRS"""
	try:
		return get_setting(for_file, 'TEMPLATE_DIRS', settings, max_height, stop_at, timeout)[0]
	except (KeyError, TypeError):
		return None
