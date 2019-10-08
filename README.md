[![Build Status](https://travis-ci.org/pastorhudson/pcobot.svg?branch=master)](https://travis-ci.org/pastorhudson/pcobot)

# PCO Bot:
PCO Bot is a bot that integrates with the Planning Center Online API.

PCO Bot is a hobby project. It is not affiliated with the awesome team at Planning Center Online, 
but they think it's super cool!

It is intended for use with [Slack](https://slack.com/), and it is built upon an extensible and modular framework.

## Accounts you will / may need:
* [Heroku Account](http://heroku.com)(if launching on Heroku)
* [GitHub Account](http://github.com) - Not needed to launch via Heroku.
* [PCO Admin access / API Tokens.]((https://api.planningcenteronline.com)
* [Slack account and API Token](https://my.slack.com/services/new/bot)
* redis add-on from [Elements](https://elements.heroku.com/addons). *see Heroku install instructions for details.


### Usage

All commands are restricted by planning center App access. 
When you run a command it will look up your Planning Center permissions. 
If you have access to that app the command will work.

#### Check your permissions
*  ```... !apps *[App Name]*```
If no app name is provided it will list all the apps you can access. 


#### People

```I need the | Do you know the | Do you have a | Can somebody tell me the...```

*  :lock:  ```... number for *[Any Name]*```   
*  :lock: ```... birthday for *[Any Name]*```
*  :lock: ```... email address for *[Any Name]*```
*  :lock: ```... address for  *[Any Name]*```

#### Check-ins (Attendance)
* ```When was the last time *[Any Name]* was here?```
* ```Was *[Any Name]* here Sunday?```

#### Services (Plans)
* ```Show the set list for *[Any future service date]*```
* ```Show the set list for *[Any future service date]*```
* ```What is the arrangement for [Any Song]?```
* ```Who is *[serving|scheduled]* *[on|for]* the *[Any Services team]* team *[Any future day/date/time]*?```
    * Examples:
    * "Who is serving on the band team on Sunday at 10a?"
    * "Who is scheduled for the Downtown Band team today?"
* ```[!serving|!scheduled] *[Any Services team]* *[Any future day/date/time]*```
    * Note: for teams with more than one word in the name, wrap the team name in quotes. E.g. `!serving 'Downtown Band' Sunday`
* ```!notify-team *[Any Services team]* in channel [channel name]```
    * Example: "!notify-team Band in channel band"
    * This sets pcobot to check every 15 minutes if the team is scheduled to be on duty in 15 minutes. If so, it sends a message to the specified channel.
* ```!team-notifications```
    * Displays a list of team notifications set up.
* ```!remove-notification *[Services team set up with notifications]*```
    * Removes a team from on-duty notifications.
    

If you specify a time, it will try to find the team for that precise service time—if you do not, it will simply try to match the team for the day provided.

#### Access Control Lists
This isn't really used in the pcobot but it is used for Will bot commands
* :lock: ```!acl``` (Displays the current access lists.)

To change the access control list, see configuration instructions below and this [enhancement](https://github.com/pastorhudson/pcobot/issues/17)

### Before You Install

1. Create a #bot and # general channel.

2. Verify Slack account(s) Profile Names
  *Slack accounts should match name / email of your PCO users accounts.* 
  
3. Create a Slack Bot and [generate an API Token](https://my.slack.com/services/new/bot)
	*Keep this Token handy, you'll need it when installing your app.
	
4. Create API Keys for PCO
	To Create an PCO API Key, [log on here.](https://api.planningcenteronline.com)
	Click on *‘Create Personal Access Token’*
	Create a Name for the Token, i.e. PCO Slack Bot, etc.
	*Keep these tokens handy; you will need the PCO API Token and Secret key for your environment variables.
	
4. Make a list of your environment variables listed below.

  
#### All Installs  
| Env Var      		       | Value   										| Example    |   
| ------------- 	       |--------------										| --------   |
| WILL_PCO_API_SECRET	       | [GET PCO PERSONAL KEY*](https://api.planningcenteronline.com/oauth/applications)       | ```AJS7F7ZIJ2...```|
| WILL_PCO_APPLICATION_KEY     | [GET PCO PERSONAL KEY*](https://api.planningcenteronline.com/oauth/applications)       | ```X0579RTGV7...```|
| WILL_SLACK_API_TOKEN         | [GET SLACK API TOKEN](https://my.slack.com/services/new/bot)  				| ```xoxb-X3WTL...```|
| WILL_SECRET_KEY	       | [Make your own](https://www.random.org/strings/?num=10&len=20&digits=on&loweralpha=on&unique=on&format=html&rnd=new```)  | - |    
| WILL_SLACK_DEFAULT_CHANNEL   | bot  |  bot |    

#### Heroku-Only
| Env Var      		       | Value   										|  Example   |   
| ------------- 	       |--------------										| --------   |
| WILL_PUBLIC_URL	       | The URL of your Heroku App 			        | ```http://your-app-name.herokuapp.com``` |
| TZ			       | [IANA tz code](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)       | ```America/Los_Angeles``` |

  
 **Note:** The user who owns the PCO Personal Access Key must have permissions to access to all the apps you want the bot to access. You'll also need to ensure that your church has signed up to the People app. (It's free with any other app!) You can use the Personal access key from one of your PCO [Organization Administrators](https://pcoaccounts.zendesk.com/hc/en-us/articles/204462420-Organization-Administrators-Billing-Managers), or you may even choose to create a dedicated user just for this bot.

## Installation
----------------------------------

### Install on Heroku
Click the button!

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

If everything goes well, you will have your own instance of pcobot running.


### Update existing One-Click Heroku Deployment
Prepare for updates:
 - [Install the heroku command line interface](https://devcenter.heroku.com/categories/command-line)

#### Create local repo pointing to the Heroku remote
`heroku git:clone --app YOUR_HEROKU_APPNAME && cd YOUR_HEROKU_APPNAME`
It may tell you that you've cloned an empty repository. That is fine. 

#### Attach the GitHub repository of pcobot as a new remote
`git remote add origin https://github.com/pastorhudson/pcobot`

From now on you can simply update your Heroku instance by running:
```
cd YOUR_HEROKU_APPNAME
git pull origin master # pull down the latest version from GitHub

git push heroku master # push all updates back to your Heroku app instance
```

### Install on Linux 
*(example code assumes Debian - including Ubuntu, Mint, KNOPPIX, Raspbian)*

**Note:** If deploying on Rasbian Jessie (Raspberry Pi), you will need to ensure you build your virtual environment with Python3, and you may need to ```pip install redis-server``` as well.


1. Install virtualenv ```pip install virtualenv```.
3. Clone this repository
 ```git clone https://github.com/pastorhudson/pcobot.git```
4. Change to pcobot directory. ```cd pcobot```
5. Setup the pcobot folder as a virtualenv using the following command. ```virtualenv .```  (**Important:** the `.` references the current folder)
6. Activate your virtual environment. ```source bin/activate``` . (The name of the current virtual environment will now appear on the left of the prompt to let you know that it’s active. From now on, any package that you install using pip will be installed to the virtual environment, isolated from the global Python installation.)
7. Get the requirements. ```pip install -r requirements.txt``` 
10. Add your API Keys and environment variables in the start.sh file. This file is just for setting environment
variables and executing as sudo user. (Sudo is needed to open port 80.)
11. Do ```chmod +x ./start.sh``` to make your startup executable.
Then run ```./start.sh```

Find more install help here:
http://skoczen.github.io/will/

## Configuration

### Slack Channels

Invite your bot to the #announcements and #general channels, and any other channels you'd like. Make sure it has permissions to post. If a channel is restricted to Workspace Owners and Workspace Admins, the bot will not be able to post.

#### #announcements 
This channel is where scheduled announcements will be posted. You can change this using the !achannel command. 
* :lock:```!achannel``` Responds with the current announcement channel
* :lock:```!achannel [any channel]``` Sets the announcement channel for all announcements.
You'll need to invite the bot to any channel you want it to post.

* :lock:```!toggle``` Responds with a list of the current announcement toggles.
* :lock:```!toggle <announcement name>``` Turns announcements on and off.
* :lock:```!twipe``` Clears and revitalizes the announcement toggles. Use this after you upgrade if you are missing new toggles.



#### WebHooks
Some announcements like "New Person Created" need to have Planning Center webhooks configured.

Current webhooks PCObot will need:
* people.v2.events.person.created (Needed for "New Person Created Announcement")
* services.v2.events.plan.live.updated (Needed for "Live Service Update Announcement")

##### Create the webhook:
* [Open PCO Webhooks](https://api.planningcenteronline.com/webhooks#/)
* Click "Add" button
* Check the box(es) for the webhooks you want to enable from the list above
* In the URL box put your heroku url ```https://<your-app-name>.herokuapp.com/pco/webhook``` 
* Click Subscribe
* Use the !toggle command to turn on any announcements you would like to use.

### Bot Admins
Most user permissions are inherited directly from Planning Center Online.  However, a *very* limited number of commands are limited to people in the pcobot *botadmin* group. 

In your config.py file you'll find an ACL section. Add the slack handles to this acl list. You can add any other acl groups you'd like. Each entry must be in lower case!

```
# Access Control: Specify groups of users to be used in the acl=["botadmin"] parameter
# in respond_to and hear actions.
# Group names can be any string, and the list is composed of user handles.
ACL = {
    "botadmin": ["johnell", "leigh", "pastorjoe","pastorhudson"]
}
```

### Contribute!
We'd love to have your help building PCO Bot. If there's something you want to add:

1. Look to see if your feature is already an issue.
2. If it is not then make it an issue and submit it. Ideally, you can take ownership of it and comment that you're working on it!
3. Make sure it is clear whether this issue is an Enhancement or Bug and which PCO product(s) it applies to. (People, Services, Check-in, Resources, etc.)
4. See the guidelines in CONTRIBUTING.MD, write awesome code, and submit a pull request!


### PCO Bot is built on Will Bot and PyPCO

The first version of Will was built by [Steven Skoczen](http://stevenskoczen.com) while in the Greenkahuna Skunkworks (now defunct), was extended by [Ink and Feet](https://inkandfeet.com) and has been [contributed to by lots of awesome people](http://skoczen.github.io/will/improve/#the-shoulders-of-giants).

Will has docs, including a quickstart and lots of screenshots at:
**[http://skoczen.github.io/will/](http://skoczen.github.io/will)** 


[Pypco](https://github.com/billdeitrick/pypco) is an object-oriented, Pythonic library built by Bill Deitrick.

# PCO-BOT - Development instructions
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
