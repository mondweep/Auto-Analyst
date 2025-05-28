# Auto-Analyst API Documentation

This document provides comprehensive API documentation for the Auto-Analyst system, including all available endpoints across the different server components.

## System Overview

The Auto-Analyst system consists of multiple server components:

1. **Attribute Proxy Server** (Port 8080) - Routes requests between frontend and backend servers
2. **Standalone Attribute Server** (Port 8002) - Handles attribute filtering and queries
3. **Main Application Server** (Port 8000) - Provides LLM-powered analysis (optional)

All API requests should be directed to the Attribute Proxy Server, which will intelligently route them to the appropriate backend.

## Base URLs

- **Frontend**: `http://localhost:3000`
- **Attribute Proxy**: `http://localhost:8080`
- **Attribute Server**: `http://localhost:8002`
- **Main Application**: `http://localhost:8000`

## API Endpoints

### Health Check Endpoints

| Endpoint | Method | Description | Server |
|----------|--------|-------------|--------|
| `/health` | GET | Check if the server is running | All Servers |

### Attribute Filtering Endpoints

| Endpoint | Method | Description | Server |
|----------|--------|-------------|--------|
| `/api/attribute-query` | POST | Process natural language attribute queries | Attribute Server |
| `/api/direct-count` | POST | Count vehicles by specific attribute | Attribute Server |
| `/api/chat-attribute` | POST | Process attribute queries from chat | Attribute Server |

#### Attribute Query Example

```json
// Request to /api/attribute-query
{
  "query": "How many red Toyota Camrys do we have?"
}

// Response
{
  "count": 5,
  "attributes": {
    "color": "red",
    "make": "Toyota",
    "model": "Camry"
  },
  "breakdown": [
    {"year": 2020, "count": 2},
    {"year": 2021, "count": 1},
    {"year": 2022, "count": 2}
  ]
}
```

#### Direct Count Example

```json
// Request to /api/direct-count
{
  "attribute": "color",
  "value": "red"
}

// Response
{
  "count": 32,
  "attribute": "color",
  "value": "red"
}
```

### Model and Agent Endpoints

| Endpoint | Method | Description | Server |
|----------|--------|-------------|--------|
| `/model` | GET | Get available models | Attribute Server |
| `/model/<model_id>` | GET | Get specific model details | Attribute Server |
| `/model-settings` | GET | Get model settings | Attribute Server |
| `/api/model-settings` | GET | Alternative model settings endpoint | Attribute Server |
| `/settings/model` | GET/POST | Get or update model settings | Attribute Server |
| `/agents` | GET | Get available agents | Attribute Server |
| `/agents/<agent_id>` | GET | Get specific agent details | Attribute Server |

#### Model Settings Example

```json
// Response from /model-settings
{
  "models": [
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "provider": "openai",
      "description": "Most capable model for complex tasks",
      "context_length": 8192,
      "is_default": true
    },
    {
      "id": "gemini-1.5-pro",
      "name": "Gemini 1.5 Pro",
      "provider": "google",
      "description": "Google's advanced multimodal model",
      "context_length": 16384,
      "is_default": false
    }
  ],
  "current": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 4000
}
```

### Session Management Endpoints

| Endpoint | Method | Description | Server |
|----------|--------|-------------|--------|
| `/api/session-info` | GET | Get session information | Attribute Server |

#### Session Info Example

```json
// Response from /api/session-info
{
  "session_id": "user_12345",
  "created_at": "2025-05-19T12:30:45Z",
  "last_active": "2025-05-19T15:42:12Z",
  "user": {
    "id": "user_12345",
    "name": "Demo User",
    "role": "analyst"
  },
  "preferences": {
    "default_model": "gpt-4",
    "theme": "light"
  }
}
```

### Chat Endpoints

| Endpoint | Method | Description | Server |
|----------|--------|-------------|--------|
| `/chat` | POST | Process chat queries | Proxy → Appropriate Backend |

#### Chat Request Example

```json
// Request to /chat
{
  "query": "How many red Toyota vehicles do we have?",
  "session_id": "user_12345"
}

// Response
{
  "response": "We currently have 15 red Toyota vehicles in inventory.",
  "data": {
    "count": 15,
    "attributes": {
      "color": "red",
      "make": "Toyota"
    },
    "breakdown": [
      {"model": "Camry", "count": 5},
      {"model": "Corolla", "count": 4},
      {"model": "RAV4", "count": 6}
    ]
  }
}
```

### Vehicle Data Endpoints

| Endpoint | Method | Description | Server |
|----------|--------|-------------|--------|
| `/api/vehicles` | GET | Get vehicle inventory | Main App |
| `/api/market-data` | GET | Get market analysis data | Main App |
| `/api/opportunities` | GET | Get market opportunities | Main App |
| `/api/statistics` | GET | Get statistical analysis | Main App |

#### Vehicles Response Example

```json
// Response from /api/vehicles
{
  "vehicles": [
    {
      "id": 1,
      "make": "Toyota",
      "model": "Camry",
      "year": 2022,
      "color": "red",
      "price": 28500,
      "mileage": 12500,
      "condition": "Excellent",
      "days_in_inventory": 45
    },
    // Additional vehicles...
  ],
  "count": 200,
  "page": 1,
  "total_pages": 20
}
```

## Error Handling

The API uses standard HTTP status codes:

- **200 OK**: Request succeeded
- **400 Bad Request**: Invalid input
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

Error responses follow this format:

```json
{
  "error": {
    "code": 400,
    "message": "Invalid query parameter",
    "details": "The 'attribute' parameter is required for direct count queries"
  }
}
```

## Fallback Behavior

The proxy server provides fallback responses when backend servers are unavailable:

1. **Attribute Server Unavailable**: Mock responses for attribute queries
2. **Main App Unavailable**: Basic vehicle data and statistics

## CORS Configuration

The attribute proxy server handles CORS automatically, allowing requests from the following origins:

- `http://localhost:3000` (Frontend)
- `http://127.0.0.1:3000` (Frontend alternative)

## Authentication

Authentication is managed through the frontend NextAuth implementation. The backend accepts:

- **Session Cookies**: For browser-based requests
- **Authorization Header**: For API access

## Rate Limiting

Basic rate limiting is applied to prevent abuse:

- **Standard Endpoints**: 100 requests per minute
- **Chat Endpoints**: 20 requests per minute
- **Attribute Query Endpoints**: 50 requests per minute