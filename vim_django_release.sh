#!/bin/bash

set -e

if [[ $# -ne 1 ]]; then
	echo "USAGE: $0"
	exit
fi

git co $1
tar zcf vim_django-$1.tgz python/vim_django/*py plugin/vim_django.vim
git co master
