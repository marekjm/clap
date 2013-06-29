if [ $1 == '']; then
    echo "You have to give Python version (eg. 3.3 for python 3.3) as an argument."
else
    cp -R ./clap/ /usr/lib/python$1/site-packages/
fi
