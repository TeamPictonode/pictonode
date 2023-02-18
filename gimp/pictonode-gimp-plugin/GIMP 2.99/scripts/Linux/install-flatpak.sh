#!/bin/bash
pushd $( dirname "$0" )

if [ ! -d "./output" ]
then
    python3 ../GtkNodes/setup_gtknodes.py
fi

ontario=../../../../../backend/ontario/ontario
plugins_dir=~/.var/app/org.gimp.GIMP/config/GIMP/2.99/plug-ins

cp -r ../../pictonode $plugins_dir
cp -r ./output/introspection $plugins_dir/pictonode
cp -r ./output/libs $plugins_dir/pictonode
cp -r $ontario $plugins_dir/pictonode
chmod -R 777 $plugins_dir/pictonode

popd
