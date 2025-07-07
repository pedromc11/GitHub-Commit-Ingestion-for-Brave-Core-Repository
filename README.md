# GitHub Commit Ingestion for Brave Core Repository

## 📌 Project Overview

This project implements an **advanced ingestion client** to extract and store commit data from the [brave-core](https://github.com/brave/brave-core) GitHub repository into a **MongoDB** database.  
The ingestion is limited to commits **from January 1, 2019 to the present** and includes:

- Basic commit information (SHA, author, date, message, etc.)
- Extended commit details via the GitHub REST API v3:
  - **Modified files**
  - **Change statistics** (additions, deletions, total)

The commit data is stored in a local **MongoDB collection**, and rate limiting by GitHub is **efficiently managed**.

---

## ⚙️ Technologies Used

- **Python 3**
- **MongoDB** (via `pymongo`)
- **GitHub REST API** (via `requests`)

---

## 📁 MongoDB Structure

Each commit document inserted into MongoDB includes:
```json
{
  "sha": "...",
  "commit": {
    "author": {...},
    "committer": {...},
    "message": "..."
  },
  "projectId": "brave-core",
  "stats": {
    "additions": ...,
    "deletions": ...,
    "total": ...
  },
  "files": [
    {
      "filename": "...",
      "additions": ...,
      "deletions": ...,
      ...
    }
  ]
}

---

# 📥 Requirements

* Install required packages using pip:

    ```bash
    pip install requests pymongo
    ```

* Ensure MongoDB is running locally on port 27017.

---

# 🚀 How to Run

1.  Update the authentication variables:

    ```python
    username = 'YOUR_GITHUB_USERNAME'
    token = 'YOUR_GITHUB_TOKEN'
    client_id = 'YOUR_CLIENT_ID'
    client_secret = 'YOUR_CLIENT_SECRET'
    ```

2.  Adjust the following settings if needed:

    ```python
    owner = 'brave'
    repo = 'brave-core'
    date = '2019-01-01T00:00:00Z'
    ```

3.  Run the script:

    ```bash
    python ingest_commits.py
    ```

The script will:

* Fetch commit pages with pagination
* Fetch detailed commit info (`GET /repos/{owner}/{repo}/commits/{sha}`)
* Insert commit data into the collection `db_practicas3y4.github` (or `prueba` depending on version)
* Respect GitHub API rate limits and pause when necessary

---

# 🛠 GitHub API Reference Used

* **List commits:**
    `GET /repos/{owner}/{repo}/commits`
    [Docs](https://docs.github.com/rest/commits/commits#list-commits)

* **Get a commit** (used to fetch stats and files):
    `GET /repos/{owner}/{repo}/commits/{sha}`
    [Docs](https://docs.github.com/rest/commits/commits#get-a-commit)

* **Check rate limit:**
    `GET /rate_limit`
    [Docs](https://docs.github.com/rest/rate-limit)

---

# 🧠 Features

✅ **Advanced commit ingestion** with extra metadata
✅ **Efficient rate-limit handling** (pause and retry logic)
✅ **Clean MongoDB storage structure** for analytics and querying
✅ **Easy to configure** for other repositories

---

# 🧾 Deliverables

The project includes:

✅ `README.md` (this file)
✅ `ingest_commits.py` (Python client for GitHub + MongoDB)
✅ Evidence of successful ingestion via printed logs and database contents