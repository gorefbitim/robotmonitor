# robot-monitor
Maintain datalake to monitor robot real time situation

# Project Setup Instructions

## Project Overview

This project aims to connect robot logs to the internet, ensuring comprehensive
log management and instant error notification. The objectives include:
- Saving all logs in a NoSQL data store.
- Generating instant messages upon detecting errors.

We achieve this through four main steps:
1. Configure Slack for notifications.
2. Configure folder sharing from the robot to a Linux system.
3. Install and configure the Elastic Stack (ELK).
4. Run the Python service to handle logs and notifications.

## Step-by-Step Instructions

##########################
### 1. Configure Slack ###
##########################
# Slack Configuration for Notifications

This section guides you through setting up Slack to receive instant messages
when errors are detected in robot logs. Follow the steps below to create and
configure a Slack app, which will allow you to send notifications directly
to your chosen Slack channel.

## Step 1.1: Create and Configure a Slack App

1. **Create a Slack App:**
   - Navigate to [Slack API](https://api.slack.com/apps) and
     click on "Create New App." (you need to sign in first).
   - Select "From scratch," name your app, and choose the Slack workspace
     where notifications will be sent.
   - Click "Create App."

2. **Set Permissions:**
   - Go to "OAuth & Permissions" (left side, under Features)
   - Scroll down to "Scopes" and click "Add an OAuth Scope."
   - Add the following scopes to enable message sending and channel reading:
     - `chat:write`
     - `channels:read`
     - `groups:read`
     - `im:read`
     - `mpim:read`
     - `channels:history`
     - `conversations.connect:read`
     - `incoming-webhook`
   - Scroll back up to "Install to Workspace" (green) to generate and obtain the
     OAuth Access Token, which will be used to authenticate API requests.
   - Create a configuration file named .env with the following line:
       SECONDS_TO_STAY_SILENCE=3
     SLACK_TOKEN=xoxb-******

3. Incoming Webhook Setup (Optional)
   You can skip this step. It allows another method to post to slack, called
   webhook. Webhook is simpler, but with a limited functionality.
   - In the app settings, select "Incoming Webhooks" from the sidebar.
   - Toggle the activation switch to "On."
   - Click "Add New Webhook to Workspace" and select the channel where you want
     to receive notifications.
   - Copy the generated Webhook URL, which will be used in your Python script
     to send messages.

## Step 1.2: Find Your Slack Channel ID

1. **Locate Channel ID:**
  - Open your Slack workspace in a browser.
  - Navigate to the channel where notifications should appear.
  - The URL will include the Channel ID at the end, e.g.,
    `https://app.slack.com/client/T00000000/C00000000` — `C00000000`
    is your Channel ID.
  - Add to .env the following line:
    SLACK_CHANNEL_ID=C***

2. **Invite the bot to the channel.**
   Go to your Slack Channel and type the following as a message.
   /invite @bot-name

3. Test
   pip install -r requirements.txt
   python tests/test_slack_bot.py

##########################
### 2. Folder Sharing  ###
##########################

## On the Computer connected to the robot:

1. **Navigate to the Logs Folder:**
   - Go to c:\Program Files (x86)\Hamilton\

2. **Configure Sharing:**
   - Right-click the `Logs` folder and select `Properties`.
   - Switch to the `Sharing` tab and click on `Advanced Sharing`.
   - Check `Share this folder`. Set the share name, for instance, `RobotLogs`.
   - Click on `Permissions` and ensure that you grant 'Read' or 'Full Control'
     permissions, depending on the required level of access.
   - Confirm all settings by clicking `OK`.

3. **Note the Network Path:**
   - The shared folder's network path will typically look
   like `\\YOUR-PC-NAME\RobotLogs`.
   Ensure to note this path as it will be used for mounting the folder on
   Ubuntu.

## On Ubuntu:
1. install cifs
   sudo apt-get install cifs-utils

2. Create the folder for sharing
   sudo mkdir /var/log/shared_logs

3. Mount temporarily:
   Use the following command to mount the Windows shared folder to the mount point you created:

   sudo mount -t cifs -o username=YOUR_WINDOWS_USERNAME,password=YOUR_WINDOWS_PASSWORD,iocharset=utf8,noperm //YOUR-PC-NAME/RobotLogs /var/log/shared_logs

4. Configure Persistent Mounting
   Add the following line to /etc/fstab (you can use emacs/nano/vi)
//YOUR-PC-NAME/RobotLogs /var/log/shared_logs cifs username=YOUR_WINDOWS_USERNAME,password=YOUR_WINDOWS_PASSWORD,iocharset=utf8,noperm 0 0

5. remount:
   sudo mount -a

#######################
### 3. Install ELK  ###
#######################
Installtion of the ElasticSearch,Kibana,Logstash is out of the scope of this repo.
You can use paid services such as https://logz.io/, https://www.elastic.co/,
https://aws.amazon.com/opensearch-service/ or dare to install it yourself !
See e.g. here for the last option:
https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-elastic-stack-on-ubuntu-22-04

I have provided in this repo a logstash configution file
scripts/logstash.conf

To load all log files into Elasticsearch.
Make sure to update the user and password in the relevant section.

##############################
# 4. run the notifier script #
##############################
nohup python3 scripts/elasticsearch_error_notifier.py >> elasticsearch_error_notifier.log 2>&1 &


## References

- For a comprehensive guide on Slack APIs and further configuration details,
  visit the [Slack API Documentation](https://api.slack.com/start).
- For specifics on message sending methods, see
  [Sending Messages on Slack](https://api.slack.com/messaging/sending).

## Note

With the above setup, your project can send real-time notifications to a
Slack channel, enhancing the monitoring system's responsiveness to issues.
Depending on your preference and requirement, choose between using the API
for complex interactions or Webhooks for straightforward message sending.

