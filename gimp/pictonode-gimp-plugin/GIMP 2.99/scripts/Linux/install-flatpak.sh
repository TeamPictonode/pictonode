pushd $( dirname "$0" )

if [ ! -d "./output" ]
then
    python3 ../GtkNodes/setup_gtknodes.py
fi

cp -r ../../pictonode ~/.var/app/org.gimp.GIMP/config/GIMP/2.99/plug-ins
cp -r ./output/introspection ~/.var/app/org.gimp.GIMP/config/GIMP/2.99/plug-ins/pictonode
cp -r ./output/libs ~/.var/app/org.gimp.GIMP/config/GIMP/2.99/plug-ins/pictonode
chmod -R 777 ~/.var/app/org.gimp.GIMP/config/GIMP/2.99/plug-ins/pictonode

popd
