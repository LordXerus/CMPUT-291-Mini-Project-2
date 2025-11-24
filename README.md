[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/THJ5OpUp)
# CMPUT 291 Project 2 - Fall 2025

# GROUP INFORMATION
Group member names and ccids (2-3 members)  
  wpli, William Li  
  mahir2, Mahir Islam  
  ccid3, name2  

# INSTRUCTIONS
Python Environment Setup
1. Navigate to Project Directory
bashcd CMPUT-291-Mini-Project-2
2. Create Virtual Environment
bashpython3 -m venv venv
3. Activate Virtual Environment
macOS/Linux:
bashsource venv/bin/activate
Windows:
bashvenv\Scripts\activate
4. Install Dependencies
bashpip install pymongo
5. (Optional) Create requirements.txt
bashpip freeze > requirements.txt
For future installations:
bashpip install -r requirements.txt

Running the Programs
Phase 1: Loading Data into MongoDB
Command Format
bashpython3 load-json.py <json_filename> <port_number>
Example
bashpython3 load-json.py chunk_1.json 27017
Expected Output
Connecting to MongoDB on port 27017...
Connected to database: 291db
Created new 'articles' collection

Loading data from 'chunk_1.json' in batches of 5000...
Inserted 5000 documents...
Inserted 10000 documents...

✓ Successfully loaded 10000 documents into 'articles' collection
✓ Verification: Collection contains 10000 documents
✓ Database connection closed
Notes

The program drops any existing articles collection before loading
Data is inserted in batches of 5000 documents for efficiency
Default port for MongoDB is 27017


Phase 2: Querying the Database
Command Format
bashpython3 phase2_query.py <port_number>
Example
bashpython3 phase2_query.py 27017
Available Operations
1. Most Common Words by Media Type

Input: Media type (news/blog, case-insensitive)
Output: Top 5 most common words with frequency counts
Includes ties at 5th position

2. Article Count Difference Between News and Blogs

Input: Date (YYYY-MM-DD or "Month Day, Year" format)
Output: Number of news articles, blog articles, and comparison
Example dates: 2015-09-07 or September 7, 2015

3. Top 5 News Sources by Article Count (2015)

Input: None
Output: Top 5 sources that published most articles in 2015
Includes percentage of total articles

4. 5 Most Recent Articles by Source

Input: Source name (exact match)
Output: Up to 5 most recent articles from that source
Shows title and publication date

5. Exit

Closes database connection and exits program

# Names of anyone you have collaborated with (as much as it is allowed within the course policy) or a line saying that you did not collaborate with anyone else.  

Did not collaborate with anyone else other than group members.