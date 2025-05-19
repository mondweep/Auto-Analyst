import dspy
import src.agents.memory_agents as m
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv
import logging
from src.utils.logger import Logger
load_dotenv()

logger = Logger("agents", see_time=True, console_log=False)


AGENTS_WITH_DESCRIPTION = {
    "preprocessing_agent": "Cleans and prepares a DataFrame using Pandas and NumPy—handles missing values, detects column types, and converts date strings to datetime.",
    "statistical_analytics_agent": "Performs statistical analysis (e.g., regression, seasonal decomposition) using statsmodels, with proper handling of categorical data and missing values.",
    "sk_learn_agent": "Trains and evaluates machine learning models using scikit-learn, including classification, regression, and clustering with feature importance insights.",
    "data_viz_agent": "Generates interactive visualizations with Plotly, selecting the best chart type to reveal trends, comparisons, and insights based on the analysis goal."
}

PLANNER_AGENTS_WITH_DESCRIPTION = {
    "planner_preprocessing_agent": (
        "Cleans and prepares a DataFrame using Pandas and NumPy—"
        "handles missing values, detects column types, and converts date strings to datetime. "
        "Outputs a cleaned DataFrame for the planner_statistical_analytics_agent."
    ),
    "planner_statistical_analytics_agent": (
        "Takes the cleaned DataFrame from preprocessing, performs statistical analysis "
        "(e.g., regression, seasonal decomposition) using statsmodels with proper handling "
        "of categorical data and remaining missing values. "
        "Produces summary statistics and model diagnostics for the planner_sk_learn_agent."
    ),
    "planner_sk_learn_agent": (
        "Receives summary statistics and the cleaned data, trains and evaluates machine "
        "learning models using scikit-learn (classification, regression, clustering), "
        "and generates performance metrics and feature importance. "
        "Passes the trained models and evaluation results to the planner_data_viz_agent."
    ),
    "planner_data_viz_agent": (
        "Consumes trained models and evaluation results to create interactive visualizations "
        "with Plotly—selects the best chart type, applies styling, and annotates insights. "
        "Delivers ready-to-share figures that communicate model performance and key findings."
    ),
}

def get_agent_description(agent_name, is_planner=False):
    if is_planner:
        return PLANNER_AGENTS_WITH_DESCRIPTION[agent_name.lower()] if agent_name.lower() in PLANNER_AGENTS_WITH_DESCRIPTION else "No description available for this agent"
    else:
        return AGENTS_WITH_DESCRIPTION[agent_name.lower()] if agent_name.lower() in AGENTS_WITH_DESCRIPTION else "No description available for this agent"


# Agent to make a Chat history name from a query
class chat_history_name_agent(dspy.Signature):
    """You are an agent that takes a query and returns a name for the chat history"""
    query = dspy.InputField(desc="The query to make a name for")
    name = dspy.OutputField(desc="A name for the chat history (max 3 words)")

class dataset_description_agent(dspy.Signature):
    """You are an AI agent that generates a detailed description of a given dataset for both users and analysis agents.
Your description should serve two key purposes:
1. Provide users with context about the dataset's purpose, structure, and key attributes.
2. Give analysis agents critical data handling instructions to prevent common errors.

For data handling instructions, you must always include Python data types and address the following:
- Data type warnings (e.g., numeric columns stored as strings that need conversion).
- Null value handling recommendations.
- Format inconsistencies that require preprocessing.
- Explicit warnings about columns that appear numeric but are stored as strings (e.g., '10' vs 10).
- Explicit Python data types for each major column (e.g., int, float, str, bool, datetime).
- Columns with numeric values that should be treated as categorical (e.g., zip codes, IDs).
- Any date parsing or standardization required (e.g., MM/DD/YYYY to datetime).
- Any other technical considerations that would affect downstream analysis or modeling.
- List all columns and their data types with exact case sensitive spelling

If an existing description is provided, enhance it with both business context and technical guidance for analysis agents, preserving accurate information from the existing description or what the user has written.

Ensure the description is comprehensive and provides actionable insights for both users and analysis agents.


Example:
This housing dataset contains property details including price, square footage, bedrooms, and location data.
It provides insights into real estate market trends across different neighborhoods and property types.

TECHNICAL CONSIDERATIONS FOR ANALYSIS:
- price (str): Appears numeric but is stored as strings with a '$' prefix and commas (e.g., "$350,000"). Requires cleaning with str.replace('$','').replace(',','') and conversion to float.
- square_footage (str): Contains unit suffix like 'sq ft' (e.g., "1,200 sq ft"). Remove suffix and commas before converting to int.
- bedrooms (int): Correctly typed but may contain null values (~5% missing) – consider imputation or filtering.
- zip_code (int): Numeric column but should be treated as str or category to preserve leading zeros and prevent unintended numerical analysis.
- year_built (float): May contain missing values (~15%) – consider mean/median imputation or exclusion depending on use case.
- listing_date (str): Dates stored in "MM/DD/YYYY" format – convert to datetime using pd.to_datetime().
- property_type (str): Categorical column with inconsistent capitalization (e.g., "Condo", "condo", "CONDO") – normalize to lowercase for consistent grouping.
    """
    dataset = dspy.InputField(desc="The dataset to describe, including headers, sample data, null counts, and data types.")
    existing_description = dspy.InputField(desc="An existing description to improve upon (if provided).", default="")
    description = dspy.OutputField(desc="A comprehensive dataset description with business context and technical guidance for analysis agents.")


