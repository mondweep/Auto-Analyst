import { useState } from 'react';
import { Button } from './button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
import { DownloadIcon } from 'lucide-react';

// Explicitly use port 8001 for the backend file server
const BACKEND_URL = 'http://localhost:8001';

const AUTOMOTIVE_FILES = [
  {
    name: 'vehicles.csv',
    description: 'Complete vehicle inventory dataset with all vehicle details',
    path: '/exports/vehicles.csv'
  },
  {
    name: 'market_data.csv',
    description: 'Market analysis data with pricing comparisons and demand metrics',
    path: '/exports/market_data.csv'
  },
  {
    name: 'automotive_analysis.csv',
    description: 'Combined dataset with vehicle details and market information',
    path: '/exports/automotive_analysis.csv'
  }
];

export function FileDownloader() {
  const [downloading, setDownloading] = useState<string | null>(null);

  const handleDownload = async (filePath: string, fileName: string) => {
    try {
      setDownloading(fileName);
      
      // Create a URL to the file on the backend
      const fileUrl = `${BACKEND_URL}${filePath}`;
      console.log(`Attempting to download from: ${fileUrl}`);
      
      // Fetch the file
      const response = await fetch(fileUrl);
      
      if (!response.ok) {
        throw new Error(`Failed to download file: ${response.statusText}`);
      }
      
      // Get the file as a blob
      const blob = await response.blob();
      
      // Create a download link
      const downloadUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = fileName;
      
      // Trigger the download
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      document.body.removeChild(a);
      URL.revokeObjectURL(downloadUrl);
      
    } catch (error) {
      console.error('Error downloading file:', error);
      alert('Failed to download file. Please try again later.');
    } finally {
      setDownloading(null);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Automotive Data Files</CardTitle>
        <CardDescription>
          Download sample automotive datasets to use with the chat interface
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {AUTOMOTIVE_FILES.map((file) => (
          <div key={file.name} className="flex justify-between items-center p-4 border rounded-lg">
            <div>
              <h3 className="font-medium">{file.name}</h3>
              <p className="text-sm text-gray-500">{file.description}</p>
            </div>
            <Button 
              onClick={() => handleDownload(file.path, file.name)}
              disabled={downloading === file.name}
              variant="outline"
              className="flex items-center gap-2"
            >
              <DownloadIcon size={16} />
              {downloading === file.name ? 'Downloading...' : 'Download'}
            </Button>
          </div>
        ))}
        <p className="text-xs text-gray-500 mt-4">
          After downloading, you can upload these files in the chat interface and ask questions about the data.
        </p>
      </CardContent>
    </Card>
  );
} 