import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export function ApiKeyConfig({ onApiKeySet }: { onApiKeySet?: () => void }) {
  const [apiKey, setApiKey] = useState('');
  const [provider, setProvider] = useState('gemini');
  const [isSaving, setIsSaving] = useState(false);
  const { toast } = useToast();

  const handleSaveApiKey = () => {
    if (!apiKey.trim()) {
      toast({
        title: 'API Key Required',
        description: 'Please enter a valid API key',
        variant: 'destructive',
      });
      return;
    }

    setIsSaving(true);
    
    // Save to localStorage
    localStorage.setItem('userApiKey', apiKey);
    localStorage.setItem('modelProvider', provider);
    
    // Show success toast
    toast({
      title: 'API Key Saved',
      description: `Your ${provider.charAt(0).toUpperCase() + provider.slice(1)} API key has been saved and will be used for future requests.`,
      variant: 'default',
    });
    
    setIsSaving(false);
    
    // Call the callback if provided
    if (onApiKeySet) {
      onApiKeySet();
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Configure AI Provider</CardTitle>
        <CardDescription>
          Enter your API key to use with the AI chat interface
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="provider">AI Provider</Label>
          <Select value={provider} onValueChange={setProvider}>
            <SelectTrigger id="provider">
              <SelectValue placeholder="Select Provider" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="gemini">Google Gemini</SelectItem>
              <SelectItem value="openai">OpenAI</SelectItem>
              <SelectItem value="anthropic">Anthropic</SelectItem>
              <SelectItem value="groq">Groq</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="apiKey">API Key</Label>
          <Input
            id="apiKey"
            type="password"
            placeholder="Enter your API key here"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
          <p className="text-xs text-gray-500">
            Your API key is stored locally in your browser and never sent to our servers.
          </p>
        </div>
        
        <Button 
          className="w-full" 
          onClick={handleSaveApiKey} 
          disabled={isSaving}
        >
          {isSaving ? 'Saving...' : 'Save API Key'}
        </Button>
      </CardContent>
    </Card>
  );
} 