class analytical_planner(dspy.Signature):
    """
You are a data analytics planner agent. Your task is to generate the most efficient plan—using the fewest necessary agents and variables—to achieve a user-defined goal. The plan must preserve data integrity, avoid unnecessary steps, and ensure clear data flow between agents.

**Inputs**:

1. Datasets (raw or preprocessed)
2. Agent descriptions (roles, variables they create/use, constraints)
3. User-defined goal (e.g., prediction, analysis, visualization)

**Responsibilities**:

1. **Feasibility**: Confirm the goal is achievable with the provided data and agents; ask for clarification if it's unclear.
2. **Minimal Plan**: Use the smallest set of agents and variables; avoid redundant transformations; ensure agents are ordered logically and only included if essential.
3. **Instructions**: For each agent, define:

   * **create**: output variables and their purpose
   * **use**: input variables and their role
   * **instruction**: concise explanation of the agent's function and relevance to the goal
4. **Clarity**: Keep instructions precise; avoid intermediate steps unless necessary; ensure each agent has a distinct, relevant role.
5. **Attribute Filtering**: For filtering queries (e.g., "how many green vehicles?" or "which cars are under $30,000?"):
   * Identify the specific attribute being filtered (color, price, etc.)
   * Determine the filter condition (equality, less than, greater than)
   * Create a precise filtering operation that returns exactly what was asked
   * Return specific counts, lists, or summaries rather than general information
   * Always respond directly to the specific attribute-based question instead of providing general inventory information

When handling direct questions about counts, frequencies, or filters:
1. Identify the column/attribute specified in the question (color, make, year, etc.)
2. Apply the appropriate filter using pandas (df[df['column'] == value])
3. Return the exact count or list that answers the specific question
4. Structure your response to directly answer queries like "how many X?" with a number and supporting detail

Examples:
- For "how many green vehicles do we have?" - Return the count of vehicles where color='green'
- For "which cars cost less than $30,000?" - Filter by price < 30000 and list those vehicles
- For "how many vehicles are from 2022?" - Count rows where year=2022

### **Output Format**:
Example: 1 agent use
  goal: "Generate a bar plot showing sales by category after cleaning the raw data and calculating the average of the 'sales' column"
Output:
  plan: planner_data_viz_agent
{
  "planner_data_viz_agent": {
    "create": [
      "cleaned_data: DataFrame - cleaned version of df (pd.Dataframe) after removing null values"
    ],
    "use": [
      "df: DataFrame - unprocessed dataset (pd.Dataframe) containing sales and category information"
    ],
    "instruction": "Clean df by removing null values, calculate the average sales, and generate a bar plot showing sales by category."
  }
}

Example 3 Agent 
goal:"Clean the dataset, run a linear regression to model the relationship between marketing budget and sales, and visualize the regression line with confidence intervals."
plan: planner_preprocessing_agent -> planner_statistical_analytics_agent -> planner_data_viz_agent

{
  "planner_preprocessing_agent": {
    "create": [
      "cleaned_data: DataFrame - cleaned version of df with missing values handled and proper data types inferred"
    ],
    "use": [
      "df: DataFrame - dataset containing marketing budgets and sales figures"
    ],
    "instruction": "Clean df by handling missing values and converting column types (e.g., dates). Output cleaned_data for modeling."
  },

  "planner_statistical_analytics_agent": {
    "create": [
      "regression_results: dict - model summary including coefficients, p-values, R², and confidence intervals"
    ],
    "use": [
      "cleaned_data: DataFrame - preprocessed dataset ready for regression"
    ],
    "instruction": "Perform linear regression using cleaned_data to model sales as a function of marketing budget. Return regression_results including coefficients and confidence intervals."
  },

  "planner_data_viz_agent": {
    "create": [
      "regression_plot: PlotlyFigure - visual plot showing regression line with confidence intervals"
    ],
    "use": [
      "cleaned_data: DataFrame - original dataset for plotting",
      "regression_results: dict - output of linear regression"
    ],
    "instruction": "Generate a Plotly regression plot using cleaned_data and regression_results. Show the fitted line, scatter points, and 95% confidence intervals."
  }
}

Keep it as simple as possible, unless user specifies indepth query!

    """
    dataset = dspy.InputField(desc="Available datasets loaded in the system, use this df, columns set df as copy of df")
    Agent_desc = dspy.InputField(desc="The agents available in the system")
    goal = dspy.InputField(desc="The user defined goal")

    plan = dspy.OutputField(desc="The plan that would achieve the user defined goal", prefix='Plan:')
    plan_instructions = dspy.OutputField(desc="Detailed variable-level instructions per agent for the plan")
class planner_preprocessing_agent(dspy.Signature):
    """
You are a preprocessing agent in a multi-agent data analytics system.

You are given:

* A  dataset  (already loaded as `df`).
* A  user-defined analysis goal  (e.g., predictive modeling, exploration, cleaning).
*  Agent-specific plan instructions  that tell you what variables you are expected to  create  and what variables you are  receiving  from previous agents.
* processed_df is just an arbitrary name, it can be anything the planner says to clean!

### Your Responsibilities:

*  Follow the provided plan  and create only the required variables listed in the 'create' section of the plan instructions.
*  Do not create fake data  or introduce variables not explicitly part of the instructions.
*  Do not read data from CSV ; the dataset (`df`) is already loaded and ready for processing.
* Generate Python code using  NumPy  and  Pandas  to preprocess the data and produce any intermediate variables as specified in the plan instructions.

### Best Practices for Preprocessing:


1.  Create a copy of the original DataFrame : It will always be stored as df, it already exists use it!

    ```python
    processed_df = df.copy()
    ```

2.  Separate column types :

    ```python
    numeric_cols = processed_df.select_dtypes(include='number').columns
    categorical_cols = processed_df.select_dtypes(include='object').columns
    ```

3.  Handle missing values :

    ```python
    for col in numeric_cols:
        processed_df[col] = processed_df[col].fillna(processed_df[col].median())
    
    for col in categorical_cols:
        processed_df[col] = processed_df[col].fillna(processed_df[col].mode()[0] if not processed_df[col].mode().empty else 'Unknown')
    ```

4.  Convert string columns to datetime safely :

    ```python
    def safe_to_datetime(x):
        try:
            return pd.to_datetime(x, errors='coerce', cache=False)
        except (ValueError, TypeError):
            return pd.NaT
    
    cleaned_df['date_column'] = cleaned_df['date_column'].apply(safe_to_datetime)
    ```

> Replace `processed_df`,'cleaned_df' and `date_column` with whatever names the user or planner provides.


5.  Do not alter the DataFrame index :
   Avoid using `reset_index()`, `set_index()`, or reindexing unless explicitly instructed.

6.  Log assumptions and corrections  in comments to clarify any choices made during preprocessing.

7.  Do not mutate global state : Avoid in-place modifications unless clearly necessary (e.g., using `.copy()`).

8.  Handle data types properly :

   * Avoid coercing types blindly (e.g., don't compare timestamps to strings or floats).
   * Use `pd.to_datetime(..., errors='coerce')` for safe datetime parsing.

9.  Preserve column structure : Only drop or rename columns if explicitly instructed.

### Output:

1.  Code : Python code that performs the requested preprocessing steps as per the plan instructions.
2.  Summary : A brief explanation of what preprocessing was done (e.g., columns handled, missing value treatment).

### Principles to Follow:

-Never alter the DataFrame index  unless explicitly instructed.
-Handle missing data  explicitly, filling with default values when necessary.
-Preserve column structure  and avoid unnecessary modifications.
-Ensure data types are appropriate  (e.g., dates parsed correctly).
-Log assumptions  in the code.

    """
    dataset = dspy.InputField(desc="The dataset, preloaded as df")
    goal = dspy.InputField(desc="User-defined goal for the analysis")
    plan_instructions = dspy.InputField(desc="Agent-level instructions about what to create and receive")
    
    code = dspy.OutputField(desc="Generated Python code for preprocessing")
    summary = dspy.OutputField(desc="Explanation of what was done and why")
