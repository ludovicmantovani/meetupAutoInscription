#!/usr/bin/python3

import json
import requests
from pprint import pprint
import configparser
import sys
import time

API_URL_BASE = 'https://api.meetup.com/'
MY_API_KEY = None
MY_MEMBER_ID = None
GROUPS = None
SECOND_TIMER = 60 * 5

def decode_response(response):
    if response.status_code in (200, 201):
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

def get_request(url):
    response = requests.get(url)
    return decode_response(response)

def post_request(url):
    response = requests.post(url)
    return decode_response(response)

def print_events_name(json_group_events):
    for event in json_group_events:
        print(event["name"])


def find_group_events(group):
    return get_request('{0}{1}/events'.format(API_URL_BASE, group))

def member_already_subscribe(group, event_id, member_id):
    subscriber = False
    json_event = get_request('{0}{1}/events/{2}/rsvps'.format(API_URL_BASE, group, event_id))
    for subscribe in json_event:
        if str(subscribe['member']['id']) == member_id:
            subscriber = True
    return subscriber

def subscribe_to_event(group, event_id, response='yes'):
    url="{0}{1}/events/{2}/rsvps?&key={3}&response={4}".format(API_URL_BASE, group, event_id, MY_API_KEY, response)
    return post_request(url)


def main():
    for group in GROUPS:
            print('[' + group + ']')
            # Cherche tous les évènements du groupe
            json_ret = find_group_events(group)
            print_events_name(json_ret)
            # Récupération de l'id des évènements
            events_id_list = [event['id'] for event in json_ret]
            # Pour chaques évènements
            for event_id in events_id_list:
                # Vérification inscription du membre
                already_subscribe = member_already_subscribe(group, event_id, MY_MEMBER_ID)
                # Si non inscrit
                if already_subscribe == False:
                    #Inscription
                    json_ret = subscribe_to_event(group, event_id)
                    pprint(json_ret)

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('./meetupAutoInscriptionBot.ini')
    if 'secret' in config:
            MY_API_KEY = config['secret']['MY_API_KEY']
            MY_MEMBER_ID = config['secret']['MY_MEMBER_ID']
    else:
            print('Rubrique "secret" non trouvée.')
            sys.exit(1)

    if 'groups' in config:
            GROUPS = config['groups']['NOM'].split()
    else:
            print('Rubrique "groups" non trouvée.')
            sys.exit(1)

    while True:
            try:
                    main()
            except:
                    pass
            finally:
                    time.sleep(SECOND_TIMER)