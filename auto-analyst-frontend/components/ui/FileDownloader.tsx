import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

// Demo files always available
const DEMO_FILES = [
  { 
    id: 1, 
    name: 'market_data.csv',
    description: 'Sample market data for automotive pricing analysis',
    size: '8.9 KB',
    url: '/demo-files/market_data.csv'
  },
  { 
    id: 2, 
    name: 'vehicles.csv',
    description: 'Sample vehicle inventory data', 
    size: '16.7 KB',
    url: '/demo-files/vehicles.csv'
  },
  { 
    id: 3, 
    name: 'automotive_analysis.csv',
    description: 'Comprehensive automotive market analysis',
    size: '14.2 KB', 
    url: '/demo-files/automotive_analysis.csv'
  }
];

export function FileDownloader() {
  const [files, setFiles] = useState(DEMO_FILES);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  
  const handleDownload = (file: any) => {
    // Create an anchor element to trigger the download
    const a = document.createElement('a');
    a.href = file.url;
    a.download = file.name;
    a.click();
  };

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = event.target.files?.[0];
    if (!uploadedFile) return;
    
    setIsUploading(true);
    setUploadError(null);
    
    try {
      // In demo mode, we just simulate a file upload by adding it to the list
      // without actually uploading it to a server
      const newFile = {
        id: files.length + 1,
        name: uploadedFile.name,
        description: 'Uploaded file (demo)',
        size: `${(uploadedFile.size / 1024).toFixed(1)} KB`,
        url: URL.createObjectURL(uploadedFile) // Create a local object URL
      };
      
      // Add to the state
      setFiles(prev => [...prev, newFile]);
      
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log('File uploaded successfully (demo mode)');
    } catch (error) {
      console.error('File upload error:', error);
      setUploadError('Failed to upload file. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col space-y-2">
        <h2 className="text-2xl font-bold mb-4">Available Datasets</h2>
        
        {/* File upload section */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Upload New Dataset</CardTitle>
            <CardDescription>
              Upload CSV files for analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4">
              <input
                type="file"
                id="file-upload"
                className="hidden"
                accept=".csv"
                onChange={handleUpload}
                disabled={isUploading}
              />
              <label
                htmlFor="file-upload"
                className={`cursor-pointer inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 ${
                  isUploading ? "opacity-50 cursor-not-allowed" : ""
                }`}
              >
                {isUploading ? "Uploading..." : "Upload CSV"}
              </label>
              {uploadError && (
                <span className="text-red-500 text-sm">{uploadError}</span>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Files list */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {files.map((file) => (
            <Card key={file.id} className="overflow-hidden">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">{file.name}</CardTitle>
                <CardDescription className="text-xs">
                  {file.size}
                </CardDescription>
              </CardHeader>
              <CardContent className="pb-2">
                <p className="text-sm text-muted-foreground">
                  {file.description}
                </p>
              </CardContent>
              <CardFooter>
                <Button
                  variant="default"
                  size="sm"
                  onClick={() => handleDownload(file)}
                  className="w-full"
                >
                  Download
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
} 