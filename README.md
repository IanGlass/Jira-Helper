# Raspi-Jira-Display-Board
This project uses the MVC design pattern and assumes the user is using the following Jira workflow:

To run the program, please run the Jira-Helper.sh script, which will install all dependencies and launch the program.
## Display Boards
Three dashboards are currently available, which can be disabled/enabled from the *Settings* tab. The boards are automatically cycled every 15 seconds:

1). Displays overdue tickets waiting on support staff, either in black, red or flashing red. The time until a ticket becomes overdue can be configured in the settings panel.
2). Displays the current number of tickets:
* Waiting for support staff
* Waiting for response from the customer
* In progress
* In the development
* In design
* In test and waiting release 
This board also displays a timeline of ticket history for waiting for support, waiting for customer and in progress tickets. *NOTE* Ticket history is saved every 5 minutes and will take up to 5 minutes to begin populating after valid credentials are provided.
3). Displays current build tickets with the suffix of *-1* in one of three stages:
* In development
* In design
* In test and waiting release
The board will populate with dev tickets first, then design then test tickets with a capacity of 20 tickets.

## New Tickets
A new ticket window will pop up when a new ticket is received into the support queue, however the program only searches for tickets which were received less than 15 seconds ago. The ticket key, summary and reporter are displayed for 15 seconds before the window closes itself.

## Automated Cleanup
The program can also perform automated cleanup in the background. An automated message (user defined) is sent to waiting on customer tickets which have not had a reply for longer than a user defined period. This function can be toggled with the *Clean Queue* button. The ticket is then set to *Resolved* unless the customer replies, in which case it returns to the waiting on support queue. The transition to resolve tickets must be named *Resolve this issue* for this functionality to work.

## User Configuration
The user must provide the following information which can be entered into the *Settings* tab:

* The Jira project URL
* The Jira user as an email address
* The user API key
* The status names for each of the 7 queues
* An automated message

## Development
The following dependencies are automatically installed when running the Jira-Helper.sh script:

* pip package manager - Required to install other dependencies
* PyQt5 - The main framework used by this application and heavily relied upon for the GUI. Also used to store settings via a QSettings obj and to perform threading.
* jira - A library used to fetch and manipulate Jira issues
* pycodestyle - Checks for coding style as a pre-commit hook. The pre-commit hooks are created by the jira-helper.sh script
* matplotlib - Used to plot two week analytics of support, customer and in progress tickets
* SQLAlchemy - ORM used to manipulate the SQLite DB, which stores ticket history collected by the jira_service module
* pysqlite3 - Connector for SQLAlchemy to connect to the SQLite DB

To clean the ticket history in the DB:
* Download SQLite
* Create an alias for SQLite CLI command
* Connect to DB using *SQLite jira-helper.db*
* Run *delete from ticket_history;*
* Run *.exit*



TODO

*Add to README*
* Flow diagram of software workflow
* Flow diagram of expected jira and staff workflow to make most of project
* Video of software in action
* Block descriptions of code
* Setup instructions to get running on a raspberry pi 3B
* Section on manually accessing the PSQL DB


