import os
import time
import requests
import logging
from dotenv import load_dotenv


load_dotenv()
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
SECONDS_TO_STAY_SILENCE = int(os.getenv("SECONDS_TO_STAY_SILENCE"))
HAMILTON_BOT_ID=os.getenv("SLACK_HAMILTON_BOT_ID")

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {os.getenv("SLACK_TOKEN")}'
}


def post_message_to_slack(text):
    slack_api_url = 'https://slack.com/api/chat.postMessage'

    payload = {
        'channel': CHANNEL_ID,
        'text': text,
    }
    response = requests.post(slack_api_url, headers=headers, json=payload)
    if response.status_code != 200:
        raise ValueError(
            f"Request to Slack returned an error {response.status_code}, "
            f"the response is: {response.text}")
    else:
        update_response = response.json()
        if not update_response['ok']:
            raise ValueError(
                f"Error from Slack API: {update_response['error']}")


def post_or_update_slack(text):
    try:
        # Step 1: Get all messages from the last minute
        slack_api_url = 'https://slack.com/api/conversations.history'
        params = {
            'channel': CHANNEL_ID,
            'limit':1
        }

        response = requests.get(slack_api_url, headers=headers, params=params)
        if response.status_code != 200:
            raise ValueError(
                f"Request to Slack returned an error {response.status_code}, "
                f"the response is: {response.text}")
        messages = response.json()
        if not messages['ok']:
            raise ValueError(f"Error from Slack API: {messages['error']}")

        # Step 2: Get the most recent message from the bot
        cur_message = [m for m in messages['messages'] if m.get('bot_id') == HAMILTON_BOT_ID][0]


        if float(cur_message['ts']) < time.time() - SECONDS_TO_STAY_SILENCE:
            post_message_to_slack(text)

        # Step 3: Update the most recent message by appending the input text
        slack_api_url = 'https://slack.com/api/chat.update'
        payload = {
            'channel': CHANNEL_ID,
            'ts': cur_message['ts'],
            'text': cur_message['text'] + "\n" + text
        }

        response = requests.post(slack_api_url, headers=headers, json=payload)
        if response.status_code != 200:
            raise ValueError(f"Request to Slack returned an error {response.status_code}, the response is: {response.text}")
        update_response = response.json()
        if not update_response['ok']:
            raise ValueError(f"Error from Slack API: {update_response['error']}")
        print("Message updated successfully")
    
    except Exception as e:
        # If any error occurs, post a new message
        post_message_to_slack(text)
