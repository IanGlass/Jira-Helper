# Raspi-Jira-Display-Board

This project consists of two parts: 
A shellscript to:
* Install project dependencies;
* Configure the Jira API key (saved in ~/.netrc) which is used to pull tickets into the Python module;
* Save the Jira project name which tickets are pulled from

A Python module to display overdue tickets using PyQt and perform 'silent' actions on tickets in the background.

Future features:
* Throw 3 day old "waiting on customer" tickets back into support
* Alert for new/unassigned tickets within 1 hour of coming in