class planner_data_viz_agent(dspy.Signature):
    """
    ### **Data Visualization Agent Definition**

    You are the **data visualization agent** in a multi-agent analytics pipeline. Your primary responsibility is to **generate visualizations** based on the **user-defined goal** and the **plan instructions**.

    You are provided with:

    * **goal**: A user-defined goal outlining the type of visualization the user wants (e.g., "plot sales over time with trendline").
    * **dataset**: The dataset (e.g., `df_cleaned`) which will be passed to you by other agents in the pipeline. **Do not assume or create any variables** — **the data is already present and valid** when you receive it.
    * **styling_index**: Specific styling instructions (e.g., axis formatting, color schemes) for the visualization.
    * **plan_instructions**: A dictionary containing:

    * **'create'**: List of **visualization components** you must generate (e.g., 'scatter_plot', 'bar_chart').
    * **'use'**: List of **variables you must use** to generate the visualizations. This includes datasets and any other variables provided by the other agents.
    * **'instructions'**: A list of additional instructions related to the creation of the visualizations, such as requests for trendlines or axis formats.

    ---

    ### **Responsibilities**:

    1. **Strict Use of Provided Variables**:

    * You must **never create fake data**. Only use the variables and datasets that are explicitly **provided** to you in the `plan_instructions['use']` section. All the required data **must already be available**.
    * If any variable listed in `plan_instructions['use']` is missing or invalid, **you must return an error** and not proceed with any visualization.

    2. **Visualization Creation**:

    * Based on the **'create'** section of the `plan_instructions`, generate the **required visualization** using **Plotly**. For example, if the goal is to plot a time series, you might generate a line chart.
    * Respect the **user-defined goal** in determining which type of visualization to create.

    3. **Performance Optimization**:

    * If the dataset contains **more than 50,000 rows**, you **must sample** the data to **5,000 rows** to improve performance. Use this method:

        ```python
        if len(df) > 50000:
            df = df.sample(5000, random_state=42)
        ```

    4. **Layout and Styling**:

    * Apply formatting and layout adjustments as defined by the **styling_index**. This may include:

        * Axis labels and title formatting.
        * Tick formats for axes.
        * Color schemes or color maps for visual elements.
    * You must ensure that all axes (x and y) have **consistent formats** (e.g., using `K`, `M`, or 1,000 format, but not mixing formats).

    5. **Trendlines**:

    * Trendlines should **only be included** if explicitly requested in the **'instructions'** section of `plan_instructions`.

    6. **Displaying the Visualization**:

    * Use Plotly's `fig.show()` method to display the created chart.
    * **Never** output raw datasets or the **goal** itself. Only the visualization code and the chart should be returned.

    7. **Error Handling**:

    * If the required dataset or variables are missing or invalid (i.e., not included in `plan_instructions['use']`), return an error message indicating which specific variable is missing or invalid.
    * If the **goal** or **create** instructions are ambiguous or invalid, return an error stating the issue.

    8. **No Data Modification**:

    * **Never** modify the provided dataset or generate new data. If the data needs preprocessing or cleaning, assume it's already been done by other agents.

    ---

    ### **Strict Conditions**:

    * You **never** create any data.
    * You **only** use the data and variables passed to you.
    * If any required data or variable is missing or invalid, **you must stop** and return a clear error message.

    By following these conditions and responsibilities, your role is to ensure that the **visualizations** are generated as per the user goal, using the valid data and instructions given to you.

        """
    goal = dspy.InputField(desc="User-defined chart goal (e.g. trendlines, scatter plots)")
    dataset = dspy.InputField(desc="Details of the dataframe (`df`) and its columns")
    styling_index = dspy.InputField(desc="Instructions for plot styling and layout formatting")
    plan_instructions = dspy.InputField(desc="Variables to create and receive for visualization purposes")

    code = dspy.OutputField(desc="Plotly Python code for the visualization")
    summary = dspy.OutputField(desc="Plain-language summary of what is being visualized")

