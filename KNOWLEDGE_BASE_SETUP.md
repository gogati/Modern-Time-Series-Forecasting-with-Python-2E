# Knowledge Base Quick Setup Guide

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
pip install -r requirements_knowledge_base.txt
```

Or install just the essentials:

```bash
pip install chromadb sentence-transformers
```

### Step 2: Run the Enhanced Pipeline

```bash
python agentic_pipeline_with_kb.py
```

That's it! The knowledge base will be created automatically at `./agent_knowledge_base/`

## 📊 What You Get

### Before (Without Knowledge Base):
```
Agent makes decision → Executes → Done
❌ No memory of past decisions
❌ Can't learn from mistakes
❌ Repeats analysis for similar problems
```

### After (With Knowledge Base):
```
Agent makes decision → Queries KB for similar cases →
Learns from past → Makes informed decision → Stores result
✅ Remembers past decisions
✅ Learns from successes and failures
✅ Gets smarter over time
```

## 🔍 Example Usage

```python
from agentic_pipeline_with_kb import AgenticKnowledgeBase

# Initialize
kb = AgenticKnowledgeBase()

# Store a decision
kb.store_decision(
    agent_id="model_agent",
    decision={
        'context': 'Weekly seasonal data with trend',
        'action': 'Selected SARIMA + Prophet ensemble',
        'outcome': 'MAPE improved from 15% to 8.5%',
        'performance': 0.915,
        'confidence': 0.92,
        'tags': ['seasonality', 'ensemble']
    }
)

# Find similar cases later
similar = kb.find_similar_decisions(
    "Need to forecast weekly patterns"
)

for case in similar:
    print(f"Past case: {case['document']}")
    print(f"Performance: {case['metadata']['performance']}")
```

## 📁 Knowledge Base Structure

```
agent_knowledge_base/
├── chroma.sqlite3          # Main database
└── [collection files]      # Embeddings & metadata

Collections:
├── agent_decisions         # All agent decisions
├── data_patterns          # Recognized patterns
└── error_solutions        # Known errors & fixes
```

## 🔧 Configuration Options

### Change Storage Location

```python
kb = AgenticKnowledgeBase(
    persist_directory="./my_custom_kb"
)
```

### Use Different Embedding Model

```python
# Faster but less accurate
from chromadb.utils import embedding_functions

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"  # Default: fast
    # model_name="all-mpnet-base-v2"  # Better quality
)
```

## 📈 Scaling Options

### Current Setup: ChromaDB (Local)
- **Good for**: Development, testing, small teams
- **Data size**: Up to 1M documents
- **Cost**: Free

### Upgrade Path 1: Pinecone
```bash
pip install pinecone-client

# In your code:
import pinecone
pinecone.init(api_key="your-key")
```
- **Good for**: Production, cloud deployment
- **Data size**: Billions of documents
- **Cost**: Free tier available, then usage-based

### Upgrade Path 2: Hybrid (ChromaDB + PostgreSQL)
```bash
pip install sqlalchemy psycopg2-binary

# Store:
# - Embeddings → ChromaDB
# - Metrics → PostgreSQL
# - Relationships → Optional: Neo4j
```
- **Good for**: Complex queries, analytics
- **Data size**: Scalable
- **Cost**: Free (self-hosted)

## 🎯 Common Use Cases

### 1. Learn from Past Model Selections

```python
# Agent checks: "What models worked for this pattern before?"
similar_decisions = kb.find_similar_decisions(
    "Weekly seasonality with upward trend"
)

# Result: "SARIMA worked well (MAPE: 8.5%)"
# Agent: "I'll try SARIMA first!"
```

### 2. Remember Error Solutions

```python
# Store when you solve an error
kb.store_error_solution(
    error_type="forecast_drift",
    solution={
        'symptoms': 'Accuracy degrading over time',
        'root_cause': 'Concept drift',
        'solution': 'Retrain with recent 90 days',
        'prevention': 'Monitor drift metrics'
    }
)

# Next time: Agent finds and applies solution automatically
```

### 3. Build Pattern Library

```python
# Every time you encounter a pattern, store it
kb.store_pattern(
    pattern_type='weekly_with_holiday_effects',
    characteristics={
        'seasonality': 'weekly',
        'external_factors': ['holidays'],
        'recommended_models': ['Prophet', 'SARIMA with exog'],
        'success_rate': 0.93
    }
)
```

## 🧪 Testing Your Setup

```python
# Quick test script
from agentic_pipeline_with_kb import AgenticKnowledgeBase

kb = AgenticKnowledgeBase()

# Store test data
kb.store_decision("test_agent", {
    'context': 'test context',
    'action': 'test action',
    'outcome': 'success',
    'performance': 0.95,
    'confidence': 0.9,
    'tags': ['test']
})

# Verify
stats = kb.get_statistics()
print(f"✅ Knowledge Base working! Stored {stats['total_decisions']} decisions")
```

## 📚 Knowledge Base vs. Traditional Database

| Feature | Traditional DB | Knowledge Base |
|---------|---------------|----------------|
| Search | Exact match | Semantic similarity |
| Queries | SQL | Natural language |
| Relationships | Foreign keys | Embeddings |
| Learning | Static | Continuous |
| Use case | Structured data | Unstructured insights |

## 🎓 Best Practices

1. **Store Meaningful Context**: Include enough detail for future retrieval
   ```python
   # ❌ Bad
   decision = {'action': 'used SARIMA'}

   # ✅ Good
   decision = {
       'context': 'Weekly seasonal data, 2 years history, 2.5% missing',
       'action': 'Selected SARIMA(1,1,1)(1,1,1,7)',
       'reasoning': 'Strong weekly pattern, needed seasonal model',
       'outcome': 'MAPE: 8.5%, beat baseline by 6.5%'
   }
   ```

2. **Tag Appropriately**: Tags help filter
   ```python
   tags = ['seasonality', 'weekly', 'ensemble', 'production']
   ```

3. **Regular Maintenance**: Clean old/irrelevant data
   ```python
   # Delete decisions older than 1 year
   # Or decisions with poor performance
   ```

4. **Monitor Size**: Track knowledge base growth
   ```python
   stats = kb.get_statistics()
   if stats['total_decisions'] > 100000:
       print("⚠️  Consider archiving old data")
   ```

## 🐛 Troubleshooting

### ChromaDB Installation Issues

```bash
# On M1/M2 Mac:
pip install chromadb --no-binary chromadb

# On Windows (if issues):
pip install chromadb --no-deps
pip install hnswlib pydantic>=1.9
```

### Embedding Model Download Issues

```python
# Pre-download models
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
# This will cache the model locally
```

### Permission Errors

```bash
# Make sure directory is writable
chmod 755 ./agent_knowledge_base
```

## 🔗 Resources

- ChromaDB Docs: https://docs.trychroma.com/
- Sentence Transformers: https://www.sbert.net/
- Pinecone Docs: https://docs.pinecone.io/
- Neo4j Docs: https://neo4j.com/docs/

## 💡 Next Steps

1. ✅ Run `python agentic_pipeline_with_kb.py`
2. 📖 Read `KNOWLEDGE_BASE_INTEGRATION.md` for detailed options
3. 🏗️ Integrate with your existing pipeline
4. 📊 Monitor and optimize based on your needs

---

**Questions?** Check the main documentation in `KNOWLEDGE_BASE_INTEGRATION.md`
