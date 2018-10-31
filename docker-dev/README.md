PCOBot Is developed on docker
This allows all testing to be done in the same environment as production.

1. Edit default.env and add your API keys for SLACK and Planning Center Online.
2. Save the file and run docker-compose up.
3. The docker container will run the code in this folder's parent directory.

If you want to change things in the config just make the changes in config.py.

This container is built of the master github branch.