class planner_statistical_analytics_agent(dspy.Signature):
    """
**Agent Definition:**

You are a statistical analytics agent in a multi-agent data analytics pipeline.

You are given:

* A dataset (usually a cleaned or transformed version like `df_cleaned`).
* A user-defined goal (e.g., regression, seasonal decomposition).
* Agent-specific **plan instructions** specifying:

  * Which **variables** you are expected to **CREATE** (e.g., `regression_model`).
  * Which **variables** you will **USE** (e.g., `df_cleaned`, `target_variable`).
  * A set of **instructions** outlining additional processing or handling for these variables (e.g., handling missing values, adding constants, transforming features, etc.).

**Your Responsibilities:**

* Use the `statsmodels` library to implement the required statistical analysis.
* Ensure that all strings are handled as categorical variables via `C(col)` in model formulas.
* Always add a constant using `sm.add_constant()`.
* Do **not** modify the DataFrame's index.
* Convert `X` and `y` to float before fitting the model.
* Handle missing values before modeling.
* Avoid any data visualization (that is handled by another agent).
* Write output to the console using `print()`.

**If the goal is regression:**

* Use `statsmodels.OLS` with proper handling of categorical variables and adding a constant term.
* Handle missing values appropriately.

**If the goal is seasonal decomposition:**

* Use `statsmodels.tsa.seasonal_decompose`.
* Ensure the time series and period are correctly provided (i.e., `period` should not be `None`).

**You must not:**

* You must always create the variables in `plan_instructions['CREATE']`.
* **Never create the `df` variable**. Only work with the variables passed via the `plan_instructions`.
* Rely on hardcoded column names — use those passed via `plan_instructions`.
* Introduce or modify intermediate variables unless they are explicitly listed in `plan_instructions['CREATE']`.

**Instructions to Follow:**

1. **CREATE** only the variables specified in `plan_instructions['CREATE']`. Do not create any intermediate or new variables.
2. **USE** only the variables specified in `plan_instructions['USE']` to carry out the task.
3. Follow any **additional instructions** in `plan_instructions['INSTRUCTIONS']` (e.g., preprocessing steps, encoding, handling missing values).
4. **Do not reassign or modify** any variables passed via `plan_instructions`. These should be used as-is.

**Example Workflow:**
Given that the `plan_instructions` specifies variables to **CREATE** and **USE**, and includes instructions, your approach should look like this:

1. Use `df_cleaned` and the variables like `X` and `y` from `plan_instructions` for analysis.
2. Follow instructions for preprocessing (e.g., handle missing values or scale features).
3. If the goal is regression:

   * Use `sm.OLS` for model fitting.
   * Handle categorical variables via `C(col)` and add a constant term.
4. If the goal is seasonal decomposition:

   * Ensure `period` is provided and use `sm.tsa.seasonal_decompose`.
5. Store the output variable as specified in `plan_instructions['CREATE']`.

### Example Code Structure:

```python
import statsmodels.api as sm

def statistical_model(X, y, goal, period=None):
    try:
        X = X.dropna()
        y = y.loc[X.index].dropna()
        X = X.loc[y.index]
        
        for col in X.select_dtypes(include=['object', 'category']).columns:
            X[col] = X[col].astype('category')
        
        # Add constant term to X
        X = sm.add_constant(X)

        if goal == 'regression':
            formula = 'y ~ ' + ' + '.join([f'C({col})' if X[col].dtype.name == 'category' else col for col in X.columns])
            model = sm.OLS(y.astype(float), X.astype(float)).fit()
            regression_model = model.summary()  # Specify as per CREATE instructions
            return regression_model
        
        elif goal == 'seasonal_decompose':
            if period is None:
                raise ValueError("Period must be specified for seasonal decomposition")
            decomposition = sm.tsa.seasonal_decompose(y, period=period)
            seasonal_decomposition = decomposition  # Specify as per CREATE instructions
            return seasonal_decomposition
        
        else:
            raise ValueError("Unknown goal specified.")
        
    except Exception as e:
        return f"An error occurred: {e}"
```

**Summary:**

1. Always **USE** the variables passed in `plan_instructions['USE']` to carry out the task.
2. Only **CREATE** the variables specified in `plan_instructions['CREATE']`. Do not create any additional variables.
3. Follow any **additional instructions** in `plan_instructions['INSTRUCTIONS']` (e.g., handling missing values, adding constants).
4. Ensure reproducibility by setting the random state appropriately and handling categorical variables.
5. Focus on statistical analysis and avoid any unnecessary data manipulation.

**Output:**

* The **code** implementing the statistical analysis, including all required steps.
* A **summary** of what the statistical analysis does, how it's performed, and why it fits the goal.

    """
    dataset = dspy.InputField(desc="Preprocessed dataset, often named df_cleaned")
    goal = dspy.InputField(desc="The user's statistical analysis goal, e.g., regression or seasonal_decompose")
    plan_instructions = dspy.InputField(desc="Instructions on variables to create and receive for statistical modeling")
    
    code = dspy.OutputField(desc="Python code for statistical modeling using statsmodels")
    summary = dspy.OutputField(desc="Explanation of statistical analysis steps")
    
    
class planner_sk_learn_agent(dspy.Signature):
    """
    **Agent Definition:**

    You are a machine learning agent in a multi-agent data analytics pipeline.

    You are given:

    * A dataset (often cleaned and feature-engineered).
    * A user-defined goal (e.g., classification, regression, clustering).
    * Agent-specific **plan instructions** specifying:

    * Which **variables** you are expected to **CREATE** (e.g., `trained_model`, `predictions`).
    * Which **variables** you will **USE** (e.g., `df_cleaned`, `target_variable`, `feature_columns`).
    * A set of **instructions** outlining additional processing or handling for these variables (e.g., handling missing values, applying transformations, or other task-specific guidelines).

    **Your Responsibilities:**

    * Use the scikit-learn library to implement the appropriate ML pipeline.
    * Always split data into training and testing sets where applicable.
    * Use `print()` for all outputs.
    * Ensure your code is:

    * **Reproducible**: Set `random_state=42` wherever applicable.
    * **Modular**: Avoid deeply nested code.
    * **Focused on model building**, not visualization (leave plotting to the `data_viz_agent`).
    * Your task may include:

    * Preprocessing inputs (e.g., encoding).
    * Model selection and training.
    * Evaluation (e.g., accuracy, RMSE, classification report).

    **You must not:**

    * Visualize anything (that's another agent's job).
    * Rely on hardcoded column names — use those passed via `plan_instructions`.
    * **Never create or modify any variables not explicitly mentioned in `plan_instructions['CREATE']`.**
    * **Never create the `df` variable**. You will **only** work with the variables passed via the `plan_instructions`.
    * Do not introduce intermediate variables unless they are listed in `plan_instructions['CREATE']`.

    **Instructions to Follow:**

    1. **CREATE** only the variables specified in the `plan_instructions['CREATE']` list. Do not create any intermediate or new variables.
    2. **USE** only the variables specified in the `plan_instructions['USE']` list. You are **not allowed** to create or modify any variables not listed in the plan instructions.
    3. Follow any **processing instructions** in the `plan_instructions['INSTRUCTIONS']` list. This might include tasks like handling missing values, scaling features, or encoding categorical variables. Always perform these steps on the variables specified in the `plan_instructions`.
    4. Do **not reassign or modify** any variables passed via `plan_instructions`. These should be used as-is.

    **Example Workflow:**
    Given that the `plan_instructions` specifies variables to **CREATE** and **USE**, and includes instructions, your approach should look like this:

    1. Use `df_cleaned` and `feature_columns` from the `plan_instructions` to extract your features (`X`).
    2. Use `target_column` from `plan_instructions` to extract your target (`y`).
    3. If instructions are provided (e.g., scale or encode), follow them.
    4. Split data into training and testing sets using `train_test_split`.
    5. Train the model based on the received goal (classification, regression, etc.).
    6. Store the output variables as specified in `plan_instructions['CREATE']`.

    ### Example Code Structure:

    ```python
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report
    from sklearn.preprocessing import StandardScaler

    # Ensure that all variables follow plan instructions:
    # Use received inputs: df_cleaned, feature_columns, target_column
    X = df_cleaned[feature_columns]
    y = df_cleaned[target_column]

    # Apply any preprocessing instructions (e.g., scaling if instructed)
    if 'scale' in plan_instructions['INSTRUCTIONS']:
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Select and train the model (based on the task)
    model = LogisticRegression(random_state=42)
    model.fit(X_train, y_train)

    # Generate predictions
    predictions = model.predict(X_test)

    # Create the variable specified in 'plan_instructions': 'metrics'
    metrics = classification_report(y_test, predictions)

    # Print the results
    print(metrics)

    # Ensure the 'metrics' variable is returned as requested in the plan
    ```

    **Summary:**

    1. Always **USE** the variables passed in `plan_instructions['USE']` to build the pipeline.
    2. Only **CREATE** the variables specified in `plan_instructions['CREATE']`. Do not create any additional variables.
    3. Follow any **additional instructions** in `plan_instructions['INSTRUCTIONS']` (e.g., preprocessing steps).
    4. Ensure reproducibility by setting `random_state=42` wherever necessary.
    5. Focus on model building, evaluation, and saving the required outputs—avoid any unnecessary variables.

    **Output:**

    * The **code** implementing the ML task, including all required steps.
    * A **summary** of what the model does, how it is evaluated, and why it fits the goal.



    """
    dataset = dspy.InputField(desc="Input dataset, often cleaned and feature-selected (e.g., df_cleaned)")
    goal = dspy.InputField(desc="The user's machine learning goal (e.g., classification or regression)")
    plan_instructions = dspy.InputField(desc="Instructions indicating what to create and what variables to receive")

    code = dspy.OutputField(desc="Scikit-learn based machine learning code")
    summary = dspy.OutputField(desc="Explanation of the ML approach and evaluation")

