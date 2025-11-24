"""
Reasoning Agentic AI Pipeline with Knowledge Base Integration

This module demonstrates the agentic AI pipeline enhanced with a ChromaDB-based
knowledge base for storing and retrieving learned experiences.

Installation:
    pip install chromadb sentence-transformers
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
import json
from datetime import datetime

# Note: ChromaDB import - install with: pip install chromadb
try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  ChromaDB not installed. Running in demo mode.")
    print("   Install with: pip install chromadb sentence-transformers")


class AgentStatus(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ReasoningStep:
    """Represents a single step in the reasoning chain"""
    thought: str
    action: str
    observation: str
    reflection: str
    confidence: float
    knowledge_used: Optional[str] = None  # New: track if KB was used


class AgenticKnowledgeBase:
    """
    Knowledge base for storing and retrieving agent decisions,
    patterns, and learned experiences using ChromaDB
    """

    def __init__(self, persist_directory: str = "./agent_knowledge_base"):
        if not CHROMADB_AVAILABLE:
            print("Running in mock mode - ChromaDB not available")
            self.mock_mode = True
            self.mock_storage = {
                'decisions': [],
                'patterns': [],
                'errors': []
            }
            return

        self.mock_mode = False

        # Initialize ChromaDB with persistence
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
            'errors': self._get_or_create_collection('error_solutions')
        }

        print(f"✓ Knowledge Base initialized at: {persist_directory}")

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
        if self.mock_mode:
            self.mock_storage['decisions'].append({
                'agent_id': agent_id,
                'decision': decision,
                'timestamp': datetime.now().isoformat()
            })
            return

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
        if self.mock_mode:
            self.mock_storage['patterns'].append({
                'pattern_type': pattern_type,
                'characteristics': characteristics,
                'timestamp': datetime.now().isoformat()
            })
            return

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

    def find_similar_decisions(self, context: str, n_results: int = 3) -> List[Dict]:
        """Find similar past decisions based on context"""
        if self.mock_mode:
            # Return mock results
            return [{
                'id': 'mock_001',
                'document': 'Previous similar case: Used SARIMA for weekly seasonal data',
                'metadata': {'performance': '0.92', 'confidence': '0.88'},
                'distance': 0.15
            }]

        try:
            results = self.collections['decisions'].query(
                query_texts=[context],
                n_results=n_results
            )
            return self._format_results(results)
        except:
            return []

    def find_pattern_strategies(self, pattern_description: str, n_results: int = 3) -> List[Dict]:
        """Find strategies for handling similar patterns"""
        if self.mock_mode:
            return [{
                'id': 'pattern_mock_001',
                'document': 'Pattern: weekly_seasonality - Use SARIMA, Prophet, or N-BEATS',
                'metadata': {'success_rate': '0.92'},
                'distance': 0.12
            }]

        try:
            results = self.collections['patterns'].query(
                query_texts=[pattern_description],
                n_results=n_results
            )
            return self._format_results(results)
        except:
            return []

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
        if self.mock_mode:
            return {
                'total_decisions': len(self.mock_storage['decisions']),
                'total_patterns': len(self.mock_storage['patterns']),
                'total_error_solutions': len(self.mock_storage['errors'])
            }

        return {
            'total_decisions': self.collections['decisions'].count(),
            'total_patterns': self.collections['patterns'].count(),
            'total_error_solutions': self.collections['errors'].count()
        }


class BaseAgent:
    """Base class for all specialized agents with KB integration"""

    def __init__(self, agent_id: str, name: str, knowledge_base: AgenticKnowledgeBase):
        self.agent_id = agent_id
        self.name = name
        self.status = AgentStatus.IDLE
        self.kb = knowledge_base  # Knowledge base reference

    def reason(self, context: Dict[str, Any]) -> List[ReasoningStep]:
        """Implement reasoning chain - override in specialized agents"""
        raise NotImplementedError

    def act(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task - override in specialized agents"""
        raise NotImplementedError


