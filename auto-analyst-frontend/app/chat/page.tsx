"use client"

import { useEffect, useState } from "react"
import ChatInterface from "@/components/chat/ChatInterface"
import ResponsiveLayout from "../../components/ResponsiveLayout"
import "../globals.css"
import { useFreeTrialStore } from "@/lib/store/freeTrialStore"
import { useSession } from "next-auth/react"
import { ApiKeyConfig } from "@/components/chat/ApiKeyConfig"
import { FileDownloader } from "@/components/ui/FileDownloader"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function ChatPage() {
  const { status } = useSession()
  const { queriesUsed, hasFreeTrial, setHasFreeTrial } = useFreeTrialStore()
  // Always set hasApiKey to true in demo mode
  const [hasApiKey, setHasApiKey] = useState(true)
  
  // Check for first-time free trial users and set model provider
  useEffect(() => {
    // Always enable free trial mode and set infinite queries for demo
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('freeTrialQueries', '0')
      localStorage.setItem('freeTrialEnabled', 'true')
      
      // Force free trial to always be available
      setHasFreeTrial(true)

      // Set model provider (default to gemini if not set)
      const defaultProvider = 'gemini'
      localStorage.setItem('modelProvider', defaultProvider)
    
    // Get API key from environment variables based on provider
    const apiKeys = {
      openai: process.env.NEXT_PUBLIC_OPENAI_API_KEY,
      anthropic: process.env.NEXT_PUBLIC_ANTHROPIC_API_KEY,
      groq: process.env.NEXT_PUBLIC_GROQ_API_KEY,
      gemini: process.env.NEXT_PUBLIC_GEMINI_API_KEY
    }
    
    // Set the API key for the current provider
    const apiKey = apiKeys[defaultProvider as keyof typeof apiKeys] || 'demo-api-key'
    if (apiKey && apiKey !== 'your_') {
      localStorage.setItem('userApiKey', apiKey)
      console.log(`Using ${defaultProvider} with provided API key`)
    } else {
      console.warn('Using demo mode - no valid API key found')
      localStorage.setItem('userApiKey', 'demo-api-key')
    }
  }
  }, [status, queriesUsed, setHasFreeTrial])

  const handleApiKeySet = () => {
    setHasApiKey(true)
  }
  
  return (
    <ResponsiveLayout>
      <div className="container mx-auto py-4">
        <Tabs defaultValue="chat" className="w-full">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-3 mb-4">
            <TabsTrigger value="chat">Chat</TabsTrigger>
            <TabsTrigger value="settings">API Settings</TabsTrigger>
            <TabsTrigger value="datasets">Datasets</TabsTrigger>
          </TabsList>
          
          <TabsContent value="chat">
            <ChatInterface />
          </TabsContent>
          
          <TabsContent value="settings">
            <div className="max-w-md mx-auto">
              <ApiKeyConfig onApiKeySet={handleApiKeySet} />
            </div>
          </TabsContent>
          
          <TabsContent value="datasets">
            <FileDownloader />
          </TabsContent>
        </Tabs>
      </div>
    </ResponsiveLayout>
  )
}

