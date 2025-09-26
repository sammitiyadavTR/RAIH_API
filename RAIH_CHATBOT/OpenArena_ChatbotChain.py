import re
import logging
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from langchain.schema import HumanMessage, SystemMessage
from SQLAgent import SimpleSQLAgent, SQLAgent, OpenAIClient
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Enumeration for query types"""
    SQL_QUERY = "sql"
    RAG_QUERY = "rag"
    AMBIGUOUS = "ambiguous"

@dataclass
class ClassificationResult:
    """Result of query classification"""
    query_type: QueryType
    confidence: float
    reasoning: str
    suggested_route: str

class QueryClassifier:
    """Advanced query classifier using multiple classification strategies"""
    
    def __init__(self, llm_client, db_agent):
        self.llm = llm_client
        self.db_agent = db_agent
        self.available_tables = []
        self.table_columns = {}
        self._initialize_db_schema()
        
        self.sql_keywords = {
            # Strong SQL indicators
            'select': 0.9, 'from': 0.9, 'where': 0.9, 'join': 0.9, 'group by': 0.9,
            'order by': 0.9, 'having': 0.9, 'count': 0.8, 'sum': 0.8, 'avg': 0.8,
            'max': 0.8, 'min': 0.8, 'distinct': 0.8, 'limit': 0.8, 'top': 0.8,
            
            # Data operation indicators
            'show me': 0.7, 'list': 0.7, 'find': 0.6, 'get': 0.6, 'retrieve': 0.6,
            'display': 0.6, 'fetch': 0.6, 'extract': 0.6, 'query': 0.7,
            
            # Quantitative indicators
            'how many': 0.8, 'how much': 0.8, 'total': 0.7, 'number of': 0.7,
            'amount': 0.7, 'revenue': 0.7, 'sales': 0.7, 'profit': 0.7,
            'cost': 0.7, 'price': 0.7, 'value': 0.6,
            
            # Comparison indicators
            'compare': 0.7, 'versus': 0.7, 'vs': 0.7, 'between': 0.6,
            'greater than': 0.7, 'less than': 0.7, 'highest': 0.8, 'lowest': 0.8,
            'best': 0.7, 'worst': 0.7, 'top': 0.8, 'bottom': 0.8,
            
            # Time-based indicators
            'last': 0.7, 'previous': 0.7, 'recent': 0.7, 'current': 0.7,
            'this year': 0.7, 'this month': 0.7, 'today': 0.7, 'yesterday': 0.7,
            'trend': 0.7, 'over time': 0.7, 'monthly': 0.7, 'yearly': 0.7,
            'quarterly': 0.7, 'daily': 0.7
        }
        

        self.rag_keywords = {
            # Conceptual/explanation indicators
            'what is': 0.9, 'explain': 0.9, 'describe': 0.9, 'define': 0.9,
            'how does': 0.8, 'why': 0.8, 'concept': 0.8, 'meaning': 0.8,
            'definition': 0.8, 'overview': 0.8, 'introduction': 0.7,
            
            # Knowledge-based indicators
            'tell me about': 0.8, 'information about': 0.8, 'details about': 0.7,
            'background': 0.7, 'history': 0.7, 'context': 0.7, 'summary': 0.7,
            
            # Process/procedure indicators
            'how to': 0.8, 'steps': 0.7, 'process': 0.7, 'procedure': 0.7,
            'method': 0.7, 'approach': 0.7, 'way to': 0.7, 'guide': 0.7,
            
            # Analysis/interpretation indicators
            'analyze': 0.7, 'interpretation': 0.7, 'insight': 0.7, 'opinion': 0.8,
            'recommendation': 0.8, 'advice': 0.8, 'suggestion': 0.8,
            
            # General knowledge indicators
            'generally': 0.6, 'typically': 0.6, 'usually': 0.6, 'common': 0.6,
            'best practice': 0.8, 'standard': 0.7, 'policy': 0.7, 'regulation': 0.7
        }
    
    def _initialize_db_schema(self):
        """Initialize database schema information for better classification"""
        try:
            self.available_tables = self.db_agent.get_available_tables()
            
            for table in self.available_tables[:18]:  
                try:
                    table_info = self.db_agent.get_table_ddl(table)
                    if table_info.columns:
                        self.table_columns[table.lower()] = [
                            col['COLUMN_NAME'].lower() for col in table_info.columns
                        ]
                except Exception as e:
                    logger.warning(f"Could not get schema for table {table}: {e}")
                    continue
            
            logger.info(f"Initialized schema for {len(self.table_columns)} tables")
            
        except Exception as e:
            logger.error(f"Error initializing database schema: {e}")
            self.available_tables = []
            self.table_columns = {}
    
    def _keyword_analysis(self, query: str) -> Tuple[float, float]:
        """Analyze query using keyword matching"""
        query_lower = query.lower()
        
        sql_score = 0.0
        sql_matches = 0
        for keyword, weight in self.sql_keywords.items():
            if keyword in query_lower:
                sql_score += weight
                sql_matches += 1
        
        rag_score = 0.0
        rag_matches = 0
        for keyword, weight in self.rag_keywords.items():
            if keyword in query_lower:
                rag_score += weight
                rag_matches += 1
        
        # Normalize scores
        if sql_matches > 0:
            sql_score = sql_score / sql_matches
        if rag_matches > 0:
            rag_score = rag_score / rag_matches
        
        return sql_score, rag_score
    
    def _database_context_analysis(self, query: str) -> float:
        """Analyze if query references database tables or columns"""
        query_lower = query.lower()
        context_score = 0.0
        
        # Check for table name references
        table_matches = 0
        for table in self.available_tables:
            if table.lower() in query_lower:
                context_score += 0.8
                table_matches += 1
        
        # Check for column name references
        column_matches = 0
        for table, columns in self.table_columns.items():
            for column in columns:
                if column in query_lower and len(column) > 3:  
                    context_score += 0.6
                    column_matches += 1
        
        
        db_terms = ['table', 'database', 'record', 'row', 'column', 'field', 'data']
        db_term_matches = sum(1 for term in db_terms if term in query_lower)
        context_score += db_term_matches * 0.3
        
        # Normalize based on matches found
        total_matches = table_matches + column_matches + db_term_matches
        if total_matches > 0:
            context_score = min(context_score / total_matches, 1.0)
        
        return context_score
    
    def _pattern_analysis(self, query: str) -> Tuple[float, float]:
        """Analyze query patterns using regex"""
        sql_patterns = [
            r'\b(show|list|get|find|retrieve)\s+(all|top|first|\d+)?\s*\w+',
            r'\b(how many|count of|number of|total)\b',
            r'\b(sum|average|max|min|count)\s+of\b',
            r'\b(greater than|less than|between|equals?)\s+\d+',
            r'\b(last|previous|recent|current)\s+(year|month|week|day)',
            r'\b(compare|versus|vs)\b',
            r'\b(group by|order by|sort by)\b',
            r'\bwhere\s+\w+\s*(=|>|<|>=|<=)',
            r'\b(join|inner join|left join|right join)\b'
        ]
        
        rag_patterns = [
            r'\b(what is|what are|what does)\b',
            r'\b(explain|describe|define)\b',
            r'\b(how to|how do|how can)\b',
            r'\b(why|because|reason)\b',
            r'\b(tell me about|information about)\b',
            r'\b(concept of|meaning of|definition of)\b',
            r'\b(best practice|recommendation|advice)\b',
            r'\b(generally|typically|usually|commonly)\b'
        ]
        
        query_lower = query.lower()
        
        # Count SQL pattern matches
        sql_pattern_score = 0.0
        for pattern in sql_patterns:
            if re.search(pattern, query_lower):
                sql_pattern_score += 1.0
        sql_pattern_score = min(sql_pattern_score / len(sql_patterns), 1.0)
        
        # Count RAG pattern matches
        rag_pattern_score = 0.0
        for pattern in rag_patterns:
            if re.search(pattern, query_lower):
                rag_pattern_score += 1.0
        rag_pattern_score = min(rag_pattern_score / len(rag_patterns), 1.0)
        
        return sql_pattern_score, rag_pattern_score
    
    def _llm_classification(self, query: str) -> Tuple[QueryType, float, str]:
        """Use LLM for sophisticated classification"""
        # Create context about available tables
        tables_context = ""
        if self.available_tables:
            tables_sample = self.available_tables[:10]  # Show first 10 tables
            tables_context = f"Available database tables include: {', '.join(tables_sample)}"
            if len(self.available_tables) > 10:
                tables_context += f" (and {len(self.available_tables) - 10} more)"
        
        prompt = f"""
