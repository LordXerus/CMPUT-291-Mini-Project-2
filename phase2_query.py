#!/usr/bin/env python3
"""
Phase 2: Query operations on MongoDB document store
Usage: python3 phase2_query.py <port_number>
"""

import sys
import re
from collections import Counter
from datetime import datetime
from pymongo import MongoClient


def connect_to_mongodb(port):
    """Connect to MongoDB and return database object"""
    try:
        client = MongoClient('localhost', port)
        db = client['291db']
        # Test connection
        db.list_collection_names()
        return client, db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        sys.exit(1)


def most_common_words(db):
    """Operation 1: Find top 5 most common words by media type"""
    print("\n" + "="*70)
    print("MOST COMMON WORDS BY MEDIA TYPE")
    print("="*70)
    
    media_type = input("Enter media type (news/blog): ").strip()
    
    # Case insensitive match
    media_type_title = media_type.capitalize()
    
    # Get all articles of this media type
    articles = db.articles.find({"media-type": media_type_title}, {"content": 1})
    
    # Count words
    word_counter = Counter()
    article_count = 0
    
    for article in articles:
        article_count += 1
        content = article.get('content', '')
        words = re.findall(r'[\w-]+', content.lower())
        word_counter.update(words)
    
    if article_count == 0:
        print(f"\nNo articles found for media type: {media_type}")
        return
    
    # Get top 5 most common words, including ties at 5th position
    most_common = word_counter.most_common()
    
    if len(most_common) == 0:
        print("\nNo words found in articles")
        return
    
    # Find top 5, including ties
    top_words = []
    for i, (word, count) in enumerate(most_common):
        if i < 5:
            top_words.append((word, count))
        elif i >= 5 and count == top_words[4][1]:
            top_words.append((word, count))
        else:
            break
    
    print(f"\nTop {len(top_words)} most common words in {media_type_title} articles:")
    print(f"   (Based on {article_count:,} articles)\n")
    print(f"{'Rank':<6} {'Word':<25} {'Occurrences':>15}")
    print("-" * 70)
    for i, (word, count) in enumerate(top_words, 1):
        print(f"{i:<6} {word:<25} {count:>15,}")


def article_count_by_date(db):
    """Operation 2: Count news vs blog articles on a specific date"""
    print("\n" + "="*70)
    print("ARTICLE COUNT DIFFERENCE BETWEEN NEWS AND BLOGS")
    print("="*70)
    
    date_str = input("Enter date (YYYY-MM-DD or 'Month Day, Year'): ").strip()
    
    # Parse date - try multiple formats
    target_date = None
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        try:
            target_date = datetime.strptime(date_str, "%B %d, %Y")
        except ValueError:
            print("\nInvalid date format. Please use YYYY-MM-DD or 'Month Day, Year'")
            return
    
    # Format date to match MongoDB format
    date_start = target_date.strftime("%Y-%m-%d")
    regex_pattern = f"^{date_start}"
    
    news_count = db.articles.count_documents({
        "media-type": "News",
        "published": {"$regex": regex_pattern}
    })
    
    blog_count = db.articles.count_documents({
        "media-type": "Blog",
        "published": {"$regex": regex_pattern}
    })
    
    total_count = news_count + blog_count
    
    print(f"\nResults for {date_start}:")
    print("-" * 70)
    
    if total_count == 0:
        print("No articles were published on this day.")
        return
    
    print(f"{'Media Type':<20} {'Article Count':>20}")
    print("-" * 70)
    print(f"{'News':<20} {news_count:>20,}")
    print(f"{'Blog':<20} {blog_count:>20,}")
    print("-" * 70)
    print(f"{'Total':<20} {total_count:>20,}")
    print()
    
    if news_count > blog_count:
        difference = news_count - blog_count
        percentage = (difference / blog_count * 100) if blog_count > 0 else 0
        print(f"News had MORE articles by {difference:,} ({percentage:.1f}% more)")
    elif blog_count > news_count:
        difference = blog_count - news_count
        percentage = (difference / news_count * 100) if news_count > 0 else 0
        print(f"Blog had MORE articles by {difference:,} ({percentage:.1f}% more)")
    else:
        print("News and Blog had the SAME number of articles")


