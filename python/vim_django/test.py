import os
import shutil
import unittest
import time#TODO

import vim_django
from vim_django import *

def mkpath(name):
	return os.path.join(*name.split('/'))

def mkfile(name):
	name = mkpath(name)
	if not os.path.exists(name):
		f = open(name, 'w')
		f.close()

def mkdir(name):
	name = mkpath(name)
	if not os.path.exists(name):
		os.makedirs(name)

class Test_findfile_in_dir(unittest.TestCase):
	def setUp(self):
		mkdir('___test/1')

	def test_finds_in_current_dir(self):
		mkfile('___test/file')
		self.assertEqual(mkpath('./___test/file'), findfile_in_dir('file', '.'))

	def test_finds_in_sub_dir(self):
		mkfile('___test/1/file')
		self.assertEqual(mkpath('./___test/1/file'), findfile_in_dir('file', '.'))

	def test_times_out(self):
		self.assertEqual(None, findfile_in_dir('random_filename_that_doesnt_exist_83t4jos', '/', time.time() + .1))
		
	
	def tearDown(self):
		shutil.rmtree('___test')


class Test_findfile_outside(unittest.TestCase):
	def setUp(self):
		mkdir('___test/1')
		mkdir('___test/2')

	def test_skips_outside(self):
		mkfile('___test/1/file')
		mkfile('___test/2/file')
		self.assertEqual(mkpath('___test/1/file'), findfile_in_dir('file', '___test')) #Normal find would find this
		self.assertEqual(mkpath('___test/2/file'), findfile_outside('file', '___test', '1'))
	
	def tearDown(self):
		shutil.rmtree('___test')


class Test_findfile(unittest.TestCase):
	def setUp(self):
		mkdir('___test/1/2a/3a')
		mkdir('___test/1/2a/3b')
		mkdir('___test/1/2b')
		vim_django.SKIP_STOP_AT_CHECK_FOR_TEST = False
		vim_django.SKIP_ROOT_CHECK_FOR_TEST = False

	def test_finds_in_current_dir(self):
		mkfile('___test/file')
		self.assertEqual(mkpath('./___test/file'), findfile('file', '.'))

	def test_finds_in_sub_dir(self):
		mkfile('___test/1/file')
		self.assertEqual(mkpath('./___test/1/file'), findfile('file', '.'))

	def test_breaks_on_max_height(self):
		self.assertEqual(None, findfile('file', mkpath('./___test/1/2a/'), 2))

	def test_breaks_on_root(self):
		vim_django.SKIP_STOP_AT_CHECK_FOR_TEST = True
		self.assertEqual(None, findfile('file', mkpath('./___test/1/2a/'), sys.maxint))

	def test_breaks_on_stop_at(self):
		vim_django.SKIP_ROOT_CHECK_FOR_TEST = True
		self.assertEqual(None, findfile('file', mkpath('./___test/1/2a/'), sys.maxint, [os.path.abspath(os.curdir)]))

	def test_times_out(self):
		self.assertEqual(None, findfile('random_filename_that_doesnt_exist_srg94234', '/', sys.maxint, [os.path.abspath(os.curdir)], .1))

	def test_finds_in_parent_dir(self):
		mkfile('___test/1/file')
		self.assertEqual(mkpath('./___test/1/file'), findfile('file', mkpath('./___test/1/2a/'), 2))

	def tearDown(self):
		shutil.rmtree('___test')

class Test_get_template_dir(unittest.TestCase):

	def setUp(self):
		mkdir('___test/project')

	def test_no_template_dir_in_settings_gives_none(self):
		settings = '___test/settings.py'
		mkfile(settings)
		self.assertEqual(None, get_template_dir(settings))

	def test_template_dir_in_settings_gives_template(self):
		settings = os.path.abspath('___test/project/settings.py')
		f = open (settings, 'w')
		expected = '/home/user/project/templates'
		f.write('TEMPLATE_DIRS = ("%s",)' % expected)
		f.close()
		self.assertEqual(expected, get_template_dir(settings))

	def tearDown(self):
		shutil.rmtree('___test')


class Test_get_app_name(unittest.TestCase):

	def test_file_in_app_root(self):
		mkdir('___test/project/app')
		mkfile('___test/project/settings.py')
		mkfile('___test/project/app/views.py')
		#self.assertEqual('app', '___test/project/app/views.py')
