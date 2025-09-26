import os
import json
import re
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import snowflake.connector
from sqlalchemy import create_engine, text
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import requests
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

import os
from dotenv import load_dotenv
load_dotenv()

SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")
SNOWFLAKE_PRIVATE_KEY = os.getenv("SNOWFLAKE_PRIVATE_KEY")
PRIVATE_KEY_PASSPHRASE = os.getenv("PRIVATE_KEY_PASSPHRASE")

OPENAI_WORKSPACE_ID = os.getenv("OPENAI_WORKSPACE_ID")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
OPENAI_ASSET_ID = os.getenv("OPENAI_ASSET_ID")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

TR_CLIENT_ID = os.getenv("TR_CLIENT_ID")
TR_CLIENT_SECRET = os.getenv("TR_CLIENT_SECRET")
TR_AUDIENCE = os.getenv("TR_AUDIENCE")
TR_TOKEN_URL = os.getenv("TR_TOKEN_URL")

OPEN_ARENA_WORKFLOW_ID = os.getenv("OPEN_ARENA_WORKFLOW_ID")
OPEN_ARENA_API_VERSION = os.getenv("OPEN_ARENA_API_VERSION")
OPEN_ARENA_BASE_URL = os.getenv("OPEN_ARENA_BASE_URL")

DEFAULT_AUTH_TOKEN = os.getenv("DEFAULT_AUTH_TOKEN")

DB_ALLOWED_TABLES = os.getenv("DB_ALLOWED_TABLES")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QueryResult:
    """Data class for query results"""
    success: bool
    data: Optional[pd.DataFrame] = None
    error: Optional[str] = None
    query: Optional[str] = None
    execution_time: Optional[float] = None
    row_count: Optional[int] = None

@dataclass
class TableInfo:
    """Data class for table information"""
    table_name: str
    columns: List[Dict[str, Any]]
    sample_data: Optional[pd.DataFrame] = None
    row_count: Optional[int] = None

