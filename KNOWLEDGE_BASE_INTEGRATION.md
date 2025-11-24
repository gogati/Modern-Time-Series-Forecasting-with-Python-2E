# Knowledge Base Integration Guide

## Overview

The knowledge base is a critical component of the Agentic AI Pipeline, storing:
- Historical decisions and outcomes
- Domain knowledge about time series patterns
- Best practices and heuristics
- Model performance metrics
- Error patterns and solutions

## Recommended Knowledge Base Technologies

### Option 1: Vector Database (Recommended for Semantic Search)

**Best for**: Semantic similarity search, pattern matching, case-based reasoning

#### Top Choices:

#### 1. **ChromaDB** (Recommended for Getting Started)
```python
# Installation
pip install chromadb

# Why ChromaDB:
# ✓ Easy to set up (no server required)
# ✓ Python-native
# ✓ Built-in embedding support
# ✓ Persistent storage
# ✓ Great for development and moderate scale
```

**Use Cases**:
- Find similar forecasting problems from past
- Retrieve relevant feature engineering strategies
- Search for comparable data patterns
- Match error patterns to solutions

**Example Implementation**:
```python
import chromadb
from chromadb.config import Settings

# Initialize ChromaDB client
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./knowledge_base"
))

# Create collection for agent decisions
decisions_collection = client.create_collection(
    name="agent_decisions",
    metadata={"description": "Historical agent decisions and outcomes"}
)

# Store a decision
decisions_collection.add(
    documents=["Used SARIMA model for weekly seasonal data with trend"],
    metadatas=[{
        "agent": "model_selection",
        "patterns": "weekly_seasonality,trend",
        "performance": "MAPE=8.5%",
        "timestamp": "2025-11-23T10:00:00Z"
    }],
    ids=["decision_001"]
)

# Query similar cases
results = decisions_collection.query(
    query_texts=["Need model for daily data with weekly patterns"],
    n_results=5
)
```

#### 2. **Pinecone** (Recommended for Production)
```python
# Installation
pip install pinecone-client

# Why Pinecone:
# ✓ Fully managed (no infrastructure)
# ✓ Highly scalable
# ✓ Fast queries
# ✓ Real-time updates
# ✓ Production-ready
```

**Example Implementation**:
```python
import pinecone

# Initialize
pinecone.init(api_key="your-api-key", environment="us-west1-gcp")

# Create index
pinecone.create_index(
    name="forecasting-knowledge",
    dimension=1536,  # OpenAI embedding size
    metric="cosine"
)

index = pinecone.Index("forecasting-knowledge")

# Upsert knowledge
index.upsert(vectors=[
    {
        "id": "pattern_001",
        "values": embedding_vector,  # From OpenAI/etc
        "metadata": {
            "pattern_type": "weekly_seasonality",
            "recommended_models": ["SARIMA", "Prophet"],
            "success_rate": 0.92
        }
    }
])

# Query
results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True
)
```

#### 3. **Weaviate** (Recommended for Complex Schemas)
```python
# Installation
pip install weaviate-client

# Why Weaviate:
# ✓ Schema-based
# ✓ Hybrid search (vector + keyword)
# ✓ GraphQL API
# ✓ Built-in ML models
# ✓ Multi-modal support
```

---

### Option 2: Graph Database (Recommended for Relationships)

**Best for**: Modeling relationships between concepts, causal reasoning, decision trees

#### **Neo4j** (Top Choice)
```python
# Installation
pip install neo4j

# Why Neo4j:
# ✓ Industry standard for graph databases
# ✓ Cypher query language (intuitive)
# ✓ Excellent visualization
# ✓ ACID compliant
# ✓ Great for complex relationships
```

**Use Cases**:
- Model relationships between data patterns, features, and models
- Track causal chains (why a decision was made)
- Build decision trees for agent reasoning
- Connect similar forecasting problems

**Example Implementation**:
```python
from neo4j import GraphDatabase

class KnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def add_decision(self, pattern, model, performance):
        with self.driver.session() as session:
            session.run("""
                MERGE (p:Pattern {name: $pattern})
                MERGE (m:Model {name: $model})
                CREATE (p)-[:WORKS_WELL_WITH {
                    performance: $performance,
                    timestamp: datetime()
                }]->(m)
            """, pattern=pattern, model=model, performance=performance)

    def get_recommended_models(self, pattern):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Pattern {name: $pattern})-[r:WORKS_WELL_WITH]->(m:Model)
                RETURN m.name as model, r.performance as performance
                ORDER BY r.performance DESC
                LIMIT 5
            """, pattern=pattern)
            return [record for record in result]

# Usage
kg = KnowledgeGraph("bolt://localhost:7687", "neo4j", "password")
kg.add_decision("weekly_seasonality", "SARIMA", 0.915)
models = kg.get_recommended_models("weekly_seasonality")
```

