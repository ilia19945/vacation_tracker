# 🐍 Django Vacation tracker (admin-based) application

The database is created along with all necessary data. 

The purpose of the application is:
1. To allow Agents to submit and keep tracking their vacation requests as well as to be able to see how many vacation days left they have by current date
2. To give Supervisors and Managers to be the ability to review and approve/deny agents' requests
3. To provide access to HR team the infrormation about the overall list of agents and their vacation submissions to be able to communicate and perform their own tasks.


# 🏃‍♂️ How to run project: 

- Install requirements using ```pip install -r requirements.txt```
- Use to run the sample project the standard command ```python manage.py runserver```
- Go to ```http://127.0.0.1:8000/admin/``` and use ```admin:admin``` to login to admin console  
--------------------------------------------------
# 🤔 How to use the app: 
* Feel free to log in using the superuser to inspect groups and users sections of vacation tracker yourself. 

The example of structure consists of a few core roles and is shown below:
Example Org. Structure:  
  - **CEO** (is supposed to see the list of employees, assigned with the **Leadership** group)
    - SV1 (assigned to **Supervisors** group):
        - agent1
        - agent2
    - SV2 (assigned to **Vacation tracker** group):
        - agent3
        - agent4
        
-	itSupportAgent - they have access to the whole list of employees to be able to troubleshoot/investigate issues 
- peopleTeamUser - HR department user - suppose to have full access to every site section


# 🧠 Business logic of the app:
* . When the new hire is coming to the company:
  - **itSupportAgent** is responsible to ensure the account is created and the necessary groups are assigned (Vacation tracker is an essential group that gives access to employee's vacation days left and to submit vacation requests)
  - The **peopleTeamUser** is responsible to add the new hire to the Employees list and to make sure the Employees information provided is correct (especially: **Start date, Supervisor and Extra Supervisors**) as well as setting the **end date** when the existing employee is terminated.
    - In order to prevent the private infromation about the employees to be available to everyone who has access to Emplyees a custom logic is applied:  
      - the Supervisor can only see employees and vacation submissions from employees he / she supervises. 
 
* When the Agent, Supervisor, CEO, etc are going to go on the vacation:
  - He/she adds a new vacation request specifying the start date, end-date, and the reason (optionally) under the **"My Vacation Requests"** section.  

* When the agent submitted the vacation request :
  - His supervisor sees this request on **"My employees vacations submissions (Supervisor View)"** section and can:
    - adjust requested dates and other info
    - leave public notes to communicate with the employee.
    - change the request status (Initial -> In Progress -> Approved / Rejected)    
      
* After the vacation submission swithed to  **Approved** or **Rejected** status -> all fields become viewonly for Agent and for SV (except **Status** field for **SV**).  
  * An additional functionality removed from this project(but existed in the private corp project) - the notification is being sent to the employee notifying him / her that the vacation request has been approved. 


Also the validations steps intended to prevent 'negative dates' submissions (when 'end date' is earlier than 'start date') or submissions by hires currently not being added to the "Employees" list and the quick view for the amount of vacation days left is added to /add page

In order to invent the business logic - the permission to approve or to deny vacation request is added separately and is assigned only to **Supervisors** - "Can approve vacations". 
Additional request was to let CEO and Leadership team to be able to approve their own vacation submissions - therefore **Leadership** group has been created and a custom permissions **"Can approve myself vacation"** as has been added.
