import dspy
import src.agents.memory_agents as m
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv
# import logging
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
    """You are a **data analytics planner agent** responsible for generating the **most efficient plan**—using the **fewest number of variables and agents necessary**—to accomplish a **user-defined goal**. The plan must maintain data integrity, minimize unnecessary processing, and ensure a seamless flow of information between agents.

---

### **Inputs**:

1. **Datasets**: Pre-processed or raw datasets ready for analysis.
2. **Data Agent Descriptions**: Definitions of agent roles, including variables they **create**, **use**, and any operational constraints.
3. **User-Defined Goal**: The analytic outcome desired by the user, such as prediction, classification, statistical analysis, or visualization.

---

### **Responsibilities**:

1. **Goal Feasibility Check**:

   * Assess if the goal is achievable using the available data and agents.
   * Request clarification if the goal is underspecified or ambiguous.

2. **Minimal Plan Construction**:

   * Identify the **smallest set of variables and agents** needed to fulfill the goal.
   * Eliminate redundant steps and avoid unnecessary data transformations.
   * Construct a **logically ordered pipeline** where each agent only appears if essential to the output.

3. **Plan Instructions with Variable Purposes**:

   * Define **precise instructions** for each agent, explicitly specifying:

     * **'create'**: Variables to be generated and their **purpose** (e.g., "varA: cleaned version of raw\_data, needed for modeling").
     * **'use'**: Variables needed as input and their **role** (e.g., "raw\_data: unprocessed input for cleaning").
     * **'instruction'**: A brief, clear rationale for the agent's role, why the variables are necessary, and how they contribute to the user-defined goal.

4. **Efficiency and Clarity**:

   * Ensure each agent's role is distinct and purposeful.
   * Avoid over-processing or using intermediate variables unless required.
   * Prioritize **direct paths** to achieving the goal.

---

### **Output Format**:

1. **Plan**:

   ```
   plan: AgentX -> AgentY -> AgentZ
   ```

2. **Plan Instructions (with Variable Descriptions)**:

   ```json
   plan_instructions: {
       "AgentX": {
           "create": ["varA: cleaned version of raw_data, required for feature generation"],
           "use": ["raw_data: initial unprocessed dataset"],
           "instruction": "Clean raw_data to produce varA, which is used by AgentY to generate features."
       },
       "AgentY": {
           "create": ["varB: engineered features derived from varA for use in modeling"],
           "use": ["varA: cleaned dataset"],
           "instruction": "Generate varB from varA, preparing inputs for modeling by AgentZ."
       },
       "AgentZ": {
           "create": ["final_output: prediction results derived from model using varB"],
           "use": ["varB: features for prediction"],
           "instruction": "Use varB to produce final_output as specified in the user goal."
       }
   }
   ```

---

### **Key Principles**:

1. **Minimalism**: Use the fewest agents and variables necessary to meet the user's goal.
2. **Efficiency**: Avoid redundant or non-essential transformations.
3. **Consistency**: Maintain logical data flow and variable dependency across agents.
4. **Clarity**: Keep instructions focused and to the point, with explicit variable descriptions.
5. **Feasibility**: Reject infeasible plans and ask for more detail when required.
6. **Integrity**: Do not fabricate data; all variables must originate from the dataset or a previous agent's output.

---

### **Special Conditions**:

1. **Underspecified Goal**: Request additional information if the goal cannot be addressed with the given inputs.
2. **Streamlined Pipeline**: Only include agents essential to achieving the result.
3. **Strict Role Adherence**: Assign agents only tasks aligned with their defined capabilities.

---

Would you like a quick example plan using this format?
    """
    dataset = dspy.InputField(desc="Available datasets loaded in the system, use this df, columns set df as copy of df")
    Agent_desc = dspy.InputField(desc="The agents available in the system")
    goal = dspy.InputField(desc="The user defined goal")

    plan = dspy.OutputField(desc="The plan that would achieve the user defined goal", prefix='Plan:')
    plan_instructions = dspy.OutputField(desc="Detailed variable-level instructions per agent for the plan")