class story_teller_agent(dspy.Signature):
    # Optional helper agent, which can be called to build a analytics story 
    # For all of the analysis performed
    """ You are a story teller agent, taking output from different data analytics agents, you compose a compelling story for what was done """
    agent_analysis_list =dspy.InputField(desc="A list of analysis descriptions from every agent")
    story = dspy.OutputField(desc="A coherent story combining the whole analysis")

class code_combiner_agent(dspy.Signature):
    # Combines code from different agents into one script
    """ You are a code combine agent, taking Python code output from many agents and combining the operations into 1 output
    You also fix any errors in the code. 

    IMPORTANT: You may be provided with previous interaction history. The section marked "### Current Query:" contains the user's current request. Any text in "### Previous Interaction History:" is for context only and is NOT part of the current request.

    Double check column_names/dtypes using dataset, also check if applied logic works for the datatype
    df = df.copy()
    Also add this to display Plotly chart
    fig.show()

    Make sure your output is as intended!

    Provide a concise bullet-point summary of the code integration performed.
    
    Example Summary:
    • Integrated preprocessing, statistical analysis, and visualization code into a single workflow.
    • Fixed variable scope issues, standardized DataFrame handling (e.g., using `df.copy()`), and corrected errors.
    • Validated column names and data types against the dataset definition to prevent runtime issues.
    • Ensured visualizations are displayed correctly (e.g., added `fig.show()`).

    """
    dataset = dspy.InputField(desc="Use this double check column_names, data types")
    agent_code_list =dspy.InputField(desc="A list of code given by each agent")
    refined_complete_code = dspy.OutputField(desc="Refined complete code base")
    summary = dspy.OutputField(desc="A concise 4 bullet-point summary of the code integration performed and improvements made")
    
    
class data_viz_agent(dspy.Signature):
    # Visualizes data using Plotly
    """    
    You are an AI agent responsible for generating interactive data visualizations using Plotly.

    IMPORTANT Instructions:

    - The section marked "### Current Query:" contains the user's request. Any text in "### Previous Interaction History:" is for context only and should NOT be treated as part of the current request.
    - You must only use the tools provided to you. This agent handles visualization only.
    - If len(df) > 50000, always sample the dataset before visualization using:  
    if len(df) > 50000:  
        df = df.sample(50000, random_state=1)

    - Each visualization must be generated as a **separate figure** using go.Figure().  
    Do NOT use subplots under any circumstances.

    - Each figure must be returned individually using:  
    fig.to_html(full_html=False)

    - Use update_layout with xaxis and yaxis **only once per figure**.

    - Enhance readability and clarity by:  
    • Using low opacity (0.4-0.7) where appropriate  
    • Applying visually distinct colors for different elements or categories  

    - Make sure the visual **answers the user's specific goal**:  
    • Identify what insight or comparison the user is trying to achieve  
    • Choose the visualization type and features (e.g., color, size, grouping) to emphasize that goal  
    • For example, if the user asks for "trends in revenue," use a time series line chart; if they ask for "top-performing categories," use a bar chart sorted by value  
    • Prioritize highlighting patterns, outliers, or comparisons relevant to the question

    - For attribute-specific queries (e.g., "show me green vehicles" or "how many green vehicles do we have?"):
      • ALWAYS filter the data using case-insensitive string matching and handle NaN values:
        df['color'] = df['color'].astype(str)  # Convert to string to handle NaN
        filtered_df = df[df['color'].str.lower() == 'green']
      • For counting queries, use bar or pie charts that clearly display the count in the title
      • ALWAYS include the exact count and percentage in the chart title (e.g., "Count of Green Vehicles: 17 (8.5% of inventory)")
      • Make sure to handle case-insensitive matching by converting to lowercase before comparing
      • For comparison queries, create visualizations that show the filtered group vs. all others
      • Calculate percentages accurately: (count / total_vehicles) * 100
      • Always ensure the query result directly answers the specific question asked

    - For numerical filtering queries (e.g., "vehicles under $30,000"):
      • ALWAYS use proper comparison operators (df[df['price'] < 30000])
      • Include both the count and percentage of the total in the title
      • Choose appropriate visualization types based on the question

    - Never include the dataset or styling index in the output.

    - If there are no relevant columns for the requested visualization, respond with:  
    "No relevant columns found to generate this visualization."

    - Use only one number format consistently: either 'K', 'M', or comma-separated values like 1,000/1,000,000. Do not mix formats.

    - Only include trendlines in scatter plots if the user explicitly asks for them.

    - Output only the code and a concise bullet-point summary of what the visualization reveals.

    - Always end each visualization with:  
    fig.to_html(full_html=False)

    Example Summary:  
    • Created an interactive bar chart showing the count of green vehicles (17 vehicles or 8.5% of inventory)
    • Included a filter for only vehicles with color="green" (case-insensitive matching)
    • Added hover information showing make, model and price for each vehicle
    • Color-coded bars by vehicle condition to provide additional insight
    • Visualization clearly shows the exact count requested in the question
    """
    goal = dspy.InputField(desc="user defined goal which includes information about data and chart they want to plot")
    dataset = dspy.InputField(desc=" Provides information about the data in the data frame. Only use column names and dataframe_name as in this context")
    styling_index = dspy.InputField(desc='Provides instructions on how to style your Plotly plots')
    code= dspy.OutputField(desc="Plotly code that visualizes what the user needs according to the query & dataframe_index & styling_context")
    summary = dspy.OutputField(desc="A concise bullet-point summary of the visualization created and key insights revealed")
    
    

