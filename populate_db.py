import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Q1. Show the MongoDB insert script or Python code you used to populate the collection. ---
# This script serves as the answer to Q1.

def populate_student_collection():
    """
    Connects to the MongoDB database, clears the existing students collection,
    and inserts 10 new student documents.
    """
    # Get the MongoDB connection string from environment variables
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI not found in environment variables. Please check your .env file.")

    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client.student_records # Database name
    collection = db.students    # Collection name

    # Clear the collection to avoid duplicate data on re-runs
    print("Deleting existing documents in 'students' collection...")
    collection.delete_many({})

    # Define the student data to be inserted
    students_data = [
        {"name": "Alice Johnson", "student_id": "20230001", "department": "Computer Science", "cgpa": 3.8, "graduation_year": 2024},
        {"name": "Bob Smith", "student_id": "20230002", "department": "Mechanical Engineering", "cgpa": 3.5, "graduation_year": 2025},
        {"name": "Charlie Brown", "student_id": "20231234", "department": "Computer Science", "cgpa": 3.9, "graduation_year": 2024},
        {"name": "Diana Prince", "student_id": "20230004", "department": "Electrical Engineering", "cgpa": 3.2, "graduation_year": 2025},
        {"name": "Ethan Hunt", "student_id": "20230005", "department": "Civil Engineering", "cgpa": 2.4, "graduation_year": 2024},
        {"name": "Fiona Glenanne", "student_id": "20230006", "department": "Computer Science", "cgpa": 3.6, "graduation_year": 2025},
        {"name": "George Costanza", "student_id": "20230007", "department": "Arts", "cgpa": 2.8, "graduation_year": 2024},
        {"name": "Hannah Montana", "student_id": "20230008", "department": "Mechanical Engineering", "cgpa": 2.1, "graduation_year": 2026},
        {"name": "Ian Malcolm", "student_id": "20230009", "department": "Computer Science", "cgpa": 3.7, "graduation_year": 2025},
        {"name": "Jane Doe", "student_id": "20230010", "department": "Electrical Engineering", "cgpa": 3.4, "graduation_year": 2026},
        {"name": "Kevin McCallister", "student_id": "20230011", "department": "Civil Engineering", "cgpa": 2.2, "graduation_year": 2025}
    ]

    # Insert the data into the collection
    print(f"Inserting {len(students_data)} documents...")
    result = collection.insert_many(students_data)
    print(f"Successfully inserted documents with IDs: {result.inserted_ids}")

    # Close the connection
    client.close()

if __name__ == "__main__":
    populate_student_collection()