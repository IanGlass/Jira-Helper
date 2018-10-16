#!/bin/bash

#Install PyQt5 required to run program
pip install PyQt5

#configure .netrc
#start with \n and create .netrc if it doesn't exist
#add '~' to .netrc for final version
echo >> .netrc

#Check for "machine value" before prompting for credentials
if grep -Fx "machine Jira-Credentials" .netrc
then
echo Credentials found
else
#write machine value configured in python script
#links which credentials to grab
echo "machine Jira-Credentials" >> .netrc

#grab and write account value
echo please enter your Jira URL
read urlVar 
echo account $urlVar >> .netrc

#grab and write login
echo please enter you Jira username/email address
read userName
echo login $userName >> .netrc

#grab and write API key
echo please enter your Atlassian API key
read apiKey
echo password $apiKey >> .netrc

fi

#Check for configured project name, if none then prompt and save
file_content=$(head -c 11 source/Jira-Issue-Board.py)
if [[ $file_content = 'projectName' ]]
then
echo project name found
else
echo please enter your project name
read projectName
#write the projectName to the first line 
sed -i "1 i\projectName = \"$projectName\"" source/Jira-Issue-Board.py
echo project name added to module
fi

#Run program as a thread so script can close itself
python source/Jira-Issue-Board.py &