class code_fix(dspy.Signature):
    """
You are an expert AI developer and data analyst assistant, skilled at identifying and resolving issues in Python code related to data analytics. Another agent has attempted to generate Python code for a data analytics task but produced code that is broken or throws an error.

Your task is to:
1. Carefully examine the provided **faulty_code** and the corresponding **error** message.
2. Identify the **exact cause** of the failure based on the error and surrounding context.
3. Modify only the necessary portion(s) of the code to fix the issue, utilizing the **dataset_context** to inform your corrections.
4. Ensure the **intended behavior** of the original code is preserved (e.g., if the code is meant to filter, group, or visualize data, that functionality must be preserved).
5. Ensure the final output is **runnable**, **error-free**, and **logically consistent**.

Strict instructions:
- Assume the dataset is already loaded and available in the code context; do not include any code to read, load, or create data.
- Do **not** modify any working parts of the code unnecessarily.
- Do **not** change variable names, structure, or logic unless it directly contributes to resolving the issue.
- Do **not** output anything besides the corrected, full version of the code (i.e., no explanations, comments, or logs).
- Avoid introducing new dependencies or libraries unless absolutely required to fix the problem.
- The output must be complete and executable as-is.

Be precise, minimal, and reliable. Prioritize functional correctness.

One-shot example:
===
dataset_context: 
"This dataset contains historical price and trading data for two major financial assets: the S&P 500 index and Bitcoin (BTC). The data includes daily price metrics (open, high, low, close) and percentage changes for both assets... Change % columns are stored as strings with '%' symbol (e.g., '-5.97%') and require cleaning."

faulty_code:
# Convert percentage strings to floats
df['Change %'] = df['Change %'].str.rstrip('%').astype(float)
df['Change % BTC'] = df['Change % BTC'].str.rstrip('%').astype(float)

error:
Error in data_viz_agent: Can only use .str accessor with string values!
Traceback (most recent call last):
  File "/app/scripts/format_response.py", line 196, in execute_code_from_markdown
    exec(block_code, context)
AttributeError: Can only use .str accessor with string values!

fixed_code:
# Convert percentage strings to floats
df['Change %'] = df['Change %'].astype(str).str.rstrip('%').astype(float)
df['Change % BTC'] = df['Change % BTC'].astype(str).str.rstrip('%').astype(float)
===

    """
    dataset_context = dspy.InputField(desc="The dataset context to be used for the code fix")
    faulty_code = dspy.InputField(desc="The faulty Python code used for data analytics")
    error = dspy.InputField(desc="The error message thrown when running the code")
    fixed_code = dspy.OutputField(desc="The corrected and executable version of the code")

class code_edit(dspy.Signature):
    """
You are an expert AI code editor that specializes in modifying existing data analytics code based on user requests. The user provides a working or partially working code snippet, a natural language prompt describing the desired change, and dataset context information.

Your job is to:
1. Analyze the provided original_code, user_prompt, and dataset_context.
2. Modify only the part(s) of the code that are relevant to the user's request, using the dataset context to inform your edits.
3. Leave all unrelated parts of the code unchanged, unless the user explicitly requests a full rewrite or broader changes.
4. Ensure that your changes maintain or improve the functionality and correctness of the code.

Strict requirements:
- Assume the dataset is already loaded and available in the code context; do not include any code to read, load, or create data.
- Do not change variable names, function structures, or logic outside the scope of the user's request.
- Do not refactor, optimize, or rewrite unless explicitly instructed.
- Ensure the edited code remains complete and executable.
- Output only the modified code, without any additional explanation, comments, or extra formatting.

Make your edits precise, minimal, and faithful to the user's instructions, using the dataset context to guide your modifications.
    """
    dataset_context = dspy.InputField(desc="The dataset context to be used for the code edit, including information about the dataset's shape, columns, types, and null values")
    original_code = dspy.InputField(desc="The original code the user wants modified")
    user_prompt = dspy.InputField(desc="The user instruction describing how the code should be changed")
    edited_code = dspy.OutputField(desc="The updated version of the code reflecting the user's request, incorporating changes informed by the dataset context")

# The ind module is called when agent_name is 
# explicitly mentioned in the query
class auto_analyst_ind(dspy.Module):
    """Handles individual agent execution when explicitly specified in query"""
    
    def __init__(self, agents, retrievers):
        # Initialize agent modules and retrievers
        self.agents = {}
        self.agent_inputs = {}
        self.agent_desc = []
        
        # Create modules from agent signatures
        for i, a in enumerate(agents):
            name = a.__pydantic_core_schema__['schema']['model_name']
            self.agents[name] = dspy.ChainOfThoughtWithHint(a)
            self.agent_inputs[name] = {x.strip() for x in str(agents[i].__pydantic_core_schema__['cls']).split('->')[0].split('(')[1].split(',')}
            self.agent_desc.append(get_agent_description(name))
            
        # Initialize components
        self.memory_summarize_agent = dspy.ChainOfThought(m.memory_summarize_agent)
        self.dataset = retrievers['dataframe_index'].as_retriever(k=1)
        self.styling_index = retrievers['style_index'].as_retriever(similarity_top_k=1)
        self.code_combiner_agent = dspy.ChainOfThought(code_combiner_agent)
        
        # Initialize thread pool
        self.executor = ThreadPoolExecutor(max_workers=min(4, os.cpu_count() * 2))
    
    def execute_agent(self, specified_agent, inputs):
        """Execute agent and generate memory summary in parallel"""
        try:
            # Execute main agent
            agent_result = self.agents[specified_agent.strip()](**inputs)
            return specified_agent.strip(), dict(agent_result)
            
        except Exception as e:
            return specified_agent.strip(), {"error": str(e)}

    def execute_agent_with_memory(self, specified_agent, inputs, query):
        """Execute agent and generate memory summary in parallel"""
        try:
            # Execute main agent
            agent_result = self.agents[specified_agent.strip()](**inputs)
            agent_dict = dict(agent_result)
            
            # Generate memory summary
            memory_result = self.memory_summarize_agent(
                agent_response=specified_agent+' '+agent_dict['code']+'\n'+agent_dict['summary'],
                user_goal=query
            )
            
            return {
                specified_agent.strip(): agent_dict,
                'memory_'+specified_agent.strip(): str(memory_result.summary)
            }
        except Exception as e:
            return {"error": str(e)}

    def forward(self, query, specified_agent):
        try:
            # If specified_agent contains multiple agents separated by commas
            # This is for handling multiple @agent mentions in one query
            if "," in specified_agent:
                agent_list = [agent.strip() for agent in specified_agent.split(",")]
                return self.execute_multiple_agents(query, agent_list)
            
            # Process query with specified agent (single agent case)
            dict_ = {}
            dict_['dataset'] = self.dataset.retrieve(query)[0].text
            dict_['styling_index'] = self.styling_index.retrieve(query)[0].text
            dict_['hint'] = []
            dict_['goal'] = query
            dict_['Agent_desc'] = str(self.agent_desc)

            # Prepare inputs
            inputs = {x:dict_[x] for x in self.agent_inputs[specified_agent.strip()]}
            inputs['hint'] = str(dict_['hint']).replace('[','').replace(']','')
            
            # Execute agent
            result = self.agents[specified_agent.strip()](**inputs)
            output_dict = {specified_agent.strip(): dict(result)}

            if "error" in output_dict:
                return {"response": f"Error executing agent: {output_dict['error']}"}

            return output_dict

        except Exception as e:
            return {"response": f"This is the error from the system: {str(e)}"}
    
    def execute_multiple_agents(self, query, agent_list):
        """Execute multiple agents sequentially on the same query"""
        try:
            # Initialize resources
            dict_ = {}
            dict_['dataset'] = self.dataset.retrieve(query)[0].text
            dict_['styling_index'] = self.styling_index.retrieve(query)[0].text
            dict_['hint'] = []
            dict_['goal'] = query
            dict_['Agent_desc'] = str(self.agent_desc)
            
            results = {}
            code_list = []
            
            # Execute each agent sequentially
            for agent_name in agent_list:
                if agent_name not in self.agents:
                    results[agent_name] = {"error": f"Agent '{agent_name}' not found"}
                    continue
                
                # Prepare inputs for this agent
                inputs = {x:dict_[x] for x in self.agent_inputs[agent_name] if x in dict_}
                inputs['hint'] = str(dict_['hint']).replace('[','').replace(']','')
                
                # Execute agent
                agent_result = self.agents[agent_name](**inputs)
                agent_dict = dict(agent_result)
                results[agent_name] = agent_dict
                
                # Collect code for later combination
                if 'code' in agent_dict:
                    code_list.append(agent_dict['code'])
            
            return results
            
        except Exception as e:
            return {"response": f"Error executing multiple agents: {str(e)}"}


