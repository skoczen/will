import pypco
import os
from plugins.pco import msg_attachment
import datetime



# You need to put your Personal access token Application key and secret in your environment variables.
# Get a Personal Access Key: https://api.planningcenteronline.com/oauth/applications
# Application ID: WILL_PCO_APPLICATION_KEY environment variable
# Secret: WILL_PCO_API_SECRET environment variable

pco = pypco.PCO(os.environ["WILL_PCO_APPLICATION_KEY"], os.environ["WILL_PCO_API_SECRET"])


def get_plan_item(service_type, plan, item):
    time_to_end = 0
    length = 0
    title = ""
    for p in pco.services.service_types.get(item_id=service_type).rel.plans.list():
        if p.id == plan:
            for items in p.rel.items.list():
                if items.id == item:
                    length = datetime.timedelta(seconds=items.length)
                    title = items.title
                    time_to_end += items.length
                elif int(items.id) > int(item):
                    time_to_end += items.length
            text = f"Live Service Update:\n\nStarted: {title} - {length}\n" \
                f"Planned Time Left - {datetime.timedelta(seconds=time_to_end)}"
            attachment = msg_attachment.\
                SlackAttachment(fallback=text,
                                pco='services',
                                text=text,
                                button_text="Open Live",
                                button_url=f"https://services.planningcenteronline.com/live/{plan}")
            return attachment
    return "No Item Found"


def parse_live_hook(data):
    # data = {'type': 'ItemTime', 'id': '109014325', 'attributes': {'exclude': False, 'length_offset': 0, 'live_end_at': None, 'live_start_at': '2019-04-30T17:31:07Z'}, 'relationships': {'item': {'data': {'type': 'Item', 'id': '568592902'}}, 'plan_time': {'data': {'type': 'PlanTime', 'id': '101382539'}}, 'plan': {'data': {'type': 'Plan', 'id': '41984194'}}}, 'links': {'self': 'https://api.planningcenteronline.com/services/v2/service_types/793678/plans/41984194/live/current_item_time'}}
    meta_data = {}
    meta_data['plan_id'] = data['relationships']['plan']['data']['id']
    meta_data['service_type'] = data['links']['self'].split('/')[6]
    meta_data['item_id'] = data['relationships']['item']['data']['id']
    return meta_data


if __name__ == '__main__':
    # attachment = get_plan_item(service_type=793678, plan='41984194', item='568592902')
    # print(attachment.slack())
    data = {'type': 'ItemTime', 'id': '109014325', 'attributes': {'exclude': False, 'length_offset': 0, 'live_end_at': None, 'live_start_at': '2019-04-30T17:31:07Z'}, 'relationships': {'item': {'data': {'type': 'Item', 'id': '568592902'}}, 'plan_time': {'data': {'type': 'PlanTime', 'id': '101382539'}}, 'plan': {'data': {'type': 'Plan', 'id': '41984194'}}}, 'links': {'self': 'https://api.planningcenteronline.com/services/v2/service_types/793678/plans/41984194/live/current_item_time'}}
    meta_data = parse_live_hook(data)
    attachment = get_plan_item(meta_data['service_type'], meta_data['plan_id'], meta_data['item_id'])
    print(attachment.slack())
