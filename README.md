# Sakila Database AI Chat Assistant

An AI-powered command-line tool for querying the PostgreSQL **Sakila** sample database using natural language.
The system uses a multi-agent pipeline to translate questions into SQL, execute them safely, and summarize the results.

---

## Features

* **Natural language → SQL** translation
* **Safe SQL execution** (SELECT-only)
* **Two-agent workflow:**

  * SQL Expert Agent
  * Data Analyst Agent
* **Conversation history tracking**
* **Clean terminal interface**

---

## Architecture

```
User → SQL Expert Agent → SQL Executor → Data Analyst Agent → Answer
```

---

## Requirements

* Python **3.10+**
* PostgreSQL running the **Sakila** schema (local or Docker)
* Python libraries:

  * `autogen`
  * `psycopg2`
  * `sqlparse`

---

## Installation

Install dependencies:

```bash
pip install autogen psycopg2 sqlparse
```

Your PostgreSQL instance should match:

```
dbname: sakila
user: sakila
password: p_ssW0rd
host: localhost
port: 5432
```

---

# Using the Sakila Database with Docker

You can run a ready-to-use PostgreSQL instance containing the **Sakila** sample database with the official Docker setup:

**GitHub Repository:**
[https://github.com/sakiladb/postgres](https://github.com/sakiladb/postgres)

## 1. Pull the Docker image

```bash
docker pull sakiladb/postgres
```

## 2. Run the container (default credentials)

```bash
docker run --name sakila-db \
  -p 5432:5432 \
  -d sakiladb/postgres
```

This uses the image’s default credentials:

```
user: sakila
password: sakila
database: sakila
```

## 3. Run the container with custom credentials (recommended)

To match the credentials used in this project:

```bash
docker run --name sakila-db \
  -e POSTGRES_USER=sakila \
  -e POSTGRES_PASSWORD=p_ssW0rd \
  -e POSTGRES_DB=sakila \
  -p 5432:5432 \
  -d sakiladb/postgres
```

After this, the database will be accessible at:

```
postgresql://sakila:p_ssW0rd@localhost:5432/sakila
```

---

## Running the Chat Assistant

Start the CLI tool:

```bash
python chat.py
```

Exit commands:

```
exit
quit
q
```

---

## SQL Safety Rules

To protect the database, the executor enforces:

* **SELECT-only** queries
* **Up to 10 queries per request**
* **Max 100 rows** returned
* Blocking of:

  * INSERT
  * UPDATE
  * DELETE
  * DROP / ALTER / TRUNCATE

---

## Project File Structure

```
.
├── chat.py       # Command-line interface + conversation handling
├── agents.py     # Agent definitions and behavioral rules
└── sql.py        # SQL execution + schema profiling
```

---
