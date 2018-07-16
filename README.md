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

*  ```... number for *[Any Name]*```   
*  ```... birthday for *[Any Name]*```
*  ```... email address for *[Any Name]*```
*  ```... address for  *[Any Name]*```

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


### Install on Linux 
*(example code assumes Debian - including Ubuntu, Mint, KNOPPIX, Raspbian)*

1. Install virtualenv ```pip install virtualenv```. (If there are exceptions you may need to use sudo permissions ```sudo pip install virtualenv```
2. Install redis. 
```sudo apt-get install redis-server```
```redis-server```
3. Clone this repository
 ```git clone https://github.com/pastorhudson/pcobot.git```
4. Change to pcobot directory. ```cd pcobot```
5. Setup virtualenv ```virtualenv my_pcobot``` (You can replace *'my_pcobot'* with a folder/project name of your choice)
6. Activate your virtual environment. ```source my_pcobot/bin/activate``` . (The name of the current virtual environment will now appear on the left of the prompt (e.g. ```my_project)Your-Computer:your_project UserName$``` to let you know that it’s active. From now on, any package that you install using pip will be placed in the my_project folder, isolated from the global Python installation.)
7. Get the requirements. ```pip install -r requirements.txt```
8. You need to put your Planning Center API Personal access token application key and secret in start.sh.
Get a Personal Access Key here: https://api.planningcenteronline.com/oauth/applications
9. Get your Slack API legacy token here: https://api.slack.com/custom-integrations/legacy-tokens 
10. Add your API Keys in the start.sh file. This is just for setting environment
variables and executing as sudo user. Sudo is needed to open port 80.
```
export WILL_PCO_API_SECRET=asdflaksjdflaksjdf
export WILL_PCO_APPLICATION_KEY=lkjasdlfkjasd;lfkjasdf
export WILL_SLACK_API_TOKEN=kjasd;flkjasdflkj
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