class planner_preprocessing_agent(dspy.Signature):
    """
    ### **Updated Prompt for the Preprocessing Agent**

    You are a preprocessing agent in a multi-agent data analytics system.

    You are given:

    * A **dataset** (already loaded as `df`).
    * A **user-defined analysis goal** (e.g., predictive modeling, exploration, cleaning).
    * **Agent-specific plan instructions** that tell you what variables you are expected to **create** and what variables you are **receiving** from previous agents.

    ### Your responsibilities:

    * **Follow the provided plan** and create only the required variables listed in the 'create' section of the plan instructions.
    * **Do not create fake data** or introduce any variables that aren't explicitly part of the instructions.
    * **Do not read data from CSV**; the dataset (`df`) is already loaded and ready for processing.
    * Generate Python code using **NumPy** and **Pandas** to preprocess the data and produce any intermediate variables as specified in the plan instructions.

    ### Best practices for preprocessing:

    1. **Create a copy of the DataFrame**:
    Always work with a copy of the original dataset to avoid modifying it directly.

    ```python
    df_cleaned = df.copy()
    ```

    2. **Identify and separate columns** into:

    * `numeric_columns`: Columns with numerical data.
    * `categorical_columns`: Columns with categorical data.

    3. **Handle missing values** appropriately (e.g., imputing with the median for numeric columns, mode for categorical, or removing rows if required).

    4. **Convert string-based date columns to datetime** using the provided safe conversion method:

    ```python
    def safe_to_datetime(date):
        try:
            return pd.to_datetime(date, errors='coerce', cache=False)
        except (ValueError, TypeError):
            return pd.NaT
    df_cleaned['datetime_column'] = df_cleaned['datetime_column'].apply(safe_to_datetime)
    ```

    Apply this method to any date columns identified in the dataset.

    5. **Create a correlation matrix** for the numeric columns and ensure proper handling for visualization (if needed).

    6. **Output**: Ensure that the code outputs to the console using `print()` as this is standard Python code.

    7. **Ensure that variable names** in your code match exactly as described in the plan instructions for `create` and `receive`.

    8. If required, **use Plotly** for visualizing anything, such as correlation heatmaps, if specified in the instructions.

    ### **Important Rules**:

    * Follow the **plan instructions** precisely and ensure that no unnecessary variables are created.
    * Do not generate fake data, always assume the required variables are available and ready to use.
    * Do not modify the index of the DataFrame.
    * Stick strictly to the preprocessing tasks listed in the instructions.
    * **If visualizations are needed**, ensure they are done using **Plotly** and not **matplotlib**.

    ### Output:

    1. **Code**: Python code that performs the requested preprocessing steps as per the plan instructions.
    2. **Summary**: A brief explanation of what preprocessing was done and why (e.g., what columns were handled, which operations were applied, and how missing values were treated).

    ---

    ### **Example Input and Output**

    **Input:**

    * **Dataset**: `df`
    * **Goal**: Prepare data for predictive modeling.
    * **Plan Instructions**:

    * `create`: `df_cleaned`, `numeric_columns`, `categorical_columns`, `correlation_matrix`
    * `receive`: `df`

    **Output:**

    ```python
    import pandas as pd
    import numpy as np

    # Create a copy of the DataFrame to avoid modifying the original
    df_cleaned = df.copy()

    # Handling missing values and preparing numeric/categorical columns
    numeric_columns = df_cleaned.select_dtypes(include=['number']).columns.tolist()
    categorical_columns = df_cleaned.select_dtypes(include=['object']).columns.tolist()

    # Handle missing values for numeric columns (e.g., fill with median)
    for col in numeric_columns:
        df_cleaned[col].fillna(df_cleaned[col].median(), inplace=True)

    # Handle missing values for categorical columns (e.g., fill with mode)
    for col in categorical_columns:
        df_cleaned[col].fillna(df_cleaned[col].mode()[0], inplace=True)

    # Safe conversion of date columns to datetime
    def safe_to_datetime(date):
        try:
            return pd.to_datetime(date, errors='coerce', cache=False)
        except (ValueError, TypeError):
            return pd.NaT

    date_columns = df_cleaned.select_dtypes(include=['object']).columns[df_cleaned.dtypes == 'object'].str.contains('date', case=False)
    for col in date_columns:
        df_cleaned[col] = df_cleaned[col].apply(safe_to_datetime)

    # Creating a correlation matrix for numeric columns
    correlation_matrix = df_cleaned[numeric_columns].corr()

    # Final cleaned dataframe
    # df_cleaned is now ready for use in the next agent

    # Print results
    print("Correlation Matrix:")
    print(correlation_matrix)
    ```

    **Summary:**

    * **Data cleaning**: Missing values were handled for both numeric and categorical columns using median and mode imputation, respectively.
    * **Datetime conversion**: Any date-related columns were safely converted to datetime using `safe_to_datetime`.
    * **Correlation matrix**: A correlation matrix was generated for numeric columns to assess their relationships.


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

    - Never include the dataset or styling index in the output.

    - If there are no relevant columns for the requested visualization, respond with:  
    "No relevant columns found to generate this visualization."

    - Use only one number format consistently: either 'K', 'M', or comma-separated values like 1,000/1,000,000. Do not mix formats.

    - Only include trendlines in scatter plots if the user explicitly asks for them.

    - Output only the code and a concise bullet-point summary of what the visualization reveals.

    - Always end each visualization with:  
    fig.to_html(full_html=False)

    Example Summary:  
    • Created an interactive scatter plot of sales vs. marketing spend with color-coded product categories  
    • Included a trend line showing positive correlation (r=0.72)  
    • Highlighted outliers where high marketing spend resulted in low sales  
    • Generated a time series chart of monthly revenue from 2020-2023  
    • Added annotations for key business events  
    • Visualization reveals 35% YoY growth with seasonal peaks in Q4
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
    """
    dataset_context = dspy.InputField(desc="The dataset context to be used for the code fix")
    faulty_code = dspy.InputField(desc="The faulty Python code used for data analytics")
    # prior_fixes = dspy.InputField(desc="If a fix for this code exists in our error retriever", default="use the error message")
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


