# Sakila Database AI Chat Assistant

An AI-powered command-line tool for querying the PostgreSQL Sakila
database using natural language. It uses an agent pipeline to translate
user queries into SQL, execute them safely, and interpret the results.

## Features

-   Natural language → SQL translation.
-   Secure SELECT-only SQL execution.
-   Two-agent pipeline (SQL expert + data analyst).
-   Conversation history.
-   Clean command-line interface.

## Architecture

    User → SQL Expert Agent → SQL Executor → Data Analyst Agent → Answer

## Requirements

-   Python 3.10+
-   PostgreSQL with Sakila schema
-   Libraries: autogen, psycopg2, sqlparse

## Setup

Install dependencies:

    pip install autogen psycopg2 sqlparse

Ensure PostgreSQL is running with:

    dbname: sakila
    user: sakila
    password: p_ssW0rd
    host: localhost
    port: 5432

## Running

    python chat.py

To exit: `exit`, `quit`, or `q`.

## SQL Safety

-   Only SELECT queries allowed.
-   Max 10 queries per request.
-   Max 100 rows returned.
-   Modification statements blocked.

## File Overview

-   chat.py --- command-line interface + conversation handling
-   agents.py --- agent configuration and behavior rules
-   sql.py --- SQL execution and database schema profiling
