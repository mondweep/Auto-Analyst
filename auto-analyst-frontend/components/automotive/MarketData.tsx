'use client';

import { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';

const AUTOMOTIVE_API_URL = process.env.NEXT_PUBLIC_AUTOMOTIVE_API_URL || 'http://localhost:8003';

// Define types
interface MarketData {
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
  market_demand?: string;
  avg_days_to_sell?: number;
}

export default function MarketData() {
  // State
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [filteredData, setFilteredData] = useState<MarketData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filter states
  const [makeFilter, setMakeFilter] = useState<string>('all');
  const [demandFilter, setDemandFilter] = useState<string>('all');
  
  // Unique values for filters
  const [makes, setMakes] = useState<string[]>([]);
  const [demands, setDemands] = useState<string[]>(['High', 'Medium', 'Low']);
  
  // Fetch market data
  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        setLoading(true);
        
        // Call the API to get market data
        const response = await fetch(`${AUTOMOTIVE_API_URL}/api/market-data`);
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        const marketDataArray = data.market_data || [];
        
        // Add market demand based on price difference percent
        const enrichedData = marketDataArray.map((item: MarketData) => {
          // Calculate market demand based on price difference
          let marketDemand = 'Medium';
          if (item.price_difference_percent <= -5) {
            marketDemand = 'High';  // Priced below market, high demand
          } else if (item.price_difference_percent >= 5) {
            marketDemand = 'Low';   // Priced above market, low demand
          }
          
          // Add market demand to the item
          return {
            ...item,
            market_demand: marketDemand,
            avg_days_to_sell: Math.round(90 - (item.price_difference_percent * -2)) // Simulated data
          };
        });
        
        setMarketData(enrichedData);
        setFilteredData(enrichedData);
        
        // Extract unique makes
        const uniqueMakes = [...new Set(enrichedData.map((d: MarketData) => d.make))] as string[];
        
        setMakes(uniqueMakes);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching market data:', err);
        setError('Failed to load market data. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchMarketData();
  }, []);
  
  // Apply filters
  useEffect(() => {
    let filtered = [...marketData];
    
    // Apply make filter
    if (makeFilter && makeFilter !== 'all') {
      filtered = filtered.filter(d => d.make === makeFilter);
    }
    
    // Apply demand filter
    if (demandFilter && demandFilter !== 'all') {
      filtered = filtered.filter(d => d.market_demand === demandFilter);
    }
    
    setFilteredData(filtered);
  }, [marketData, makeFilter, demandFilter]);
  
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
  
  // Get demand badge class
  const getDemandBadgeClass = (demand: string | undefined) => {
    switch (demand) {
      case 'High':
        return 'bg-green-100 text-green-800';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'Low':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  // Get price difference class
  const getPriceDifferenceClass = (percent: number | undefined) => {
    if (!percent) return 'text-gray-600';
    
    if (percent > 10) {
      return 'text-green-600 font-semibold';
    } else if (percent > 5) {
      return 'text-green-500';
    } else if (percent < -5) {
      return 'text-red-500';
    } else if (percent < -10) {
      return 'text-red-600 font-semibold';
    } else {
      return 'text-gray-600';
    }
  };
  
  if (loading) {
    return <div className="text-center py-10">Loading market data...</div>;
  }
  
  if (error) {
    return <div className="text-center py-10 text-red-500">{error}</div>;
  }
  
  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
        <div>
          <Label htmlFor="make-filter">Make</Label>
          <Select value={makeFilter} onValueChange={setMakeFilter}>
            <SelectTrigger id="make-filter">
              <SelectValue placeholder="All Makes" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Makes</SelectItem>
              {makes.map(make => (
                <SelectItem key={make} value={make}>{make}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <div>
          <Label htmlFor="demand-filter">Market Demand</Label>
          <Select value={demandFilter} onValueChange={setDemandFilter}>
            <SelectTrigger id="demand-filter">
              <SelectValue placeholder="Any Demand" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Any Demand</SelectItem>
              {demands.map(demand => (
                <SelectItem key={demand} value={demand}>{demand}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
      
      {/* Results count */}
      <div className="text-sm text-gray-500">
        Showing {filteredData.length} of {marketData.length} market data entries
      </div>
      
      {/* Market data table */}
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Make</TableHead>
              <TableHead>Model</TableHead>
              <TableHead>Year</TableHead>
              <TableHead>Your Price</TableHead>
              <TableHead>Market Price</TableHead>
              <TableHead>Difference</TableHead>
              <TableHead>%</TableHead>
              <TableHead>Demand</TableHead>
              <TableHead>Inventory Days</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredData.length > 0 ? (
              filteredData.map((data) => (
                <TableRow key={data.id}>
                  <TableCell>{data.make}</TableCell>
                  <TableCell>{data.model}</TableCell>
                  <TableCell>{data.year}</TableCell>
                  <TableCell>{formatCurrency(data.your_price)}</TableCell>
                  <TableCell>{formatCurrency(data.market_price)}</TableCell>
                  <TableCell className={getPriceDifferenceClass(data.price_difference_percent)}>
                    {formatCurrency(data.price_difference)}
                  </TableCell>
                  <TableCell className={getPriceDifferenceClass(data.price_difference_percent)}>
                    {formatPercentage(data.price_difference_percent)}
                  </TableCell>
                  <TableCell>
                    <span className={`px-2 py-1 rounded-full text-xs ${getDemandBadgeClass(data.market_demand)}`}>
                      {data.market_demand || 'Medium'}
                    </span>
                  </TableCell>
                  <TableCell>{data.days_in_inventory} days</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <td className="text-center py-6 text-gray-500" colSpan={9}>
                  No market data matches your current filters
                </td>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
} 