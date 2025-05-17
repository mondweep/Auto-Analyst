'use client';

import { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import AUTOMOTIVE_API_URL from '@/config/automotive-api';

// Define types
interface MarketData {
  vehicle_id: number;
  make: string;
  model: string;
  year: number;
  avg_market_price: number;
  price_difference: number;
  percent_difference: number;
  is_opportunity: boolean;
  sample_size: number;
  avg_days_to_sell: number;
  market_demand: string;
}

export default function MarketData() {
  // State
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [filteredData, setFilteredData] = useState<MarketData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filter states
  const [makeFilter, setMakeFilter] = useState<string>('');
  const [demandFilter, setDemandFilter] = useState<string>('');
  
  // Unique values for filters
  const [makes, setMakes] = useState<string[]>([]);
  const [demands, setDemands] = useState<string[]>([]);
  
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
        
        setMarketData(marketDataArray);
        setFilteredData(marketDataArray);
        
        // Extract unique makes and demand levels for filters
        const uniqueMakes = [...new Set(marketDataArray.map((d: MarketData) => d.make))] as string[];
        const uniqueDemands = [...new Set(marketDataArray.map((d: MarketData) => d.market_demand))] as string[];
        
        setMakes(uniqueMakes);
        setDemands(uniqueDemands);
        
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
  
  // Get demand badge class
  const getDemandBadgeClass = (demand: string) => {
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
  const getPriceDifferenceClass = (percent: number) => {
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
              <TableHead>Market Price</TableHead>
              <TableHead>Difference</TableHead>
              <TableHead>%</TableHead>
              <TableHead>Demand</TableHead>
              <TableHead>Avg. Days to Sell</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredData.length > 0 ? (
              filteredData.map((data) => (
                <TableRow key={data.vehicle_id}>
                  <TableCell>{data.make}</TableCell>
                  <TableCell>{data.model}</TableCell>
                  <TableCell>{data.year}</TableCell>
                  <TableCell>{formatCurrency(data.avg_market_price)}</TableCell>
                  <TableCell className={getPriceDifferenceClass(data.percent_difference)}>
                    {formatCurrency(data.price_difference)}
                  </TableCell>
                  <TableCell className={getPriceDifferenceClass(data.percent_difference)}>
                    {formatPercentage(data.percent_difference)}
                  </TableCell>
                  <TableCell>
                    <span className={`px-2 py-1 rounded-full text-xs ${getDemandBadgeClass(data.market_demand)}`}>
                      {data.market_demand}
                    </span>
                  </TableCell>
                  <TableCell>{data.avg_days_to_sell} days</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colspan={8} className="text-center py-6 text-gray-500">
                  No market data matches your current filters
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
} 