You are a query classifier that determines whether a user question should be routed to a SQL database agent or a RAG knowledge base agent.

{tables_context}

Classification Guidelines:

SQL DATABASE AGENT - Route here if the query:
- Requests specific data from tables/databases
- Asks for counts, sums, averages, or other calculations
- Needs filtering, sorting, or aggregation of structured data
- Asks "how many", "show me", "list", "find records"
- Requests comparisons between data points
- Asks for trends, reports, or analytics from data
- References table names or data fields
- Needs real-time or current data from the database

RAG KNOWLEDGE AGENT - Route here if the query:
- Asks for explanations, definitions, or concepts
- Requests "what is", "explain", "describe", "define"
- Asks "how to" or procedural questions
- Seeks general knowledge or background information
- Asks for recommendations, best practices, or advice
- Requests analysis or interpretation (not raw data)
- Asks about policies, regulations, or guidelines
- Seeks opinions or subjective information

User Query: "{query}"

Respond with exactly this format:
CLASSIFICATION: [SQL or RAG]
CONFIDENCE: [0.0-1.0]
REASONING: [Brief explanation of why this classification was chosen]

Examples:
- "How many customers do we have?" → SQL (requests count from database)
- "What is customer segmentation?" → RAG (asks for concept explanation)
- "Show me top 10 sales by region" → SQL (requests specific data with sorting)
- "Explain how to improve customer retention" → RAG (asks for advice/strategy)
"""
        
        try:
            messages = [
                SystemMessage(content="You are an expert query classifier. Analyze queries and determine the best routing."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.generate_response(messages, temperature=0.1)
            
            # Parse the response
            lines = response.strip().split('\n')
            classification = QueryType.AMBIGUOUS
            confidence = 0.5
            reasoning = "Could not parse LLM response"
            
            for line in lines:
                line = line.strip()
                if line.startswith('CLASSIFICATION:'):
                    class_text = line.replace('CLASSIFICATION:', '').strip().upper()
                    if 'SQL' in class_text:
                        classification = QueryType.SQL_QUERY
                    elif 'RAG' in class_text:
                        classification = QueryType.RAG_QUERY
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line.replace('CONFIDENCE:', '').strip())
                        confidence = max(0.0, min(1.0, confidence))  # Clamp to [0,1]
                    except ValueError:
                        confidence = 0.5
                elif line.startswith('REASONING:'):
                    reasoning = line.replace('REASONING:', '').strip()
            
            return classification, confidence, reasoning
            
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return QueryType.AMBIGUOUS, 0.5, f"LLM classification error: {str(e)}"
    
    def classify_query(self, query: str) -> ClassificationResult:
        """Main classification method combining multiple strategies"""
        logger.info(f"Classifying query: {query}")
        
        # Strategy 1: Keyword analysis
        sql_keyword_score, rag_keyword_score = self._keyword_analysis(query)
        
        # Strategy 2: Database context analysis
        db_context_score = self._database_context_analysis(query)
        
        # Strategy 3: Pattern analysis
        sql_pattern_score, rag_pattern_score = self._pattern_analysis(query)
        
        # Strategy 4: LLM classification
        llm_classification, llm_confidence, llm_reasoning = self._llm_classification(query)
        
        # Combine scores with weights
        weights = {
            'keyword': 0.25,
            'context': 0.25,
            'pattern': 0.25,
            'llm': 0.25
        }
        
        # Calculate final SQL score
        final_sql_score = (
            weights['keyword'] * sql_keyword_score +
            weights['context'] * db_context_score +
            weights['pattern'] * sql_pattern_score +
            weights['llm'] * (1.0 if llm_classification == QueryType.SQL_QUERY else 0.0) * llm_confidence
        )
        
        # Calculate final RAG score
        final_rag_score = (
            weights['keyword'] * rag_keyword_score +
            weights['context'] * (1.0 - db_context_score) +  # Inverse of DB context
            weights['pattern'] * rag_pattern_score +
            weights['llm'] * (1.0 if llm_classification == QueryType.RAG_QUERY else 0.0) * llm_confidence
        )
        
        # Determine final classification
        if abs(final_sql_score - final_rag_score) < 0.1:  # Very close scores
            final_classification = QueryType.AMBIGUOUS
            confidence = 0.5
            reasoning = f"Ambiguous query. SQL score: {final_sql_score:.2f}, RAG score: {final_rag_score:.2f}"
        elif final_sql_score > final_rag_score:
            final_classification = QueryType.SQL_QUERY
            confidence = min(final_sql_score, 0.95)  # Cap at 95%
            reasoning = f"SQL classification. Scores - SQL: {final_sql_score:.2f}, RAG: {final_rag_score:.2f}. {llm_reasoning}"
        else:
            final_classification = QueryType.RAG_QUERY
            confidence = min(final_rag_score, 0.95)  # Cap at 95%
            reasoning = f"RAG classification. Scores - SQL: {final_sql_score:.2f}, RAG: {final_rag_score:.2f}. {llm_reasoning}"
        
        # Determine suggested route
        if final_classification == QueryType.SQL_QUERY:
            suggested_route = "SQL Database Agent"
        elif final_classification == QueryType.RAG_QUERY:
            suggested_route = "RAG Knowledge Agent"
        else:
            suggested_route = "Manual Review Required"
        
        result = ClassificationResult(
            query_type=final_classification,
            confidence=confidence,
            reasoning=reasoning,
            suggested_route=suggested_route
        )
        
        logger.info(f"Classification result: {result.query_type.value} (confidence: {result.confidence:.2f})")
        return result


class RouterAgent:
    """Main router agent that classifies and routes queries"""

    def __init__(self, sql_agent, llm_client, confidence_threshold: float = 0.7):
        self.sql_agent = sql_agent
        self.llm_client = llm_client
        self.classifier = QueryClassifier(llm_client, sql_agent)
        self.confidence_threshold = confidence_threshold
        # Initialize RAG function
        self.process_regular_query = process_regular_query

    def route_query(self, query: str, force_route: Optional[str] = None) -> Dict[str, any]:
        result = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'classification': None,
            'response': None,
            'agent_used': None,
            'execution_time': 0,
            'success': False,
            'error': None
        }

        start_time = time.time()

        try:
            # Parse force routing
            if query.lower().startswith('force sql '):
                force_route = 'sql'
                query = query[10:].strip()
            elif query.lower().startswith('force rag '):
                force_route = 'rag'
                query = query[10:].strip()

            # Force routing if specified
            if force_route:
                if force_route.lower() == 'sql':
                    classification_result = ClassificationResult(
                        query_type=QueryType.SQL_QUERY,
                        confidence=1.0,
                        reasoning="Forced SQL routing",
                        suggested_route="SQL Database Agent"
                    )
                elif force_route.lower() == 'rag':
                    classification_result = ClassificationResult(
                        query_type=QueryType.RAG_QUERY,
                        confidence=1.0,
                        reasoning="Forced RAG routing",
                        suggested_route="RAG Knowledge Agent"
                    )
            else:
                # Classify the query
                classification_result = self.classifier.classify_query(query)

            result['classification'] = {
                'type': classification_result.query_type.value,
                'confidence': classification_result.confidence,
                'reasoning': classification_result.reasoning,
                'suggested_route': classification_result.suggested_route
            }

            # Route based on classification
            if classification_result.query_type == QueryType.SQL_QUERY:
                if classification_result.confidence >= self.confidence_threshold or force_route:
                    response = self.sql_agent.ask(query)
                    result['response'] = response
                    result['agent_used'] = 'SQL Database Agent'
                    result['success'] = True
                else:
                    result['response'] = self._request_clarification(query, classification_result)
                    result['agent_used'] = 'Router (Clarification)'
                    result['success'] = True

            elif classification_result.query_type == QueryType.RAG_QUERY:
                if classification_result.confidence >= max(0.4, self.confidence_threshold * 0.6) or force_route:
                    response = self.process_regular_query(query)
                    result['response'] = response
                    result['agent_used'] = 'RAG Knowledge Agent'
                    result['success'] = True
                else:
                    result['response'] = self._request_clarification(query, classification_result)
                    result['agent_used'] = 'Router (Clarification)'
                    result['success'] = True

            else:  # AMBIGUOUS
                # Instead of error, route to agent with highest score
                # Get scores from classifier
                sql_keyword_score, rag_keyword_score = self.classifier._keyword_analysis(query)
                db_context_score = self.classifier._database_context_analysis(query)
                sql_pattern_score, rag_pattern_score = self.classifier._pattern_analysis(query)
                llm_classification, llm_confidence, llm_reasoning = self.classifier._llm_classification(query)
                weights = {
                    'keyword': 0.25,
                    'context': 0.25,
                    'pattern': 0.25,
                    'llm': 0.25
                }
                final_sql_score = (
                    weights['keyword'] * sql_keyword_score +
                    weights['context'] * db_context_score +
                    weights['pattern'] * sql_pattern_score +
                    weights['llm'] * (1.0 if llm_classification == QueryType.SQL_QUERY else 0.0) * llm_confidence
                )
                final_rag_score = (
                    weights['keyword'] * rag_keyword_score +
                    weights['context'] * (1.0 - db_context_score) +
                    weights['pattern'] * rag_pattern_score +
                    weights['llm'] * (1.0 if llm_classification == QueryType.RAG_QUERY else 0.0) * llm_confidence
                )
                # Choose route with highest score
                if final_sql_score > final_rag_score:
                    response = self.sql_agent.ask(query)
                    agent_used = 'SQL Database Agent'
                else:
                    response = self.process_regular_query(query)
                    agent_used = 'RAG Knowledge Agent'
                # Add clarification message
                clarification = f"\n\nThis query was ambiguous. I chose the route with the highest confidence ({agent_used}).\nIf this is not what you expected, please clarify your intent or provide more details.\n"
                result['response'] = response + clarification
                result['agent_used'] = agent_used
                result['success'] = True

        except Exception as e:
            error_msg = f"Error routing query: {str(e)}"
            logger.error(error_msg)
            result['error'] = error_msg
            result['response'] = "I encountered an error while processing your query. Please try again or rephrase your question."
            result['success'] = False

        finally:
            result['execution_time'] = time.time() - start_time

        return result

    def _request_clarification(self, query: str, classification: ClassificationResult) -> str:
        """Request clarification for low-confidence classifications"""
        return f"""