class SnowflakeConnection:
    """Manages Snowflake database connections"""
    
    def __init__(self):
        self.connection = None
        self.engine = None
        self.cursor = None
        self._setup_connection()
    
    def _setup_connection(self):
        """Initialize Snowflake connection"""
        try:
            # Load private key
            os.environ['PRIVATE_KEY_PASSPHRASE'] = PRIVATE_KEY_PASSPHRASE
            p_key = serialization.load_pem_private_key(
                SNOWFLAKE_PRIVATE_KEY.encode(),
                password=os.environ['PRIVATE_KEY_PASSPHRASE'].encode(),
                backend=default_backend()
            )

            pkb = p_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            # Create connection
            self.connection = snowflake.connector.connect(
                user=SNOWFLAKE_USER,
                account=SNOWFLAKE_ACCOUNT,
                private_key=pkb,
                warehouse=SNOWFLAKE_WAREHOUSE,
                database=SNOWFLAKE_DATABASE,
                schema=SNOWFLAKE_SCHEMA,
                role=SNOWFLAKE_ROLE
            )

            self.cursor = self.connection.cursor()

            # Create SQLAlchemy engine
            ctx = {
                "user": SNOWFLAKE_USER,
                "account": SNOWFLAKE_ACCOUNT,
                "private_key": pkb,
                "warehouse": SNOWFLAKE_WAREHOUSE,
                "database": SNOWFLAKE_DATABASE,
                "schema": SNOWFLAKE_SCHEMA,
                "role": SNOWFLAKE_ROLE,
            }

            snowflake_url = (
                f"snowflake://{ctx['user']}@{ctx['account']}/"
                f"{ctx['database']}/{ctx['schema']}"
                f"?warehouse={ctx['warehouse']}&role={ctx['role']}"
            )

            self.engine = create_engine(
                snowflake_url,
                connect_args={'private_key': pkb}
            )

            logger.info("Snowflake connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to establish Snowflake connection: {e}")
            raise
    
    def execute_query(self, query: str, timeout: int = 3000) -> QueryResult:
        """Execute SQL query with error handling"""
        start_time = time.time()
        
        try:
           
            self.cursor.execute(f"ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = {timeout}")
            
            
            self.cursor.execute(query)
            
            columns = [desc[0] for desc in self.cursor.description] if self.cursor.description else []
            rows = self.cursor.fetchall()
            
            execution_time = time.time() - start_time
            
            if columns and rows:
                df = pd.DataFrame(rows, columns=columns)
                return QueryResult(
                    success=True,
                    data=df,
                    query=query,
                    execution_time=execution_time,
                    row_count=len(df)
                )
            else:
                return QueryResult(
                    success=True,
                    data=pd.DataFrame(),
                    query=query,
                    execution_time=execution_time,
                    row_count=0
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Query execution failed: {error_msg}")
            
            return QueryResult(
                success=False,
                error=error_msg,
                query=query,
                execution_time=execution_time
            )
    
    def close(self):
        """Close database connections"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()

class OpenAIClient:
    """Manages OpenAI API client"""
    
    def __init__(self):
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Initialize OpenAI client using your existing function"""
        try:
            workspace_id = OPENAI_WORKSPACE_ID
            model_name = OPENAI_MODEL_NAME
            asset_id = OPENAI_ASSET_ID

            payload = {
                "workspace_id": workspace_id,
                "model_name": model_name
            }

            url = "https://aiplatform.gcs.int.thomsonreuters.com/v1/openai/token"
            OPENAI_BASE_URL_ENV = OPENAI_BASE_URL

            resp = requests.post(url, json=payload)
            credentials = json.loads(resp.content)

            if "openai_key" in credentials and "openai_endpoint" in credentials:
                OPENAI_API_KEY = credentials["openai_key"]
                OPENAI_DEPLOYMENT_ID = credentials["azure_deployment"]
                OPENAI_API_VERSION = credentials["openai_api_version"]
                token = credentials["token"]
                llm_profile_key = OPENAI_DEPLOYMENT_ID.split("/")[0]

                headers = {
                    "Authorization": f"Bearer {credentials['token']}",
                    "api-key": OPENAI_API_KEY,
                    "Content-Type": "application/json",
                    "x-tr-chat-profile-name": "ai-platforms-chatprofile-prod",
                    "x-tr-userid": workspace_id,
                    "x-tr-llm-profile-key": llm_profile_key,
                    "x-tr-user-sensitivity": "true",
                    "x-tr-sessionid": OPENAI_DEPLOYMENT_ID,
                    "x-tr-asset-id": asset_id,
                    "x-tr-authorization": OPENAI_BASE_URL_ENV
                }

                self.client = AzureChatOpenAI(
                    azure_endpoint=OPENAI_BASE_URL_ENV,
                    api_key=OPENAI_API_KEY,
                    api_version=OPENAI_API_VERSION,
                    azure_deployment=OPENAI_DEPLOYMENT_ID,
                    default_headers=headers
                )

                logger.info("OpenAI client initialized successfully")
            else:
                raise Exception("Failed to get OpenAI credentials")
                
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    def generate_response(self, messages: List, temperature: float = 0.1) -> str:
        """Generate response using OpenAI"""
        try:
            response = self.client.invoke(messages, temperature=temperature)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise

class SQLAgent:
    """Main SQL Agent class"""
    
    def __init__(self):
        self.db = SnowflakeConnection()
        self.llm = OpenAIClient()
        self.table_cache = {}
        self.schema_cache = {}
        
    def get_available_tables(self) -> List[str]:
        """Fetch all available tables from the database"""
        try:
            query = """
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = CURRENT_SCHEMA()
            AND ROW_COUNT IS NOT null
            AND ROW_COUNT <> 0
            AND TABLE_NAME LIKE 'ONETRUST%'
            OR TABLE_NAME LIKE 'DIA_TRACKING_DATA_OT'
            ORDER BY TABLE_NAME
            """
            
            result = self.db.execute_query(query)
            print(f"DEBUG: get_available_tables result: {result}")
            if result.success and result.data is not None:
                tables = result.data['TABLE_NAME'].tolist()
                logger.info(f"Found {len(tables)} tables")
                return tables
            else:
                logger.warning("No tables found or query failed")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching tables: {e}")
            return []
    
    def determine_relevant_tables(self, question: str, available_tables: List[str]) -> List[str]:
        """Determine which tables are relevant to the user's question"""
        if not available_tables:
            return []
        
        tables_list = "\n".join([f"- {table}" for table in available_tables])
        
        prompt = f"""
        Given the following question and list of available tables, determine which tables are most relevant to answer the question.
        
        Question: {question}
        
        Available Tables:
        {tables_list}
        
        Return only the table names that are relevant, one per line, without any additional text or explanation.
        If no tables seem relevant, return "NONE".
        """
        
        try:
            messages = [SystemMessage(content="You are a database expert. Analyze the question and return only relevant table names."),
                       HumanMessage(content=prompt)]
            
            response = self.llm.generate_response(messages)
            
            relevant_tables = []
            for line in response.strip().split('\n'):
                table_name = line.strip().strip('-').strip()
                if table_name and table_name != "NONE" and table_name in available_tables:
                    relevant_tables.append(table_name)
         
            if not relevant_tables:
                question_lower = question.lower()
                for table in available_tables:
                    table_lower = table.lower()
                    if any(word in table_lower for word in question_lower.split() if len(word) > 3):
                        relevant_tables.append(table)
            
            logger.info(f"Relevant tables identified: {relevant_tables}")
            return relevant_tables[:5]  # Limit to top 5 tables
            
        except Exception as e:
            logger.error(f"Error determining relevant tables: {e}")
            question_lower = question.lower()
            relevant_tables = []
            for table in available_tables:
                table_lower = table.lower()
                if any(word in table_lower for word in question_lower.split() if len(word) > 3):
                    relevant_tables.append(table)
            return relevant_tables[:5]
    
    def get_table_ddl(self, table_name: str) -> TableInfo:
        """Get DDL information for a specific table"""
        if table_name in self.schema_cache:
            return self.schema_cache[table_name]
        
        try:
            # Get column information
            columns_query = f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                CHARACTER_MAXIMUM_LENGTH,
                NUMERIC_PRECISION,
                NUMERIC_SCALE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name}' 
            AND TABLE_SCHEMA = CURRENT_SCHEMA()
            ORDER BY ORDINAL_POSITION
            """
            
            result = self.db.execute_query(columns_query)
            if not result.success or result.data is None:
                logger.error(f"Failed to get columns for table {table_name}")
                return TableInfo(table_name=table_name, columns=[])
            
            columns = result.data.to_dict('records')
            
            # Get sample data (first 5 rows)
            sample_query = f"SELECT * FROM {table_name} LIMIT 5"
            sample_result = self.db.execute_query(sample_query)
            sample_data = sample_result.data if sample_result.success else None
            
            # Get row count
            count_query = f"SELECT COUNT(*) as ROW_COUNT FROM {table_name}"
            count_result = self.db.execute_query(count_query)
            row_count = count_result.data.iloc[0]['ROW_COUNT'] if count_result.success and not count_result.data.empty else None
            
            table_info = TableInfo(
                table_name=table_name,
                columns=columns,
                sample_data=sample_data,
                row_count=row_count
            )
            
            self.schema_cache[table_name] = table_info
            
            return table_info
            
        except Exception as e:
            logger.error(f"Error getting DDL for table {table_name}: {e}")
            return TableInfo(table_name=table_name, columns=[])
    
    def generate_sql_query(self, question: str, table_infos: List[TableInfo]) -> str:
        """Generate SQL query based on question and table information"""
        schema_descriptions = []
        
        for table_info in table_infos:
            columns_desc = []
            for col in table_info.columns:
                col_desc = f"{col['COLUMN_NAME']} ({col['DATA_TYPE']}"
                if col['CHARACTER_MAXIMUM_LENGTH']:
                    col_desc += f"({col['CHARACTER_MAXIMUM_LENGTH']})"
                elif col['NUMERIC_PRECISION']:
                    col_desc += f"({col['NUMERIC_PRECISION']}"
                    if col['NUMERIC_SCALE']:
                        col_desc += f",{col['NUMERIC_SCALE']}"
                    col_desc += ")"
                col_desc += ")"
                if col['IS_NULLABLE'] == 'NO':
                    col_desc += " NOT NULL"
                columns_desc.append(col_desc)
            
            schema_desc = f"""
