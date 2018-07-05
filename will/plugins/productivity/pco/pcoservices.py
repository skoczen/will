from will.plugin import WillPlugin
from will.decorators import respond_to, periodic, hear, randomly, route, rendered_template, require_settings
import pypco
import datetime
import parsedatetime
import os
from sys import platform


# You need to put your Personal access token Application key and secret in your environment variables.
# Get a Personal Access Key: https://api.planningcenteronline.com/oauth/applications
# Application ID: WILL_PCO_APPLICATION_KEY environment variable
# Secret: WILL_PCO_API_SECRET environment variable

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


def get_set_list(set_date):
    # Get the Order of Service of a date and return a formatted string ready to send back.
    # This only works for future dates since PCO API doesn't let us quarry plans by date.
    cal = parsedatetime.Calendar()
    set_date, parse_status = cal.parse(set_date)
    set_date = datetime.datetime(*set_date[:6])
    # If you're running this on windows this needs to be: %#d rather than %-d
    if platform == "linux" or platform == "linux2":
        set_date = set_date.strftime('%B %-d, %Y')  # linux
    elif platform == "win32":
        set_date = set_date.strftime('%B %#d, %Y')  # windows
    set_list = str(set_date)
    for serviceType in pco.services.service_types.list():
        for plan in serviceType.rel.plans.list(filter=['future']):
            if set_date in plan.dates:

                for items in plan.rel.items.list():
                    if items.attributes['item_type' ''] == 'header':
                        set_list = "\n".join([set_list,"*" + str(items.title) + "*"])
                    elif items.attributes['item_type' ''] == 'song':
                        set_list = "\n".join([set_list, "• _" + str(items.title) + "_"])
                    else:
                        set_list = "\n".join([set_list,"• " + items.title])

    if set_list == set_date:
        set_list = "Sorry, I couldn't fine a plan for that date ¯\_(ツ)_/¯"
    # print(set_list)
    return set_list


class PcoServicesPlugin(WillPlugin):
    @hear("(?:do you |find |got |a )?(set list for |!setlist |setlist for |!sunday |songs for |order of service for )"
              "(?P<pco_date>.*?(?=(?:\'|\?)|$))")
    def pco_setlist_lookup(self, message , pco_date):
        # print("Looking up Sunday's set list")
        self.reply("Let me get that for you.")
        setList = get_set_list(pco_date)
        if setList is None:
            self.reply("Sorry I don't have " + setList + "'s set list.")
        # print(setList)
        self.reply(setList)


# Test your setup by running this file.
# If you add functions in this file please add a test below.


if __name__ == '__main__':

    print("Getting set list for 'Sunday'")
    get_set_list('sunday')
