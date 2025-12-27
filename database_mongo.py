# database_mongo.py
# MongoDB-based database layer for persistent storage
import os
from datetime import datetime
from typing import List, Dict, Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "")
DATABASE_NAME = "medium_scraper"

class MongoDB:
    """MongoDB database wrapper for persistent Q&A storage"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.jobs = None
        self.qa_pairs = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB Atlas"""
        if not MONGODB_URI or MONGODB_URI == "":
            raise ValueError("MONGODB_URI environment variable not set")
        
        try:
            self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB Atlas")
            
            # Select database
            self.db = self.client[DATABASE_NAME]
            self.jobs = self.db.jobs
            self.qa_pairs = self.db.qa_pairs
            
            # Create indexes
            self._create_indexes()
            
        except ConnectionFailure as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        # Jobs indexes
        self.jobs.create_index([("created_at", DESCENDING)])
        self.jobs.create_index([("status", ASCENDING)])
        self.jobs.create_index([("url", ASCENDING)], unique=True)
        
        # Q&A pairs indexes
        self.qa_pairs.create_index([("job_id", ASCENDING)])
        self.qa_pairs.create_index([("timestamp", DESCENDING)])
        self.qa_pairs.create_index([("question", ASCENDING)])
        
        print("✅ Database indexes created")
    
    def create_job(self, job_id: str, url: str) -> Dict:
        """Create a new scraping job"""
        job = {
            "id": job_id,
            "url": url,
            "status": "queued",
            "qa_count": 0,
            "error": None,
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        
        try:
            self.jobs.insert_one(job)
            return job
        except DuplicateKeyError:
            # URL already exists, return existing job
            return self.jobs.find_one({"url": url})
    
    def update_job_status(self, job_id: str, status: str, error: Optional[str] = None, qa_count: Optional[int] = None):
        """Update job status"""
        update_data = {
            "status": status,
            "completed_at": datetime.now().isoformat() if status in ["completed", "failed"] else None
        }
        
        if error:
            update_data["error"] = error
        if qa_count is not None:
            update_data["qa_count"] = qa_count
        
        self.jobs.update_one(
            {"id": job_id},
            {"$set": update_data}
        )
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        return self.jobs.find_one({"id": job_id}, {"_id": 0})
    
    def save_qa_pairs(self, job_id: str, url: str, qa_pairs: List[Dict]) -> int:
        """Save Q&A pairs for a job"""
        new_count = 0
        
        for qa in qa_pairs:
            # Check for duplicate question
            existing = self.qa_pairs.find_one({"question": qa["question"]})
            if not existing:
                qa_doc = {
                    "job_id": job_id,
                    "question": qa["question"],
                    "answer": qa["answer"],
                    "source_url": url,
                    "timestamp": datetime.now().isoformat()
                }
                self.qa_pairs.insert_one(qa_doc)
                new_count += 1
        
        # Update job with Q&A count
        self.update_job_status(job_id, "completed", qa_count=new_count)
        return new_count
    
    def get_job_results(self, job_id: str) -> List[Dict]:
        """Get Q&A results for a job"""
        results = list(self.qa_pairs.find(
            {"job_id": job_id},
            {"_id": 0, "job_id": 0}
        ))
        return results
    
    def get_all_qa(self, limit: int = 50, offset: int = 0) -> Dict:
        """Get all Q&A pairs with pagination"""
        total = self.qa_pairs.count_documents({})
        
        qa_list = list(self.qa_pairs.find(
            {},
            {"_id": 0, "job_id": 0}
        ).sort("timestamp", DESCENDING).skip(offset).limit(limit))
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "qa_pairs": qa_list
        }
    
    def get_stats(self) -> Dict:
        """Get system statistics"""
        total_qa = self.qa_pairs.count_documents({})
        total_jobs = self.jobs.count_documents({})
        completed_jobs = self.jobs.count_documents({"status": "completed"})
        failed_jobs = self.jobs.count_documents({"status": "failed"})
        
        # Count unique URLs
        unique_urls = len(self.jobs.distinct("url", {"status": "completed"}))
        
        success_rate = f"{(completed_jobs / total_jobs * 100):.1f}%" if total_jobs > 0 else "0%"
        
        return {
            "total_qa_pairs": total_qa,
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "unique_articles_processed": unique_urls,
            "success_rate": success_rate,
            "database_type": "MongoDB Atlas",
            "persistent": True
        }
    
    def get_processed_urls(self) -> set:
        """Get all URLs that have been successfully processed"""
        urls = self.jobs.distinct("url", {"status": "completed"})
        return set(urls)
    
    def cleanup_old_jobs(self, days: int = 30):
        """Clean up jobs older than X days"""
        from datetime import timedelta
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        result = self.jobs.delete_many({
            "created_at": {"$lt": cutoff_date},
            "status": {"$in": ["completed", "failed"]}
        })
        
        return result.deleted_count
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("✅ MongoDB connection closed")

# Singleton instance
_mongo_db = None

def get_mongo_db() -> MongoDB:
    """Get or create MongoDB instance"""
    global _mongo_db
    if _mongo_db is None:
        _mongo_db = MongoDB()
    return _mongo_db

def test_connection():
    """Test MongoDB connection"""
    try:
        db = get_mongo_db()
        stats = db.get_stats()
        print(f"✅ MongoDB connection successful!")
        print(f"   Database: {stats['database_type']}")
        print(f"   Q&A Pairs: {stats['total_qa_pairs']}")
        print(f"   Jobs: {stats['total_jobs']}")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

if __name__ == "__main__":
    # Test the connection
    test_connection()

