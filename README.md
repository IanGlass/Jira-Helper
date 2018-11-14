# Raspi-Jira-Display-Board



Review code naming convention


Provides a dashboard to display overdue tickets, with overdue tickets displayed in black text, older tickets displayed as flashing red and oldest displayed as solid red text

Display the current number of tickets in each project and on the Dev kanban board

A secondary module performs background cleanup of old tickets waiting on a response from the customer.
Sends an automated follow up message to the client after 7 days of no response. Currently, the program will send tickets with an automated message as the last comment and older than 7 days (last updated will be reset when the first automated message is sent) to a 'cold queue' to be manually processed by a human.
Button in Jira to send to 'cold queue' will need to be named "Respond to support" for this to work, transition id is dynamically fetched

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

This project uses pycodestyle and python unittest added to the git pre-commit hooks.

A Python module to display overdue tickets using PyQt and perform 'silent' actions on tickets in the background.

*Add to README*
* Flow diagram of software workflow
* Flow diagram of expected jira and staff workflow to make most of project
* Video of software in action
* Block descriptions of code
* Setup instructions to get running on a raspberry pi 3B
* Section on manually accessing the PSQL DB

psql ticketdb to access db
select * from ticket_stats;
timedate is stored in UTC and converted to local in python script

Analytics board will take up to 5 mins to start populating after correct credentials are entered
 



