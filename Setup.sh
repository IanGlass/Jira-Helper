#!/bin/bash

pip install flask

#configure .netrc
#start with \n and create .netrc if it doesn't exist
#add '~' to .netrc for final version
echo >> .netrc
#write machine value configured in pyhon script
#links which credentials to grab
echo "machine Jira-Credentials" >> .netrc

#grab and write account value
echo please enter your Jira URL
read urlVar 
echo account $urlVar >> .netrc

#grab and write login
echo please enter you Jira username
read userName
echo login $userName >> .netrc

#grab and write API key
echo please enter your Jira API key
read apiKey
echo password $apiKey >> .netrc