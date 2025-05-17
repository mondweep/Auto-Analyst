from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date

# Base models for request/response validation

class VehicleBase(BaseModel):
    """Base model for vehicle data"""
    make: str
    model: str
    year: int
    trim: str
    body_type: str
    fuel_type: str
    transmission: str
    engine_size: float
    mileage: int
    color_exterior: str
    color_interior: str
    condition: str
    features: List[str]
    acquisition_price: float
    current_price: float
    recommended_price: Optional[float] = None
    images: List[str]
    vin: str
    status: str
    location: str

class VehicleCreate(VehicleBase):
    """Model for creating a new vehicle"""
    acquisition_date: date

class VehicleUpdate(BaseModel):
    """Model for updating a vehicle"""
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    trim: Optional[str] = None
    body_type: Optional[str] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    engine_size: Optional[float] = None
    mileage: Optional[int] = None
    color_exterior: Optional[str] = None
    color_interior: Optional[str] = None
    condition: Optional[str] = None
    features: Optional[List[str]] = None
    acquisition_price: Optional[float] = None
    current_price: Optional[float] = None
    recommended_price: Optional[float] = None
    images: Optional[List[str]] = None
    status: Optional[str] = None
    location: Optional[str] = None

class VehicleResponse(VehicleBase):
    """Model for vehicle response"""
    vehicle_id: str
    acquisition_date: str
    days_on_lot: int

class VehicleList(BaseModel):
    """Model for paginated vehicle list"""
    total: int
    page: int
    limit: int
    data: List[VehicleResponse]

class MarketDataBase(BaseModel):
    """Base model for market data"""
    vehicle_type: str
    average_market_price: float
    lowest_market_price: float
    highest_market_price: float
    price_trend_30d: float
    average_days_to_sell: int
    demand_index: float
    competitor_count: int
    region: str
    seasonal_adjustment: float

class MarketDataCreate(MarketDataBase):
    """Model for creating market data"""
    pass

class MarketDataResponse(MarketDataBase):
    """Model for market data response"""
    market_id: str
    timestamp: str

class MarketDataList(BaseModel):
    """Model for market data list"""
    data: List[MarketDataResponse]

class RecommendationBase(BaseModel):
    """Base model for price recommendations"""
    vehicle_id: str
    current_price: float
    recommended_price: float
    price_change: float
    confidence_score: float
    reasoning: List[str]
    expected_days_to_sell: int
    expected_profit: float
    competitive_position: str

class RecommendationCreate(RecommendationBase):
    """Model for creating a recommendation"""
    expiration: datetime

class RecommendationResponse(RecommendationBase):
    """Model for recommendation response"""
    recommendation_id: str
    timestamp: str
    expiration: str

class RecommendationList(BaseModel):
    """Model for recommendation list"""
    data: List[RecommendationResponse]

class OpportunityBase(BaseModel):
    """Base model for market opportunities"""
    vehicle_type: str
    make: str
    model: str
    year: int
    trim: str
    estimated_market_value: float
    target_acquisition_price: float
    potential_profit: float
    confidence_score: float
    source: str
    opportunity_type: str
    days_available: int
    reasoning: List[str]

class OpportunityCreate(OpportunityBase):
    """Model for creating an opportunity"""
    pass

class OpportunityResponse(OpportunityBase):
    """Model for opportunity response"""
    opportunity_id: str
    timestamp: str

class OpportunityList(BaseModel):
    """Model for opportunity list"""
    data: List[OpportunityResponse]

class HistoricalSaleBase(BaseModel):
    """Base model for historical sales"""
    vehicle_id: str
    sale_price: float
    asking_price: float
    days_on_lot: int
    customer_type: str
    financing_type: str
    salesperson: str
    profit: float
    cost_of_preparation: float
    notes: Optional[str] = None

class HistoricalSaleCreate(HistoricalSaleBase):
    """Model for creating a historical sale"""
    sale_date: date

class HistoricalSaleResponse(HistoricalSaleBase):
    """Model for historical sale response"""
    sale_id: str
    sale_date: str

class HistoricalSaleList(BaseModel):
    """Model for historical sale list"""
    data: List[HistoricalSaleResponse]

class MarketShift(BaseModel):
    """Model for market shift in daily digest"""
    vehicle_type: str
    change: str
    note: str

class UrgentAction(BaseModel):
    """Model for urgent action in daily digest"""
    action_type: str
    vehicle_id: str
    make: str
    model: str
    year: int
    current_price: float
    recommended_price: Optional[float] = None
    urgency: str
    reason: str

class PerformingModel(BaseModel):
    """Model for top performing model in daily digest"""
    type: str
    avg_days_to_sell: int
    profit_margin: float

class PerformanceMetrics(BaseModel):
    """Model for performance metrics in daily digest"""
    average_days_to_sell: float
    average_profit_margin: float
    inventory_turnover_rate: float
    top_performing_models: List[PerformingModel]

class DigestSummary(BaseModel):
    """Model for daily digest summary"""
    new_opportunities: int
    price_adjustments_needed: int
    aging_inventory: int
    market_shifts: List[MarketShift]

class DailyDigestResponse(BaseModel):
    """Model for daily digest response"""
    date: str
    summary: DigestSummary
    urgent_actions: List[UrgentAction]
    performance_metrics: PerformanceMetrics

class QueryContext(BaseModel):
    """Model for query context"""
    page: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None

class QueryRequest(BaseModel):
    """Model for natural language query request"""
    query: str
    context: Optional[QueryContext] = None

class QueryVehicleResult(BaseModel):
    """Model for vehicle in query result"""
    vehicle_id: str
    make: str
    model: str
    year: int
    current_price: float
    recommended_price: Optional[float] = None
    potential_profit: Optional[float] = None
    days_on_lot: int
    reasoning: Optional[List[str]] = None

class VisualizationData(BaseModel):
    """Model for visualization data in query result"""
    chart_type: str
    x_axis: str
    y_axis: str
    data_points: List[Dict[str, Any]]

class QueryResults(BaseModel):
    """Model for query results"""
    vehicles: Optional[List[QueryVehicleResult]] = None
    explanation: str
    visualization_data: Optional[VisualizationData] = None

class QueryResponse(BaseModel):
    """Model for query response"""
    query_id: str
    results: QueryResults

class ErrorDetails(BaseModel):
    """Model for error details"""
    parameter: Optional[str] = None
    value: Optional[Any] = None

class ErrorResponse(BaseModel):
    """Model for error response"""
    error: Dict[str, Any]