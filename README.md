# PCO Bot:
PCO Bot is a bot that integrates with the Planning Center Online API.

PCO Bot is a is a hobby project. It is not affiliated with the awesome team at Planning Center Online, 
but they think it's supper cool!

I use it in Slack.

Currently pco bot can help with:
* Do you have a number for John Doe
* Do you know the birthday for John
* Show the set list for Sunday

### Install
To install follow the instruction in the Will Bot docs but use this repository instead.
http://skoczen.github.io/will/

### PCO Bot Specific Instructions
You need to put your Planning Center API Personal access token application key and secret in your environment variables.

1. Get a Personal Access Key here: https://api.planningcenteronline.com/oauth/applications
2. Set your "Application ID" as WILL_PCO_APPLICATION_KEY environment variable.
3. Set your "Secret" as WILL_PCO_API_SECRET environment variable.

In your config.py file you'll find an ACL section. The birthday and phone number commands are limited to 
people in the staff, and pastors groups.
The set list command is not restricted.
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
2. If it is then comment that you're working on it. If it's not then make an issue and comment that you're working on it.
or add an issue if it's not there.
3. Tag the issue People, Services, Check-in's etc
4. Write awesome code and submit a pull request!


### PCO Bot is built on Will Bot

The first version of Will was built by [Steven Skoczen](http://stevenskoczen.com) while in the Greenkahuna Skunkworks (now defunct), was extended by [Ink and Feet](https://inkandfeet.com) and has been [contributed to by lots of awesome people](http://skoczen.github.io/will/improve/#the-shoulders-of-giants).

Will has docs, including a quickstart and lots of screenshots at:
**[http://skoczen.github.io/will/](http://skoczen.github.io/will)** 
