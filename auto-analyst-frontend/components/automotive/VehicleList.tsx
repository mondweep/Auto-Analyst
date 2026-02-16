'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import API_URL, { DEMO_MODE } from '@/config/api';

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

// Fallback vehicle data for demo/offline mode
const FALLBACK_VEHICLES: Vehicle[] = [
  { id: 1, make: "Toyota", model: "Camry", year: 2021, color: "Silver", price: 28500, mileage: 32000, condition: "Excellent", fuel_type: "Gasoline", list_date: "2024-01-15", days_in_inventory: 45, vin: "1HGBH41JXMN109186", is_sold: false },
  { id: 2, make: "Honda", model: "Civic", year: 2022, color: "Blue", price: 24700, mileage: 18000, condition: "Good", fuel_type: "Gasoline", list_date: "2024-02-01", days_in_inventory: 30, vin: "2HGFC2F59MH522145", is_sold: false },
  { id: 3, make: "Ford", model: "F-150", year: 2020, color: "Red", price: 38900, mileage: 45000, condition: "Good", fuel_type: "Gasoline", list_date: "2023-12-10", days_in_inventory: 60, vin: "1FTEW1EP5LFA12345", is_sold: false },
  { id: 4, make: "Chevrolet", model: "Silverado", year: 2021, color: "White", price: 41500, mileage: 25000, condition: "Good", fuel_type: "Gasoline", list_date: "2024-01-05", days_in_inventory: 52, vin: "3GCUYDED1MG123456", is_sold: false },
  { id: 5, make: "BMW", model: "X5", year: 2020, color: "Black", price: 56800, mileage: 38000, condition: "Excellent", fuel_type: "Gasoline", list_date: "2023-11-20", days_in_inventory: 75, vin: "5UXCR6C05L9B12345", is_sold: true },
  { id: 6, make: "Toyota", model: "RAV4", year: 2023, color: "White", price: 34200, mileage: 8000, condition: "Excellent", fuel_type: "Hybrid", list_date: "2024-03-01", days_in_inventory: 15, vin: "2T3P1RFV5NW123456", is_sold: false },
  { id: 7, make: "Honda", model: "Accord", year: 2021, color: "Gray", price: 29800, mileage: 27000, condition: "Good", fuel_type: "Gasoline", list_date: "2024-01-20", days_in_inventory: 40, vin: "1HGCV1F34MA012345", is_sold: false },
  { id: 8, make: "Ford", model: "Mustang", year: 2022, color: "Yellow", price: 45600, mileage: 12000, condition: "Excellent", fuel_type: "Gasoline", list_date: "2024-02-15", days_in_inventory: 20, vin: "1FA6P8TH5N5123456", is_sold: true },
];

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

  // Helper to populate state from vehicle data
  const populateVehicleData = (vehiclesData: Vehicle[]) => {
    setVehicles(vehiclesData);
    setFilteredVehicles(vehiclesData);
    if (vehiclesData.length > 0) {
      const uniqueMakes = [...new Set(vehiclesData.map((v: Vehicle) => v.make))] as string[];
      const uniqueConditions = [...new Set(vehiclesData.map((v: Vehicle) => v.condition))] as string[];
      setMakes(uniqueMakes);
      setConditions(uniqueConditions);
    }
  };

  // Fetch vehicles data
  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        setLoading(true);

        try {
          const response = await fetch(`${API_URL}/vehicles`);

          if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
          }

          const data = await response.json();

          // Handle different response structures
          let vehiclesData = [];
          if (Array.isArray(data)) {
            vehiclesData = data;
          } else if (data.vehicles && Array.isArray(data.vehicles)) {
            vehiclesData = data.vehicles;
          } else {
            console.warn('Unexpected API response format, using fallback data');
            vehiclesData = FALLBACK_VEHICLES;
          }

          populateVehicleData(vehiclesData);
        } catch (apiError) {
          // API failed — use fallback data without showing error
          console.warn('Using fallback vehicle data due to API error:', apiError);
          populateVehicleData(FALLBACK_VEHICLES);
        }
      } catch (err) {
        console.error('Error in vehicle list component:', err);
        setError('Failed to load vehicles. Please try again later.');
        populateVehicleData(FALLBACK_VEHICLES);
      } finally {
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