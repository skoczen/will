This is the easiest way to get pcobot running:

1. Edit default.env and add your API keys for SLACK and Planning Center Online.
2. Save the file and run docker-compose up.
3. Profit.

If you want to change things in the config just make the changes in config.py.

If you want to change the plugins or use this as a dev environment:
1. Make a ./plugins directory.
2. Put the copy the pco folder from the github plugins folder including __init__.py
3. When you run docker-compose up it will run your local version of the plugin.

pastorhudson_pcobot folder:
This folder contains the Dockerfile used to build the pastorhudson/pcobot image.
You only need this if you want to roll your own image for some reason.