Table: {table_info.table_name}
Columns: {', '.join(columns_desc)}
Row Count: {table_info.row_count or 'Unknown'}
"""
            if table_info.sample_data is not None and not table_info.sample_data.empty:
                schema_desc += f"Sample Data:\n{table_info.sample_data.to_string(index=False)}\n"
            
            schema_descriptions.append(schema_desc)
        
        schemas_text = "\n".join(schema_descriptions)
        
        prompt = f"""
You are an expert SQL developer working with Snowflake. Generate a SQL query to answer the following question.

Question: {question}

Available Tables and Schema:
{schemas_text}

Guidelines:
1. Use proper Snowflake SQL syntax
2. Include appropriate JOINs if multiple tables are needed
3. Use proper aggregation functions when needed
4. Include ORDER BY clauses for better results
5. Use LIMIT when appropriate to avoid large result sets
6. Handle NULL values appropriately
7. Use proper date/time functions for Snowflake
8. Table names and column names should be properly quoted if needed

Return only the SQL query without any explanation or additional text.
"""
        
        try:
            messages = [
                SystemMessage(content="You are an expert SQL developer. Generate only valid Snowflake SQL queries."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.generate_response(messages)
            
            sql_query = response.strip()
            
            if sql_query.startswith('```sql'):
                sql_query = sql_query[6:]
            elif sql_query.startswith('```'):
                sql_query = sql_query[3:]
            
            if sql_query.endswith('```'):
                sql_query = sql_query[:-3]
            
            sql_query = sql_query.strip()
            
            logger.info(f"Generated SQL query: {sql_query}")
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            return ""
    
    def validate_query(self, query: str, table_infos: List[TableInfo]) -> Tuple[bool, str, str]:
        """Validate SQL query using LLM"""
        schema_context = []
        for table_info in table_infos:
            columns = [col['COLUMN_NAME'] for col in table_info.columns]
            schema_context.append(f"{table_info.table_name}: {', '.join(columns)}")
        
        schemas_text = "\n".join(schema_context)
        
        prompt = f"""