def top_sources_2015(db):
    """Operation 3: Top 5 news sources by article count in 2015"""
    print("\n" + "="*70)
    print("TOP 5 NEWS SOURCES BY ARTICLE COUNT (2015)")
    print("="*70)
    
    # Aggregation pipeline to count articles per source in 2015
    pipeline = [
        {
            "$match": {
                "published": {"$regex": "^2015"}
            }
        },
        {
            "$group": {
                "_id": "$source",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"count": -1}
        }
    ]
    
    results = list(db.articles.aggregate(pipeline))
    
    if not results:
        print("\nNo articles found from 2015")
        return
    
    # Get top 5, including ties at 5th position
    top_sources = []
    for i, result in enumerate(results):
        if i < 5:
            top_sources.append(result)
        elif i >= 5 and result['count'] == top_sources[4]['count']:
            top_sources.append(result)
        else:
            break
    
    total_articles = sum(r['count'] for r in results)
    top_total = sum(r['count'] for r in top_sources)
    
    print(f"\nTop {len(top_sources)} news sources in 2015:")
    print(f"   (Total articles in 2015: {total_articles:,})\n")
    print(f"{'Rank':<6} {'Source':<40} {'Articles':>15}")
    print("-" * 70)
    for i, result in enumerate(top_sources, 1):
        source = result['_id']
        count = result['count']
        percentage = (count / total_articles * 100)
        print(f"{i:<6} {source:<40} {count:>10,} ({percentage:>5.1f}%)")
    print("-" * 70)
    print(f"{'Top sources total':<46} {top_total:>10,} ({top_total/total_articles*100:>5.1f}%)")


def recent_articles_by_source(db):
    """Operation 4: Get 5 most recent articles from a specific source"""
    print("\n" + "="*70)
    print("5 MOST RECENT ARTICLES BY SOURCE")
    print("="*70)
    
    source_name = input("Enter source name: ").strip()
    
    # Check if source exists
    source_count = db.articles.count_documents({"source": source_name})
    
    if source_count == 0:
        print(f"\nSource '{source_name}' was not found.")
        return
    
    # Get up to 5 most recent articles
    articles = db.articles.find(
        {"source": source_name},
        {"title": 1, "published": 1}
    ).sort("published", -1).limit(5)
    
    articles_list = list(articles)
    
    print(f"\n📰 Most recent articles from '{source_name}'")
    print(f"   (Showing {len(articles_list)} of {source_count:,} total articles)\n")
    print(f"{'#':<4} {'Date':<15} {'Title'}")
    print("-" * 70)
    
    for i, article in enumerate(articles_list, 1):
        title = article.get('title', 'No title')
        published = article.get('published', '')
        
        # Extract date from ISO format
        if published:
            date_only = published.split('T')[0]
        else:
            date_only = "Unknown"
        
        # Truncate long titles
        if len(title) > 48:
            title = title[:45] + "..."
        
        print(f"{i:<4} {date_only:<15} {title}")


def print_menu():
    """Display main menu"""
    print("\n" + "="*70)
    print(" " * 15 + "CMPUT 291 - PHASE 2 QUERY SYSTEM")
    print("="*70)
    print("  1. Most Common Words by Media Type")
    print("  2. Article Count Difference Between News and Blogs")
    print("  3. Top 5 News Sources by Article Count (2015)")
    print("  4. 5 Most Recent Articles by Source")
    print("  5. Exit")
    print("="*70)


def main():
    """Main function"""
    
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python3 phase2_query.py <port_number>")
        print("Example: python3 phase2_query.py 27017")
        sys.exit(1)
    
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Error: Port number must be an integer")
        sys.exit(1)
    
    # Connect to MongoDB
    print(f"\nConnecting to MongoDB on port {port}...")
    client, db = connect_to_mongodb(port)
    print(f"Connected to database: 291db")
    
    # Main menu loop
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            most_common_words(db)
        elif choice == '2':
            article_count_by_date(db)
        elif choice == '3':
            top_sources_2015(db)
        elif choice == '4':
            recent_articles_by_source(db)
        elif choice == '5':
            print("\n" + "="*70)
            print("Thank you for using the query system. Goodbye!")
            print("="*70 + "\n")
            client.close()
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 5.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()