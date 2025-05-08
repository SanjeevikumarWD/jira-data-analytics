Jira Ticket Analytics Pipeline
Overview
This project implements an ETL pipeline to process and analyze mock Jira ticket data, mimicking real-world data engineering tasks for Atlassian’s Jira platform. The pipeline extracts data from a public API, transforms it into a star schema for efficient analytics, loads it into a PostgreSQL database, and generates insights through advanced SQL queries. The project demonstrates proficiency in Python, SQL, data modeling, and ETL pipeline design, making it relevant for data engineering roles.
Features

Extract: Fetches mock Jira ticket data from the JSONPlaceholder API.
Transform: Cleans and enriches data using Pandas (e.g., deduplication, date calculations, priority/project assignments).
Load: Stores data in a PostgreSQL database with a star schema (fact and dimension tables).
Analyze: Runs complex SQL queries for ticket aging, user productivity, priority distribution, and creation trends.
Error Handling: Includes robust try-except blocks for database operations.

Tech Stack

Python 3.8+: For ETL scripting and data manipulation.
Pandas: For data transformation and aggregation.
PostgreSQL: For data storage and analytics.
psycopg2: For PostgreSQL connectivity.
requests: For API data extraction.

Star Schema
The data is organized into a star schema to optimize analytical queries:

Fact Table:
fact_tickets: Stores ticket details (ticket_id, user_id, project_id, priority_id, status, created_date, resolution_date, resolution_days).


Dimension Tables:
dim_users: User metadata (user_id, user_name).
dim_projects: Project metadata (project_id, project_name: Jira, Confluence).
dim_priorities: Priority metadata (priority_id, priority_name: High, Medium, Low).


Summary Table:
ticket_summary: Aggregated metrics (ticket_count, avg_resolution_days by project, status, priority).



Prerequisites

PostgreSQL: Installed and running locally (version 12+ recommended).
Python Packages: Install via pip:pip install pandas psycopg2-binary requests


Database Setup: Create a PostgreSQL database named jira_db.

Setup

Clone the Repository:git clone <repository-url>
cd jira-ticket-analytics


Configure PostgreSQL:
Ensure PostgreSQL is running.
Update the connection details in the script (user, password, host, port, database) to match your setup.
Example:conn = psycopg2.connect(
    user="postgres",
    password="your_password",
    host="127.0.0.1",
    port="5432",
    database="jira_db"
)




Install Dependencies:pip install -r requirements.txt

(Create requirements.txt with: pandas, psycopg2-binary, requests.)
Run the Script:python jira_pipeline.py



Usage

The script executes the ETL pipeline and prints analytical results:
Ticket Aging Analysis: Counts open tickets older than 30 days by project.
User Productivity: Ranks users by average resolution days for closed tickets.
Priority Distribution: Shows ticket counts by project, priority, and status.
Monthly Trends: Tracks ticket creation by project and month.


Output is displayed in the console, and data is stored in the jira_db database for further querying.

Sample Output
Connected to PostgreSQL
1. Ticket Aging Analysis (Open > 30 days):
[('Jira', 10), ('Confluence', 8)]

2. User Productivity (Rank by Avg Resolution):
[('User_101', 5, 12.5, 1), ('User_102', 3, 15.0, 2)]

3. Priority Distribution by Project:
[('Jira', 'High', 'Open', 20), ('Jira', 'Medium', 'Closed', 15), ...]

4. Monthly Ticket Creation Trends:
[('Jira', 2025, 1, 50), ('Confluence', 2025, 2, 30), ...]


PostgreSQL connection closed.

Project Structure
jira-ticket-analytics/
├── jira_pipeline.py      # Main ETL and analytics script
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation


Future Improvements

Add PySpark for big data processing (e.g., aggregate tickets at scale).
Integrate Airflow for scheduling the pipeline.
Store data in a cloud warehouse (e.g., AWS Redshift) for production use.

Author
Sanjeevikumar Aspiring Data Engineer passionate about building efficient data pipelines.