**Graph Structure for Time Series Forecasting**:
```
(DataPattern)-[:REQUIRES]->(Feature)
(Feature)-[:FEEDS_INTO]->(Model)
(Model)-[:PRODUCES]->(Forecast)
(Forecast)-[:HAS_PERFORMANCE]->(Metric)
(Pattern)-[:SIMILAR_TO]->(Pattern)
(Error)-[:SOLVED_BY]->(Solution)
```

---

### Option 3: Hybrid Approach (Recommended for Production)

Combine multiple databases for different purposes:

#### **Architecture**:
```
┌─────────────────────────────────────────────────────┐
│              KNOWLEDGE BASE LAYER                    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Vector DB    │  │  Graph DB    │  │ SQL DB    │ │
│  │ (ChromaDB/   │  │  (Neo4j)     │  │(PostgreSQL│ │
│  │  Pinecone)   │  │              │  │           │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘ │
│         │                 │                 │       │
│         │                 │                 │       │
│  Semantic Search   Relationships    Structured Data │
│  Pattern Match     Reasoning        Metrics/History │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Implementation**:
```python
class HybridKnowledgeBase:
    def __init__(self):
        # Vector DB for semantic search
        self.vector_db = chromadb.Client(...)

        # Graph DB for relationships
        self.graph_db = GraphDatabase.driver(...)

        # SQL DB for structured data
        self.sql_db = create_engine('postgresql://...')

    def store_decision(self, decision_data):
        """Store decision across all databases"""
        # Store in vector DB for similarity search
        self.vector_db.add(
            documents=[decision_data['description']],
            metadatas=[decision_data['metadata']],
            ids=[decision_data['id']]
        )

        # Store relationships in graph DB
        with self.graph_db.session() as session:
            session.run("""
                CREATE (d:Decision {id: $id})
                -[:USES_MODEL]->(m:Model {name: $model})
            """, id=decision_data['id'], model=decision_data['model'])

        # Store metrics in SQL DB
        pd.DataFrame([decision_data['metrics']]).to_sql(
            'decision_metrics', self.sql_db, if_exists='append'
        )

    def retrieve_knowledge(self, query):
        """Multi-source knowledge retrieval"""
        # Get similar cases from vector DB
        similar_cases = self.vector_db.query(query, n_results=5)

        # Get related patterns from graph DB
        with self.graph_db.session() as session:
            relationships = session.run("""
                MATCH (p:Pattern)-[r]->(m:Model)
                WHERE p.name CONTAINS $query
                RETURN p, r, m
            """, query=query)

        # Get historical metrics from SQL
        metrics_df = pd.read_sql("""
            SELECT * FROM decision_metrics
            WHERE context LIKE %s
        """, self.sql_db, params=[f"%{query}%"])

        return {
            'similar_cases': similar_cases,
            'relationships': list(relationships),
            'metrics': metrics_df
        }
```

---

## Recommended Setup by Scale

### Small Scale (Development/Research)
```python
# ChromaDB + SQLite
pip install chromadb

# Simple, local, no infrastructure needed
# Good for: POCs, research, small teams
```

### Medium Scale (Production - Single Region)
```python
# Pinecone + PostgreSQL
pip install pinecone-client psycopg2-binary

# Managed services, moderate scale
# Good for: Startups, medium-sized deployments
```

### Large Scale (Production - Multi-Region)
```python
# Pinecone + Neo4j Aura + PostgreSQL/Timescale
pip install pinecone-client neo4j psycopg2-binary

# Fully managed, globally distributed
# Good for: Enterprises, high-traffic applications
```

---

## Implementation Example: ChromaDB Integration

Here's a complete example for the Agentic AI Pipeline:

```python
import chromadb
from chromadb.utils import embedding_functions
import json
from datetime import datetime
from typing import Dict, List, Any