Review the following SQL query for common mistakes and issues:

SQL Query:
{query}

Available Tables and Columns:
{schemas_text}

Check for:
1. Syntax errors
2. Invalid table or column names
3. Missing JOIN conditions
4. Incorrect aggregation usage
5. Data type mismatches
6. Performance issues (missing WHERE clauses, etc.)
7. Snowflake-specific syntax correctness

If the query is correct, respond with: "VALID"
If there are issues, respond with: "INVALID: [description of issues]"
If you can suggest a corrected query, also include: "CORRECTED: [corrected SQL query]"
"""
        
        try:
            messages = [
                SystemMessage(content="You are a SQL expert reviewer. Validate queries for correctness and performance."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.generate_response(messages)
            
            if response.strip().startswith("VALID"):
                return True, "Query is valid", query
            elif "INVALID:" in response:
                if "CORRECTED:" in response:
                    parts = response.split("CORRECTED:")
                    issues = parts[0].replace("INVALID:", "").strip()
                    corrected_query = parts[1].strip()
                    
                    # Clean up corrected query
                    if corrected_query.startswith('```sql'):
                        corrected_query = corrected_query[6:]
                    elif corrected_query.startswith('```'):
                        corrected_query = corrected_query[3:]
                    if corrected_query.endswith('```'):
                        corrected_query = corrected_query[:-3]
                    corrected_query = corrected_query.strip()
                    
                    return False, issues, corrected_query
                else:
                    issues = response.replace("INVALID:", "").strip()
                    return False, issues, query
            else:
                return True, "Query validation completed", query
                
        except Exception as e:
            logger.error(f"Error validating query: {e}")
            return True, f"Validation error: {e}", query
    
    def correct_query_errors(self, query: str, error_message: str, table_infos: List[TableInfo]) -> str:
        """Attempt to correct query based on database error"""
        schema_context = []
        for table_info in table_infos:
            columns = [f"{col['COLUMN_NAME']} ({col['DATA_TYPE']})" for col in table_info.columns]
            schema_context.append(f"{table_info.table_name}: {', '.join(columns)}")
        
        schemas_text = "\n".join(schema_context)
        
        prompt = f"""
