import pypco
import os
from will.plugins.pco import msg_attachment


# You need to put your Personal access token Application key and secret in your environment variables.
# Get a Personal Access Key: https://api.planningcenteronline.com/oauth/applications
# Application ID: WILL_PCO_APPLICATION_KEY environment variable
# Secret: WILL_PCO_API_SECRET environment variable

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


def get(song_title):
    for song in pco.services.songs.list(where={'title': song_title}):
        for arng in song.rel.arrangements.list():
            seq = arng.sequence_short
            arrangement_str = ("\n".join([song.title, " ".join([arng.name,arng.chord_chart_key]),
                                      ", ".join([x for x in arng.sequence_short])]))
    arrangement = msg_attachment.SlackAttachment(fallback="fallback", pco="services", text=arrangement_str)
    arrangement.set_actions(text="Open in PCO", url=("https://services.planningcenteronline.com/songs/" + song.id))

    return arrangement


if __name__ == '__main__':
    song = "Mighty To Save"
    print("Getting song info for ", song)
    print(get(song))
