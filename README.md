# PCO Bot:
PCO Bot is a bot that integrates with the Planning Center Online API.

PCO Bot is a hobby project. It is not affiliated with the awesome team at Planning Center Online, 
but they think it's supper cool!

I use it in Slack.

Currently pco bot can help with:
* Do you have a number for John Doe (Any Name)
* Do you know the birthday for John (Any Name)
* Show the set list for Sunday (Any future service date)
* Do you have the address for John (Any Name)
* When was the last time John (Any Name) was here?

### Install on Linux

1. Clone this repository
 ```git clone https://github.com/pastorhudson/pcobot.git```
2. Change to pcobot directory. ```cd pcobot```
3. Setup virtualenv ```virtualenv .```
4. Activate your virtual environment. ```source bin/activate```
5. Get the requirements. ```pip install -r requirements.txt```
6. You need to put your Planning Center API Personal access token application key and secret in start.sh.
Get a Personal Access Key here: https://api.planningcenteronline.com/oauth/applications
7. Add your API Keys in the start.sh file. This is just for setting environment
variables and executing as sudo user. Sudo is needed to open port 80.
```
export WILL_PCO_API_SECRET=asdflaksjdflaksjdf
export WILL_PCO_APPLICATION_KEY=lkjasdlfkjasd;lfkjasdf
export WILL_SLACK_API_TOKEN=kjasd;flkjasdflkj
```
8. Do ```chmod +x ./start.sh``` to make your startup executable.
Then run ```./start.sh```

Find more install help here:
http://skoczen.github.io/will/

### PCO Bot Specific Instructions

In your config.py file you'll find an ACL section. The birthday and phone number commands are limited to 
people in the staff, and pastors groups.
The set list command is not restricted. Add the slack handles to this acl list. You can add any other 
acl groups you'd like.
```
# Access Control: Specify groups of users to be used in the acl=["admins","ceos"] parameter
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
2. If it is then comment that you're working on it. 
If it's not then make an issue and comment that you're working on it.
3. Tag the issue as Enhancement and People, Services, Check-in's etc
4. Write awesome code and submit a pull request!


### PCO Bot is built on Will Bot

The first version of Will was built by [Steven Skoczen](http://stevenskoczen.com) while in the Greenkahuna Skunkworks (now defunct), was extended by [Ink and Feet](https://inkandfeet.com) and has been [contributed to by lots of awesome people](http://skoczen.github.io/will/improve/#the-shoulders-of-giants).

Will has docs, including a quickstart and lots of screenshots at:
**[http://skoczen.github.io/will/](http://skoczen.github.io/will)** 
