# Raspi-Jira-Display-Board

Provides a dashboard to display overdue tickets, with overdue tickets displayed in black text, older tickets displayed as flashing red and oldest displayed as solid red text

Display the current number of tickets in each project and on the Dev kanban board

A secondary module performs background cleanup of old tickets waiting on a response from the customer.
Sends an automated follow up message to the client after 7 days of no response. Currently, the program will send tickets with an automated message as the last comment and older than 7 days (last updated will be reset when the first automated message is sent) to a 'cold queue' to be manually processed by a human.
Button in Jira to send to 'cold queue' will need to be named "Respond to support" for this to work, transition id is dynamically fetched

In future, this will be changed so that tickets are resolved as soon as the automated message is sent, rather than being sent to a cold queue



This project assumes that your setup uses the following status':
* waiting on support
* waiting on customer
* in progress
* dev
* design
* test

This project consists of two parts: 
A shellscript to:
* Install project dependencies (PyQt, JIRA Python);
* Configure the Jira API key (saved in ~/.netrc) which is used to pull tickets into the Python module;
* Save the Jira project name which tickets are pulled from

A Python module to display overdue tickets using PyQt and perform 'silent' actions on tickets in the background.

Future features:
* Throw 3 day old "waiting on customer" tickets back into support
* Alert for new/unassigned tickets within 1 hour of coming in
* Flow diagram for app build tickets moving through the workflow
* Save ticketing statistics by the hour into a local db which will be used for graphing analytics



psql ticketdb to access db
select * from ticket_stats;
timedate is stored in UTC and converted to local in python script

add model language diagram
add intended workflow for jira helper and support staff


Add display for current SLAs, SLA will need to be named 'Time to first response'

