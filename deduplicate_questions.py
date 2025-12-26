#!/usr/bin/env python3
# deduplicate_questions.py
# Remove similar/duplicate questions using AI and fuzzy matching

import pandas as pd
from groq import Groq
from pathlib import Path
import re

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")

def normalize_question(q):
    """Normalize question for basic comparison"""
    q = q.lower().strip()
    # Remove punctuation
    q = re.sub(r'[^\w\s]', '', q)
    # Remove extra whitespace
    q = ' '.join(q.split())
    return q

def simple_similarity(q1, q2):
    """Quick similarity check (0-1)"""
    q1_norm = normalize_question(q1)
    q2_norm = normalize_question(q2)
    
    # Exact match
    if q1_norm == q2_norm:
        return 1.0
    
    # Word overlap
    words1 = set(q1_norm.split())
    words2 = set(q2_norm.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

def ai_similarity_batch(questions, threshold=0.8):
    """Use AI to find similar questions in batch"""
    client = Groq(api_key=GROQ_API_KEY)
    
    # Format questions for AI
    q_list = '\n'.join([f"{i+1}. {q}" for i, q in enumerate(questions)])
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""Analyze these iOS interview questions and identify which ones are DUPLICATES or VERY SIMILAR in meaning.

Questions:
{q_list}

Return pairs of similar question numbers in format:
Similar: 1, 5 (both ask about closures)
Similar: 3, 7 (both ask about ARC)

Only return pairs that ask essentially the same thing. If no duplicates, return "NO_DUPLICATES".

Similar pairs:"""
            }],
            temperature=0,
            max_tokens=500
        )
        
        result = response.choices[0].message.content.strip()
        
        if "NO_DUPLICATES" in result:
            return []
        
        # Parse similar pairs
        pairs = []
        for line in result.split('\n'):
            if 'Similar:' in line:
                # Extract numbers
                numbers = re.findall(r'\d+', line)
                if len(numbers) >= 2:
                    pairs.append((int(numbers[0])-1, int(numbers[1])-1))
        
        return pairs
        
    except Exception as e:
        print(f"  ⚠️  AI similarity check failed: {str(e)[:50]}")
        return []

def deduplicate_qa_data(input_file, output_file=None, similarity_threshold=0.7):
    """Remove duplicate/similar questions from Q&A data"""
    
    print("\n" + "="*70)
    print("🔍 DEDUPLICATION PROCESS")
    print("="*70)
    print(f"📁 Input: {input_file}")
    print(f"🎯 Similarity threshold: {similarity_threshold}")
    print()
    
    # Read data
    df = pd.read_csv(input_file)
    print(f"📊 Original: {len(df)} Q&A pairs")
    print()
    
    # Step 1: Remove exact duplicates (case-insensitive)
    print("Step 1: Removing exact duplicates...")
    df['question_normalized'] = df['question'].apply(normalize_question)
    df_unique = df.drop_duplicates(subset=['question_normalized'], keep='first')
    exact_dupes = len(df) - len(df_unique)
    print(f"  ✓ Removed {exact_dupes} exact duplicates")
    print()
    
    # Step 2: Find similar questions using simple word overlap
    print("Step 2: Finding similar questions (word overlap)...")
    questions = df_unique['question'].tolist()
    to_remove = set()
    similar_found = 0
    
    for i in range(len(questions)):
        if i in to_remove:
            continue
        for j in range(i + 1, len(questions)):
            if j in to_remove:
                continue
            
            similarity = simple_similarity(questions[i], questions[j])
            if similarity >= similarity_threshold:
                # Keep the first one, mark second for removal
                to_remove.add(j)
                similar_found += 1
                print(f"  Similar ({similarity:.2f}): '{questions[i][:50]}...' ≈ '{questions[j][:50]}...'")
    
    print(f"  ✓ Found {similar_found} similar pairs (word overlap)")
    print()
    
    # Step 3: AI-powered similarity check (optional, for remaining questions)
    if len(questions) <= 50:  # Only for smaller datasets
        print("Step 3: AI-powered similarity check...")
        remaining_questions = [q for i, q in enumerate(questions) if i not in to_remove]
        
        if len(remaining_questions) > 5:
            ai_similar_pairs = ai_similarity_batch(remaining_questions[:30])  # Limit to avoid API costs
            
            if ai_similar_pairs:
                print(f"  ✓ AI found {len(ai_similar_pairs)} additional similar pairs")
                for pair in ai_similar_pairs:
                    # Map back to original indices
                    if pair[1] < len(remaining_questions):
                        original_idx = questions.index(remaining_questions[pair[1]])
                        to_remove.add(original_idx)
            else:
                print(f"  ✓ No additional similar questions found by AI")
        print()
    else:
        print("Step 3: Skipping AI check (dataset too large, use word overlap only)")
        print()
    
    # Remove duplicates
    df_final = df_unique.iloc[[i for i in range(len(df_unique)) if i not in to_remove]].copy()
    df_final = df_final.drop(columns=['question_normalized'])
    
    # Save results
    if output_file is None:
        output_file = input_file.replace('.csv', '_deduplicated.csv')
    
    df_final.to_csv(output_file, index=False)
    df_final.to_json(output_file.replace('.csv', '.json'), orient='records', indent=2)
    
    # Summary
    print("="*70)
    print("📊 RESULTS")
    print("="*70)
    print(f"Original questions:     {len(df)}")
    print(f"Exact duplicates:       -{exact_dupes}")
    print(f"Similar questions:      -{len(to_remove) - exact_dupes}")
    print(f"Final unique questions: {len(df_final)}")
    print(f"Reduction:              {((len(df) - len(df_final)) / len(df) * 100):.1f}%")
    print()
    print(f"💾 Saved to:")
    print(f"   - {output_file}")
    print(f"   - {output_file.replace('.csv', '.json')}")
    print("="*70)
    print()
    
    return df_final

if __name__ == "__main__":
    # Find latest Q&A file
    qa_files = list(Path('.').glob('ios_qa_pairs_*.csv'))
    
    if not qa_files:
        print("No Q&A files found. Run monitor_qa_browsing.py first.")
        exit(1)
    
    latest_file = max(qa_files, key=lambda p: p.stat().st_mtime)
    
    # Deduplicate
    deduplicate_qa_data(
        str(latest_file),
        similarity_threshold=0.7  # Adjust: 0.5 = loose, 0.9 = strict
    )
    
    print("✅ Deduplication complete!")
    print()
    print("💡 Tip: Adjust similarity_threshold in the code:")
    print("   0.5 = Find loosely similar questions")
    print("   0.7 = Balanced (default)")
    print("   0.9 = Only very similar questions")