class AgenticKnowledgeBase:
    """
    Knowledge base for storing and retrieving agent decisions,
    patterns, and learned experiences
    """

    def __init__(self, persist_directory: str = "./knowledge_base"):
        # Initialize ChromaDB
        self.client = chromadb.Client(chromadb.Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))

        # Use sentence transformers for embeddings
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # Create collections for different knowledge types
        self.collections = {
            'decisions': self._get_or_create_collection('agent_decisions'),
            'patterns': self._get_or_create_collection('data_patterns'),
            'strategies': self._get_or_create_collection('strategies'),
            'errors': self._get_or_create_collection('error_solutions')
        }

    def _get_or_create_collection(self, name: str):
        """Get or create a collection"""
        try:
            return self.client.get_collection(
                name=name,
                embedding_function=self.embedding_fn
            )
        except:
            return self.client.create_collection(
                name=name,
                embedding_function=self.embedding_fn
            )

    def store_decision(self, agent_id: str, decision: Dict[str, Any]):
        """Store an agent decision"""
        doc_id = f"{agent_id}_{datetime.now().timestamp()}"

        # Create searchable text
        text = f"""
        Agent: {agent_id}
        Context: {decision.get('context', '')}
        Decision: {decision.get('action', '')}
        Reasoning: {decision.get('reasoning', '')}
        Outcome: {decision.get('outcome', '')}
        """

        self.collections['decisions'].add(
            documents=[text],
            metadatas=[{
                'agent_id': agent_id,
                'timestamp': datetime.now().isoformat(),
                'performance': str(decision.get('performance', 0)),
                'confidence': str(decision.get('confidence', 0)),
                'tags': ','.join(decision.get('tags', []))
            }],
            ids=[doc_id]
        )

    def store_pattern(self, pattern_type: str, characteristics: Dict[str, Any]):
        """Store a data pattern with successful handling strategies"""
        doc_id = f"pattern_{pattern_type}_{datetime.now().timestamp()}"

        text = f"""
        Pattern Type: {pattern_type}
        Characteristics: {json.dumps(characteristics)}
        Recommended Models: {', '.join(characteristics.get('recommended_models', []))}
        Features: {', '.join(characteristics.get('features', []))}
        """

        self.collections['patterns'].add(
            documents=[text],
            metadatas=[{
                'pattern_type': pattern_type,
                'seasonality': str(characteristics.get('seasonality', '')),
                'trend': str(characteristics.get('trend', '')),
                'success_rate': str(characteristics.get('success_rate', 0))
            }],
            ids=[doc_id]
        )

    def store_error_solution(self, error_type: str, solution: Dict[str, Any]):
        """Store error patterns and their solutions"""
        doc_id = f"error_{error_type}_{datetime.now().timestamp()}"

        text = f"""
        Error Type: {error_type}
        Symptoms: {solution.get('symptoms', '')}
        Root Cause: {solution.get('root_cause', '')}
        Solution: {solution.get('solution', '')}
        Prevention: {solution.get('prevention', '')}
        """

        self.collections['errors'].add(
            documents=[text],
            metadatas=[{
                'error_type': error_type,
                'severity': solution.get('severity', 'medium'),
                'solved': 'true',
                'timestamp': datetime.now().isoformat()
            }],
            ids=[doc_id]
        )

    def find_similar_decisions(self, context: str, n_results: int = 5) -> List[Dict]:
        """Find similar past decisions based on context"""
        results = self.collections['decisions'].query(
            query_texts=[context],
            n_results=n_results
        )

        return self._format_results(results)

    def find_pattern_strategies(self, pattern_description: str, n_results: int = 3) -> List[Dict]:
        """Find strategies for handling similar patterns"""
        results = self.collections['patterns'].query(
            query_texts=[pattern_description],
            n_results=n_results
        )

        return self._format_results(results)

    def find_error_solutions(self, error_description: str, n_results: int = 3) -> List[Dict]:
        """Find solutions for similar errors"""
        results = self.collections['errors'].query(
            query_texts=[error_description],
            n_results=n_results
        )

        return self._format_results(results)

    def _format_results(self, results: Dict) -> List[Dict]:
        """Format query results"""
        formatted = []
        if results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                formatted.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        return formatted

    def get_statistics(self) -> Dict[str, int]:
        """Get knowledge base statistics"""
        return {
            'total_decisions': self.collections['decisions'].count(),
            'total_patterns': self.collections['patterns'].count(),
            'total_strategies': self.collections['strategies'].count(),
            'total_error_solutions': self.collections['errors'].count()
        }