I'm not entirely sure how to best answer your question: "{query}"

Based on my analysis, I think you might be looking for:
- {classification.suggested_route} (confidence: {classification.confidence:.1%})

To help me provide the best answer, could you clarify:

If you want specific data from our database, try rephrasing like:
• "Show me [specific data] from [table/category]"
• "How many [items] are there?"
• "List the top [number] [items] by [criteria]"

If you want explanations or general information, try:
• "Explain what [concept] means"
• "What is the definition of [term]?"
• "How does [process] work?"

Or you can specify your preference:
• Add "from database" to query our data
• Add "explain" to get conceptual information

Classification reasoning: {classification.reasoning}
"""

    def _handle_ambiguous_query(self, query: str, classification: ClassificationResult) -> str:
        """Handle ambiguous queries that could go either way"""
        return f"""
Your question "{query}" could be answered in multiple ways. Let me provide both perspectives:

**Data-based Answer:**
{self.sql_agent.process_question(query)}

**Knowledge-based Answer:**
{self.process_regular_query(query)}

---
Classification details: {classification.reasoning}

For future queries, you can specify your preference by adding:
• "from our database" for data queries
• "explain" or "what is" for conceptual questions
"""

# Your existing RAG function
def process_regular_query(query):
    """RAG/Knowledge base agent for unstructured queries. Returns a string answer."""
    try:
        from open_arena_lib.auth import AuthClient
        from open_arena_lib.chat import Chat
        import re
        auth = AuthClient(token_provider=lambda: open('Token.txt').read().strip())
        workflow_id = "cae4aa4f-4600-4b3d-9c00-ab26d2a2d2ee"
        chat = Chat(auth=auth, workflow_id=workflow_id)
        response = chat.chat(query)
        if response and "answer" in response:
            answer = response["answer"].strip()
            answer = re.sub(r'^\s*ANALYSIS RESULT:\s*', '', answer)
            answer = re.sub(r'^=+\s*', '', answer)
            answer = re.sub(r'\s*=+$', '', answer)
            return answer
        else:
            return "I couldn't generate a response. Please try again."
    except Exception as e:
        return f"Error processing regular query: {str(e)}"

def main():
    """Main function to demonstrate the router agent"""
    from datetime import datetime
    import time
    
    sql_agent = SimpleSQLAgent() 
    llm_client = OpenAIClient()  
  
    router = RouterAgent(sql_agent, llm_client, confidence_threshold=0.7)
    
    try:
        print("Router Agent initialized successfully!")
        print("I can route your questions to either the SQL database or knowledge base.")
        print("Type 'quit' to exit, or 'force sql/rag [question]' to force routing.\n")
        
        while True:
            user_input = input("Enter your question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
            
            force_route = None
            if user_input.lower().startswith('force sql '):
                force_route = 'sql'
                query = user_input[10:].strip()
            elif user_input.lower().startswith('force rag '):
                force_route = 'rag'
                query = user_input[10:].strip()
            else:
                query = user_input
            
            print(f"\nProcessing: {query}")
            if force_route:
                print(f"Forced routing to: {force_route.upper()}")
            
            # Route the query
            result = router.route_query(query, force_route=force_route)
            
            # Display results
            print("\n" + "="*80)
            print(f"Query: {result['query']}")
            print(f"Classification: {result['classification']['type'].upper()} "
                  f"(confidence: {result['classification']['confidence']:.1%})")
            print(f"Agent Used: {result['agent_used']}")
            print(f"Execution Time: {result['execution_time']:.2f} seconds")
            print(f"Success: {result['success']}")
            
            if result['classification']['reasoning']:
                print(f"Reasoning: {result['classification']['reasoning']}")
            
            print("\nResponse:")
            print(result['response'])
            
            if result['error']:
                print(f"\nError: {result['error']}")
            
            print("="*80 + "\n")
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        sql_agent.close()

class SimpleRouterAgent:
    """Simplified interface for the router agent"""
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.sql_agent = SimpleSQLAgent()
        self.llm_client = OpenAIClient()
        self.router = RouterAgent(self.sql_agent, self.llm_client, confidence_threshold)
    
    def ask(self, question: str, force_route: Optional[str] = None) -> str:
        """Simple method to ask a question and get a response"""
        result = self.router.route_query(question, force_route)
        return result['response']
    
    def classify(self, question: str) -> ClassificationResult:
        """Get classification details for a question"""
        return self.router.classifier.classify_query(question)
    
    def close(self):
        """Close the router agent"""
        self.sql_agent.close()

if __name__ == "__main__":
    main()