'use client';

import { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@mui/material';
import AUTOMOTIVE_API_URL from '@/config/automotive-api';

// Define types
interface Opportunity {
  id: number;
  make: string;
  model: string;
  year: number;
  color: string;
  price: number;
  mileage: number;
  condition: string;
  days_in_inventory: number;
  market_data: {
    avg_market_price: number;
    price_difference: number;
    percent_difference: number;
    market_demand: string;
  };
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
        const opportunitiesData = data.opportunities || [];
        
        setOpportunities(opportunitiesData);
        setFilteredOpportunities(opportunitiesData);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching opportunities:', err);
        setError('Failed to load opportunities. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchOpportunities();
  }, []);
  
  // Apply percent difference filter
  useEffect(() => {
    const filtered = opportunities.filter(
      opportunity => opportunity.market_data.percent_difference >= minPercentDifference
    );
    setFilteredOpportunities(filtered);
  }, [opportunities, minPercentDifference]);
  
  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };
  
  // Format percentage
  const formatPercentage = (value: number) => {
    return `${value.toFixed(2)}%`;
  };
  
  // Handle slider change
  const handleSliderChange = (_event: Event, value: number | number[]) => {
    setMinPercentDifference(value as number);
  };
  
  // Calculate profit potential
  const calculateProfitPotential = (opportunity: Opportunity) => {
    return opportunity.market_data.price_difference;
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
                    <div className="text-sm text-gray-500">{opportunity.color}, {opportunity.mileage.toLocaleString()} miles</div>
                  </TableCell>
                  <TableCell>{opportunity.condition}</TableCell>
                  <TableCell>{formatCurrency(opportunity.price)}</TableCell>
                  <TableCell>{formatCurrency(opportunity.market_data.avg_market_price)}</TableCell>
                  <TableCell className="text-green-600 font-semibold">
                    {formatPercentage(opportunity.market_data.percent_difference)}
                  </TableCell>
                  <TableCell className="text-green-600 font-semibold">
                    {formatCurrency(calculateProfitPotential(opportunity))}
                  </TableCell>
                  <TableCell>{opportunity.days_in_inventory} days</TableCell>
                  <TableCell>
                    <Badge 
                      variant={opportunity.market_data.market_demand === 'High' ? 'default' : 'secondary'}
                    >
                      {opportunity.market_data.market_demand}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-6 text-gray-500">
                  No opportunities match your current criteria
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
} 