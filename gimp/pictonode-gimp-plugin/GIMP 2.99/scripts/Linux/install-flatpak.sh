pushd $( dirname "$0" )
cp -r ../../pictonode ~/.var/app/org.gimp.GIMP/config/GIMP/2.99/plug-ins
chmod -R 777 ~/.var/app/org.gimp.GIMP/config/GIMP/2.99/plug-ins/pictonode
popd
