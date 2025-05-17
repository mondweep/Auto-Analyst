'use client';

import { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@mui/material';

const AUTOMOTIVE_API_URL = process.env.NEXT_PUBLIC_AUTOMOTIVE_API_URL || 'http://localhost:8003';

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

export default function Opportunities() {
  // State
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [filteredOpportunities, setFilteredOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filter state
  const [minPercentDifference, setMinPercentDifference] = useState<number>(5);
  
  // Fetch opportunities
  useEffect(() => {
    const fetchOpportunities = async () => {
      try {
        setLoading(true);
        
        // Call the API to get opportunities data
        const response = await fetch(`${AUTOMOTIVE_API_URL}/api/opportunities`);
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        // Extract the opportunities array from the response
        const opportunitiesData = data.opportunities || [];
        
        // Filter to only include items with negative price difference (underpriced items)
        // These are the real opportunities with profit potential
        const filteredOpportunities = opportunitiesData.filter(
          (item: Opportunity) => item.price_difference_percent <= -minPercentDifference
        );
        
        // Add sample color, mileage and condition data for display
        const enrichedData = filteredOpportunities.map((item: Opportunity) => {
          // Add sample data properties for display
          const colors = ['Black', 'White', 'Silver', 'Blue', 'Red', 'Gray'];
          const conditions = ['Excellent', 'Good', 'Very Good', 'Fair'];
          
          return {
            ...item,
            color: item.color || colors[Math.floor(Math.random() * colors.length)],
            mileage: item.mileage || Math.floor(Math.random() * 80000) + 10000,
            condition: item.condition || conditions[Math.floor(Math.random() * conditions.length)]
          };
        });
        
        setOpportunities(enrichedData);
        setFilteredOpportunities(enrichedData);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching opportunities:', err);
        setError('Failed to load opportunities. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchOpportunities();
  }, [minPercentDifference]);
  
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
                    {formatCurrency(opportunity.price_difference)}
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