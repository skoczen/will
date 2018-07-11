import pypco
import os
from will.plugins.pco import msg_attachment


# You need to put your Personal access token Application key and secret in your environment variables.
# Get a Personal Access Key: https://api.planningcenteronline.com/oauth/applications
# Application ID: WILL_PCO_APPLICATION_KEY environment variable
# Secret: WILL_PCO_API_SECRET environment variable

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])

# TODO see what happens with multiple arrangements

def get(song_title):
    used_dates = []
    arrangement_str = ""
    for song in pco.services.songs.list(where={'title': song_title}):
        for arng in song.rel.arrangements.list():
            seq = arng.sequence_short

            arrangement_str = ("\n".join([song.title, " ".join([arng.name,arng.chord_chart_key]),
                                      ", ".join([x for x in arng.sequence_short]),"Last Used:\n"]))
        for used in song.rel.song_schedules.list(filter=['three_most_recent']):
            used_dates.append(used.plan_dates)
    used_dates.reverse()
    for rdates in used_dates:
        arrangement_str += rdates + "\n"
    arrangement = msg_attachment.SlackAttachment(fallback="Open in Services", pco="services", text=arrangement_str)
    arrangement.add_button(text="Open in PCO", url=("https://services.planningcenteronline.com/songs/" + song.id))

    return arrangement


def get_last_used(song_title):
    for song in pco.services.songs.list(where={'title': song_title}):
        for used in song.rel.song_schedules.list(filter=["three_most_recent"], order=["-plan_sort_date"]):
            last_used = used.plan_dates
            last_used = reversed(last_used)

    arrangement = msg_attachment.SlackAttachment(fallback="fallback", pco="services", text=last_used)
    return last_used


if __name__ == '__main__':
    song = "Mighty To Save"
    print("Getting song info for ", song)
    x = get(song)
    print(x.txt())

