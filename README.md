[![Build Status](https://travis-ci.org/pastorhudson/pcobot.svg?branch=master)](https://travis-ci.org/pastorhudson/pcobot)
# PCO Bot:
PCO Bot is a bot that integrates with the Planning Center Online API.

PCO Bot is a hobby project. It is not affiliated with the awesome team at Planning Center Online, 
but they think it's super cool!

It is intended for use with [Slack](https://slack.com/), and it is built upon an extensible and modular framework.

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

#### Access Control Lists
This isn't really used in the pcobot but it is used for Will bot commands
* :lock: ```!acl``` (Displays the current access lists.)

To change the access control list, see configuration instructions below and this [enhancement](https://github.com/pastorhudson/pcobot/issues/17)

----------------------------------
### Get API Tokens

  * Get a Planning Center Personal Access Key here: https://api.planningcenteronline.com/oauth/applications
  * Get a Slack legacy token here: https://api.slack.com/custom-integrations/legacy-tokens
  * Create a bot user. https://my.slack.com/services/new/bot
  
  **Note:** The user who owns the Personal Access Key must have permissions to access to all the apps you want the bot to access. You'll also need to ensure that your church has signed up to the People app. (It's free with any other app!) You can use the Personal access key from one o your PCO *Organization Administrators*, or you may even choose to create a dedicated user just for this bot.

### Install on Heroku

1. Fork this repository.
2. Get a Heroku account.
3. Add a redis add-on from [Elements](https://elements.heroku.com/addons). (e.g. Redis Cloud will work automatically) Note: You will need to verify your account with a credit card even to install a free add-on.
4. Enter your config vars on the [settings](https://dashboard.heroku.com/apps/your_app/settings) page. You can set your timezone with a variable. Permissible values can be found in the [IANA TZ list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

 	* WILL_PCO_API_SECRET		```AJS7F7ZIJ2...```
 	* WILL_PCO_APPLICATION_KEY	```X0579RTGV7...```
 	* WILL_SLACK_API_TOKEN		```xoxb-X3WTBK0PZL...```
	* WILL_SECRET_KEY 		[Make your own](https://www.random.org/strings/?num=10&len=20&digits=on&loweralpha=on&unique=on&format=html&rnd=new```)
	* TZ    			```America/Los_Angeles```
		
5. Choose github as your deployment method in heroku and connect to your fork of pcobot.
6. Deploy the master branch.

### Install on Linux 
*(example code assumes Debian - including Ubuntu, Mint, KNOPPIX, Raspbian)*

**Note:** If deploying on Rasbian Jessie (Raspberry Pi), you will need to ensure you build your virtual environment with Python3, and you may need to ```pip install redis-server``` as well.


1. Install virtualenv ```pip install virtualenv```.
3. Clone this repository
 ```git clone https://github.com/pastorhudson/pcobot.git```
4. Change to pcobot directory. ```cd pcobot```
5. Setup the pcobot folder as a virtualenv using the following command. ```virtualenv .```  (**Important:** the `.` references the current folder)
6. Activate your virtual environment. ```source bin/activate``` . (The name of the current virtual environment will now appear on the left of the prompt to let you know that it’s active. From now on, any package that you install using pip will be isntalled to the virtual environment, isolated from the global Python installation.)
7. Get the requirements. ```pip install -r requirements.txt``` 
10. Add your API Keys in the start.sh file. This is just for setting environment
variables and executing as sudo user. (Sudo is needed to open port 80.)

e.g. (using random strings as keys)
```
export WILL_PCO_API_SECRET=AJS7F7ZIJ2
export WILL_PCO_APPLICATION_KEY=X0579RTGV7
export WILL_SLACK_API_TOKEN=xoxb-X3WTBK0PZL
```
	
11. Do ```chmod +x ./start.sh``` to make your startup executable.
Then run ```./start.sh```

Find more install help here:
http://skoczen.github.io/will/

### PCO Bot Configuration Instructions

In your config.py file you'll find an ACL section. Certain commands are limited to people in the *staff* and *pastors* groups.
The set list command is not restricted. Add the slack handles to this acl list. You can add any other 
acl groups you'd like. Each entry must be in lower case!
```
# Access Control: Specify groups of users to be used in the acl=["pastors","staff"] parameter
# in respond_to and hear actions.
# Group names can be any string, and the list is composed of user handles.
ACL = {
    "staff": ["johnell", "leigh", "pastorjoe","pastorhudson"],
    "pastors": ["pastorjoe","pastorhudson"],
	"media_team": ["joe.eafrati"],
}
```

### Contribute!
I'd love to have your help building PCO Bot. 
If there's something you want to add 
1. Look to see if your feature is already an issue.
2. If it is not then make it an issue and submit it. Ideally, you can take ownership of it and comment that you're working on it!
3. Make sure it is clear whether this issue is an Enhancement or Bug and which PCO product(s) it applies to. (People, Services, Check-in, Resources, etc.)
4. Write awesome code and submit a pull request!


### PCO Bot is built on Will Bot and PyPCO

The first version of Will was built by [Steven Skoczen](http://stevenskoczen.com) while in the Greenkahuna Skunkworks (now defunct), was extended by [Ink and Feet](https://inkandfeet.com) and has been [contributed to by lots of awesome people](http://skoczen.github.io/will/improve/#the-shoulders-of-giants).

Will has docs, including a quickstart and lots of screenshots at:
**[http://skoczen.github.io/will/](http://skoczen.github.io/will)** 


[Pypco](https://github.com/billdeitrick/pypco) is an object-oriented, Pythonic library built by Bill Deitrick.
