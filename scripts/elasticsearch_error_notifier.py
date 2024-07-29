# tool to continuously search Elasticsearch for a new error, and then push it to slack.
#/usr/bin/python3
# export PASSWORD='*******'
# rm elasticsearch_error_notifier.log;/usr/bin/python3 scripts/elasticsearch_error_notifier.py >> elasticsearch_error_notifier.log 2>&1 &
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from time import sleep
import logging
import urllib3
from scripts.slack import post_or_update_slack


# Configure logging
logging.basicConfig(filename='elasticsearch_error_notifier.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()


# Settings
SLEEP_BETWEEN_MESSAGES = 0.2
es_url = os.getenv("ELASTIC_SEARCH_URL")
es_index = os.getenv("ELASTIC_SEARCH_INDEX")
hours_ago = int(os.getenv("ERROR_LOOKBACK_HOURS", 3))  # Default to 3 if not specified
fetch_size = int(os.getenv("MAX_ERRORS_TO_SLACK_PER_RUN", 1))  # Default to 1 if not specified
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
sent_messages_list = set()


def get_es_query(hours, size):
    """Generates the Elasticsearch query."""
    start_time_str = (datetime.utcnow() - timedelta(hours=hours)).strftime('%Y-%m-%dT%H:%M:%S') + "Z"
    return {
        "query": {
            "bool": {
                "must": [
                    {"match": {"message": "Microlab"}},
                    {"match": {"message": "Abort error)"}}
                ],
                "filter": [{"range": {"@timestamp": {"gte": start_time_str}}}],
                "must_not": [{"exists": {"field": "sent"}}]
            }
        },
        "sort": [{"@timestamp": {"order": "desc"}}],
        "size": size
    }


def make_request(url, query):
    return requests.post(url,
                         json=query,
                         headers={"Content-Type": "application/json"},
                         auth=(username, password),
                         verify=False)  # This is equivalent to curl -k    


def query_elasticsearch(query):
    """Queries Elasticsearch and returns the result."""
    response = make_request(f"{es_url}/{es_index}/_search", query)
    return response.json()['hits']['hits'] if response.status_code == 200 else []


def post_to_slack_and_mark_as_sent(errors):
    for error in errors:
        post_or_update_slack(f"Error: {error['_source']['message']}")
        
        sent_messages_list.add(error['_id'])
        error_id = error['_id']
        cur_index = error['_index']
        update_response = make_request(f"{es_url}/{cur_index}/_update/{error_id}",
                                       {"doc": {"sent": True}})
        if update_response.status_code not in [200, 201]:
            print(f"Failed to mark document as sent in Elasticsearch: {update_response.text}")


def main():
    print(f"Starting the error notifier service with fetch size: {fetch_size}")
    try:
        # TODO use scheduler instead
        while True:
            try:
                errors = query_elasticsearch(get_es_query(hours_ago, fetch_size))
                new_errors = [e for e in errors if e['_id'] not in sent_messages_list]
                if new_errors:
                    post_to_slack_and_mark_as_sent(new_errors)
                    logging.info(f"Wrote {len(new_errors)} errors")
                
            except Exception as e:
                logging.error(f"Error during processing: {str(e)}")

            sleep(SLEEP_BETWEEN_MESSAGES)
    except KeyboardInterrupt:
        logging.info("Error notifier service interrupted by user.")
    

if __name__ == "__main__":
    main()
