#!/usr/bin/env python3
"""
Test script to verify RAG retrieval is working properly
"""
import json
import sys
import os

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag_engine import ask
from logger.logger import Logger

def test_retrieval():
    """Test the RAG system with sample questions"""
    logger = Logger.get_instance()
    
    # Test questions
    test_questions = [
        "do you have any idea of what information are power supply types ?",
        "How does a CPU work?",
        "What are the different types of storage devices?",
        "Explain motherboard components",
        "What is GPU?"
    ]
    
    print("=" * 60)
    print("TESTING RAG SYSTEM RETRIEVAL")
    print("=" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 40)
        
        try:
            answer, sources = ask(question)
            print(f"Answer: {answer}")
            print(f"Sources: {sources}")
            
            # Check if we got a meaningful response
            if "don't know" in answer.lower() or len(answer.strip()) < 10:
                print("⚠️  WARNING: Got a short or 'don't know' response")
            else:
                print("✅ Got a meaningful response")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_retrieval()
