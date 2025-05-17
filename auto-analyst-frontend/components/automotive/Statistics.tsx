'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PieChart, Pie, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import AUTOMOTIVE_API_URL from '@/config/automotive-api';

// Define types
interface Statistics {
  total_vehicles: number;
  available_vehicles: number;
  sold_vehicles: number;
  make_distribution: Record<string, number>;
  condition_distribution: Record<string, number>;
  avg_prices_by_make: Record<string, number>;
  opportunities_count: number;
}

// Custom colors for charts
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658', '#8dd1e1', '#a4de6c', '#d0ed57'];

export default function Statistics() {
  // State
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Format data for charts
  const [makeData, setMakeData] = useState<any[]>([]);
  const [conditionData, setConditionData] = useState<any[]>([]);
  const [priceData, setPriceData] = useState<any[]>([]);
  
  // Fetch statistics
  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        setLoading(true);
        
        // Call the API to get statistics data
        const response = await fetch(`${AUTOMOTIVE_API_URL}/api/statistics`);
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        setStatistics(data);
        
        // Format make distribution for chart
        const makeChartData = Object.entries(data.make_distribution || {}).map(([name, value]) => ({
          name,
          value
        }));
        setMakeData(makeChartData);
        
        // Format condition distribution for chart
        const conditionChartData = Object.entries(data.condition_distribution || {}).map(([name, value]) => ({
          name,
          value
        }));
        setConditionData(conditionChartData);
        
        // Format price data for chart
        const priceChartData = Object.entries(data.avg_prices_by_make || {}).map(([name, value]) => ({
          name,
          price: value
        }));
        setPriceData(priceChartData);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching statistics:', err);
        setError('Failed to load statistics. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchStatistics();
  }, []);
  
  // Format currency
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(value);
  };
  
  // Format numbers with commas
  const formatNumber = (value: number) => {
    return new Intl.NumberFormat('en-US').format(value);
  };
  
  // Calculate percentage
  const calculatePercentage = (value: number, total: number) => {
    return ((value / total) * 100).toFixed(1);
  };
  
  // Custom tooltip for bar chart
  const PriceTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-2 border border-gray-200 shadow-md">
          <p className="font-medium">{payload[0].payload.name}</p>
          <p className="text-sm">Avg. Price: {formatCurrency(payload[0].value)}</p>
        </div>
      );
    }
    return null;
  };
  
  if (loading) {
    return <div className="text-center py-10">Loading statistics...</div>;
  }
  
  if (error) {
    return <div className="text-center py-10 text-red-500">{error}</div>;
  }
  
  if (!statistics) {
    return <div className="text-center py-10 text-red-500">No data available</div>;
  }
  
  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Total Vehicles</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(statistics.total_vehicles)}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Available</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {formatNumber(statistics.available_vehicles)}
              <span className="text-sm font-normal text-gray-500 ml-2">
                ({calculatePercentage(statistics.available_vehicles, statistics.total_vehicles)}%)
              </span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Sold</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {formatNumber(statistics.sold_vehicles)}
              <span className="text-sm font-normal text-gray-500 ml-2">
                ({calculatePercentage(statistics.sold_vehicles, statistics.total_vehicles)}%)
              </span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Opportunities</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {formatNumber(statistics.opportunities_count)}
              <span className="text-sm font-normal text-gray-500 ml-2">
                ({calculatePercentage(statistics.opportunities_count, statistics.available_vehicles)}% of available)
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Make Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Inventory by Make</CardTitle>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={makeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {makeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatNumber(value as number)} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        {/* Condition Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Vehicles by Condition</CardTitle>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={conditionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {conditionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatNumber(value as number)} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        
        {/* Average Price by Make */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Average Price by Make</CardTitle>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={priceData}
                margin={{
                  top: 5,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <XAxis dataKey="name" />
                <YAxis tickFormatter={(value) => `$${value / 1000}k`} />
                <Tooltip content={<PriceTooltip />} />
                <Legend />
                <Bar dataKey="price" fill="#8884d8">
                  {priceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 