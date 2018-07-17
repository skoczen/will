import pypco
import os


pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])

attachment_list = []


def get(name):
    # Get the phone number of person(s) and return a formatted string ready to send back.
    try:
        fl_name = {'first_name': name.split()[0], 'last_name': name.split()[1]}

    except IndexError:
        fl_name = {'first_name': name.split()[0]}

    finally:
        for x in pco.people.people.list(where=fl_name):
                print("https://people.planningcenteronline.com/people/" + x.id)


if __name__ == '__main__':
    name = "John"
    print("Testing pco API: ", name)
    print("This should print links to the profiles in your people database that have a first name John.")
    get(name)