The following SQL query failed with an error. Please correct it:

Original Query:
{query}

Error Message:
{error_message}

Available Tables and Columns:
{schemas_text}

Please provide a corrected SQL query that fixes the error. Return only the corrected SQL query without any explanation.
"""
        
        try:
            messages = [
                SystemMessage(content="You are a SQL expert. Fix broken queries based on error messages."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.generate_response(messages)
            
            # Clean up the response
            corrected_query = response.strip()
            if corrected_query.startswith('```sql'):
                corrected_query = corrected_query[6:]
            elif corrected_query.startswith('```'):
                corrected_query = corrected_query[3:]
            if corrected_query.endswith('```'):
                corrected_query = corrected_query[:-3]
            
            corrected_query = corrected_query.strip()
            
            logger.info(f"Corrected query: {corrected_query}")
            return corrected_query
            
        except Exception as e:
            logger.error(f"Error correcting query: {e}")
            return query
    
    def format_response(self, question: str, query_result: QueryResult, query: str) -> str:
        """Format the final response to the user, using LLM to summarize results and providing a CSV download link if data exists."""
        import uuid
        from datetime import datetime
        import os

        if not query_result.success:
            return f"""
I apologize, but I encountered an error while executing the query for your question: "{question}"

Error: {query_result.error}

Query attempted: {query}

Please try rephrasing your question or check if the requested data exists in the database.
"""

        if query_result.data is None or query_result.data.empty:
            return f"""
I successfully executed your query for: "{question}"

However, no data was returned. This could mean:
- The data you're looking for doesn't exist
- The filtering conditions are too restrictive
- The tables might be empty

Query executed: {query}
Execution time: {query_result.execution_time:.2f} seconds
"""

        # Prepare data for LLM summarization (show only first 10 rows for context)
        data_preview = query_result.data.head(10)
        data_str = data_preview.to_string(index=False)

        # Save the full results as a CSV file in static/ with a unique name
        csv_filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.csv"
        csv_path = os.path.join("static", csv_filename)
        try:
            query_result.data.to_csv(csv_path, index=False)
            csv_link = f"/static/{csv_filename}"
        except Exception as e:
            csv_link = None

        # Construct prompt for LLM
        prompt = f"""
You are a data analyst. Summarize the following SQL query results in plain English for the user, highlighting key findings, trends, or insights. If the data is tabular, mention notable values, counts, or patterns. Be concise and user-friendly.

User Question:
{question}

SQL Query Executed:
{query}

Results (showing up to 10 rows):
{data_str}

If the data is too large, summarize only what is shown. If the data is simple, provide a brief summary.
"""

        try:
            messages = [
                SystemMessage(content="You are a helpful data analyst who summarizes SQL results for business users."),
                HumanMessage(content=prompt)
            ]
            summary = self.llm.generate_response(messages)
        except Exception as e:
            summary = "(Could not generate summary: " + str(e) + ")\n" + data_str

        response = f"""
Summary for your question: "{question}"

{summary.strip()}
"""
        if query_result.row_count > 10:
            response += f"\n(Showing first 10 rows out of {query_result.row_count} total rows)"

        if csv_link:
            response += f"\n\nYou can also download the attached CSV with all relevant records: [Download CSV]({csv_link})"

        response += f"""

