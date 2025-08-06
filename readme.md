# Mod 6 Project: AI Agent to Retrieve Data from MongoDB

This project contains an AI-powered agent that accepts natural language queries and retrieves relevant data from a MongoDB database.

## Setup Instructions

1.  **Clone the repository.**

2.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    -   Create a `.env` file.
    -   Fill in your MongoDB Atlas connection string (`MONGO_URI`) and your OpenAI API key (`OPENAI_API_KEY`).

5.  **Populate the MongoDB database:**
    -   Run the population script. This will create the `student_records` database and the `students` collection.
    ```bash
    python populate_db.py
    ```

## Usage

To run the AI agent and start asking questions, execute the main script:

```bash
python mongo_agent.py
```

You can then type your questions in the terminal. Type `exit` to quit.

### Example Queries

-   "Show me all students with CGPA above 3.5"
-   "List students graduating in 2025"
-   "Get details of student with ID 20231234"
-   "Who are the students in the CSE department?"
-   "How many students have CGPA less than 2.5?"
-   (Ambiguous query) "Find the best students"