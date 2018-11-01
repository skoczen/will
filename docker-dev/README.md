### Setup your Dev environment:

#### Using Docker Exclusively
* If you're mainly working on Planning Center functionality this is a great option.
  If you want to work on will backend stuff you should probably use the other dev option.
* If you don't have docker installed [install it here](https://store.docker.com/search?offering=community&type=edition)
* If you're on linux `sudo apt-get install docker-ce docker-compose` should work.
* Fork this repository.
* Clone your repository to your local computer
* Edit the default.env file in the `pcobot/docker-dev` folder.
* From command line run `docker-compose up` to start pcobot!
* It will run all the code from your local repository


#### Docker / Local Hybrid

* This is best on mac and linux. I haven't tried this on windows.
* Fork and clone the repository and switch to the dev branch.
* Create a virtual environment in the pcobot directory
    * `python -m venv .`
    * activate `source bin/activate`
* Install requirements `pip install -r requirements.txt`
    * You may need to upgrade pip and setup tools if markdownify doesn't install.
    * You may need to `apt install build-essential python-dev libxml2-dev libxslt1-dev zlib1g-dev`
    * Work through any other errors until requirements.txt installs successfully
* Use Docker compose for redis
    * In the `docker-dev` folder there is a `redis-only` folder.
    * Assuming you have docker and docker-compose installed run `docker-compose up` and that 
    will run redis in a container ready to accept connections on localhost:6379
* Edit `start.sh` in the pcobot folder.
    * Add your API keys, and Slack Legacy bot token.
    * Set start.sh to executable `chmod +x ./start.sh`
* Run `./start.sh` it should run. If not then work through the errors.

#### Final Instructions
* [Join us on Slack!](https://join.slack.com/t/pcobot/shared_invite/enQtNDY4MDUxNTI2Mjc5LTk4MzAxYTAyNzRkYzhkMDM2NGQ5YzU2OTdkNWU1MTMwMjc1OTFhNzY0Y2MxMDQ0NzljZmUzZGU5YmI3MzE3M2M)
* Please make all pull requests on the Dev Branch.
* All pull requests are required to pass PEP8 and Travis CI