Query executed: {query}
Execution time: {query_result.execution_time:.2f} seconds
"""
        return response
    
    def process_question(self, question: str, max_retries: int = 2) -> str:
        """Main method to process user questions"""
        logger.info(f"Processing question: {question}")
        
        try:
            # Step 1: Get available tables
            available_tables = self.get_available_tables()
            if not available_tables:
                return "I couldn't find any tables in the database. Please check the database connection and permissions."
            
            # Step 2: Determine relevant tables
            relevant_tables = self.determine_relevant_tables(question, available_tables)
            if not relevant_tables:
                return f"I couldn't find any tables relevant to your question: '{question}'. Available tables: {', '.join(available_tables[:10])}"
            
            # Step 3: Get DDL for relevant tables
            table_infos = []
            for table_name in relevant_tables:
                table_info = self.get_table_ddl(table_name)
                if table_info.columns:  # Only include tables with valid schema
                    table_infos.append(table_info)
            
            if not table_infos:
                return f"I couldn't retrieve schema information for the relevant tables: {', '.join(relevant_tables)}"
            
            # Step 4: Generate SQL query
            query = self.generate_sql_query(question, table_infos)
            if not query:
                return "I couldn't generate a SQL query for your question. Please try rephrasing it."
            
            # Step 5: Validate query
            is_valid, validation_message, validated_query = self.validate_query(query, table_infos)
            if not is_valid:
                logger.info(f"Query validation issues: {validation_message}")
                query = validated_query  # Use corrected query if available
            
            # Step 6: Execute query with retry logic
            retry_count = 0
            while retry_count <= max_retries:
                result = self.db.execute_query(query)
                
                if result.success:
                    # Step 7: Format and return response
                    return self.format_response(question, result, query)
                else:
                    # Step 8: Try to correct errors
                    if retry_count < max_retries:
                        logger.info(f"Query failed, attempting correction (attempt {retry_count + 1})")
                        corrected_query = self.correct_query_errors(query, result.error, table_infos)
                        if corrected_query != query:
                            query = corrected_query
                            retry_count += 1
                            continue
                    
                    # If we can't correct the error, return error message
                    return self.format_response(question, result, query)
            
            return "I encountered persistent errors while trying to answer your question. Please try rephrasing it or contact support."
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return f"I encountered an unexpected error while processing your question: {str(e)}"
    
    def close(self):
        """Clean up resources"""
        self.db.close()

# Usage example and main interface
def main():
    """Main function to demonstrate the SQL agent"""
    agent = SQLAgent()
    
    try:
        print("SQL Agent initialized successfully!")
        print("You can now ask questions about your Snowflake database.")
        print("Type 'quit' to exit.\n")
        
        while True:
            question = input("Enter your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if not question:
                continue
            
            print("\nProcessing your question...")
            response = agent.process_question(question)
            print("\n" + "="*80)
            print(response)
            print("="*80 + "\n")
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        agent.close()

# Alternative interface for programmatic use
class SimpleSQLAgent:
    """Simplified interface for the SQL agent"""
    
    def __init__(self):
        self.agent = SQLAgent()
    
    def ask(self, question: str) -> str:
        """Simple method to ask a question and get a response"""
        return self.agent.process_question(question)
    
    def get_tables(self) -> List[str]:
        """Get list of available tables"""
        return self.agent.get_available_tables()
    
    # Add this method:
    def get_available_tables(self) -> List[str]:
        """Get list of available tables (alias for get_tables)"""
        return self.agent.get_available_tables()
    
    def get_table_info(self, table_name: str) -> TableInfo:
        """Get detailed information about a specific table"""
        return self.agent.get_table_ddl(table_name)
    
    # Add this method too:
    def get_table_ddl(self, table_name: str) -> TableInfo:
        """Get DDL information for a table (alias for get_table_info)"""
        return self.agent.get_table_ddl(table_name)
    
    def close(self):
        """Close the agent"""
        self.agent.close()

if __name__ == "__main__":
    main()