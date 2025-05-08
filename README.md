# 📊 Jira Ticket Analytics Pipeline

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-1.0+-150458?style=for-the-badge&logo=pandas&logoColor=white)

*A data engineering project that extracts, transforms, and analyzes mock Jira ticket data*

</div>

## 🌟 Overview

This project implements an ETL pipeline to process and analyze mock Jira ticket data, mimicking real-world data engineering tasks for Atlassian's Jira platform. The pipeline extracts data from a public API, transforms it into a star schema for efficient analytics, loads it into a PostgreSQL database, and generates insights through advanced SQL queries.

## ✨ Features

- **Extract**: Fetches mock Jira ticket data from the JSONPlaceholder API
- **Transform**: Cleans and enriches data using Pandas (deduplication, date calculations, priority/project assignments)
- **Load**: Stores data in a PostgreSQL database with a star schema (fact and dimension tables)
- **Analyze**: Runs complex SQL queries for ticket aging, user productivity, priority distribution, and creation trends
- **Error Handling**: Includes robust try-except blocks for database operations

## 🛠️ Tech Stack

- **Python 3.8+**: For ETL scripting and data manipulation
- **Pandas**: For data transformation and aggregation
- **PostgreSQL**: For data storage and analytics
- **psycopg2**: For PostgreSQL connectivity
- **requests**: For API data extraction

## 📐 Data Model: Star Schema

The data is organized into a star schema to optimize analytical queries:

### Fact Table
- **fact_tickets**: Stores ticket details
  - ticket_id, user_id, project_id, priority_id, status, created_date, resolution_date, resolution_days

### Dimension Tables
- **dim_users**: User metadata (user_id, user_name)
- **dim_projects**: Project metadata (project_id, project_name: Jira, Confluence)
- **dim_priorities**: Priority metadata (priority_id, priority_name: High, Medium, Low)

### Summary Table
- **ticket_summary**: Aggregated metrics (ticket_count, avg_resolution_days by project, status, priority)

## 🚀 Getting Started

### Prerequisites

- PostgreSQL: Installed and running locally (version 12+ recommended)
- Python Packages: Install via pip:
  ```bash
  pip install pandas psycopg2-binary requests
