# Auto-Analyst Data Flow

This document details the data flow through the Auto-Analyst system, showing how information is processed, transformed, and displayed.

## System Overview

The Auto-Analyst application has three main services:

1. **Frontend (Next.js)** - Runs on port 3000
2. **File Server (Python)** - Runs on port 8001
3. **Automotive API (Python)** - Runs on port 8003

## Core Data Flows

### 1. User Authentication and Session Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant SessionStorage
    participant APIServer
    
    User->>Frontend: Access application
    Frontend->>SessionStorage: Generate session ID
    
    alt Logged In User
        User->>Frontend: Login
        Frontend->>APIServer: Authenticate
        APIServer-->>Frontend: Return user data
        Frontend->>SessionStorage: Store user session
    else Guest User
        Frontend->>SessionStorage: Store anonymous session
    end
    
    Frontend->>User: Display UI based on auth status
```

### 2. File Upload and Processing Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant FileServer
    
    User->>Frontend: Select and upload CSV file
    Frontend->>FileServer: POST /upload with FormData
    
    FileServer->>FileServer: Validate file format
    
    alt Valid CSV
        FileServer->>FileServer: Parse CSV
        FileServer->>FileServer: Process data
        FileServer-->>Frontend: Return structured data and success message
        Frontend->>Frontend: Store data in state
        Frontend->>User: Display data visualization
    else Invalid File
        FileServer-->>Frontend: Return error message
        Frontend->>User: Display error feedback
    end
```

### 3. Automotive Data Query Flow

```mermaid
sequenceDiagram
    actor User
    participant AutomativeUI
    participant AutomotiveAPI
    
    User->>AutomativeUI: Access automotive page
    
    par Vehicle Data Request
        AutomativeUI->>AutomotiveAPI: GET /api/vehicles
        AutomotiveAPI-->>AutomativeUI: Return vehicle inventory data
        AutomativeUI->>User: Display vehicle list
    and Market Data Request
        AutomativeUI->>AutomotiveAPI: GET /api/market-data
        AutomotiveAPI-->>AutomativeUI: Return market pricing data
        AutomativeUI->>User: Display market analysis
    and Opportunities Request
        AutomativeUI->>AutomotiveAPI: GET /api/opportunities
        AutomotiveAPI-->>AutomativeUI: Return pricing opportunities
        AutomativeUI->>User: Display opportunities
    and Statistics Request
        AutomativeUI->>AutomotiveAPI: GET /api/statistics
        AutomotiveAPI-->>AutomativeUI: Return statistical analysis
        AutomativeUI->>User: Display statistics charts
    end
```

### 4. Chat Interface Data Flow

```mermaid
sequenceDiagram
    actor User
    participant ChatInterface
    participant APIServer
    participant FileServer
    participant PlotlyRenderer
    
    User->>ChatInterface: Submit analysis query
    ChatInterface->>APIServer: POST /chat with query
    
    APIServer->>FileServer: Fetch necessary dataset
    FileServer-->>APIServer: Return dataset
    
    APIServer->>APIServer: Process query
    
    alt Visualization Request
        APIServer->>APIServer: Generate Plotly data
        APIServer-->>ChatInterface: Return PlotlyMessage
        ChatInterface->>PlotlyRenderer: Render visualization
        PlotlyRenderer-->>User: Display chart
    else Text Response
        APIServer-->>ChatInterface: Return text response
        ChatInterface->>User: Display text response
    end
```

### 5. Error Handling and Fallback Flow

```mermaid
sequenceDiagram
    participant Frontend
    participant FileServer
    participant AutomotiveAPI
    participant Fallbacks
    
    alt Network Error with File Server
        Frontend->>FileServer: Request data
        FileServer--xFrontend: Connection error
        Frontend->>Fallbacks: Generate fallback data
        Fallbacks-->>Frontend: Return mock data
        Frontend->>Frontend: Display with error indicator
    end
    
    alt Invalid File Format
        Frontend->>FileServer: Upload invalid file
        FileServer->>FileServer: Validation fails
        FileServer-->>Frontend: Return error details
        Frontend->>Frontend: Display error message
    end
    
    alt API Timeout
        Frontend->>AutomotiveAPI: Request data
        AutomotiveAPI--xFrontend: Timeout
        Frontend->>Fallbacks: Generate fallback visualization
        Fallbacks-->>Frontend: Return fallback data
        Frontend->>Frontend: Display with warning
    end
```

## Data Transformation Process

