from jira import JIRA
from tkinter import Tk, Label, Button
from datetime import datetime
from dateutil import parser
import netrc

secrets = netrc.netrc()
username,account,password = secrets.authenticators('Jira-Credentials')  

#Create a JIRA object using netrc credentials
jira = JIRA(basic_auth=(username,password), options={'server': account})

print('project=Wherewolf\ Support AND status=Waiting\ For\ Support')
print("Tickets overdue") 
delayLimit = 86400 #(seconds) search tickets which are older than a day
for issue in jira.search_issues('project=Wherewolf\ Support AND status=Waiting\ For\ Support', maxResults=10):
    date = datetime.now() #get current date
    ticket_date = parser.parse(issue.fields.updated[0:23]) #truncate and convert string to datetime obj
    diff = (date - ticket_date).total_seconds()
    if diff > delayLimit:
        print('Ticket Number:{}, Summary:{}, Assignee:{}, Updated:{}'.format(issue.key, issue.fields.summary, issue.fields.assignee, issue.fields.updated))


