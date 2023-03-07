pushd $( dirname "$0" )

if [ ! -d "./output" ]
then
    python3 ../scripts/GtkNodes/setup_gtknodes.py
fi

ontario=../../../../backend/ontario/ontario
cp -r $ontario .

popd