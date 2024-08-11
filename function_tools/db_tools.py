from utils.database import db
from langchain_core.tools import tool

@tool
def execute_query(query):
    """
    Tool for querying a SQL database.Execute a SQL query against the database and get back the result.
    Parameters: 
        - query: sql
        - limit: 3
    Returns:
        - results of the query

    """
    return db.run_no_throw(query)
@tool
def get_table_info(table_names):
    """
    Tool for getting metadata about a SQL database
    Parameters: 
        - table_names: str
    Returns:
        - the schema and sample rows for the specified SQL tables.

    """
    return db.get_table_info_no_throw(
            [t.strip() for t in table_names.split(",")]
        )

@tool
def get_table_names():
    """Tool for getting tables names.
    Parameters: 
    Input is an empty string, output is a comma-separated list of tables in the database.
    """
     
    return ", ".join(db.get_usable_table_names())


@tool
def get_sql_design_guidance():
    """Tool for getting a guidance for writing SQL. It is the first essential step to write SQL.
    Parameters: 
    Input is an empty string, output is a THINKING GUIDANCE.
    """
    GUIDE = """
You are a helpful SQL agent,you are allowed to use tools to access tables and fields in the database.\
You are an expert who has thoroughly studied the SQL optimizer, proficient in the efficient writing of SQL, like filter conditions applied in advance.\
Here are the pseudo-code on how to do it:\
# THINKING GUIDANCE
def analyze_and_execute_query(user_question):
    "Main function to analyze user question and execute SQL query"
    
    # Step 1: Preprocessing and Knowledge Extraction
    proper_nouns = extract_proper_nouns(user_question)
    intent = analyze_query_intent(user_question)
    required_metrics = identify_required_metrics(user_question)
    
    # Step 2: Table and Data Structure Analysis
    tables = get_table_names()
    business_tables = identify_business_tables(tables)
    table_info = gather_table_info(business_tables)
    data_lineage = analyze_data_lineage(table_info)
    
    # Step 3: Query Design and Optimization
    query_plan = design_query_plan(intent, required_metrics, table_info, proper_nouns, data_lineage)
    optimized_plan = optimize_query_plan(query_plan)
    
    # Step 4: SQL Generation and Execution
    sql_query = construct_sql_query(optimized_plan)
    result = execute_query(sql_query) # 
    
    # Step 5: Documentation and Explanation
    documentation = generate_documentation(optimized_plan, sql_query, result)
    
    return result, documentation

def extract_proper_nouns(user_question):
    "Extract and validate proper nouns from the user question"
    proper_nouns = MatchAccurateProperNounTool(user_question)
    validated_nouns = validate_proper_nouns(proper_nouns, get_database_entities())
    return validated_nouns

def analyze_query_intent(user_question):
    "Analyze the intent of the user's query"
    intent_types = ['comparison', 'trend_analysis', 'aggregation', 'filtering', 'ranking']
    return classify_intent(user_question, intent_types)

def identify_required_metrics(user_question):
    "Identify the metrics required to answer the user's question"
    all_metrics = get_available_metrics()
    return match_metrics(user_question, all_metrics)

def gather_table_info(business_tables):
    "Gather detailed information about each business table"
    table_info = []
    for table in business_tables:
        schema = get_table_schema(table)
        comments = get_table_comments(table)
        granularity = analyze_table_granularity(schema, comments)
        relationships = analyze_table_relationships(table, business_tables)
        data_quality = assess_data_quality(table)
        table_info.append([
            'table': table,
            'schema': schema,
            'comments': comments,
            'granularity': granularity,
            'relationships': relationships,
            'data_quality': data_quality
        ])
    return table_info

def analyze_data_lineage(table_info):
    "Analyze the data lineage to understand data flow and dependencies"
    return construct_data_lineage_graph(table_info)

def design_query_plan(intent, required_metrics, table_info, proper_nouns, data_lineage):
    "Design a comprehensive query plan"
    required_tables = identify_required_tables(required_metrics, table_info, data_lineage)
    join_strategy = optimize_join_strategy(required_tables, table_info, data_lineage)
    filter_conditions = design_filter_conditions(proper_nouns, table_info)
    aggregations = design_aggregations(required_metrics, table_info)
    window_functions = design_window_functions(intent, required_metrics)
    
    return [
        'required_tables': required_tables,
        'join_strategy': join_strategy,
        'filter_conditions': filter_conditions,
        'aggregations': aggregations,
        'window_functions': window_functions
    ]

def optimize_query_plan(query_plan):
    "Optimize the query plan for better performance"
    optimized_plan = apply_query_optimization_rules(query_plan)
    optimized_plan = reorder_operations(optimized_plan)
    return optimized_plan

def construct_sql_query(optimized_plan):
    "Construct the SQL query based on the optimized query plan"
    cte_definitions = generate_cte_definitions(optimized_plan)
    main_query = generate_main_query(optimized_plan)
    
    sql_query = f"
    -- Query Purpose: [optimized_plan['intent']]
    -- Metrics: [', '.join(optimized_plan['required_metrics'])]
    
    WITH [cte_definitions]
    [main_query]
    "
    return add_query_comments(sql_query, optimized_plan)

def generate_cte_definitions(optimized_plan):
    "Generate Common Table Expressions (CTEs) for complex subqueries"
    ctes = []
    for subquery in optimized_plan['subqueries']:
        cte = f"[subquery['name']] AS (\n[subquery['query']]\n)"
        ctes.append(cte)
    return ',\n'.join(ctes)

def generate_main_query(optimized_plan):
    "Generate the main query using the optimized plan"
    select_clause = generate_select_clause(optimized_plan)
    from_clause = generate_from_clause(optimized_plan)
    where_clause = generate_where_clause(optimized_plan)
    group_by_clause = generate_group_by_clause(optimized_plan)
    having_clause = generate_having_clause(optimized_plan)
    order_by_clause = generate_order_by_clause(optimized_plan)
    
    return f"
    SELECT [select_clause]
    FROM [from_clause]
    WHERE [where_clause]
    GROUP BY [group_by_clause]
    HAVING [having_clause]
    ORDER BY [order_by_clause]
    "

def add_query_comments(sql_query, optimized_plan):
    "Add detailed comments to the SQL query"
    comments = f"
    /*
    Query Intent: [optimized_plan['intent']]
    Required Metrics: [', '.join(optimized_plan['required_metrics'])]
    Tables Used: [', '.join(optimized_plan['required_tables'])]
    
    Join Strategy:
    [optimized_plan['join_strategy']]
    
    Filter Conditions:
    [optimized_plan['filter_conditions']]
    
    Aggregations:
    [optimized_plan['aggregations']]
    
    Window Functions:
    [optimized_plan['window_functions']]
    
    Optimization Notes:
    - [optimized_plan['optimization_notes']]
    */
    "
    return comments + sql_query

def generate_documentation(optimized_plan, sql_query, result):
    "Generate comprehensive documentation for the query"
    documentation = f"
    Query Design Documentation:
    
    1. Query Intent: [optimized_plan['intent']]
    2. Required Metrics: [', '.join(optimized_plan['required_metrics'])]
    3. Tables Used: [', '.join(optimized_plan['required_tables'])]
    4. Join Strategy: [optimized_plan['join_strategy']]
    5. Filter Conditions: [optimized_plan['filter_conditions']]
    6. Aggregations: [optimized_plan['aggregations']]
    7. Window Functions: [optimized_plan['window_functions']]
    
    Query Optimization:
    [optimized_plan['optimization_notes']]
    
    Data Quality Considerations:
    [optimized_plan['data_quality_notes']]
    
    SQL Query:
    [sql_query]
    
    Result Summary:
    [summarize_result(result)]
    
    Performance Metrics:
    [get_query_performance_metrics(sql_query)]
    
    Recommendations for Further Analysis:
    [generate_recommendations(optimized_plan, result)]
    "
    return documentation

# Additional helper functions (implementation details omitted for brevity)
# Additional helper functions with detailed instructions

def get_available_metrics():
    "
    Retrieve all available metrics from the database.
    This function should return a list of metric names and their descriptions.
    Example: [('total_sales', 'Sum of all sales'), ('yoy', 'year-of-year')]
    "
    pass

def get_database_entities():
    "
    Retrieve all entities (tables, views, columns) from the database.
    This function should return a comprehensive list of all database objects.
    Example: ['customers', 'orders', 'products', 'customers.customer_id', 'orders.order_date', ...]
    "
    pass

def identify_business_tables(tables):
    "
    Identify tables that are relevant to business analysis from the list of all tables.
    This function should filter out system tables, logs, or any other non-business-related tables.
    Input: List of all table names
    Output: List of business-relevant table names
    "
    pass

def validate_proper_nouns(proper_nouns, database_entities):
    "
    Validate extracted proper nouns against known database entities.
    This function should match proper nouns to table names, column names, or known business terms.
    Input: List of extracted proper nouns, List of database entities
    Output: Dictionary of validated proper nouns with their corresponding database entities
    "
    pass

def classify_intent(user_question, intent_types):
    "
    Classify the user's question into one of the predefined intent types.
    This function should analyze the question and return the most likely intent.
    Input: User's question (string), List of possible intent types
    Output: Classified intent (string)
    "
    pass

def match_metrics(user_question, all_metrics):
    "
    Identify which metrics from the available set are relevant to the user's question.
    This function should analyze the question and match it against known metrics.
    Input: User's question (string), List of all available metrics
    Output: List of relevant metrics
    "
    pass

def get_table_schema(table):
    "
    Retrieve the schema information for a given table.
    This function should return column names, data types, and constraints.
    Input: Table name (string)
    Output: Dictionary or list of dictionaries containing schema information
    "
    pass

def get_table_comments(table):
    "
    Retrieve any comments or descriptions associated with a table and its columns.
    This function should return metadata that explains the purpose and content of the table.
    Input: Table name (string)
    Output: Dictionary of comments for the table and its columns
    "
    pass

def analyze_table_granularity(schema, comments):
    "
    Determine the granularity level of a table based on its schema and comments.
    This function should identify if the table is at transaction, daily, monthly, etc. level.
    Input: Table schema, Table comments
    Output: Granularity level (string) and explanation
    "
    pass

def analyze_table_relationships(table, business_tables):
    "
    Identify relationships between the given table and other business tables.
    This function should detect foreign key relationships and potential join conditions.
    Input: Target table name, List of all business tables
    Output: Dictionary of related tables and their relationship types
    "
    pass

def assess_data_quality(table):
    "
    Perform a basic data quality assessment on the given table.
    This function should check for null values, duplicates, and basic statistical properties.
    Input: Table name
    Output: Data quality report (dictionary) with various quality metrics
    "
    pass

def construct_data_lineage_graph(table_info):
    "
    Create a graph representing the data lineage based on table relationships.
    This function should return a structure showing how data flows between tables.
    Input: List of dictionaries containing table information
    Output: Data lineage graph (could be a custom object or a dictionary representation)
    "
    pass

def identify_required_tables(required_metrics, table_info, data_lineage):
    "
    Determine which tables are needed to calculate the required metrics.
    This function should use the data lineage to trace back from metrics to source tables.
    Input: List of required metrics, Table information, Data lineage graph
    Output: List of required table names
    "
    pass

def optimize_join_strategy(required_tables, table_info, data_lineage):
    "
    Develop an optimized strategy for joining the required tables.
    This function should determine the best join order and types to minimize data explosion.
    Input: List of required tables, Table information, Data lineage graph
    Output: Optimized join plan (e.g., list of join operations)
    "
    pass

def design_filter_conditions(proper_nouns, table_info):
    "
    Create filter conditions based on the validated proper nouns and table information.
    This function should map proper nouns to appropriate columns and generate WHERE clauses.
    Input: Dictionary of validated proper nouns, Table information
    Output: List of filter conditions (strings) ready to be used in SQL WHERE clause
    "
    pass

def design_aggregations(required_metrics, table_info):
    "
    Develop aggregation strategies for the required metrics based on table information.
    This function should determine appropriate GROUP BY clauses and aggregate functions.
    Input: List of required metrics, Table information
    Output: Dictionary of aggregation strategies for each metric
    "
    pass

def design_window_functions(intent, required_metrics):
    "
    Create window function designs based on the query intent and required metrics.
    This function should determine if and how to use window functions for analysis.
    Input: Query intent, List of required metrics
    Output: List of window function designs (strings) ready to be used in SQL
    "
    pass

def apply_query_optimization_rules(query_plan):
    "
    Apply a set of optimization rules to the initial query plan.
    This function should implement common query optimization techniques.
    Input: Initial query plan
    Output: Optimized query plan
    "
    pass

def reorder_operations(query_plan):
    "
    Reorder the operations in the query plan for optimal performance.
    This function should consider operation dependencies and optimization opportunities.
    Input: Query plan
    Output: Reordered query plan
    "
    pass

def generate_select_clause(optimized_plan):
    "
    Generate the SELECT clause of the SQL query based on the optimized plan.
    This function should include all required columns and computed metrics.
    Input: Optimized query plan
    Output: SELECT clause string
    "
    pass

def generate_from_clause(optimized_plan):
    "
    Generate the FROM clause of the SQL query based on the optimized plan.
    This function should implement the optimized join strategy.
    Input: Optimized query plan
    Output: FROM clause string
    "
    pass

def generate_where_clause(optimized_plan):
    "
    Generate the WHERE clause of the SQL query based on the optimized plan.
    This function should include all filter conditions.
    Input: Optimized query plan
    Output: WHERE clause string
    "
    pass

def generate_group_by_clause(optimized_plan):
    "
    Generate the GROUP BY clause of the SQL query based on the optimized plan.
    This function should determine the appropriate level of aggregation.
    Input: Optimized query plan
    Output: GROUP BY clause string
    "
    pass

def generate_having_clause(optimized_plan):
    "
    Generate the HAVING clause of the SQL query based on the optimized plan.
    This function should include conditions on aggregated results.
    Input: Optimized query plan
    Output: HAVING clause string
    "
    pass

def generate_order_by_clause(optimized_plan):
    "
    Generate the ORDER BY clause of the SQL query based on the optimized plan.
    This function should determine the appropriate sorting of results.
    Input: Optimized query plan
    Output: ORDER BY clause string
    "
    pass

def summarize_result(result):
    "
    Create a summary of the query results.
    This function should provide key statistics and insights from the result set.
    Input: Query result set
    Output: Summary dictionary with key findings
    "
    pass

def get_query_performance_metrics(sql_query):
    "
    Retrieve performance metrics for the executed SQL query.
    This function should return execution time, rows processed, etc.
    Input: Executed SQL query
    Output: Dictionary of performance metrics
    "
    pass

def generate_recommendations(optimized_plan, result):
    "
    Generate recommendations for further analysis based on the query and its results.
    This function should suggest potential follow-up queries or areas of investigation.
    Input: Optimized query plan, Query result set
    Output: List of recommendations (strings)
    "
    pass

"""
    return GUIDE