# Agent Validation Questions - Frontend Testing Guide

**Date:** December 29, 2024  
**Purpose:** Comprehensive test questions for validating each agent from the frontend  
**Status:** ✅ All agents tested and working  

## 🧪 Test Results Summary

✅ **API Authentication:** WORKING  
✅ **Data Visualization Agent:** WORKING  
✅ **Statistical Analytics Agent:** WORKING  
✅ **Preprocessing Agent:** WORKING  
✅ **Machine Learning Agent:** WORKING  

---

## 📊 Data Visualization Agent (`data_viz_agent`)

**Purpose:** Creates charts, graphs, and visual representations of data

### Basic Questions
1. **"How many vehicles do we have in total?"**
   - Expected: Bar chart or summary showing total count

2. **"Create a bar chart showing vehicle distribution by make"**
   - Expected: Horizontal/vertical bar chart with vehicle makes

3. **"Show me a pie chart of vehicle conditions"**
   - Expected: Pie chart showing different condition categories

4. **"Create a scatter plot of price vs year"**
   - Expected: Scatter plot showing relationship between price and year

### Advanced Questions
5. **"Visualize the price distribution with a histogram"**
   - Expected: Histogram showing price ranges and frequencies

6. **"Create a line chart showing average prices by year"**
   - Expected: Line chart with time series data

7. **"Show me a heatmap of vehicle features correlation"**
   - Expected: Correlation matrix heatmap

8. **"Create a box plot comparing prices across different makes"**
   - Expected: Box plot showing price distributions by manufacturer

### Complex Queries
9. **"Create a dashboard showing top 5 most expensive vehicles with their details"**
   - Expected: Multi-element visualization or table

10. **"Visualize market opportunities with price vs market value"**
    - Expected: Scatter plot with opportunity indicators

---

## 📈 Statistical Analytics Agent (`statistical_analytics_agent`)

**Purpose:** Performs statistical analysis, calculations, and hypothesis testing

### Basic Questions
1. **"Calculate basic statistics for vehicle prices"**
   - Expected: Mean, median, standard deviation, min/max

2. **"What's the average price by vehicle make?"**
   - Expected: Statistical summary grouped by manufacturer

3. **"Find the correlation between price and year"**
   - Expected: Correlation coefficient and interpretation

4. **"Calculate percentiles for vehicle prices (25th, 50th, 75th)"**
   - Expected: Quartile analysis

### Advanced Questions
5. **"Perform a statistical analysis of price differences across conditions"**
   - Expected: ANOVA or similar statistical test

6. **"Calculate confidence intervals for average vehicle prices"**
   - Expected: Statistical confidence intervals

7. **"Analyze the distribution of vehicle ages"**
   - Expected: Distribution analysis with statistical measures

8. **"Test if there's a significant difference in prices between makes"**
   - Expected: Hypothesis testing results

### Complex Queries
9. **"Perform a comprehensive market analysis with statistical insights"**
   - Expected: Multi-faceted statistical report

10. **"Calculate market efficiency metrics and statistical significance"**
    - Expected: Advanced statistical analysis

---

## 🧹 Preprocessing Agent (`preprocessing_agent`)

**Purpose:** Cleans, transforms, and prepares data for analysis

### Basic Questions
1. **"Clean and prepare the dataset for analysis"**
   - Expected: Data cleaning steps and recommendations

2. **"Check for missing values and outliers in the dataset"**
   - Expected: Data quality assessment

3. **"Standardize the price column for analysis"**
   - Expected: Data normalization/standardization steps

4. **"Convert categorical variables to numerical format"**
   - Expected: Encoding recommendations and implementation

### Advanced Questions
5. **"Create new features from existing vehicle data"**
   - Expected: Feature engineering suggestions

6. **"Remove duplicates and handle inconsistent data entries"**
   - Expected: Data deduplication and consistency checks

7. **"Prepare the dataset for machine learning model training"**
   - Expected: Comprehensive data preparation pipeline

8. **"Handle categorical variables and create dummy variables"**
   - Expected: One-hot encoding or label encoding steps

### Complex Queries
9. **"Perform complete data preprocessing including scaling and encoding"**
   - Expected: End-to-end preprocessing pipeline

10. **"Prepare separate datasets for different types of analysis"**
    - Expected: Multiple dataset preparation strategies

---

## 🤖 Machine Learning Agent (`sk_learn_agent`)

**Purpose:** Builds and trains machine learning models

### Basic Questions
1. **"Build a machine learning model to predict vehicle prices"**
   - Expected: Model training code and evaluation metrics

2. **"Create a classification model to predict vehicle condition"**
   - Expected: Classification model with accuracy metrics

3. **"Train a regression model for price prediction"**
   - Expected: Regression model with performance metrics

4. **"Build a clustering model to group similar vehicles"**
   - Expected: Clustering algorithm and cluster analysis

### Advanced Questions
5. **"Compare different regression algorithms for price prediction"**
   - Expected: Model comparison with evaluation metrics

6. **"Build an ensemble model combining multiple algorithms"**
   - Expected: Ensemble method implementation

7. **"Create a feature importance analysis for price prediction"**
   - Expected: Feature importance ranking and visualization

8. **"Implement cross-validation for model evaluation"**
   - Expected: Cross-validation results and model stability

### Complex Queries
9. **"Build a complete ML pipeline with preprocessing and model selection"**
   - Expected: End-to-end machine learning pipeline

10. **"Create a recommendation system for vehicle investments"**
    - Expected: Advanced ML system for recommendations

---

## 🔄 Multi-Agent Testing

### Combined Agent Queries
Test these questions that should involve multiple agents working together:

1. **"Analyze the vehicle dataset and create visualizations with statistical insights"**
   - Expected: Both statistical analysis and visualizations

2. **"Preprocess the data and build a predictive model with visualizations"**
   - Expected: Preprocessing + ML + Visualization

3. **"Perform complete market analysis with cleaning, statistics, and ML predictions"**
   - Expected: All agents working together

4. **"Create a comprehensive report on vehicle pricing trends"**
   - Expected: Multi-agent collaborative analysis

---

## ✅ Validation Checklist

For each test question, verify:

- [ ] **Response Time:** < 30 seconds for simple queries, < 60 seconds for complex
- [ ] **No Authentication Errors:** No "Authentication failed" messages
- [ ] **Proper Code Generation:** Python code is syntactically correct
- [ ] **Relevant Analysis:** Response addresses the specific question
- [ ] **Error Handling:** Graceful handling of edge cases
- [ ] **Data Context:** Agent understands the vehicle/housing dataset context

---

## 🚨 Known Limitations

1. **Dataset Context:** Agents may sometimes reference "housing" instead of "vehicles" due to the underlying default dataset
2. **Model Execution:** Generated code shows implementation but doesn't execute automatically
3. **Data Size:** Agents work with available data samples, may suggest sampling for large datasets

---

## 🔧 Troubleshooting

If any agent fails:

1. **Check Server Status:** Ensure backend is running on port 8000
2. **Verify API Keys:** Confirm GEMINI_API_KEY is set correctly
3. **Check Logs:** Review server logs for specific error messages
4. **Session Reset:** Try with a new session ID
5. **Simple Test:** Start with basic questions before complex ones

---

**Ready for testing!** 🎯 Use these questions to thoroughly validate each agent's functionality from the frontend interface. 