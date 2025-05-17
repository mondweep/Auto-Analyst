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
  const { queriesUsed, hasFreeTrial } = useFreeTrialStore()
  const [hasApiKey, setHasApiKey] = useState(false)
  
  // Check for first-time free trial users
  useEffect(() => {
    if (status === "unauthenticated" && queriesUsed === 0 && hasFreeTrial()) {
      // First-time free trial user, set flag to show onboarding tooltip
      if (!localStorage.getItem('hasSeenOnboarding')) {
        localStorage.setItem('showOnboarding', 'true')
      }
    }
    
    // Check if API key is stored
    const userApiKey = localStorage.getItem('userApiKey')
    setHasApiKey(!!userApiKey)
  }, [status, queriesUsed, hasFreeTrial])

  const handleApiKeySet = () => {
    setHasApiKey(true)
  }
  
  return (
    <ResponsiveLayout>
      <div className="container mx-auto py-4">
        <Tabs defaultValue={hasApiKey ? "chat" : "settings"} className="w-full">
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

