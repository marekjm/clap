#!/usr/bin/env python3

import sys, os

install_location = ""

for path in sys.path:
    path = path.split("/")
    if path[-1] == "site-packages" and path[1] != "home": 
        install_location = "/".join(path)
        break

print("{0}/pyproperties.py".format(install_location))
os.remove("{0}/pyproperties.py".format(install_location))