# Usage Example
if __name__ == "__main__":
    # Initialize knowledge base
    kb = AgenticKnowledgeBase()

    # Store a decision
    kb.store_decision(
        agent_id="model_selection_agent",
        decision={
            'context': 'Weekly seasonal data with upward trend',
            'action': 'Selected SARIMA model with ensemble',
            'reasoning': 'SARIMA handles seasonality well, ensemble adds robustness',
            'outcome': 'MAPE improved from 15% to 8.5%',
            'performance': 0.915,
            'confidence': 0.92,
            'tags': ['seasonality', 'trend', 'ensemble']
        }
    )

    # Store a pattern
    kb.store_pattern(
        pattern_type='weekly_seasonality_with_trend',
        characteristics={
            'seasonality': 'weekly',
            'trend': 'upward',
            'recommended_models': ['SARIMA', 'Prophet', 'N-BEATS'],
            'features': ['lag_7', 'lag_14', 'day_of_week', 'rolling_mean_7'],
            'success_rate': 0.92
        }
    )

    # Store an error solution
    kb.store_error_solution(
        error_type='forecast_drift',
        solution={
            'symptoms': 'Forecast accuracy degrading over time',
            'root_cause': 'Concept drift in underlying data distribution',
            'solution': 'Retrain model with recent data, implement sliding window',
            'prevention': 'Monitor distribution shift, set up automated retraining',
            'severity': 'high'
        }
    )

    # Query for similar decisions
    print("\n=== Finding Similar Decisions ===")
    similar = kb.find_similar_decisions(
        "Need to forecast data with daily seasonality and trend"
    )
    for result in similar:
        print(f"\nSimilarity: {1 - result['distance']:.2%}")
        print(f"Document: {result['document'][:200]}...")

    # Query for pattern strategies
    print("\n=== Finding Pattern Strategies ===")
    strategies = kb.find_pattern_strategies(
        "Weekly patterns in sales data"
    )
    for result in strategies:
        print(f"\nDocument: {result['document'][:200]}...")

    # Get statistics
    print("\n=== Knowledge Base Statistics ===")
    stats = kb.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
```

---

## Integration with Agents

Update agents to use knowledge base:

```python
class DataAgentWithKB(BaseAgent):
    def __init__(self, knowledge_base: AgenticKnowledgeBase):
        super().__init__("data_agent_001", "Data Agent")
        self.kb = knowledge_base

    def reason(self, context: Dict[str, Any]) -> List[ReasoningStep]:
        # Check knowledge base for similar patterns
        pattern_desc = f"Data with {context.get('patterns', [])}"
        similar_patterns = self.kb.find_pattern_strategies(pattern_desc)

        steps = []

        if similar_patterns:
            # Use learned knowledge
            step = ReasoningStep(
                thought=f"Found {len(similar_patterns)} similar patterns in knowledge base",
                action="Apply learned strategies from past successes",
                observation=f"Past strategies: {similar_patterns[0]['metadata']}",
                reflection="Leveraging institutional knowledge improves decisions",
                confidence=0.95
            )
            steps.append(step)
        else:
            # No similar patterns, proceed with fresh analysis
            step = ReasoningStep(
                thought="No similar patterns found, analyzing from first principles",
                action="Perform comprehensive pattern analysis",
                observation="New pattern - will add to knowledge base",
                reflection="This will be valuable for future cases",
                confidence=0.75
            )
            steps.append(step)

        return steps

    def act(self, task: Dict[str, Any]) -> AgentMessage:
        # ... existing logic ...

        # Store decision in knowledge base
        self.kb.store_decision(
            agent_id=self.agent_id,
            decision={
                'context': str(task.get('context')),
                'action': 'Data quality analysis completed',
                'reasoning': str(reasoning_steps),
                'outcome': str(results),
                'performance': 0.9,
                'confidence': 0.92
            }
        )

        return message
```

---

## Recommendation Summary

### **For Time Series Forecasting Agentic AI:**

**Best Overall Choice: Hybrid Approach**
```
ChromaDB (Semantic Search) + PostgreSQL (Metrics/History)
```

**Why:**
1. **ChromaDB**: Easy setup, great for finding similar forecasting scenarios
2. **PostgreSQL**: Reliable storage for structured performance metrics
3. **Cost-effective**: Both can run locally or with minimal infrastructure
4. **Python-native**: Seamless integration
5. **Scalable**: Can upgrade to Pinecone + TimescaleDB later

**Quick Start:**
```bash
pip install chromadb sqlalchemy psycopg2-binary pandas
```

This gives you:
- ✅ Semantic search for agent reasoning
- ✅ Structured storage for metrics
- ✅ Easy development and testing
- ✅ Clear upgrade path to production scale
