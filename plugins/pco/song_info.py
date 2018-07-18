import pypco
import os
from plugins.pco import msg_attachment


# You need to put your Personal access token Application key and secret in your environment variables.
# Get a Personal Access Key: https://api.planningcenteronline.com/oauth/applications
# Application ID: WILL_PCO_APPLICATION_KEY environment variable
# Secret: WILL_PCO_API_SECRET environment variable

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])

# TODO see what happens with multiple arrangements


def get(song_title):
    arrangement_list = []
    used_dates = []
    arrangement = []
    arrangement_str = ""
    try:
        for song in pco.services.songs.list(where={'title': song_title}):
            for arng in song.rel.arrangements.list():
                if arng.sequence_short:
                    sequence = ", ".join([x for x in arng.sequence_short])
                else:
                    sequence = "No sequence found."
                if arng.chord_chart_key:
                    song_key = arng.chord_chart_key
                else:
                    song_key = "No key set."
                arrangement_str = ("\n".join([song.title, " ".join([arng.name + ':', song_key]),
                                              sequence]))
            for used in song.rel.song_schedules.list(filter=['three_most_recent']):
                used_dates.append(used.plan_dates)
            used_dates.reverse()
            if used_dates:
                arrangement_str += "\nLast Used: \n"
                for rdates in used_dates:
                    arrangement_str += rdates + "\n"
            else:
                arrangement_str += "\nNever Used."
            arrangement = msg_attachment.SlackAttachment(fallback="Open in Services",
                                                         pco="services", text=arrangement_str)
            arrangement.add_button(text="Open in PCO",
                                   url=("https://services.planningcenteronline.com/songs/" + song.id))
            arrangement_list.append(arrangement)
            arrangement = []
            arrangement_str = ""
            used_dates = []

    except UnboundLocalError:
        arrangement_str = " ".join(["I couldn't find any song titled:", '"' + song_title + '"', "¯\_(ツ)_/¯"])
        arrangement = msg_attachment.SlackAttachment(fallback="Open in Services", pco="services", text=arrangement_str)

    finally:
        return arrangement_list


def get_last_used(song_title):
    for song in pco.services.songs.list(where={'title': song_title}):
        for used in song.rel.song_schedules.list(filter=["three_most_recent"], order=["-plan_sort_date"]):
            last_used = used.plan_dates
            last_used = reversed(last_used)

    return last_used


if __name__ == '__main__':
    song = "amazing"
    print("Getting song info for ", song)
    for song in get(song):
        print(song.slack())
