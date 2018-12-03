# Raspi-Jira-Display-Board
This project uses the MVC design pattern and assumes the user is using the following Jira workflow:

To run the program, please run the Jira-Helper.sh script
## Display Boards
Provides three dashboards:
1). Displays overdue tickets waiting on support staff, either in black, red or flashing red. The time until a ticket becomes overdue can be configured in the settings panel.
2). Displays the current number of tickets:
* Waiting on support staff
* Waiting on response from the customer
* In progress
* In the development
* In design
* In test and waiting release 
3). Displays current build tickets with the suffix of '-1' in one of three stages:
* In development
* In design
* In test and waiting release

## Automated Cleanup
The program can also perform automated cleanup in the background. An automated message (user defined) is sent to waiting on customer tickets which have not had a reply for longer than a user defined period. This function can be toggled with the 'Clean Queue' button. The ticket is then set to 'Resolved' unless the customer replied, in which case it returns to the waiting on support queue. The transition to resolve tickets must be named 'Resolve this issue' for this functionality to work.

##User Configuration
The user must provide the following information which can be entered into the 'Settings' tab:
* The Jira project URL
* The Jira user as an email address
* The user API key
* The status names for each of the 7 queues
* An automated message

## Development
The following dependencies are automatically installed when running the Jira-Helper.sh script:



This project uses pycodestyle added to the git pre-commit hooks.

*Add to README*
* Flow diagram of software workflow
* Flow diagram of expected jira and staff workflow to make most of project
* Video of software in action
* Block descriptions of code
* Setup instructions to get running on a raspberry pi 3B
* Section on manually accessing the PSQL DB

development board will populate with dev tickets first, then design then test if there is space
Some defaults exist for clean queue delay and automated message


