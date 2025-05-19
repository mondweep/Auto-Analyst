'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import API_URL from '@/config/api';

// Define vehicle type
interface Vehicle {
  id: number;
  make: string;
  model: string;
  year: number;
  color: string;
  price: number;
  mileage: number;
  condition: string;
  fuel_type: string;
  list_date: string;
  days_in_inventory: number;
  vin: string;
  is_sold: boolean;
}

export default function VehicleList() {
  // State
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [filteredVehicles, setFilteredVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filter states
  const [makeFilter, setMakeFilter] = useState<string>('');
  const [minPrice, setMinPrice] = useState<string>('');
  const [maxPrice, setMaxPrice] = useState<string>('');
  const [conditionFilter, setConditionFilter] = useState<string>('');
  const [soldFilter, setSoldFilter] = useState<string>('');
  
  // Unique values for filters
  const [makes, setMakes] = useState<string[]>([]);
  const [conditions, setConditions] = useState<string[]>([]);
  
  // Fetch vehicles data
  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/api/vehicles`);
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        setVehicles(data.vehicles || []);
        setFilteredVehicles(data.vehicles || []);
        
        // Extract unique makes and conditions for filters
        const uniqueMakes = [...new Set(data.vehicles.map((v: Vehicle) => v.make))] as string[];
        const uniqueConditions = [...new Set(data.vehicles.map((v: Vehicle) => v.condition))] as string[];
        
        setMakes(uniqueMakes);
        setConditions(uniqueConditions);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching vehicles:', err);
        setError('Failed to load vehicles. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchVehicles();
  }, []);
  
  // Apply filters
  useEffect(() => {
    let filtered = [...vehicles];
    
    // Apply make filter
    if (makeFilter && makeFilter !== 'all') {
      filtered = filtered.filter(v => v.make === makeFilter);
    }
    
    // Apply price filters
    if (minPrice) {
      filtered = filtered.filter(v => v.price >= parseInt(minPrice));
    }
    
    if (maxPrice) {
      filtered = filtered.filter(v => v.price <= parseInt(maxPrice));
    }
    
    // Apply condition filter
    if (conditionFilter && conditionFilter !== 'all') {
      filtered = filtered.filter(v => v.condition === conditionFilter);
    }
    
    // Apply sold filter
    if (soldFilter === 'true') {
      filtered = filtered.filter(v => v.is_sold);
    } else if (soldFilter === 'false') {
      filtered = filtered.filter(v => !v.is_sold);
    }
    
    setFilteredVehicles(filtered);
  }, [vehicles, makeFilter, minPrice, maxPrice, conditionFilter, soldFilter]);
  
  // Reset filters
  const resetFilters = () => {
    setMakeFilter('');
    setMinPrice('');
    setMaxPrice('');
    setConditionFilter('');
    setSoldFilter('');
    setFilteredVehicles(vehicles);
  };
  
  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };
  
  if (loading) {
    return <div className="text-center py-10">Loading vehicle inventory...</div>;
  }
  
  if (error) {
    return <div className="text-center py-10 text-red-500">{error}</div>;
  }
  
  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
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
          <Label htmlFor="min-price">Min Price</Label>
          <Input
            id="min-price"
            type="number"
            placeholder="$0"
            value={minPrice}
            onChange={(e) => setMinPrice(e.target.value)}
          />
        </div>
        
        <div>
          <Label htmlFor="max-price">Max Price</Label>
          <Input
            id="max-price"
            type="number"
            placeholder="No Limit"
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
          />
        </div>
        
        <div>
          <Label htmlFor="condition-filter">Condition</Label>
          <Select value={conditionFilter} onValueChange={setConditionFilter}>
            <SelectTrigger id="condition-filter">
              <SelectValue placeholder="Any Condition" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Any Condition</SelectItem>
              {conditions.map(condition => (
                <SelectItem key={condition} value={condition}>{condition}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <div>
          <Label htmlFor="sold-filter">Status</Label>
          <Select value={soldFilter} onValueChange={setSoldFilter}>
            <SelectTrigger id="sold-filter">
              <SelectValue placeholder="All Vehicles" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Vehicles</SelectItem>
              <SelectItem value="false">Available</SelectItem>
              <SelectItem value="true">Sold</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="md:col-span-5 flex justify-end">
          <Button variant="outline" onClick={resetFilters}>
            Reset Filters
          </Button>
        </div>
      </div>
      
      {/* Results count */}
      <div className="text-sm text-gray-500">
        Showing {filteredVehicles.length} of {vehicles.length} vehicles
      </div>
      
      {/* Vehicle table */}
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Make</TableHead>
              <TableHead>Model</TableHead>
              <TableHead>Year</TableHead>
              <TableHead>Color</TableHead>
              <TableHead>Price</TableHead>
              <TableHead>Mileage</TableHead>
              <TableHead>Condition</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredVehicles.length > 0 ? (
              filteredVehicles.map((vehicle) => (
                <TableRow key={vehicle.id}>
                  <TableCell>{vehicle.make}</TableCell>
                  <TableCell>{vehicle.model}</TableCell>
                  <TableCell>{vehicle.year}</TableCell>
                  <TableCell>{vehicle.color}</TableCell>
                  <TableCell>{formatCurrency(vehicle.price)}</TableCell>
                  <TableCell>{vehicle.mileage.toLocaleString()}</TableCell>
                  <TableCell>{vehicle.condition}</TableCell>
                  <TableCell>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      vehicle.is_sold 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {vehicle.is_sold ? 'Sold' : 'Available'}
                    </span>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <tr>
                <td colSpan={8} className="text-center py-6 text-gray-500">
                  No vehicles match your current filters
                </td>
              </tr>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
} 