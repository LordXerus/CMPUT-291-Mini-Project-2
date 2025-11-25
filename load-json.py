#!/usr/bin/env python3
"""
Phase 1: Load JSON data into MongoDB
Usage: python3 load-json.py <json_filename> <port_number>
"""

import sys
import json
from pymongo import MongoClient

def load_json_to_mongodb(json_filename, port):
    """
    Load JSON data from file into MongoDB collection.
    
    Args:
        json_filename: Name of the JSON file to load
        port: Port number where MongoDB is running
    """
    try:
        # Connect to MongoDB
        print(f"Connecting to MongoDB on port {port}...")
        client = MongoClient('localhost', port)
        
        # Create/access database
        db = client['291db']
        print("Connected to database: 291db")
        
        # Drop existing collection if it exists
        if 'articles' in db.list_collection_names():
            db.articles.drop()
            print("Dropped existing 'articles' collection")
        
        # Create new collection
        collection = db['articles']
        print("Created new 'articles' collection")
        
        # Process file in batches
        batch_size = 5000  # Adjust between 1k-10k as needed
        batch = []
        total_inserted = 0
        line_number = 0
        
        print(f"\nLoading data from '{json_filename}' in batches of {batch_size}...")
        
        with open(json_filename, 'r', encoding='utf-8') as file:
            for line in file:
                line_number += 1
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                try:
                    # Parse JSON object from line
                    document = json.loads(line)
                    batch.append(document)
                    
                    # Insert batch when it reaches batch_size
                    if len(batch) >= batch_size:
                        collection.insert_many(batch)
                        total_inserted += len(batch)
                        print(f"Inserted {total_inserted} documents...")
                        batch = []  # Clear batch
                        
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping invalid JSON on line {line_number}: {e}")
                    continue
        
        # Insert remaining documents in final batch
        if batch:
            collection.insert_many(batch)
            total_inserted += len(batch)
            print(f"Inserted {total_inserted} documents...")
        
        print(f"\n✓ Successfully loaded {total_inserted} documents into 'articles' collection")
        
        # Verify the data
        count = collection.count_documents({})
        print(f"✓ Verification: Collection contains {count} documents")
        
        # Close connection
        client.close()
        print("✓ Database connection closed")
        
    except FileNotFoundError:
        print(f"Error: File '{json_filename}' not found in current directory")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main function to parse arguments and call load function"""
    
    # Check command line arguments
    if len(sys.argv) != 3:
        print("Usage: python3 load-json.py <json_filename> <port_number>")
        print("Example: python3 load-json.py chunk_1.json 27017")
        sys.exit(1)
    
    json_filename = sys.argv[1]
    
    try:
        port = int(sys.argv[2])
    except ValueError:
        print("Error: Port number must be an integer")
        sys.exit(1)
    
    # Load data
    load_json_to_mongodb(json_filename, port)


if __name__ == "__main__":
    main()