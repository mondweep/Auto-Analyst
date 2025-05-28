# Auto-Analyst Application Documentation

## Overview

The `app.py` file is the main entry point for the Auto-Analyst backend service. It provides a web-based API that connects the user interface to powerful data analysis capabilities. The application can analyze datasets, generate visualizations, and provide intelligent insights without requiring users to have technical knowledge of data science.

## Key Components

### 1. Server Framework

The application uses FastAPI, a modern web framework, to create a responsive and robust API server. This allows the Auto-Analyst to:
- Process requests from the user interface
- Handle file uploads and downloads
- Manage user sessions
- Deliver analysis results

### 2. AI System

At the core of Auto-Analyst is an intelligent system that:
- Understands natural language queries about data
- Interprets what users are asking
- Formulates analysis plans
- Executes specialized analysis tasks
- Presents results in a user-friendly format

### 3. Session Management

The application maintains user sessions to:
- Keep track of datasets being analyzed
- Remember conversations with the AI
- Store user preferences and settings
- Manage API keys and model configurations

### 4. Visualization Support

The application includes styling instructions and special handlers to:
- Create beautiful and informative charts
- Format data visualizations consistently
- Apply appropriate styling to different chart types (bar charts, line charts, etc.)
- Make data easy to understand visually

### 5. File Server Integration

The application connects to a file server to:
- Access uploaded datasets
- Retrieve default datasets
- Export analysis results
- Preview data files

## Specialized Agents

The application employs a set of specialized AI agents to perform different analytical tasks:

### 1. Available Agents

These agents can be directly called by users and are accessible through the `/chat/{agent_name}` endpoint:

- **data_viz_agent**: Creates data visualizations like charts, graphs, and plots based on the dataset and user queries. It can generate bar charts, line graphs, scatter plots, and other visual representations to help users understand their data at a glance.

- **sk_learn_agent**: Implements machine learning capabilities using the scikit-learn library. This agent can perform tasks like classification, regression, clustering, and dimensionality reduction, making predictive analysis accessible to non-technical users.

- **statistical_analytics_agent**: Performs statistical analysis on datasets, including descriptive statistics (mean, median, standard deviation), hypothesis testing, correlation analysis, and other statistical methods to identify patterns and relationships in the data.

- **preprocessing_agent**: Handles data cleaning and preparation tasks such as handling missing values, encoding categorical variables, normalizing numerical features, and transforming data into formats suitable for analysis or machine learning.

### 2. Planner Agents

These agents work behind the scenes to organize and coordinate the analytical process:

- **planner_preprocessing_agent**: Plans the data preprocessing steps needed for a given analysis, determining which cleaning, transformation, and feature engineering operations should be applied to the dataset.

- **planner_sk_learn_agent**: Designs machine learning workflows, selecting appropriate algorithms, parameters, and evaluation methods based on the user's goals and the characteristics of the data.

- **planner_statistical_analytics_agent**: Develops plans for statistical analysis, choosing the right statistical methods to answer specific questions or test particular hypotheses.

- **planner_data_viz_agent**: Creates visualization strategies, determining the most effective chart types, layouts, and styling options to communicate insights clearly and effectively.

The application's AI system uses these planner agents to create a comprehensive analysis plan before executing the actual analysis using the specialized agents. This two-tier approach ensures that the analysis is well-structured, efficient, and appropriate for the user's needs.

## Data Flow

### 1. User Request Processing

When a user asks a question or makes a request:
1. The request enters through one of the API endpoints
2. The system identifies the type of request (data analysis, chat, visualization)
3. The request is enhanced with context from previous interactions
4. The appropriate agent or process is selected to handle the request

### 2. Analysis Planning

For analytical requests:
1. The AI planner reviews the query and available data
2. It creates a step-by-step plan for analysis
3. The plan is broken down into smaller tasks for specialized agents
4. Results from each step are combined for a comprehensive response

### 3. Dataset Handling

When working with data:
1. The application can retrieve datasets from the file server
2. Data is loaded into memory and prepared for analysis
3. The system creates appropriate contexts based on the data structure
4. Analysis is performed directly on the data

### 4. Response Generation

After processing:
1. Results are formatted into user-friendly responses
2. Visualizations are rendered with appropriate styling
3. Complex information is presented in readable formats
4. Responses are sent back to the user interface

## Main Functionality

### 1. Natural Language Data Analysis

Users can ask questions in plain English, such as:
- "How many green vehicles do we have?"
- "What's the average price by make and model?"
- "Show me trends in vehicle sales over time"

The system interprets these requests and provides appropriate analysis.

### 2. Specialized Analytical Agents

The system employs different specialist agents:
- **Data Visualization Agent**: Creates charts and graphs
- **Statistical Analytics Agent**: Performs statistical calculations
- **Preprocessing Agent**: Cleans and prepares data for analysis

### 3. File Management

The application offers:
- Dataset uploading capabilities
- File previews before full analysis
- Default datasets for immediate use
- Export functionality for analysis results

### 4. User Session Handling

The system provides:
- Persistent conversation history
- Dataset memory between interactions
- Model and configuration preferences
- Session-specific analysis context

### 5. API Endpoints

Key endpoints include:
- `/chat`: For general AI conversation
- `/chat/{agent_name}`: For specialized agent interaction
- `/api/analyze-file`: For dataset analysis
- `/api/file-server/datasets`: For dataset management
- `/health`: For system status checking

## Technical Implementation Notes

While keeping this non-technical, it's worth mentioning that the application:
- Uses a virtual environment for dependency management
- Leverages external AI models via API connections
- Employs a SQLite database for usage tracking
- Integrates with multiple AI services (OpenAI, Gemini, Groq, Anthropic)
- Implements sophisticated error handling and fallback mechanisms

## Environment Configuration

The application can be configured through:
- Environment variables for API keys and settings
- Session-specific model configuration
- Server address and port settings
- Security settings for cross-origin requests

## Conclusion

The Auto-Analyst application provides a sophisticated but user-friendly interface between non-technical users and advanced data analysis capabilities. It interprets natural language, performs complex data processing, and delivers insights in accessible formats, all while maintaining security and performance standards. 