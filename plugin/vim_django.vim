" Vim plugin for working with Django projects
" Version:     0.1
" Last change: 2011-05-28
" Author:      Anders Schau Knatten
" Contact:     anders AT knatten DOT org
" License:     This file is placed in the public domain.

" TODO
" Configurable max_height, stop_at and timeout
" Cache location of settings for each file

if exists("g:loaded_vim_django")
	finish
endif
let g:loaded_vim_django = 1

if !exists(":VimDjangoCommandTTemplate")
	command -nargs=0  VimDjangoCommandTTemplate  :call VimDjangoCommandTTemplate()
endif

function VimDjangoCommandTTemplate()
	exec "CommandT".VimDjangoGetTemplateDirForApp()
endfunction

function VimDjangoGetTemplateDirForApp()
	let directory=expand('%:p:h')
	let app=split(directory, '/')[-1]
	let template_dir = VimDjangoGetTemplateDir().'/'.app
	return template_dir
endfunction

function VimDjangoGetTemplateDir()
python << endpython
settings = vim_django.find_settings(vim.current.buffer.name, vim.eval("g:VimDjangoSettingsFile"))
vim.command('return "%s"' % vim_django.get_template_dir(settings))
endpython
endfunction

python << endpython
import os
import vim
path = os.path.join(os.environ['HOME'], '.vim', 'python')
if not path in sys.path:
	sys.path.append(path)
from vim_django import vim_django
endpython
if !exists("VimDjangoSettingsFile")
	let VimDjangoSettingsFile = 'settings.py'
endif