# Add stub for goal_refiner_agent
class goal_refiner_agent(dspy.Signature):
    """
    This is a stub for the goal_refiner_agent that refines user goals into more specific tasks.
    The actual implementation has been moved or is not available.
    """
    goal = dspy.InputField(desc="The original user goal")
    dataset = dspy.InputField(desc="The dataset context")
    
    refined_goal = dspy.OutputField(desc="The refined, more specific goal")
    reason = dspy.OutputField(desc="Reasoning for the refinement")


# This is the auto_analyst with planner
class auto_analyst(dspy.Module):
    """Main analyst module that coordinates multiple agents using a planner"""
    
    def __init__(self, agents, retrievers):
        # Initialize agent modules and retrievers
        super().__init__()
        
        # Fix: Using a different approach to initialize available_agents
        self.agents = {}
        self.agent_inputs = {}
        self.agent_desc = []
        
        for i, a in enumerate(agents):
            name = a.__class__.__name__
            self.agents[name] = dspy.ChainOfThought(a)
        
        # Store retrievers
        self.available_retrievers = {r.__class__.__name__: r for r in retrievers}
        
        # Fix: Using a direct approach instead of goal_refiner_agent
        self.predictor = analytical_planner
        
        # Initialize coordination agents
        self.planner = dspy.ChainOfThought(analytical_planner)
        # Remove the problematic line that references goal_refiner_agent
        # self.refine_goal = dspy.ChainOfThought(goal_refiner_agent)
        self.code_combiner_agent = dspy.ChainOfThought(code_combiner_agent)
        self.story_teller = dspy.ChainOfThought(story_teller_agent)
        self.memory_summarize_agent = dspy.ChainOfThought(m.memory_summarize_agent)
                
        # Initialize retrievers
        self.dataset = retrievers['dataframe_index'].as_retriever(k=1)
        self.styling_index = retrievers['style_index'].as_retriever(similarity_top_k=1)
        
        # Initialize thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=min(len(agents) + 2, os.cpu_count() * 2))

    def detect_attribute_query(self, query):
        """Detect if a query is asking about a specific attribute"""
        # Common patterns for attribute-specific queries
        attribute_patterns = [
            # Color-based queries
            r'how many (green|red|blue|black|white|silver|gray|yellow|orange|purple|pink|brown) vehicles',
            r'count of (green|red|blue|black|white|silver|gray|yellow|orange|purple|pink|brown) (cars|vehicles)',
            r'show me (green|red|blue|black|white|silver|gray|yellow|orange|purple|pink|brown) (cars|vehicles)',
            
            # Price-based queries
            r'how many (cars|vehicles) (cost|are|priced) (less|more|under|over) than \$?\d+',
            r'vehicles (under|over) \$\d+',
            
            # Make-based queries
            r'how many (toyota|honda|ford|bmw|mercedes|audi|tesla|hyundai|kia|nissan|chevrolet) (cars|vehicles)',
            r'count of (toyota|honda|ford|bmw|mercedes|audi|tesla|hyundai|kia|nissan|chevrolet)',
            
            # Condition-based queries
            r'how many (excellent|good|fair|poor) condition (cars|vehicles)',
            
            # Year-based queries
            r'how many (cars|vehicles) from (year|\d{4})',
            r'how many (cars|vehicles) (made|manufactured) in (\d{4})'
        ]
        
        import re
        for pattern in attribute_patterns:
            if re.search(pattern, query.lower()):
                return True
        return False
        
    def get_attribute_plan(self, query):
        """Generate a plan specifically for attribute filtering"""
        attribute_type = None
        attribute_value = None
        
        # Detect attribute patterns
        import re
        
        # Check for color attributes
        color_match = re.search(r'how many (\w+) vehicles|show me (\w+) vehicles|count of (\w+) (vehicles|cars)', query.lower())
        if color_match:
            # Extract the matched group that contains the color
            color_value = next((group for group in color_match.groups() if group and group not in ['vehicles', 'cars']), None)
            if color_value and color_value.lower() in ['green', 'red', 'blue', 'black', 'white', 'silver', 'gray', 'yellow', 'orange', 'purple', 'pink', 'brown']:
                attribute_type = "color"
                attribute_value = color_value
        
        # Check for make attributes
        make_match = re.search(r'how many (\w+) (vehicles|cars)', query.lower())
        if make_match and not attribute_type:
            make_value = make_match.group(1)
            if make_value.lower() in ['toyota', 'honda', 'ford', 'bmw', 'mercedes', 'audi', 'tesla', 'hyundai', 'kia', 'nissan', 'chevrolet']:
                attribute_type = "make"
                attribute_value = make_value
        
        # Check for condition attributes
        condition_match = re.search(r'(excellent|good|fair|poor) condition', query.lower())
        if condition_match and not attribute_type:
            attribute_type = "condition"
            attribute_value = condition_match.group(1)
            
        # Check for year attributes
        year_match = re.search(r'from (\d{4})|made in (\d{4})|manufactured in (\d{4})', query.lower())
        if year_match and not attribute_type:
            # Extract the matched year from whichever group it's in
            year_value = next((group for group in year_match.groups() if group), None)
            if year_value:
                attribute_type = "year"
                attribute_value = year_value
                
        # Check for price attributes
        price_match = re.search(r'(under|over) \$?(\d+)', query.lower())
        if price_match and not attribute_type:
            comparison = price_match.group(1)
            price_value = price_match.group(2)
            attribute_type = "price"
            attribute_value = price_value
            
            # Add comparison type for price
            comparison_operator = "<" if comparison == "under" else ">"
            
            plan = {
                "plan": "planner_data_viz_agent",
                "plan_instructions": {
                    "planner_data_viz_agent": {
                        "create": [
                            "price_filtered_chart: PlotlyFigure - chart showing vehicles filtered by price"
                        ],
                        "use": [
                            "df: DataFrame - the vehicles dataset with price information"
                        ],
                        "instruction": f"Filter the dataset for vehicles where price {comparison_operator} {attribute_value} and create a visualization showing the count and percentage of total. Make sure to explicitly state the count in the chart title."
                    }
                }
            }
            return plan
        
        # If we identified an attribute query, create a specialized plan
        if attribute_type and attribute_value:
            plan = {
                "plan": "planner_data_viz_agent",
                "plan_instructions": {
                    "planner_data_viz_agent": {
                        "create": [
                            f"{attribute_type}_filtered_chart: PlotlyFigure - chart showing count of vehicles filtered by {attribute_type}"
                        ],
                        "use": [
                            "df: DataFrame - the vehicles dataset with attribute information"
                        ],
                        "instruction": f"Filter the dataset to count vehicles where {attribute_type}='{attribute_value}' (case-insensitive) and create a visualization showing the count and percentage of total. Make sure to explicitly state the count in the chart title and use case-insensitive matching by converting values to lowercase before comparing."
                    }
                }
            }
            return plan
        return None

    def execute_agent(self, agent_name, inputs):
        """Execute a single agent with given inputs"""
        try:
            result = self.agents[agent_name.strip()](**inputs)
            return agent_name.strip(), dict(result)
        except Exception as e:
            return agent_name.strip(), {"error": str(e)}

    def get_plan(self, query):
        """Get the analysis plan"""
        # Check if this is an attribute-specific query
        if self.detect_attribute_query(query):
            attribute_plan = self.get_attribute_plan(query)
            if attribute_plan:
                return attribute_plan
        
        # Continue with normal planning for non-attribute queries
        dict_ = {}
        dict_['dataset'] = self.dataset.retrieve(query)[0].text
        dict_['styling_index'] = self.styling_index.retrieve(query)[0].text
        dict_['goal'] = query
        dict_['Agent_desc'] = str(self.agent_desc)
        
        plan = self.planner(goal=dict_['goal'], dataset=dict_['dataset'], Agent_desc=dict_['Agent_desc'])
        return dict(plan)

    async def execute_plan(self, query, plan):
        """Execute the plan and yield results as they complete"""
        dict_ = {}
        dict_['dataset'] = self.dataset.retrieve(query)[0].text
        dict_['styling_index'] = self.styling_index.retrieve(query)[0].text
        dict_['hint'] = []
        dict_['goal'] = query
        
        import json

        # Clean and split the plan string into agent names
        plan_text = plan.get("plan", "").replace("Plan", "").replace(":", "").strip()
        plan_list = [agent.strip() for agent in plan_text.split("->") if agent.strip()]

        # Parse the attached plan_instructions into a dict
        raw_instr = plan.get("plan_instructions", {})
        if isinstance(raw_instr, str):
            try:
                plan_instructions = json.loads(raw_instr)
            except Exception:
                plan_instructions = {}
        elif isinstance(raw_instr, dict):
            plan_instructions = raw_instr
        else:
            plan_instructions = {}

        # If no plan was produced, short-circuit
        if not plan_list:
            yield "plan_not_found", dict(plan), {"error": "No plan found"}
            return

        # Launch each agent in parallel, attaching its own instructions
        futures = []
        for idx, agent_name in enumerate(plan_list):
            key = agent_name.strip()
            # gather input fields except plan_instructions
            inputs = {
                param: dict_[param]
                for param in self.agent_inputs[key]
                if param != "plan_instructions"
            }
            
            # attach the specific instructions for this agent with prev/next format
            if "plan_instructions" in self.agent_inputs[key]:
                # Get current agent instructions
                current_instructions = plan_instructions.get(key, {"create": [], "use": [], "instruction": ""})
                
                # Format instructions with your_task first
                formatted_instructions = {"your_task": current_instructions}
                
                # Add previous agent instructions if available
                if idx > 0:
                    prev_agent = plan_list[idx-1].strip()
                    prev_instructions = plan_instructions.get(prev_agent, {}).get("instruction", "")
                    formatted_instructions[f"Previous Agent {prev_agent}"] = prev_instructions
                
                # Add next agent instructions if available
                if idx < len(plan_list) - 1:
                    next_agent = plan_list[idx+1].strip()
                    next_instructions = plan_instructions.get(next_agent, {}).get("instruction", "")
                    formatted_instructions[f"Next Agent {next_agent}"] = next_instructions
                
                
                inputs["plan_instructions"] = str(formatted_instructions)
            logger.log_message(f"Inputs: {inputs}", level=logging.INFO)
            future = self.executor.submit(self.execute_agent, agent_name, inputs)
            futures.append((agent_name, inputs, future))
        
        # Yield results as they complete 
        completed_results = []
        for agent_name, inputs, future in futures:
            try:
                name, result = await asyncio.get_event_loop().run_in_executor(None, future.result)
                completed_results.append((name, result))
                yield name, inputs, result
            except Exception as e:
                yield agent_name, inputs, {"error": str(e)}