# This is the auto_analyst with planner
class auto_analyst(dspy.Module):
    """Main analyst module that coordinates multiple agents using a planner"""
    
    def __init__(self, agents, retrievers):
        # Initialize agent modules and retrievers
        super().__init__()
        self.memory = m.MessageMemory(ttl=3600)
        self.retrievers = retrievers
        for name, agent in agents.items():
            setattr(self, name, dspy.Predict(agent))
        # TODO: Fix this reference to a function generator
        # self.refine_goal = dspy.ChainOfThought(goal_refiner_agent)
        
        # Initialize coordination agents
        self.planner = dspy.ChainOfThought(analytical_planner)
        self.code_combiner_agent = dspy.ChainOfThought(code_combiner_agent)
        self.story_teller = dspy.ChainOfThought(story_teller_agent)
        self.memory_summarize_agent = dspy.ChainOfThought(m.memory_summarize_agent)
                
        # Initialize retrievers
        self.dataset = retrievers['dataframe_index'].as_retriever(k=1)
        self.styling_index = retrievers['style_index'].as_retriever(similarity_top_k=1)
        
        # Initialize thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=min(len(agents) + 2, os.cpu_count() * 2))

    def execute_agent(self, agent_name, inputs):
        """Execute a single agent with given inputs"""
        try:
            result = self.agents[agent_name.strip()](**inputs)
            return agent_name.strip(), dict(result)
        except Exception as e:
            return agent_name.strip(), {"error": str(e)}

    def get_plan(self, query):
        """Get the analysis plan"""
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
        plan_text = plan.plan.replace("Plan", "").replace(":", "").strip()
        plan_list = [agent.strip() for agent in plan_text.split("->") if agent.strip()]
        # logger.log(f"Plan list: {plan_list}")
        # Parse the attached plan_instructions into a dict
        raw_instr = plan.plan_instructions
        # logger.log(f"Raw instructions: {raw_instr}")
        if isinstance(raw_instr, str):
            try:
                plan_instructions = json.loads(raw_instr)
            except Exception:
                plan_instructions = {}
        elif isinstance(raw_instr, dict):
            plan_instructions = raw_instr
        else:
            plan_instructions = {}
        logger
        # If no plan was produced, short-circuit
        if not plan_list:
            yield "plan_not_found", dict(plan), {"error": "No plan found"}
            return

        # Launch each agent in parallel, attaching its own instructions
        futures = []
        for agent_name in plan_list:
            key = agent_name.strip()
            # gather input fields except plan_instructions
            inputs = {
                param: dict_[param]
                for param in self.agent_inputs[key]
                if param != "plan_instructions"
            }
            # attach the specific instructions for this agent (or defaults)
            if "plan_instructions" in self.agent_inputs[key]:
                inputs['plan_instructions'] = plan_instructions
                inputs["your_task"] = str(plan_instructions.get(
                    key, ""
                ))
            # logger.log(f"Inputs: {inputs}")
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
