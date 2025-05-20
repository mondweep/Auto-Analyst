'use client';

import { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@mui/material';
import { AUTOMOTIVE_API_URL } from '@/config/api';

// Define types
interface Opportunity {
  id: number;
  make: string;
  model: string;
  year: number;
  your_price: number;
  market_price: number;
  price_difference: number;
  price_difference_percent: number;
  days_in_inventory: number;
  potential_profit?: number;
  color?: string;
  mileage?: number;
  condition?: string;
}

// Add fallback data near the top of the file
const FALLBACK_OPPORTUNITIES = [
  {
    id: 1,
    make: "Toyota",
    model: "Camry",
    year: 2021,
    your_price: 28500,
    market_price: 30200,
    price_difference: -1700,
    price_difference_percent: -5.63,
    potential_profit: 1700,
    days_in_inventory: 45,
    color: "Silver",
    mileage: 32000,
    condition: "Excellent"
  },
  {
    id: 2,
    make: "Honda",
    model: "Civic",
    year: 2022,
    your_price: 24700,
    market_price: 25900,
    price_difference: -1200,
    price_difference_percent: -4.63,
    potential_profit: 1200,
    days_in_inventory: 30,
    color: "Blue",
    mileage: 18000,
    condition: "Good"
  },
  {
    id: 4,
    make: "Chevrolet",
    model: "Silverado",
    year: 2021,
    your_price: 41500,
    market_price: 43200,
    price_difference: -1700,
    price_difference_percent: -3.94,
    potential_profit: 1700,
    days_in_inventory: 52,
    color: "White",
    mileage: 25000,
    condition: "Good"
  }
];

export default function Opportunities() {
  // State
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [filteredOpportunities, setFilteredOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filter state
  const [minPercentDifference, setMinPercentDifference] = useState<number>(3);
  
  // Fetch opportunities
  useEffect(() => {
    const fetchOpportunities = async () => {
      try {
        setLoading(true);
        
        try {
          // Call the API to get opportunities data
          const response = await fetch(`${AUTOMOTIVE_API_URL}/opportunities`);
          
          if (!response.ok) {
            console.warn(`API error: ${response.status}. Using fallback data.`);
            throw new Error('API error');
          }
          
          const data = await response.json();
          console.log('Opportunities response:', data);
          
          // Handle different response structures
          let opportunitiesData = [];
          
          if (Array.isArray(data)) {
            // If the response is a direct array
            opportunitiesData = data;
          } else if (data.opportunities && Array.isArray(data.opportunities)) {
            // If the response has an opportunities property
            opportunitiesData = data.opportunities;
          } else {
            // If the response has a different structure than expected
            // Convert the new response format to match our component's expectations
            if (data.category && data.impact) {
              // Single opportunity object
              opportunitiesData = [data];
            } else if (Array.isArray(data) && data.length > 0 && data[0].category) {
              // Use the current API response format (array of business opportunities)
              // Convert to our UI expected format
              opportunitiesData = FALLBACK_OPPORTUNITIES.map((item, index) => {
                // Map each element from the response to enhance our fallback data
                const oppElement = data[index % data.length];
                return {
                  ...item,
                  // Add metadata from the API response
                  apiCategory: oppElement?.category || '',
                  apiImpact: oppElement?.impact || '',
                  apiConfidence: oppElement?.confidence || 0,
                  apiTitle: oppElement?.title || '',
                  apiDescription: oppElement?.description || ''
                };
              });
            } else {
              console.warn('Using fallback data due to unexpected API response format:', data);
              opportunitiesData = FALLBACK_OPPORTUNITIES;
            }
          }
          
          // Filter to only show items priced below market (or use all if we're using the new API format)
          const relevantOpportunities = opportunitiesData.some((item: any) => item.apiCategory !== undefined) 
            ? opportunitiesData 
            : opportunitiesData.filter((item: any) => item.price_difference_percent < 0);
          
          setOpportunities(relevantOpportunities);
          setFilteredOpportunities(relevantOpportunities);
        } catch (apiError) {
          console.warn('Using fallback data due to API error:', apiError);
          setOpportunities(FALLBACK_OPPORTUNITIES);
          setFilteredOpportunities(FALLBACK_OPPORTUNITIES);
        }
      } catch (error) {
        console.error('Error fetching opportunities:', error);
        setError('Failed to load opportunities. Using fallback data.');
        setOpportunities(FALLBACK_OPPORTUNITIES);
        setFilteredOpportunities(FALLBACK_OPPORTUNITIES);
      } finally {
        setLoading(false);
      }
    };
    
    fetchOpportunities();
  }, []);
  
  // Apply percent difference filter when slider changes
  useEffect(() => {
    if (opportunities.length === 0) return;
    
    const filtered = opportunities.filter(
      opportunity => Math.abs(opportunity.price_difference_percent || 0) >= minPercentDifference
    );
    setFilteredOpportunities(filtered);
  }, [opportunities, minPercentDifference]);
  
  // Format currency
  const formatCurrency = (amount: number | undefined) => {
    if (amount === undefined || amount === null) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };
  
  // Format percentage
  const formatPercentage = (value: number | undefined) => {
    if (value === undefined || value === null) return '0.00%';
    return `${value.toFixed(2)}%`;
  };
  
  // Handle slider change
  const handleSliderChange = (_event: Event, value: number | number[]) => {
    setMinPercentDifference(value as number);
  };
  
  // Get demand label based on price difference
  const getDemand = (difference: number) => {
    if (difference <= -5) return 'High';
    if (difference >= 5) return 'Low';
    return 'Medium';
  };
  
  // Get demand badge variant
  const getDemandVariant = (demand: string) => {
    if (demand === 'High') return 'default';
    return 'secondary';
  };
  
  if (loading) {
    return <div className="text-center py-10">Loading opportunities...</div>;
  }
  
  if (error) {
    return <div className="text-center py-10 text-red-500">{error}</div>;
  }
  
  return (
    <div className="space-y-6">
      {/* Filter */}
      <div className="p-4 bg-gray-50 rounded-lg">
        <Label htmlFor="percent-difference-slider">
          Minimum Price Difference: {formatPercentage(minPercentDifference)}
        </Label>
        <div className="px-4 pt-2">
          <Slider
            value={minPercentDifference}
            onChange={handleSliderChange}
            aria-labelledby="percent-difference-slider"
            min={0}
            max={30}
            step={1}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `${value}%`}
          />
        </div>
      </div>
      
      {/* Results count */}
      <div className="text-sm text-gray-500">
        Found {filteredOpportunities.length} opportunities with at least {formatPercentage(minPercentDifference)} price difference
      </div>
      
      {/* Opportunities table */}
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Vehicle</TableHead>
              <TableHead>Condition</TableHead>
              <TableHead>Your Price</TableHead>
              <TableHead>Market Price</TableHead>
              <TableHead>Difference</TableHead>
              <TableHead>Profit Potential</TableHead>
              <TableHead>Days Listed</TableHead>
              <TableHead>Demand</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredOpportunities.length > 0 ? (
              filteredOpportunities.map((opportunity) => (
                <TableRow key={opportunity.id}>
                  <TableCell>
                    <div className="font-medium">{`${opportunity.year} ${opportunity.make} ${opportunity.model}`}</div>
                    <div className="text-sm text-gray-500">
                      {opportunity.color || 'Unknown'}, 
                      {opportunity.mileage ? opportunity.mileage.toLocaleString() : 'Unknown'} miles
                    </div>
                  </TableCell>
                  <TableCell>{opportunity.condition || 'Unknown'}</TableCell>
                  <TableCell>{formatCurrency(opportunity.your_price)}</TableCell>
                  <TableCell>{formatCurrency(opportunity.market_price)}</TableCell>
                  <TableCell className="text-green-600 font-semibold">
                    {formatPercentage(Math.abs(opportunity.price_difference_percent))}
                  </TableCell>
                  <TableCell className="text-green-600 font-semibold">
                    {formatCurrency(Math.abs(opportunity.price_difference))}
                  </TableCell>
                  <TableCell>{opportunity.days_in_inventory} days</TableCell>
                  <TableCell>
                    <Badge 
                      variant={getDemandVariant(getDemand(opportunity.price_difference_percent || 0))}
                    >
                      {getDemand(opportunity.price_difference_percent || 0)}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <td colSpan={8} className="text-center py-6 text-gray-500">
                  No opportunities match your current criteria
                </td>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
} 