```mermaid
flowchart TD
    RawCSV[Raw CSV File] -->|Upload| Validator[CSV Validator]
    Validator -->|Valid| Parser[CSV Parser]
    Validator -->|Invalid| ErrorHandler[Error Handler]
    
    Parser -->|Extract| Headers[CSV Headers]
    Parser -->|Extract| Rows[CSV Data Rows]
    
    Headers --> SchemaDetector[Schema Detector]
    Rows --> Transformer[Data Transformer]
    
    SchemaDetector -->|Infer types| TypeConverter[Type Converter]
    TypeConverter --> Transformer
    
    Transformer -->|Clean data| DataCleaner[Data Cleaner]
    DataCleaner -->|Normalize| NormalizedData[Normalized Data]
    
    NormalizedData -->|Format for API| APIModel[API Data Model]
    NormalizedData -->|Format for visualization| VisData[Visualization Data]
    
    APIModel --> AnalysisEngine[Analysis Engine]
    VisData --> Renderer[Data Visualization Renderer]
    
    AnalysisEngine -->|Generate insights| Insights[Data Insights]
    Renderer -->|Create visualization| Charts[Interactive Charts]
    
    Insights --> ResponseFormatter[Response Formatter]
    Charts --> ResponseFormatter
    
    ResponseFormatter -->|Return to user| UI[User Interface]
```

## Key API Interactions

### File Server API

| Endpoint | Method | Description | Request Format | Response Format |
|----------|--------|-------------|----------------|-----------------|
| `/upload` | POST | Upload CSV file | FormData with file | JSON with parsed data |
| `/exports/<filename>` | GET | Download file | URL path | File content |
| `/api/default-dataset` | GET | Get default data | N/A | JSON with dataset |
| `/health` | GET | Health check | N/A | JSON status |

### Automotive API

| Endpoint | Method | Description | Request Format | Response Format |
|----------|--------|-------------|----------------|-----------------|
| `/api/vehicles` | GET | Get vehicle inventory | Query parameters | JSON array of vehicles |
| `/api/market-data` | GET | Get market pricing | Query parameters | JSON array of market data |
| `/api/opportunities` | GET | Get pricing opportunities | Query parameters | JSON array of opportunities |
| `/api/statistics` | GET | Get statistics | Query parameters | JSON with statistics |
| `/health` | GET | Health check | N/A | JSON status |

## Data Storage

The system primarily uses in-memory storage and file-based storage:

1. **Frontend State**: React state and context for UI data
2. **File Server**: Stores CSV files in the `/exports` directory
3. **Local Storage**: Used for user preferences and session information

## Error Handling Strategy

The system implements multiple layers of error handling:

```mermaid
flowchart TD
    Error[Error Detected] --> Categorize[Categorize Error]
    
    Categorize --> Network[Network Error]
    Categorize --> Validation[Validation Error]
    Categorize --> Processing[Processing Error]
    Categorize --> UI[UI Error]
    
    Network --> Retry[Retry Logic]
    Retry -->|Success| Success[Continue Processing]
    Retry -->|Failure| Fallback[Use Fallback Data]
    
    Validation --> UserFeedback[Display User Feedback]
    UserFeedback --> Suggestion[Suggest Correction]
    
    Processing --> Logging[Log Error Details]
    Logging --> GracefulDegradation[Graceful Degradation]
    
    UI --> BoundaryCapture[Error Boundary Capture]
    BoundaryCapture --> RecoverUI[Recover UI]
    
    Fallback --> DisplayWarning[Display Warning Indicator]
    GracefulDegradation --> PartialFunctionality[Offer Partial Functionality]
    RecoverUI --> ResetState[Reset Component State]
    
    DisplayWarning --> UserExperience[Preserve User Experience]
    PartialFunctionality --> UserExperience
    ResetState --> UserExperience
    Suggestion --> UserExperience
```

## Performance Considerations

1. **Data Pagination**: Large datasets are paginated to improve rendering performance
2. **Lazy Loading**: Components and visualizations are loaded on demand
3. **Data Caching**: Frequently accessed data is cached in memory
4. **Throttled API Calls**: Requests to the same endpoint are throttled to prevent overloading

## Future Enhancements

1. **Real-time Updates**: Implement WebSocket connections for live data updates
2. **Database Integration**: Add persistent storage with a proper database
3. **Advanced Caching**: Implement Redis or similar for distributed caching
4. **Microservice Architecture**: Further decompose services for better scalability 