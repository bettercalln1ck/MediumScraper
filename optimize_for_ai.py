#!/usr/bin/env python3
# optimize_for_ai.py
# Convert Q&A data to AI-friendly formats with minimal tokens

import pandas as pd
import json
from pathlib import Path

# Find the most recent Q&A file
qa_files = list(Path('.').glob('ios_qa_pairs_*.csv'))
if not qa_files:
    print("No Q&A files found. Run monitor_qa_browsing.py first.")
    exit(1)

latest_file = max(qa_files, key=lambda p: p.stat().st_mtime)
print(f"📁 Processing: {latest_file}")
print()

df = pd.read_csv(latest_file)
print(f"📊 Found {len(df)} Q&A pairs")
print()

# Create different optimized formats
output_formats = {}

# ============================================================================
# Format 1: JSONL (Compact, one line per Q&A, abbreviated keys)
# ============================================================================
jsonl_lines = []
for _, row in df.iterrows():
    jsonl_lines.append(json.dumps({
        "q": row['question'],
        "a": row['answer']
    }, ensure_ascii=False))

output_formats['jsonl'] = '\n'.join(jsonl_lines)

# ============================================================================
# Format 2: Plain Text Q&A (Simplest, very readable)
# ============================================================================
plain_lines = []
for i, row in df.iterrows():
    plain_lines.append(f"Q: {row['question']}")
    plain_lines.append(f"A: {row['answer']}")
    plain_lines.append("")  # Blank line separator

output_formats['txt'] = '\n'.join(plain_lines).strip()

# ============================================================================
# Format 3: Markdown (Best for viewing, good for AI)
# ============================================================================
md_lines = ["# iOS Interview Q&A", ""]
for i, row in df.iterrows():
    md_lines.append(f"## Q{i+1}: {row['question']}")
    md_lines.append(f"{row['answer']}")
    md_lines.append("")

output_formats['md'] = '\n'.join(md_lines)

# ============================================================================
# Format 4: Ultra Compact (Pipe-separated, no metadata)
# ============================================================================
compact_lines = []
for _, row in df.iterrows():
    compact_lines.append(f"{row['question']}|{row['answer']}")

output_formats['compact'] = '\n'.join(compact_lines)

# ============================================================================
# Format 5: System/User format for Chat APIs
# ============================================================================
chat_format = []
for _, row in df.iterrows():
    chat_format.append({
        "messages": [
            {"role": "user", "content": row['question']},
            {"role": "assistant", "content": row['answer']}
        ]
    })

output_formats['chat_jsonl'] = '\n'.join([json.dumps(c, ensure_ascii=False) for c in chat_format])

# ============================================================================
# Format 6: XML (Sometimes more compact than JSON)
# ============================================================================
xml_lines = ['<?xml version="1.0"?>', '<qa_pairs>']
for _, row in df.iterrows():
    xml_lines.append('  <pair>')
    xml_lines.append(f'    <q>{row["question"]}</q>')
    xml_lines.append(f'    <a>{row["answer"]}</a>')
    xml_lines.append('  </pair>')
xml_lines.append('</qa_pairs>')

output_formats['xml'] = '\n'.join(xml_lines)

# ============================================================================
# Save all formats and calculate token counts
# ============================================================================
print("="*70)
print("💾 GENERATED FORMATS (Token estimates)")
print("="*70)

results = []

for format_name, content in output_formats.items():
    filename = f"ios_qa_optimized.{format_name}"
    
    # Save file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Estimate tokens (rough: 4 chars = 1 token)
    estimated_tokens = len(content) // 4
    file_size_kb = len(content.encode('utf-8')) / 1024
    
    results.append({
        'format': format_name.upper(),
        'file': filename,
        'size_kb': f"{file_size_kb:.1f} KB",
        'est_tokens': estimated_tokens,
        'chars': len(content)
    })
    
    print(f"✓ {filename:<30} {estimated_tokens:>6} tokens  ({file_size_kb:.1f} KB)")

print()
print("="*70)
print("📊 FORMAT COMPARISON")
print("="*70)

# Sort by token count
results_sorted = sorted(results, key=lambda x: x['est_tokens'])

print(f"{'Format':<15} {'Tokens':<10} {'Size':<12} {'Best For'}")
print("-"*70)

format_recommendations = {
    'COMPACT': 'Minimal tokens, hard to parse',
    'TXT': 'Simple, readable, good balance ⭐',
    'JSONL': 'Structured, easy to parse',
    'CHAT_JSONL': 'Direct API training format',
    'MD': 'Human readable, documentation',
    'XML': 'Structured, verbose'
}

for r in results_sorted:
    rec = format_recommendations.get(r['format'], '')
    print(f"{r['format']:<15} {r['est_tokens']:<10} {r['size_kb']:<12} {rec}")

print()
print("="*70)
print("🎯 RECOMMENDATIONS")
print("="*70)

# Find most compact
most_compact = results_sorted[0]
print(f"""
1️⃣  MOST COMPACT: {most_compact['file']}
   • {most_compact['est_tokens']} tokens
   • Use for: Cost optimization, large datasets
   • Format: {most_compact['format']}

2️⃣  BEST BALANCE: ios_qa_optimized.txt ⭐
   • Simple Q:/A: format
   • Easy to parse and read
   • Good for prompts and fine-tuning

3️⃣  FOR CHAT APIs: ios_qa_optimized.chat_jsonl
   • Ready for OpenAI/Anthropic fine-tuning
   • User/Assistant message format
   • Direct import to training pipelines

4️⃣  FOR DOCUMENTATION: ios_qa_optimized.md
   • Markdown format
   • Best for human review
   • Can be fed to AI as context
""")

print("="*70)
print()

# Show sample of most compact format
print("📝 SAMPLE OUTPUT (Compact Format):")
print("-"*70)
print(output_formats['compact'].split('\n')[0][:200] + "...")
print()

print("📝 SAMPLE OUTPUT (Plain Text Format):")
print("-"*70)
print('\n'.join(output_formats['txt'].split('\n')[:6]))
print("...")
print()

print("✅ All formats saved! Use the one that fits your needs.")

