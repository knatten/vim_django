#!/bin/bash

set -e

if [[ $# -ne 1 ]]; then
	echo "USAGE: $0 <version>"
	exit
fi


if [ `git status | grep modified | wc -l` -ne 0 ]; then
    echo "You have local modifications, please check in before running this script";
    exit
fi

version=$1

echo -n "Bumping version to $version... "
sed "s/^\"\ Version.*/\"\ Version:\ \ \ \ \ $version/" plugin/vim_django.vim > plugin/vim_django.vim.tmp
mv plugin/vim_django.vim.tmp plugin/vim_django.vim
git add plugin/vim_django.vim
git commit plugin/vim_django.vim -m 'Bumped version'
echo "ok"

echo -n "Tagging version $version... "
git tag $version
echo "ok"

echo -n "Making tarball... "
tar zcf vim_django-$version.tgz python/vim_django/*py plugin/vim_django.vim
echo "ok"
echo
echo "Finished making release $version"
echo "You can now upload the tarball and do git push --tags"
