import logging

from dotenv import load_dotenv
from sqlalchemy import create_engine

from langchain.tools import Tool, StructuredTool
# from langchain_groq.chat_models import ChatGroq
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
# from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import tool
from pydantic import BaseModel

from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseTool:
    def __init__(self, llm, db_type: str, user: str = None,
                 password: str = None, host: str = None, port: str = None,
                 database: str = None):
        """
        Initializes the DatabaseTool instance.

        Args:
            llm (BaseChatModel): Language model to be used for interacting with the database.
            db_type (str): Type of the database (e.g., 'mysql', 'postgresql', 'sqlite', 'mssql', 'oracle').
            user (str, optional): Username for database connection (if applicable).
            password (str, optional): Password for database connection (if applicable).
            host (str, optional): Hostname for the database (if applicable).
            port (str, optional): Port number for the database (if applicable).
            database (str): Name of the database.

        Raises:
            ValueError: If the database type is unsupported.
        """
        self.db_type = db_type
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.engine = self.get_engine()
        self.db = self.get_db()
        self.llm = llm
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.tools = self.toolkit.get_tools()
        self.full_schema = self.db.get_context()
        logger.info("DatabaseTool initialized.")

    def get_engine(self) -> Any:
        """
        Creates a SQLAlchemy engine based on the specified database type.

        Returns:
            sqlalchemy.engine.Engine: The SQLAlchemy engine connected to the database.

        Raises:
            ValueError: If the database type is unsupported.
        """
        db_url_map = {
            'mysql': 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}',
            'postgresql': 'postgresql://{0}:{1}@{2}:{3}/{4}',
            'sqlite': 'sqlite:///{4}',
            'mssql': 'mssql+pyodbc://{0}:{1}@{2}:{3}/{4}?driver=ODBC+Driver+17+for+SQL+Server',
            'oracle': 'oracle+cx_oracle://{0}:{1}@{2}:{3}/{4}'
        }

        if self.db_type not in db_url_map:
            logger.error(f"Unsupported database type: {self.db_type}")
            raise ValueError(f"Unsupported database type: {self.db_type}")

        url = db_url_map[self.db_type].format(self.user, self.password, self.host, self.port, self.database)
        return create_engine(url)

    def get_db(self) -> SQLDatabase:
        """
        Creates a SQLDatabase instance from the provided engine.

        Returns:
            SQLDatabase: An instance of SQLDatabase connected to the engine.
        """
        return SQLDatabase(self.engine)
    
    
    def list_tables(self,input=None) -> List[str]:
        """
        Lists all tables in the database. No Inputs is required for this tool.

        Returns:
            List[str]: A list of table names in the database.
        """
        print(f"tool called with input: {input}.")
        list_tables_tool = next(tool for tool in self.tools if tool.name == "sql_db_list_tables")
        # return {"tables" : list_tables_tool.invoke("")}
        return list_tables_tool.invoke("")
    
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Retrieves the schema for a specific table.

        Args:
            table_name (str): The name of the table to get the schema for.

        Returns:
            Dict[str, Any]: The schema information of the specified table.
        """
        get_schema_tool = next(tool for tool in self.tools if tool.name == "sql_db_schema")
        return get_schema_tool.invoke(table_name)
    
    
    def query(self, query_string: str) -> List[Dict[str, Any]]:
        """
        Executes a SQL query.

        Args:
            query_string (str): The SQL query to execute.

        Returns:
            List[Dict[str, Any]]: The result of the SQL query.
        """
        query_sql_db_tool = next(tool for tool in self.tools if tool.name == "sql_db_query")
        return query_sql_db_tool.invoke(query_string)
    
    
    def check_query(self, query_string: str) -> Dict[str, Any]:
        """
        Checks a SQL query for correctness.

        Args:
            query_string (str): The SQL query to check.

        Returns:
            Dict[str, Any]: The result of the query check, indicating validity.
        """
        query_checker_tool = next(tool for tool in self.tools if tool.name == "sql_db_query_checker")
        return query_checker_tool.invoke(query_string)
    
    
    # def get_full_schema(self) -> Dict[str, Any]:
    def get_full_schema(self, input=""):
        """
        Gets the full schema context of the database.

        Returns:
            Dict[str, Any]: The full schema information of the database.
        """
        print("db: ", self.full_schema)
        # return self.db.get_context()
        return self.full_schema
    
    def create_tools(self) -> Dict[str, Tool]:
        tools = {}
        # tools =[]

        # Tool for listing tables
        tools["list_tables"] = Tool(
        # tools.append(Tool(
            name="list_tables",
            func=self.list_tables,
            description="Lists all tables in the database. No input is required for this tool.",
            args=[]  # No arguments needed
        )

        # Tool for getting table schema
        # tools.append(Tool(
        tools["get_table_schema"] = Tool(
            name="get_table_schema",
            func=self.get_table_schema,
            description="Retrieves the schema for a specific table. \n"
                        "Arguments:\n"
                        "- `table_name` (str): The name of the table to get the schema for.\n"
                        "Example: `get_table_schema('Album')`",
            args=[{"name": "table_name", "type": "str", "description": "The name of the table."}]
        )

        # Tool for querying the database
        tools["query_db"] = Tool(
        # tools.append(Tool(
            name="query_db",
            func=self.query,
            description="Executes a SQL query. \n"
                        "Arguments:\n"
                        "- `query_string` (str): The SQL query to execute.\n"
                        "Example: `query('SELECT * FROM Album LIMIT 5')`",
            args=[{"name": "query_string", "type": "str", "description": "The SQL query to execute."}]
        )

        # Tool for checking query correctness
        tools["check_query"] = Tool(
        # tools.append(Tool(
            name="check_query",
            func=self.check_query,
            description="Checks a SQL query for correctness. \n"
                        "Arguments:\n"
                        "- `query_string` (str): The SQL query to check.\n"
                        "Example: `check_query('SELECT * FROM Album')`",
            args=[{"name": "query_string", "type": "str", "description": "The SQL query to check."}]
        )

        tools["get_full_schema"] = Tool(
            name="get_full_schema",
            description="Gets the full schema context of the database. No input is required for this tool.",
            func=self.get_full_schema,
            args=[] # No arguments needed
        )

        return tools