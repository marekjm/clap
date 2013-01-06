#!/usr/bin/env python3

import sys, shutil, os

install_location = ""

for path in sys.path:
    path = path.split("/")
    if path[-1] == "site-packages" and path[1] != "home": 
        install_location = "/".join(path)
        break

print("./clap.py -> {0}".format(install_location))
shutil.copy("./clap.py", install_location)
