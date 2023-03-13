#!/bin/bash
pushd $( dirname "$0" )

if [ ! -d "./output" ]
then
    python3 ../GtkNodes/setup_gtknodes.py
fi

if [ "$1" == "" ]
then
   plugins_dir=~/.var/app/org.gimp.GIMP/config/GIMP/2.99/plug-ins
else
   plugins_dir=$1
   mkdir $plugins_dir
   chmod 777 $plugins_dir
fi

ontario=../../../../../backend/ontario/ontario

cp -r ../../pictonode $plugins_dir
cp -r ./output/introspection $plugins_dir/pictonode
cp -r ./output/libs $plugins_dir/pictonode
cp -r $ontario $plugins_dir/pictonode

chmod -R 777 $plugins_dir/pictonode

popd