class DataAgentWithKB(BaseAgent):
    """
    Data Agent enhanced with knowledge base for learning from past experiences
    """

    def __init__(self, knowledge_base: AgenticKnowledgeBase):
        super().__init__("data_agent_001", "Data Agent", knowledge_base)

    def reason(self, context: Dict[str, Any]) -> List[ReasoningStep]:
        """Reasoning chain enhanced with knowledge base lookup"""
        steps = []

        # Step 0: Check knowledge base for similar patterns
        pattern_desc = f"Data patterns: {context.get('patterns', [])}"
        similar_patterns = self.kb.find_pattern_strategies(pattern_desc)

        if similar_patterns and len(similar_patterns) > 0:
            kb_info = similar_patterns[0]
            step0 = ReasoningStep(
                thought="Checking knowledge base for similar data patterns encountered before",
                action="Query knowledge base with pattern characteristics",
                observation=f"Found {len(similar_patterns)} similar pattern(s) in knowledge base",
                reflection=f"KB suggests: {kb_info['document'][:100]}... (confidence from past: {kb_info['metadata'].get('success_rate', 'N/A')})",
                confidence=0.95,
                knowledge_used=f"Pattern ID: {kb_info['id']}"
            )
            steps.append(step0)

        # Step 1: Assess data availability
        step1 = ReasoningStep(
            thought="Need to verify sufficient historical data is available",
            action="Load and inspect data shape and coverage",
            observation=f"Found {context.get('data_points', 0)} data points",
            reflection="Data volume is adequate for modeling" if context.get('data_points', 0) > 1000
                      else "May need more data for robust modeling",
            confidence=0.9 if context.get('data_points', 0) > 1000 else 0.6
        )
        steps.append(step1)

        # Step 2: Check data quality
        step2 = ReasoningStep(
            thought="Data quality issues can severely impact forecast accuracy",
            action="Scan for missing values, outliers, and anomalies",
            observation=f"Missing: {context.get('missing_pct', 0)}%, Outliers: {context.get('outliers', 0)}",
            reflection="Quality is acceptable, minor cleaning needed" if context.get('missing_pct', 0) < 5
                      else "Significant quality issues detected",
            confidence=0.95 if context.get('missing_pct', 0) < 5 else 0.7
        )
        steps.append(step2)

        # Step 3: Identify temporal patterns
        step3 = ReasoningStep(
            thought="Understanding temporal patterns helps select appropriate models",
            action="Analyze autocorrelation, trend, and seasonality",
            observation=f"Detected: {context.get('patterns', [])}",
            reflection="Clear patterns identified that can guide model selection",
            confidence=0.85
        )
        steps.append(step3)

        return steps

    def act(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data analysis task with KB integration"""
        self.status = AgentStatus.THINKING

        context = {
            'data_points': 5000,
            'missing_pct': 2.5,
            'outliers': 15,
            'patterns': ['weekly_seasonality', 'upward_trend']
        }

        reasoning_steps = self.reason(context)
        self.status = AgentStatus.ACTING

        results = {
            'data_shape': (5000, 3),
            'data_quality': 'good',
            'temporal_patterns': ['weekly_seasonality', 'upward_trend'],
            'recommendations': [
                'Use seasonal models',
                'Consider trend modeling',
                'Interpolate missing values'
            ]
        }

        # Store decision in knowledge base
        self.kb.store_decision(
            agent_id=self.agent_id,
            decision={
                'context': f"Analyzed {context['data_points']} data points",
                'action': 'Data quality analysis and pattern detection',
                'reasoning': f"{len(reasoning_steps)} reasoning steps executed",
                'outcome': f"Quality: {results['data_quality']}, Patterns: {results['temporal_patterns']}",
                'performance': 0.92,
                'confidence': 0.90,
                'tags': ['data_analysis', 'quality_check', 'pattern_detection']
            }
        )

        # Store pattern for future reference
        self.kb.store_pattern(
            pattern_type='weekly_seasonality_with_trend',
            characteristics={
                'seasonality': 'weekly',
                'trend': 'upward',
                'data_quality': 'good',
                'recommended_models': ['SARIMA', 'Prophet', 'N-BEATS'],
                'features': ['lag_7', 'day_of_week', 'rolling_mean_7'],
                'success_rate': 0.92
            }
        )

        self.status = AgentStatus.COMPLETED

        return {
            'task_id': task.get('task_id'),
            'agent_id': self.agent_id,
            'status': 'success',
            'results': results,
            'reasoning': reasoning_steps,
            'next_agent': 'feature_engineering_agent'
        }


class ModelSelectionAgentWithKB(BaseAgent):
    """
    Model Selection Agent enhanced with knowledge base
    """

    def __init__(self, knowledge_base: AgenticKnowledgeBase):
        super().__init__("model_sel_agent_001", "Model Selection Agent", knowledge_base)

    def reason(self, context: Dict[str, Any]) -> List[ReasoningStep]:
        """Reasoning chain with KB-informed model selection"""
        steps = []

        # Check KB for similar forecasting scenarios
        scenario_desc = f"Forecast with patterns: {context.get('patterns', [])}, horizon: {context.get('forecast_horizon', 30)} days"
        similar_decisions = self.kb.find_similar_decisions(scenario_desc)

        if similar_decisions:
            kb_info = similar_decisions[0]
            step0 = ReasoningStep(
                thought="Consulting knowledge base for similar forecasting scenarios",
                action="Retrieve past model selection decisions with similar characteristics",
                observation=f"Found {len(similar_decisions)} similar case(s)",
                reflection=f"Past experience: {kb_info['document'][:120]}...",
                confidence=0.93,
                knowledge_used=f"Decision ID: {kb_info['id']}"
            )
            steps.append(step0)

        patterns = context.get('patterns', [])
        horizon = context.get('forecast_horizon', 30)

        # Model complexity reasoning
        step1 = ReasoningStep(
            thought=f"With {context.get('data_points', 0)} points, assess model complexity budget",
            action="Evaluate data sufficiency for complex models",
            observation="Sufficient data for ensemble approaches",
            reflection="Can use multiple models and create ensemble for robustness",
            confidence=0.9
        )
        steps.append(step1)

        # Seasonality handling
        if 'weekly_seasonality' in patterns:
            step2 = ReasoningStep(
                thought="Strong seasonal patterns require specialized models",
                action="Prioritize seasonal models (SARIMA, Prophet, seasonal ML)",
                observation="Multiple seasonal models available",
                reflection="Combining statistical and ML approaches will be robust",
                confidence=0.92
            )
            steps.append(step2)

        return steps

    def act(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute model selection with KB integration"""
        self.status = AgentStatus.THINKING

        context = task.get('context', {})
        reasoning_steps = self.reason(context)

        self.status = AgentStatus.ACTING

        selected_models = {
            'statistical': ['SARIMA', 'Prophet'],
            'machine_learning': ['XGBoost', 'LightGBM'],
            'deep_learning': ['N-BEATS'],
            'ensemble': 'WeightedAverage'
        }

        results = {
            'selected_models': selected_models,
            'rationale': {
                'SARIMA': 'Handles seasonality and trend well',
                'Prophet': 'Robust to missing data',
                'XGBoost': 'Captures non-linear patterns',
                'N-BEATS': 'State-of-art deep learning',
                'Ensemble': 'Combines strengths'
            },
            'expected_performance': 'MAPE < 10%'
        }

        # Store decision
        self.kb.store_decision(
            agent_id=self.agent_id,
            decision={
                'context': f"Patterns: {context.get('patterns', [])}, Horizon: {context.get('forecast_horizon')} days",
                'action': f"Selected {sum(len(v) if isinstance(v, list) else 1 for v in selected_models.values())} models",
                'reasoning': 'Multi-model ensemble for robustness',
                'outcome': results['expected_performance'],
                'performance': 0.915,
                'confidence': 0.90,
                'tags': ['model_selection', 'ensemble', 'seasonality']
            }
        )

        self.status = AgentStatus.COMPLETED

        return {
            'task_id': task.get('task_id'),
            'agent_id': self.agent_id,
            'status': 'success',
            'results': results,
            'reasoning': reasoning_steps,
            'next_agent': 'validation_agent'
        }


class OrchestratorWithKB:
    """
    Orchestrator enhanced with knowledge base
    """

    def __init__(self, knowledge_base: AgenticKnowledgeBase):
        self.agent_id = "orchestrator_001"
        self.kb = knowledge_base
        self.agents = {
            'data': DataAgentWithKB(knowledge_base),
            'model_selection': ModelSelectionAgentWithKB(knowledge_base)
        }
        self.workflow_state = {}

    def execute_workflow(self, workflow: List[str], initial_context: Dict[str, Any]):
        """Execute workflow with KB-enhanced agents"""
        context = initial_context
        results = {}

        for agent_name in workflow:
            print(f"\n{'-'*80}")
            print(f"Executing: {agent_name.replace('_', ' ').title()} Agent")
            print(f"{'-'*80}")

            agent = self.agents[agent_name]

            task = {
                'task_id': f"{agent_name}_{datetime.now().timestamp()}",
                'context': context
            }

            # Execute task
            message = agent.act(task)

            # Display reasoning with KB usage highlighted
            if message.get('reasoning'):
                print(f"\n🧠 Reasoning Chain ({len(message['reasoning'])} steps):")
                for i, step in enumerate(message['reasoning'], 1):
                    print(f"\n  Step {i}:")
                    print(f"    💭 Thought: {step.thought}")
                    print(f"    🎬 Action: {step.action}")
                    print(f"    👁️  Observation: {step.observation}")
                    print(f"    🤔 Reflection: {step.reflection}")
                    print(f"    📊 Confidence: {step.confidence:.2%}")
                    if step.knowledge_used:
                        print(f"    📚 Knowledge Used: {step.knowledge_used}")

            # Display results
            print(f"\n📋 Results:")
            payload_results = message.get('results', {})
            for key, value in payload_results.items():
                if isinstance(value, list) and len(value) > 5:
                    print(f"  • {key}: {value[:5]} ... ({len(value)} total)")
                elif isinstance(value, dict):
                    print(f"  • {key}:")
                    for k, v in value.items():
                        print(f"      - {k}: {v}")
                else:
                    print(f"  • {key}: {value}")

            results[agent_name] = message['results']

            # Update context
            if 'patterns' not in context and agent_name == 'data':
                context['patterns'] = results['data'].get('temporal_patterns', [])
                context['data_points'] = 5000
                context['forecast_horizon'] = 30

        return results


def main():
    """Main execution with knowledge base integration"""
    print("\n" + "="*80)
    print(" "*15 + "REASONING AGENTIC AI PIPELINE")
    print(" "*20 + "With Knowledge Base Integration")
    print("="*80 + "\n")

    # Initialize knowledge base
    print("Initializing Knowledge Base...")
    kb = AgenticKnowledgeBase()

    # Pre-populate with some knowledge (simulating learning from past)
    print("\n📚 Pre-populating knowledge base with past experiences...")
    kb.store_pattern(
        pattern_type='daily_seasonality',
        characteristics={
            'seasonality': 'daily',
            'trend': 'stable',
            'recommended_models': ['SARIMA', 'Prophet'],
            'features': ['hour_of_day', 'day_of_week'],
            'success_rate': 0.88
        }
    )

    # Initialize orchestrator with KB
    orchestrator = OrchestratorWithKB(kb)

    # Workflow
    workflow = ['data', 'model_selection']
    initial_context = {
        'data_points': 5000,
        'forecast_horizon': 30,
        'frequency': 'daily'
    }

    # Execute
    results = orchestrator.execute_workflow(workflow, initial_context)

    # Show KB statistics
    print(f"\n{'='*80}")
    print("KNOWLEDGE BASE STATISTICS")
    print(f"{'='*80}\n")

    stats = kb.get_statistics()
    for key, value in stats.items():
        print(f"  • {key.replace('_', ' ').title()}: {value}")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
