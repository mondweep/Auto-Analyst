# Auto-Analyst Data Flow and Folder Structure Documentation

## 📊 Data Directory Structure Overview

The Auto-Analyst application has **multiple data directories** that serve different purposes in a hierarchical data flow system. Here's the complete breakdown:

## 🎯 Primary Answer to Your Questions

### Where does `/api/file-server/datasets` get data from?

The endpoint `/api/file-server/datasets` follows this **priority order**:

1. **First Priority:** `/Users/mondweep/BI-Tool/Auto-Analyst/auto-analyst-frontend/public/demo-files/`
2. **Fallback:** `/Users/mondweep/BI-Tool/Auto-Analyst/auto-analyst-backend/data/` 
3. **Final Fallback:** File Server at `http://localhost:8001` (serves from `exports/`)

### Current Configuration Status:
Based on the startup logs: `"Frontend demo directory not found, using /Users/mondweep/BI-Tool/Auto-Analyst/auto-analyst-backend/data as fallback"`

**Answer: Currently picking up from `/Users/mondweep/BI-Tool/Auto-Analyst/auto-analyst-backend/data/`**

## 📁 Directory Purposes Explained

### 1. `/exports/` Directory
- **Purpose:** Backend processing and attribute filtering
- **Usage:** TDD attribute filtering implementation
- **Location:** `/Users/mondweep/BI-Tool/Auto-Analyst/auto-analyst-backend/exports/`
- **Contents:**
  - `vehicles.csv` (51 records - our TDD test data)
  - `market_data.csv`
  - `automotive_analysis.csv`
  - `README.md`

**Role:** This is where our **TDD-implemented attribute filtering** looks for data:
```python
EXPORTS_DIR = os.getenv("EXPORTS_DIR", "exports")
DEFAULT_VEHICLES_FILE = os.path.join(EXPORTS_DIR, "vehicles.csv")
```

### 2. `/data/` Directory  
- **Purpose:** Main application data storage (larger datasets)
- **Usage:** General AI analytics and file server fallback
- **Location:** `/Users/mondweep/BI-Tool/Auto-Analyst/auto-analyst-backend/data/`
- **Contents:**
  - `vehicles.csv` (202 records - larger dataset)
  - `market_data.csv`
  - `vehicles.json`
  - `market_data.json`

**Role:** Primary data source for the main application and `/api/file-server/datasets`

### 3. Frontend Demo Files Directory
- **Purpose:** Demo data for frontend integration and user interface
- **Usage:** Default data for frontend components
- **Location:** `/Users/mondweep/BI-Tool/Auto-Analyst/auto-analyst-frontend/public/demo-files/`
- **Contents:**
  - `vehicles.csv` (202 records)
  - `market_data.csv`
  - `automotive_analysis.csv`
  - `file_list.json`

**Role:** Intended to be the **first priority** for data serving but currently not found by the application

## 🔄 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA FLOW PRIORITY                       │
└─────────────────────────────────────────────────────────────┘

1. Frontend Demo Files (Intended Primary)
   └── /auto-analyst-frontend/public/demo-files/
       ├── vehicles.csv (202 records)
       ├── market_data.csv
       └── automotive_analysis.csv

2. Backend Data Directory (Current Primary) 
   └── /auto-analyst-backend/data/
       ├── vehicles.csv (202 records) ← Currently served by /api/file-server/datasets
       ├── market_data.csv
       ├── vehicles.json
       └── market_data.json

3. Backend Exports Directory (TDD/Specific Features)
   └── /auto-analyst-backend/exports/
       ├── vehicles.csv (51 records) ← Used by TDD attribute filtering
       ├── market_data.csv
       └── automotive_analysis.csv

4. File Server Fallback (Port 8001)
   └── Serves files from exports/ directory
```

## 🎯 Different Endpoints, Different Data Sources

### Attribute Filtering Endpoints (Our TDD Implementation)
- **Endpoints:** `/api/direct-count`, `/api/attribute-query`
- **Data Source:** `exports/vehicles.csv` (51 records)
- **Code Reference:**
```python
DEFAULT_VEHICLES_FILE = os.path.join(EXPORTS_DIR, "vehicles.csv")
# Points to: auto-analyst-backend/exports/vehicles.csv
```

### File Server Endpoints  
- **Endpoints:** `/api/file-server/datasets`, `/api/file-server/default-dataset`
- **Data Source:** `data/` directory (202 records)
- **Fallback Chain:** Frontend demo → Backend data → File server

### General AI Analytics
- **Usage:** Chat agents, data visualization, ML analysis
- **Data Source:** Dynamically loaded via `load_dataset_from_file_server()`
- **Priority:** Frontend demo → Backend data → File server exports

## 🚗 Why All Automotive Data?

The application appears to be **specifically designed for automotive/vehicle analysis**:

1. **Domain Focus:** Auto-Analyst = Automotive Analytics
2. **Sample Data Strategy:** All folders contain vehicle-related datasets to provide:
   - Consistent schema across environments
   - Real-world automotive business scenarios
   - Test data for development and demos

3. **Business Context:**
   - Vehicle inventory management
   - Market analysis for automotive dealers
   - Sales performance tracking
   - Customer preference analysis

## ✅ Current Working Configuration

**Status:** All systems operational with current data setup

### What's Working:
- ✅ **Attribute Filtering:** Using `exports/vehicles.csv` (51 records)
- ✅ **File Server API:** Using `data/vehicles.csv` (202 records)  
- ✅ **TDD Tests:** All 23 tests passing with exports data
- ✅ **Main Application:** Running with data directory fallback

### Recommended Actions:

1. **Keep Current Setup** - Everything is working correctly
2. **Consider Consolidation** - All three directories serve similar purposes
3. **Frontend Integration** - Fix the frontend demo path when ready for production

## 🔧 Technical Configuration

### Environment Variables:
```bash
FRONTEND_DEMO_DIR=/path/to/frontend/public/demo-files  # Currently not found
EXPORTS_DIR=exports  # Used by attribute filtering
FILE_SERVER_URL=http://localhost:8001  # Fallback file server
```

### Key Code Locations:
- **Main App Config:** `app.py` lines 50-55
- **Attribute Filtering:** `app.py` lines 1334-1335
- **File Server:** `file_server.py` line 12
- **Data Loading:** `app.py` lines 1134-1172

## 📈 Data Size Comparison

| Directory | Dataset | Records | Purpose |
|-----------|---------|---------|---------|
| `exports/` | vehicles.csv | 51 | TDD testing, attribute filtering |
| `data/` | vehicles.csv | 202 | Main application, AI analytics |
| `frontend/demo-files/` | vehicles.csv | 202 | Frontend demos, UI components |

## 🎯 Conclusion

The multi-directory structure provides **separation of concerns**:
- **`exports/`** - Specific feature testing and attribute filtering
- **`data/`** - Main application data and AI analytics  
- **`frontend/demo-files/`** - Frontend integration and user demos

This architecture allows different parts of the application to use appropriately sized datasets while maintaining consistency in schema and domain focus. 