# Raspi-Jira-Display-Board

Provides a dashboard to display overdue tickets, with overdue tickets displayed in black text, older tickets displayed as flashing red and oldest displayed as solid red text


A secondary module performs background cleanup of old tickets waiting on a response from the customer.
Amends '(follow up with client)' to start of summary.
This is performed in update board class so that the background thread closes when the board is closed
Button to respond to support will need to be named "Respond to support" for this to work

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
