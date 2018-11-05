#!/bin/bash

#Install psql in linux

#Install python in linux

#Install latest version of pip package manager
python -m pip install --upgrade pip

#Install PyQt5 required to run program
pip install PyQt5

#Install JIRA API for Python
pip install jira

#Install for postgresql
pip install psycopg2

#install matplotlib required to plot in analytics board
python -m pip install -U matplotlib

#Check for "machine value" before prompting for credentials
if grep -Fxq "machine Jira-Credentials" ~/.netrc
then
echo Credentials found
else
#write machine value configured in python script
#links which credentials to grab
echo "machine Jira-Credentials" >> ~/.netrc

#grab and write account value
echo please enter your Jira URL
read urlVar 
echo account $urlVar >> ~/.netrc

#grab and write login
echo please enter you Jira username/email address
read userName
echo login $userName >> ~/.netrc

#grab and write API key
echo please enter your Atlassian API key
read apiKey
echo password $apiKey >> ~/.netrc

fi

#Can remove these assuming user has status' outlined in README.md
#No longer using project name var in module, project assumes that everything works on status
#Check for configured project name, if none then prompt and save
file_content=$(head -c 21 source/jira_ticket_board.py)
if [[ $file_content = 'SUPPORT_TICKET_STATUS' ]]
then
echo project status names found
else
echo please enter the status name of tickets waiting for support
read supportStatus
#write the board ticket status to the second line 
sed -i "1 i\SUPPORT_TICKET_STATUS = \"$supportStatus\"" source/jira_ticket_board.py

echo please enter the status name of tickets waiting for customer
read customerStatus
#write the queue ticket status to the third line 
sed -i "2 i\CUSTOMER_TICKET_STATUS = \"$customerStatus\"" source/jira_ticket_board.py

echo please enter the status name of tickets in progress
read inProgressStatus
#write the queue ticket status to the third line 
sed -i "3 i\IN_PROGRESS_TICKET_STATUS = \"$inProgressStatus\"" source/jira_ticket_board.py

echo please enter the status name of tickets in development
read devStatus
#write the queue ticket status to the third line 
sed -i "4 i\DEV_TICKET_STATUS = \"$devStatus\"" source/jira_ticket_board.py

echo please enter the status name of tickets in design
read inProgressStatus
#write the queue ticket status to the third line 
sed -i "5 i\DESIGN_TICKET_STATUS = \"$inProgressStatus\"" source/jira_ticket_board.py

echo please enter the status name of tickets test
read testStatus
#write the queue ticket status to the third line 
sed -i "6 i\TEST_TICKET_STATUS = \"$testStatus\"" source/jira_ticket_board.py


fi

#Change to use python flags
echo Would you like to run a cleanup of the \'waiting on customer queue\'?
read reply
if [[ $reply == y ]]
then 
echo please enter the ticket number of a sample ticket in the project
read sampleTicket
#write the sample ticket name to the fourth line
sed -i '7d' source/jira_ticket_board.py
sed -i "7 i\SAMPLE_TICKET = \"$sampleTicket\"" source/jira_ticket_board.py
else
sed -i '7d' source/jira_ticket_board.py
sed -i "7 i\SAMPLE_TICKET = \"\"" source/jira_ticket_board.py
fi

#Run program as a thread so script can close itself
python source/jira_ticket_board.py &

