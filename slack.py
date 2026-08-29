#!/usr/bin/env python3

import os, datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class Slack:

    def __init__(self):
        self.client = None

    def get_channel_id(self, channel_name):
        response = self.client.conversations_list()
        for result in response:
            for channel in result['channels']:
                if channel_name in channel['name']:
                    return channel['id']
        return None

    def connect(self,token=None):
        try:
            self.client = WebClient(token=token)
        except Exception as e:
            print(e)
            assert e.response["error"]

    def get_user_id(self,name):
        try:
            cursor = None
            Done = False
            while not Done:
                response = self.client.users_list(cursor=cursor,limit=100)
                for result in response['members']:
                    if result['name'] == name:
                        Done = True
                        user_id = result['id']
                        user_name = result['name']
                        return user_id
                if not Done and 'response_metadata' in response and 'next_cursor' in response['response_metadata']: cursor = response['response_metadata']['next_cursor']
        except SlackApiError as e:
            print(e)
            assert e.response["error"]
        return None

    def postMessage(self,id,message):
        try:
            response = self.client.chat_postMessage(channel=id, text=message)
            return response
        except SlackApiError as e:
            print(e)
            assert e.response["error"]
        return None

    def update(self,ts,id,message):
        try:
            response = self.client.chat_update(ts=str(ts), channel=id, text=message)
            return response
        except SlackApiError as e:
            print(e)
            assert e.response["error"]
        return None

    def conversations_history(self,id,oldest):
        try:
            response = self.client.conversations_history(channel=id, oldest=oldest)
            return response
        except SlackApiError as e:
            print(e)
            assert e.response["error"]
        return None

    def users_info(self,user):
        try:
            response = self.client.users_info(user=user)
            return response
        except SlackApiError as e:
            print(e)
            assert e.response["error"]
        return None

if __name__ == "__main__":
    client = Slack()
    client.connect(token)
    #user_id = client.get_user_id('dan.campbell')
    #print(user_id)
    channel_id = client.get_channel_id('test-printer-tickets')
    print(channel_id)
    #client.postMessage(user_id,str(datetime.datetime.now()))
    client.postMessage(channel_id,str(datetime.datetime.now()))

