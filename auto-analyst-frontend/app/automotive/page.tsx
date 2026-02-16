'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Home } from 'lucide-react';
import { useRouter } from 'next/navigation';
import VehicleList from '@/components/automotive/VehicleList';
import MarketData from '@/components/automotive/MarketData';
import Opportunities from '@/components/automotive/Opportunities';
import Statistics from '@/components/automotive/Statistics';

export default function AutomotivePage() {
  const router = useRouter();

  return (
    <div className="container mx-auto py-8">
      <div className="flex justify-between items-center mb-4">
        <Button 
          variant="outline" 
          size="sm" 
          className="flex items-center gap-1"
          onClick={() => router.push('/')}
        >
          <Home size={16} />
          <span>Home</span>
        </Button>
      </div>

      <div className="mb-8">
        <h1 className="text-3xl font-bold">Automotive Analytics</h1>
        <p className="text-gray-500">
          Analyze vehicle inventory, market data, and identify pricing opportunities
        </p>
      </div>

      <Tabs defaultValue="inventory" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="inventory">Inventory</TabsTrigger>
          <TabsTrigger value="market">Market Data</TabsTrigger>
          <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
          <TabsTrigger value="statistics">Statistics</TabsTrigger>
        </TabsList>
        
        <TabsContent value="inventory">
          <Card>
            <CardHeader>
              <CardTitle>Vehicle Inventory</CardTitle>
              <CardDescription>
                Browse and filter your current vehicle inventory
              </CardDescription>
            </CardHeader>
            <CardContent>
              <VehicleList />
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="market">
          <Card>
            <CardHeader>
              <CardTitle>Market Data</CardTitle>
              <CardDescription>
                Compare your inventory against market prices
              </CardDescription>
            </CardHeader>
            <CardContent>
              <MarketData />
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="opportunities">
          <Card>
            <CardHeader>
              <CardTitle>Pricing Opportunities</CardTitle>
              <CardDescription>
                Identify undervalued vehicles in your inventory
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Opportunities />
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="statistics">
          <Card>
            <CardHeader>
              <CardTitle>Inventory Statistics</CardTitle>
              <CardDescription>
                Overview of your automotive inventory
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Statistics />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 