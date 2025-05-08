import pandas as pd
import requests
import psycopg2
from psycopg2 import Error
from datetime import datetime, timedelta
import random

# Set up PostgreSQL connection
try:
    conn = psycopg2.connect(
        user="postgres",
        password="password",
        host="127.0.0.1",
        port="5432",
        database="jira_db"
    )
    cursor = conn.cursor()
    print("Connected to PostgreSQL")

    # Create star schema tables
    cursor.execute("""
        DROP TABLE IF EXISTS fact_tickets;
        DROP TABLE IF EXISTS dim_users;
        DROP TABLE IF EXISTS dim_projects;
        DROP TABLE IF EXISTS dim_priorities;
        DROP TABLE IF EXISTS ticket_summary;
        CREATE TABLE dim_users (
            user_id INTEGER PRIMARY KEY,
            user_name VARCHAR(100)
        );
        CREATE TABLE dim_projects (
            project_id INTEGER PRIMARY KEY,
            project_name VARCHAR(100)
        );
        CREATE TABLE dim_priorities (
            priority_id INTEGER PRIMARY KEY,
            priority_name VARCHAR(50)
        );
        CREATE TABLE fact_tickets (
            ticket_id INTEGER PRIMARY KEY,
            user_id INTEGER REFERENCES dim_users(user_id),
            project_id INTEGER REFERENCES dim_projects(project_id),
            priority_id INTEGER REFERENCES dim_priorities(priority_id),
            ticket_title VARCHAR(255),
            status VARCHAR(50),
            created_date DATE,
            resolution_date DATE,
            resolution_days INTEGER
        );
        CREATE TABLE ticket_summary (
            project_id INTEGER,
            status VARCHAR(50),
            priority_id INTEGER,
            ticket_count INTEGER,
            avg_resolution_days FLOAT,
            PRIMARY KEY (project_id, status, priority_id)
        );
    """)
    conn.commit()

    # Extract: Fetch mock Jira data and enrich
    response = requests.get('https://jsonplaceholder.typicode.com/todos')
    data = response.json()
    df = pd.DataFrame(data)

    # Transform: Clean and enrich data
    df = df.rename(columns={'id': 'ticket_id', 'userId': 'user_id', 'title': 'ticket_title'})
    df['status'] = df['completed'].map({True: 'Closed', False: 'Open'})
    df = df.drop_duplicates(subset=['ticket_id'])
    df['status'] = df['status'].fillna('Unknown')
    df['created_date'] = pd.to_datetime('2025-01-01') + pd.to_timedelta(df['ticket_id'] % 120, unit='D')
    df['resolution_date'] = df.apply(
        lambda x: x['created_date'] + timedelta(days=random.randint(1, 60)) if x['status'] == 'Closed' else None, 
        axis=1
    )
    df['resolution_days'] = df.apply(
        lambda x: (x['resolution_date'] - x['created_date']).days if x['status'] == 'Closed' else None, 
        axis=1
    )
    df['priority_id'] = df['ticket_id'].apply(lambda x: (x % 3) + 1)  # 1: High, 2: Medium, 3: Low
    df['project_id'] = df['ticket_id'].apply(lambda x: (x % 2) + 1)   # 1: Jira, 2: Confluence
    df['user_name'] = df['user_id'].apply(lambda x: f"User_{x}")
    df['project_name'] = df['project_id'].map({1: 'Jira', 2: 'Confluence'})
    df['priority_name'] = df['priority_id'].map({1: 'High', 2: 'Medium', 3: 'Low'})

    # Create dimension DataFrames
    dim_users = df[['user_id', 'user_name']].drop_duplicates().reset_index(drop=True)
    dim_projects = df[['project_id', 'project_name']].drop_duplicates().reset_index(drop=True)
    dim_priorities = df[['priority_id', 'priority_name']].drop_duplicates().reset_index(drop=True)

    # Aggregate for summary
    summary = df.groupby(['project_id', 'status', 'priority_id']).agg(
        ticket_count=('ticket_id', 'size'),
        avg_resolution_days=('resolution_days', 'mean')
    ).reset_index()
    summary['avg_resolution_days'] = summary['avg_resolution_days'].fillna(0)

    # Load: Save to PostgreSQL
    for _, row in dim_users.iterrows():
        cursor.execute("""
            INSERT INTO dim_users (user_id, user_name)
            VALUES (%s, %s)
        """, (row['user_id'], row['user_name']))
    for _, row in dim_projects.iterrows():
        cursor.execute("""
            INSERT INTO dim_projects (project_id, project_name)
            VALUES (%s, %s)
        """, (row['project_id'], row['project_name']))
    for _, row in dim_priorities.iterrows():
        cursor.execute("""
            INSERT INTO dim_priorities (priority_id, priority_name)
            VALUES (%s, %s)
        """, (row['priority_id'], row['priority_name']))
    for _, row in df[['ticket_id', 'user_id', 'project_id', 'priority_id', 'ticket_title', 'status', 'created_date', 'resolution_date', 'resolution_days']].iterrows():
        cursor.execute("""
            INSERT INTO fact_tickets (ticket_id, user_id, project_id, priority_id, ticket_title, status, created_date, resolution_date, resolution_days)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (row['ticket_id'], row['user_id'], row['project_id'], row['priority_id'], row['ticket_title'], row['status'], row['created_date'], row['resolution_date'] if pd.notnull(row['resolution_date']) else None, row['resolution_days'] if pd.notnull(row['resolution_days']) else None))
    for _, row in summary.iterrows():
        cursor.execute("""
            INSERT INTO ticket_summary (project_id, status, priority_id, ticket_count, avg_resolution_days)
            VALUES (%s, %s, %s, %s, %s)
        """, (row['project_id'], row['status'], row['priority_id'], row['ticket_count'], row['avg_resolution_days']))
    conn.commit()

    # Analyze: Complex analytics queries
    print("1. Ticket Aging Analysis (Open > 30 days):")
    cursor.execute("""
        SELECT p.project_name, COUNT(*) as aged_tickets
        FROM fact_tickets t
        JOIN dim_projects p ON t.project_id = p.project_id
        WHERE t.status = 'Open'
        AND CURRENT_DATE - t.created_date > 30
        GROUP BY p.project_name
        ORDER BY aged_tickets DESC
    """)
    print(cursor.fetchall())

    print("\n2. User Productivity (Rank by Avg Resolution):")
    cursor.execute("""
        SELECT u.user_name, 
               COUNT(t.ticket_id) as total_tickets,
               AVG(t.resolution_days) as avg_resolution_days,
               RANK() OVER (ORDER BY AVG(t.resolution_days) ASC) as resolution_rank
        FROM fact_tickets t
        JOIN dim_users u ON t.user_id = u.user_id
        WHERE t.status = 'Closed'
        GROUP BY u.user_name
        HAVING COUNT(t.ticket_id) > 1
        ORDER BY resolution_rank
        LIMIT 5
    """)
    print(cursor.fetchall())

    print("\n3. Priority Distribution by Project:")
    cursor.execute("""
        SELECT p.project_name, pr.priority_name, t.status, COUNT(*) as ticket_count
        FROM fact_tickets t
        JOIN dim_projects p ON t.project_id = p.project_id
        JOIN dim_priorities pr ON t.priority_id = pr.priority_id
        GROUP BY p.project_name, pr.priority_name, t.status
        ORDER BY p.project_name, pr.priority_name, t.status
    """)
    print(cursor.fetchall())

    print("\n4. Monthly Ticket Creation Trends:")
    cursor.execute("""
        SELECT p.project_name, 
               EXTRACT(YEAR FROM t.created_date) as year,
               EXTRACT(MONTH FROM t.created_date) as month,
               COUNT(*) as ticket_count
        FROM fact_tickets t
        JOIN dim_projects p ON t.project_id = p.project_id
        GROUP BY p.project_name, EXTRACT(YEAR FROM t.created_date), EXTRACT(MONTH FROM t.created_date)
        ORDER BY p.project_name, year, month
    """)
    print(cursor.fetchall())

except (Exception, Error) as error:
    print("Error with PostgreSQL:", error)

finally:
    if conn:
        cursor.close()
        conn.close()
        print("PostgreSQL connection closed.")