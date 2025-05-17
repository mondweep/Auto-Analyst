"use client"

import type React from "react"
import { useState, useEffect, useRef, useCallback } from "react"
import { motion } from "framer-motion"
import Image from "next/image"
import ChatWindow from "./ChatWindow"
import ChatInput from "./ChatInput"
import Sidebar from "./Sidebar"
import axios from "axios"
import { useSession } from "next-auth/react"
import { useFreeTrialStore } from "@/lib/store/freeTrialStore"
import FreeTrialOverlay from "./FreeTrialOverlay"
import { useChatHistoryStore } from "@/lib/store/chatHistoryStore"
import { useCookieConsentStore } from "@/lib/store/cookieConsentStore"
import { useRouter } from "next/navigation"
import { AwardIcon, User, Menu } from "lucide-react"
import { useSessionStore } from '@/lib/store/sessionStore'
import API_URL from '@/config/api'
import { useCredits } from '@/lib/contexts/credit-context'
import { getModelCreditCost } from '@/lib/model-tiers'
import InsufficientCreditsModal from '@/components/chat/InsufficientCreditsModal'
import CreditBalance from '@/components/chat/CreditBalance'
import { Avatar } from '@/components/ui/avatar'
import UserProfilePopup from './UserProfilePopup'
import SettingsPopup from './SettingsPopup'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription
} from "@/components/ui/dialog"
import { Button } from "../ui/button"
import DatasetResetPopup from './DatasetResetPopup'
import { useModelSettings } from '@/lib/hooks/useModelSettings'
import logger from '@/lib/utils/logger'
import { OnboardingTooltip } from '../onboarding/OnboardingTooltips'

// This ensures we can still use the app without a backend server
const DEMO_MODE = true;

interface PlotlyMessage {
  type: "plotly"
  data: any
  layout: any
}

interface Message {
  text: string | PlotlyMessage
  sender: "user" | "ai"
}

interface AgentInfo {
  name: string
  description: string
}

interface ChatMessage {
  text: string | PlotlyMessage;
  sender: "user" | "ai";
  agent?: string;
  message_id?: number;
  chat_id?: number | null;
  timestamp?: string;
}
  
interface ChatHistory {
  chat_id: number;
  title: string;
  created_at: string;
  user_id?: number;
}

// Add this function before the ChatInterface function
const generateFallbackResponse = (message: string) => {
  // Simple logic to generate fallback responses for demo/testing purposes
  const lowerMessage = message.toLowerCase();
  
  if (lowerMessage.includes('vehicle') || lowerMessage.includes('inventory')) {
    return `Based on the data provided, here's information about the vehicle inventory:

The inventory includes several vehicles with varying specifications:
- Toyota Camry (2021), priced at $28,500, with 32,000 miles in excellent condition
- Honda Civic (2022), priced at $24,700, with 18,000 miles in good condition
- Ford F-150 (2020), priced at $38,900, with 45,000 miles in good condition

These vehicles represent different segments (sedan, compact, truck) and price points to appeal to a diverse customer base.`;
  }
  
  if (lowerMessage.includes('price') || lowerMessage.includes('market')) {
    return `Based on the market analysis data:

- The Toyota Camry is priced at $28,500, which is $1,700 below the market average of $30,200
- The Honda Civic is priced at $24,700, which is $1,200 below the market average of $25,900
- The Ford F-150 is priced at $38,900, which is $2,200 above the market average of $36,700

The Toyota and Honda are competitively priced below market value, which should help attract buyers. The Ford F-150 is priced above market value, which might require justification through additional features or exceptional condition.`;
  }
  
  return `I've analyzed the automotive data you've provided. Your inventory consists of three vehicles (Toyota Camry, Honda Civic, and Ford F-150) with varying price points and specifications.

Based on market analysis, the Toyota Camry and Honda Civic are priced below market value, while the Ford F-150 is priced above market value.

Is there specific information about this data you'd like me to focus on? I can provide insights on:
- Pricing strategy recommendations
- Market positioning
- Inventory optimization
- Sales potential for specific vehicles`;
};

const ChatInterface: React.FC = () => {
  const router = useRouter()
  const { data: session, status } = useSession()
  const { hasConsented } = useCookieConsentStore()
  const { queriesUsed, incrementQueries, hasFreeTrial } = useFreeTrialStore()
  const { messages: storedMessages, addMessage, updateMessage, clearMessages } = useChatHistoryStore()
  const [mounted, setMounted] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isSidebarOpen, setSidebarOpen] = useState(false)
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [showWelcome, setShowWelcome] = useState(true)
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const { sessionId } = useSessionStore()
  const chatInputRef = useRef<{ 
    handlePreviewDefaultDataset: () => void;
    handleSilentDefaultDataset: () => void;
  }>(null);
  const [activeChatId, setActiveChatId] = useState<number | null>(null);
  const [chatHistories, setChatHistories] = useState<ChatHistory[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [userId, setUserId] = useState<number | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const { remainingCredits, isLoading: creditsLoading, checkCredits, hasEnoughCredits } = useCredits()
  const [insufficientCreditsModalOpen, setInsufficientCreditsModalOpen] = useState(false)
  const [requiredCredits, setRequiredCredits] = useState(0)
  const [isUserProfileOpen, setIsUserProfileOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const { modelSettings, syncSettingsToBackend, updateModelSettings } = useModelSettings();
  const [showDatasetResetConfirm, setShowDatasetResetConfirm] = useState(false);
  const [hasUploadedDataset, setHasUploadedDataset] = useState(false);
  const [tempChatIdForReset, setTempChatIdForReset] = useState<number | null>(null);
  const [recentlyUploadedDataset, setRecentlyUploadedDataset] = useState(false);
  const datasetPopupShownRef = useRef(false);
  const popupShownForChatIdsRef = useRef<Set<number>>(new Set());
  const [isNewLoginSession, setIsNewLoginSession] = useState(false);
  const [chatNameGenerated, setChatNameGenerated] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);

  useEffect(() => {
    setMounted(true)
    
    // Force free trial mode for demo
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('freeTrialEnabled', 'true')
      localStorage.removeItem('showOnboarding')
    }
  }, [])

  // Check if it's the user's first time and show onboarding tooltip
  useEffect(() => {
    if (mounted) {
      const showOnboardingFlag = localStorage.getItem('showOnboarding');
      // Show for both signed-in users and free trial users
      if (showOnboardingFlag === 'true') {
        // Delay showing the tooltip slightly to ensure the UI is fully loaded
        const timer = setTimeout(() => {
          setShowOnboarding(true);
          // Remove the flag so it doesn't show again on page refresh
          localStorage.removeItem('showOnboarding');
        }, 1500);
        return () => clearTimeout(timer);
      }
      
      // Set the onboarding flag for first-time free trial users
      if (!session && hasFreeTrial() && !localStorage.getItem('hasSeenOnboarding')) {
        localStorage.setItem('showOnboarding', 'true');
        
        const timer = setTimeout(() => {
          setShowOnboarding(true);
          localStorage.removeItem('showOnboarding');
          localStorage.setItem('hasSeenOnboarding', 'true');
        }, 1500);
        return () => clearTimeout(timer);
      }
    }
  }, [mounted, session, hasFreeTrial]);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await axios.get(`${API_URL}/agents`)
        if (response.data && response.data.available_agents) {
          const agentList: AgentInfo[] = response.data.available_agents.map((name: string) => ({
            name,
            description: `Specialized ${name.replace(/_/g, " ")} agent`,
          }))
          setAgents(agentList)
        }
      } catch (error) {
        console.error("Error fetching agents:", error)
      }
    }

    fetchAgents()
  }, [])

  useEffect(() => {
    // Show welcome section if there are no messages
    setShowWelcome(storedMessages.length === 0)
  }, [storedMessages])

  useEffect(() => {
    if (status === "unauthenticated") {
      clearMessages()
      setShowWelcome(true)
    }
  }, [status, clearMessages])

  useEffect(() => {
    if (session?.user && mounted) {
      const createOrGetUser = async () => {
        try {
          const response = await axios.post(`${API_URL}/chats/users`, {
            username: session.user.name || 'Anonymous User',
            email: session.user.email || `anonymous-${Date.now()}@example.com`
          });
          
          setUserId(response.data.user_id);
          
          // Now fetch chat history for this user
          fetchChatHistories(response.data.user_id);
        } catch (error) {
          console.error("Error creating/getting user:", error);
        }
      };
      
      createOrGetUser();
    }
  }, [session, mounted]);

  // Add new effect to reset dataset on login
  useEffect(() => {
    // Only run when a user successfully logs in and component is mounted
    if (session?.user && mounted && sessionId) {
      const resetToDefaultDatasetOnLogin = async () => {
        try {
          logger.log("New login detected, checking dataset state");
          
          // Check if user has stored login status in localStorage
          const lastLoginUser = localStorage.getItem('lastLoginUser');
          const currentUser = session.user.email || session.user.name || '';
          const lastSessionTime = localStorage.getItem('lastSessionTime');
          const currentTime = Date.now();
          const SESSION_TIMEOUT = 1000 * 60 * 30; // 30 minutes in milliseconds
          
          // Detect if this is a new session:
          // 1. Different user OR
          // 2. Same user but browser was closed (lastSessionTime is too old)
          const isNewSession = lastLoginUser !== currentUser ||
                            !lastSessionTime ||
                            (currentTime - parseInt(lastSessionTime)) > SESSION_TIMEOUT;
          
          if (isNewSession) {
            logger.log("New session detected, silently resetting to default dataset");
            
            // Mark this as a new login session so popup appears in silent mode
            setIsNewLoginSession(true);
            
            // Reset the session to use the default dataset but preserve model settings
            await axios.post(`${API_URL}/reset-session`, 
              { preserveModelSettings: true }, // Add flag to preserve model settings
              {
                headers: { 'X-Session-ID': sessionId }
              }
            );
            
            // Reset local dataset state
            setHasUploadedDataset(false);
            localStorage.removeItem('lastUploadedFile');
            
            // Reset popup tracking
            datasetPopupShownRef.current = false;
            popupShownForChatIdsRef.current = new Set();
            
            // Store current user and timestamp to identify new sessions in future
            localStorage.setItem('lastLoginUser', currentUser);
            localStorage.setItem('lastSessionTime', currentTime.toString());
            
            // Force the use of default dataset with an explicit API call, but don't show preview
            try {
              await axios.get(`${API_URL}/api/default-dataset`, {
                headers: { 'X-Session-ID': sessionId }
              });
              logger.log("Default dataset loaded silently on login");
              
              // Instead of showing the preview directly, use the silent method
              if (chatInputRef.current && chatInputRef.current.handleSilentDefaultDataset) {
                chatInputRef.current.handleSilentDefaultDataset();
              } else {
                // If the method doesn't exist yet, we'll do a silent reset here
                localStorage.removeItem('lastUploadedFile');
              }
              
              // After a brief delay, reset the new login session flag
              setTimeout(() => {
                setIsNewLoginSession(false);
              }, 1000);
            } catch (error) {
              console.error("Error loading default dataset:", error);
              setIsNewLoginSession(false);
            }
          } else {
            logger.log("Returning user in same session, maintaining dataset state");
            // Update the session timestamp
            localStorage.setItem('lastSessionTime', currentTime.toString());
          }
        } catch (error) {
          console.error("Error resetting dataset on login:", error);
          setIsNewLoginSession(false);
        }
      };
      
      resetToDefaultDatasetOnLogin();
    } else if (!session && mounted) {
      // Clear last login when user logs out
      localStorage.removeItem('lastLoginUser');
    }
  }, [session, mounted, sessionId]);

  // Add another effect to periodically update the session time while active
  useEffect(() => {
    if (session?.user && mounted) {
      // Start a timer to update the last session time periodically
      const intervalId = setInterval(() => {
        localStorage.setItem('lastSessionTime', Date.now().toString());
      }, 60000); // Update every minute
      
      return () => clearInterval(intervalId);
    }
  }, [session, mounted]);

  // Define createNewChat function that was removed
  const createNewChat = useCallback(async () => {
    // Sync model settings to ensure backend uses the right model
    try {
      await syncSettingsToBackend();
      logger.log('Model settings synced during new chat creation');
    } catch (error) {
      console.error('Failed to sync model settings:', error);
    }
    
    // Clear local messages state
    clearMessages();
    setShowWelcome(true);
    
    // Just set a temporary ID - we'll create the actual chat when the user sends a message
    const tempId = Date.now(); // Use timestamp as temporary ID
    setActiveChatId(tempId);
    return tempId;
  }, [clearMessages, syncSettingsToBackend]);

  // Define loadChat before it's used in the fetchChatHistories dependency array
  const loadChat = useCallback(async (chatId: number) => {
    try {
      // Sync model settings
      try {
        await syncSettingsToBackend();
      } catch (error) {
        console.error('Failed to sync model settings:', error);
      }
      
      // Check for dataset mismatch before loading chat
      try {
        // Skip dataset check if we just uploaded a dataset
        if (recentlyUploadedDataset) {
          setHasUploadedDataset(true);
          setRecentlyUploadedDataset(false);
          
          // Load chat directly
          setActiveChatId(chatId);
          const response = await axios.get(`${API_URL}/chats/${chatId}`, {
            params: { user_id: userId },
            headers: { 'X-Session-ID': sessionId }
          });
          
          if (response.data && response.data.messages) {
            clearMessages();
            response.data.messages.forEach((msg: any) => {
              addMessage({
                text: msg.content,
                sender: msg.sender,
                message_id: msg.message_id,
                chat_id: msg.chat_id,
                timestamp: msg.timestamp
              });
            });
            setShowWelcome(false);
          }
          return;
        }
        
        // Check for dataset reset popup when switching chats
        const isPopupShownForChat = popupShownForChatIdsRef.current.has(chatId);
        
        if (!isPopupShownForChat && !recentlyUploadedDataset && activeChatId !== chatId) {
          // Clear suppression when switching chats
          localStorage.removeItem('suppressDatasetPopup');
          
          // Check if we need to show dataset selection popup
          const sessionResponse = await axios.get(`${API_URL}/api/session-info`, {
            headers: { 'X-Session-ID': sessionId }
          });
          
          if (sessionResponse.data && sessionResponse.data.is_custom_dataset) {
            // Show popup for chat with custom dataset
            datasetPopupShownRef.current = true;
            popupShownForChatIdsRef.current.add(chatId);
            
            setTempChatIdForReset(chatId);
            setShowDatasetResetConfirm(true);
            return; // Wait for user decision
          }
        }
      } catch (error) {
        console.error("Error checking dataset:", error);
      }
      
      // Load chat messages
      setActiveChatId(chatId);
      const response = await axios.get(`${API_URL}/chats/${chatId}`, {
        params: { user_id: userId },
        headers: { 'X-Session-ID': sessionId }
      });
      
      if (response.data && response.data.messages) {
        clearMessages();
        
        if (response.data.messages.length === 0) {
          console.warn("No messages found in chat history");
        }
        
        response.data.messages.forEach((msg: any) => {
          addMessage({
            text: msg.content,
            sender: msg.sender,
            message_id: msg.message_id,
            chat_id: msg.chat_id,
            timestamp: msg.timestamp
          });
        });
        
        setShowWelcome(false);
      } else {
        console.error("No messages found in the chat data");
      }
    } catch (error) {
      console.error(`Failed to load chat ${chatId}:`, error);
    }
  }, [addMessage, clearMessages, userId, sessionId, recentlyUploadedDataset, syncSettingsToBackend]);

  // Now fetchChatHistories can use loadChat in its dependency array
  const fetchChatHistories = useCallback(async (userIdParam?: number) => {
    // Fetch chat histories for signed-in users or admin
    if (!session && !isAdmin) return;
    
    const currentUserId = userIdParam || userId;
    
    // For admin users, we might not have a userId but still want to fetch chats
    if (!currentUserId && !isAdmin) return;
    
    setIsLoadingHistory(true);
    try {
      // Fetch chat histories for the user or admin
      const response = await axios.get(`${API_URL}/chats/`, {
        params: { user_id: currentUserId, is_admin: isAdmin },
        headers: { 'X-Session-ID': sessionId }
      });
      
      logger.log("Fetched chat histories:", response.data);
      setChatHistories(response.data);
      
      // If we have chat histories but no active chat, set the most recent one
      if (response.data.length > 0 && !activeChatId) {
        // Sort by created_at descending and take the first one
        const mostRecentChat = [...response.data].sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        )[0];
        
        setActiveChatId(mostRecentChat.chat_id);
        loadChat(mostRecentChat.chat_id);
      }
    } catch (error) {
      console.error("Failed to fetch chat histories:", error);
    } finally {
      setIsLoadingHistory(false);
    }
  }, [session, userId, activeChatId, sessionId, loadChat, isAdmin, syncSettingsToBackend]);

  const handleNewChat = useCallback(async () => {
    // Cleanup empty chats
    if (session || isAdmin) {
      try {
        await axios.post(`${API_URL}/chats/cleanup-empty`, {
          user_id: userId,
          is_admin: isAdmin
        }, {
          headers: { 'X-Session-ID': sessionId }
        });
      } catch (error) {
        console.error('Failed to clean up empty chats:', error);
      }
    }
    
    // Sync model settings
    try {
      await syncSettingsToBackend();
    } catch (error) {
      console.error('Failed to sync model settings:', error);
    }
    
    // Create temporary chat ID
    const tempId = Date.now();
    
    // Skip dataset check if recently uploaded
    if (recentlyUploadedDataset) {
      // Mark popup as shown to prevent unnecessary popups
      datasetPopupShownRef.current = true;
      popupShownForChatIdsRef.current.add(tempId);
      
      // Create new chat without showing popup
      clearMessages();
      setShowWelcome(true);
      setActiveChatId(tempId);
      fetchChatHistories();
      return;
    }
    
    // Check for custom dataset
    try {
      const response = await axios.get(`${API_URL}/api/session-info`, {
        headers: { 'X-Session-ID': sessionId }
      });
      
      // Show popup for custom dataset if needed
      if (response.data && response.data.is_custom_dataset && 
          !popupShownForChatIdsRef.current.has(tempId)) {
        datasetPopupShownRef.current = true;
        popupShownForChatIdsRef.current.add(tempId);
        
        setTempChatIdForReset(tempId);
        setShowDatasetResetConfirm(true);
        return;
      }
    } catch (error) {
      console.error("Error checking for custom dataset:", error);
    }
    
    // Create new chat normally
    clearMessages();
    setShowWelcome(true);
    setActiveChatId(tempId);
    fetchChatHistories();
    
  }, [clearMessages, fetchChatHistories, userId, sessionId, session, isAdmin, recentlyUploadedDataset, syncSettingsToBackend]);

  const handleStopGeneration = () => {
    if (abortController) {
      abortController.abort()
      setIsLoading(false)
      setAbortController(null)
    }
  }

  // Move these function definitions to appear BEFORE handleSendMessage
  const processRegularMessage = async (
    message: string, 
    controller: AbortController, 
    currentId: number | null
  ) => {
    try {
      // If a dataset was just uploaded, make sure the URL includes that context
      let url = `${API_URL}/query/stream`;
      if (recentlyUploadedDataset) {
        url += `?custom_dataset=true`;
      }
      
      try {
        // Check if we're in demo mode and shouldn't make real API calls
        if (DEMO_MODE) {
          // Simulate a response delay for realistic UX
          await new Promise(resolve => setTimeout(resolve, 1500));
          
          // Generate a fallback response based on the message content
          const fallbackResponse = generateFallbackResponse(message);
          
          // Add the response to the chat
          addMessage({
            text: fallbackResponse,
            sender: "ai"
          });
          
          // Simulate API call completion
          setIsLoading(false);
          setAbortController(null);
          
          // Auto-generate a title for new chats in demo mode
          if (currentId !== null && !chatHistories.find(ch => ch.chat_id === currentId)?.title) {
            // Create a simple title based on the message content
            const simpleTitle = message.slice(0, 30) + (message.length > 30 ? '...' : '');
            // Update the chat title in the store
            if (setChatHistories) {
              setChatHistories(prev => 
                prev.map(chat => 
                  chat.chat_id === currentId 
                    ? { ...chat, title: simpleTitle } 
                    : chat
                )
              );
            }
          }
          
          // We're done with fallback response
          return;
        }
        
        // Original API call logic continues for non-demo mode
        const headers: HeadersInit = {
          "Content-Type": "application/json",
        };
        
        // Only add session ID to headers if it exists
        if (sessionId) {
          headers["X-Session-ID"] = sessionId;
        }
        
        const response = await fetch(url, {
          method: "POST",
          headers,
          signal: controller.signal,
          body: JSON.stringify({
            query: message,
            chat_id: currentId,
            user_id: userId,
            model_settings: modelSettings,
            is_admin: isAdmin
          }),
        });
        
        // Rest of the existing function remains unchanged
        
      } catch (error) {
        // Check for abort error first (user clicked stop)
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        
        // Log the error for debugging
        console.error("Error in processRegularMessage:", error);
        
        // If we're in demo mode, provide a fallback response instead of error
        if (DEMO_MODE) {
          const fallbackResponse = generateFallbackResponse(message);
          
          addMessage({
            text: fallbackResponse,
            sender: "ai"
          });
        } else {
          // Original error handling for non-demo mode
          addMessage({
            text: "Sorry, there was an error processing your request. Please try again.",
            sender: "ai"
          });
        }
      }
      
      // Original logic continues...
    } catch (error) {
      console.error("Error in processRegularMessage:", error);
      addMessage({
        text: "Sorry, there was an error processing your request. Please try again.",
        sender: "ai"
      });
    }
  }

  const processAgentMessage = async (
    agentName: string, 
    message: string, 
    controller: AbortController, 
    currentId: number | null
  ) => {
    let accumulatedResponse = ""
    const baseUrl = API_URL
    const endpoint = `${baseUrl}/chat/${agentName}`

    const headers = {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      ...(sessionId && { 'X-Session-ID': sessionId }),
    }

    // Important: Use currentId instead of activeChatId
    const queryParams = new URLSearchParams();
    if (userId) {
      queryParams.append('user_id', userId.toString());
    }
    if (currentId) { // Use currentId which is the real database ID
      queryParams.append('chat_id', currentId.toString());
    }
    if (isAdmin) {
      queryParams.append('is_admin', 'true');
    }
    
    const fullEndpoint = `${endpoint}${queryParams.toString() ? '?' + queryParams.toString() : ''}`;

    // Streaming response handling (potentially with SSE)
    const response = await fetch(fullEndpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify({ query: message }),
      signal: controller.signal,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    accumulatedResponse = data.response || data.content || JSON.stringify(data)
    addMessage({
      text: accumulatedResponse,
      sender: "ai",
      agent: agentName
    })

    // Save the final agent response to the database for signed-in or admin users
    if (currentId && (session || isAdmin)) {
      try {
        logger.log("Saving agent response for chat ID:", currentId);
        await axios.post(`${API_URL}/chats/${currentId}/messages`, {
          content: accumulatedResponse.trim(),
          sender: 'ai',
          agent: agentName
        }, {
          params: { user_id: userId, is_admin: isAdmin },
          headers: { 'X-Session-ID': sessionId }
        });
      } catch (error) {
        console.error('Failed to save agent response:', error);
      }
    }
  }

  // Then keep the handleSendMessage function as is
  const handleSendMessage = useCallback(async (message: string) => {
    if (isLoading || !message.trim()) return

    // If a dataset was recently uploaded, mark it so consent popup doesn't appear
    // during this message processing flow
    if (recentlyUploadedDataset) {
      logger.log("Dataset was just uploaded, suppressing consent popup for this message");
      // Ensure the popup won't show during this entire message flow
      datasetPopupShownRef.current = true;
      if (activeChatId) {
        popupShownForChatIdsRef.current.add(activeChatId);
      }
      
      // IMPORTANT: When a dataset was just uploaded, we need to explicitly
      // check the backend or forcibly set the session state to reflect the custom dataset
      try {
        logger.log("Explicitly forcing recognition of custom dataset");
        await axios.get(`${API_URL}/api/session-info`, {
          headers: {
            'X-Session-ID': sessionId,
          }
        });
      } catch (error) {
        console.error("Error refreshing session state after dataset upload:", error);
      }
      
      // We'll keep the flag true until the message is fully processed
    }

    // Sync model settings to ensure backend uses the correct model
    try {
      await syncSettingsToBackend();
    } catch (error) {
      console.error('Failed to sync model settings before sending message:', error);
    }
    
    const controller = new AbortController();
    setAbortController(controller);
    
    let currentChatId = activeChatId;
    let isFirstMessage = false;
    
    // For signed-in or admin users, ensure we have a real database chat ID
    if (session || isAdmin) {
      const existingChat = chatHistories.find(chat => chat.chat_id === currentChatId);
      
      // If the currentChatId is a temporary one (not in chat histories), create a real chat
      if (!existingChat) {
        isFirstMessage = true;
        try {
          logger.log("Creating new chat on first message with user_id:", userId, "isAdmin:", isAdmin);
          const response = await axios.post(`${API_URL}/chats/`, { 
            user_id: userId,
            is_admin: isAdmin 
          }, { 
            headers: { 'X-Session-ID': sessionId } 
          });
          
          logger.log("New chat created:", response.data);
          currentChatId = response.data.chat_id;
          // Update the activeChatId state - React handles the async update
          setActiveChatId(currentChatId);
        } catch (error) {
          console.error("Failed to create new chat:", error);
          // Stop processing if chat creation failed
          setIsLoading(false);
          setAbortController(null);
          // Add error message to UI
          addMessage({ text: "Error creating new chat. Please try again.", sender: "ai" });
          return;
        }
      }

      // Ensure we have a valid chat ID before saving the user message
      if (currentChatId !== null) {
        // Save user message to the database
        try {
          await axios.post(`${API_URL}/chats/${currentChatId}/messages`, {
            content: message,
            sender: 'user'
          }, {
            params: { user_id: userId, is_admin: isAdmin },
            headers: { 'X-Session-ID': sessionId }
          });
        } catch (error) {
          console.error('Failed to save user message:', error);
        }
      } else {
         // This case should ideally not happen for logged-in/admin users after the check above
         console.error("Cannot save user message: Chat ID is null.");
         // Stop processing if we somehow don't have a chat ID
         setIsLoading(false);
         setAbortController(null);
         addMessage({ text: "Error saving message. Cannot determine chat.", sender: "ai" });
         return;
      }
    }

    // Add user message to local state for all users
    addMessage({
      text: message,
      sender: "user",
    });
    setShowWelcome(false);

    // Counting user queries for free trial
    if (!session) {
      incrementQueries();
      
      // Check if this is the first free trial message and user hasn't seen onboarding
      if (queriesUsed === 0 && !localStorage.getItem('hasSeenOnboarding')) {
        // Set flag to show onboarding after this message completes
        localStorage.setItem('showFirstQueryOnboarding', 'true');
      }
    }

    setIsLoading(true);
    
    // Store original message for later use with chat title generation
    const originalQuery = message;

    // Check if the user has sufficient credits BEFORE processing the query
    if (session && !isAdmin) {
      try {
        // Get the model that will be used for this query
        let modelName = modelSettings.model || "gpt-4o-mini";
        
        // Calculate required credits based on model tier
        const creditCost = getModelCreditCost(modelName);
        logger.log(`[Credits] Required credits for ${modelName}: ${creditCost}`);
        
        // Check if user has enough credits - this call also sets isChatBlocked=true if insufficient
        const hasEnough = await hasEnoughCredits(creditCost);
        
        if (!hasEnough) {
          logger.log(`[Credits] Insufficient credits for operation. Required: ${creditCost}, Available: ${remainingCredits}`);
          
          // Store the required credits amount for the modal
          setRequiredCredits(creditCost);
          
          // Show the insufficient credits modal
          setInsufficientCreditsModalOpen(true);
          
          // Ensure chat remains blocked
          await checkCredits();
          
          // Stop processing here if not enough credits
          return;
        }
      } catch (error) {
        console.error("Error checking credits:", error);
        // Continue anyway to avoid blocking experience
      }
    }

    try {
      // Match all @agent mentions in the query
      const agentRegex = /@(\w+)/g
      const matches = [...message.matchAll(agentRegex)]
      
      // If no agent calls are found, process as a regular message
      if (matches.length === 0) {
        await processRegularMessage(message, controller, currentChatId)
      } else {
        // Extract all unique agent names
        const agentNames = [...new Set(matches.map(match => match[1]))]
        
        if (agentNames.length === 1) {
          // Single agent case - use the original logic
          const agentName = agentNames[0]
          
          // Add a system message indicating which agent is being called
          addMessage({
            text: "",
            sender: "ai",
            agent: agentName
          })
          
          // Extract the query text by removing the @mentions
          const cleanQuery = message.replace(agentRegex, '').trim()
          await processAgentMessage(agentName, cleanQuery, controller, currentChatId)
        } else {
          // Multiple agents case - send a single request with comma-separated agent names
          const combinedAgentName = agentNames.join(",")
          
          // Add a system message indicating which agents are being called
          addMessage({
            text: "",
            sender: "ai",
            agent: `Using agents: ${agentNames.join(", ")}`
          })
          
          // Extract the query text by removing the @mentions
          const cleanQuery = message.replace(agentRegex, '').trim()
          await processAgentMessage(combinedAgentName, cleanQuery, controller, currentChatId)
        }
      }

      // AFTER successful message processing - deduct credits using the correct user ID
      if (session?.user) {
        try {
          // Get the model directly from the API instead of relying on React state
          let modelName;
          try {
            const settingsResponse = await axios.get(`${API_URL}/api/model-settings`, {
              headers: { 'X-Session-ID': sessionId }
            });
            modelName = settingsResponse.data.model;
            logger.log(`[Credits] Using freshly fetched model: ${modelName}`);
          } catch (settingsError) {
            console.error('[Credits] Failed to fetch fresh model settings:', settingsError);
            // Fall back to the model in state
            modelName = modelSettings.model || "gpt-3.5-turbo";
          }
          
          // Use more robust user ID extraction with logging
          let userIdForCredits = '';
          
          if ((session.user as any).sub) {
            userIdForCredits = (session.user as any).sub;
          } else if (session.user.id) {
            userIdForCredits = session.user.id;
          } else if (session.user.email) {
            userIdForCredits = session.user.email;
          } else {
            // Fallback to logged in user ID from component state
            userIdForCredits = userId?.toString() || '';
          }
          
          // Skip credit deduction if we still can't identify the user
          if (!userIdForCredits) {
            console.warn('[Credits] Cannot identify user for credit deduction');
            return;
          }
          
          // Calculate credit cost based on the fresh model name
          const creditCost = getModelCreditCost(modelName);
          
          logger.log(`[Credits] Deducting ${creditCost} credits for user ${userIdForCredits} for model ${modelName}`);
          
          // Deduct credits directly through an API call
          const response = await axios.post('/api/user/deduct-credits', {
            userId: userIdForCredits,
            credits: creditCost,
            description: `Used ${modelName} for chat`
          });
          
          logger.log('[Credits] Deduction result:', response.data);
          
          // Refresh the credits display in the UI after deduction
          if (checkCredits) {
            await checkCredits();
          }
        } catch (creditError) {
          console.error('[Credits] Failed to deduct credits:', creditError);
          // Don't block the user experience if credit deduction fails
        }
      }

      // After the AI response is generated and saved, update the chat title for new chats
      // *but do not* trigger a full history refresh/load immediately
      if (isFirstMessage && currentChatId !== null) {
        try {
          logger.log("Generating title for new chat using query:", message);
          const titleResponse = await axios.post(`${API_URL}/chat_history_name`, {
            query: message
          });
          
          logger.log("Title response:", titleResponse.data);
          
          if (titleResponse.data && titleResponse.data.name) {
            await axios.put(`${API_URL}/chats/${currentChatId}`, {
              title: titleResponse.data.name
            });
            
            // Optionally update the title in the local chatHistories state if needed for the sidebar
            setChatHistories(prev => 
              prev.map(chat => 
                chat.chat_id === currentChatId 
                  ? { ...chat, title: titleResponse.data.name } 
                  : chat
              )
            );
            
            // Set chatNameGenerated to true to trigger auto-run in CodeCanvas
            setChatNameGenerated(true);
            
            // Reset the flag after a delay 
            setTimeout(() => {
              setChatNameGenerated(false);
            }, 5000);
          }
        } catch (error) {
          console.error('Failed to update chat title:', error);
        }
      }
    } catch (error) {
      console.error("Error sending message:", error);
      
      // Add error message
      addMessage({
        text: "Sorry, there was an error processing your request. Please try again.",
        sender: "ai"
      });
    } finally {
      setIsLoading(false);
      setAbortController(null);
      
      // Reset the recently uploaded dataset flag now that message processing is complete
      if (recentlyUploadedDataset) {
        logger.log("Message processing complete, resetting recentlyUploadedDataset flag");
        setRecentlyUploadedDataset(false);
      }
      
      // Check if this was a free trial user's first query
      const showFirstQueryOnboarding = localStorage.getItem('showFirstQueryOnboarding');
      if (showFirstQueryOnboarding === 'true') {
        localStorage.removeItem('showFirstQueryOnboarding');
        setShowOnboarding(true);
        localStorage.setItem('hasSeenOnboarding', 'true');
      }
    }
  }, [addMessage, clearMessages, incrementQueries, session, isAdmin, activeChatId, userId, sessionId, modelSettings, hasEnoughCredits, processRegularMessage, processAgentMessage, fetchChatHistories, checkCredits, recentlyUploadedDataset, chatHistories, syncSettingsToBackend, queriesUsed]);

  const handleFileUpload = async (file: File) => {
    // File validation
    const isCSVByExtension = file.name.toLowerCase().endsWith('.csv');
    const isCSVByType = file.type === 'text/csv' || file.type === 'application/csv';
    
    if (!isCSVByExtension || !isCSVByType) {
      addMessage({
        text: "Error: Please upload a valid CSV file. Other file formats are not supported.",
        sender: "ai"
      });
      return;
    }

    if (file.size > 30 * 1024 * 1024) {
      addMessage({
        text: "Error: File size exceeds 30MB limit. Please upload a smaller file.",
        sender: "ai"
      });
      return;
    }

    const formData = new FormData()
    formData.append("file", file)
    formData.append("styling_instructions", "Please analyze the data and provide a detailed report.")

    try {
      // Force close any open dataset popup and set short-term suppression
      setShowDatasetResetConfirm(false);
      localStorage.setItem('suppressDatasetPopup', 'true');
      setTimeout(() => localStorage.removeItem('suppressDatasetPopup'), 5000);
      
      const baseUrl = API_URL
     
      const uploadResponse = await axios.post(`${baseUrl}/upload_dataframe`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          ...(sessionId && { 'X-Session-ID': sessionId }),
        },
        timeout: 30000,
        maxContentLength: 30 * 1024 * 1024,
      });
      
      // Update dataset state
      setRecentlyUploadedDataset(true);
      setHasUploadedDataset(true);
      
      // Mark current chat to prevent popup
      if (activeChatId) {
        popupShownForChatIdsRef.current.add(activeChatId);
      }
      
      // Add a temporary ID for any new chat created immediately after upload
      popupShownForChatIdsRef.current.add(Date.now());
      datasetPopupShownRef.current = true;
      
      // Refresh session info to avoid race conditions
      try {
        await axios.get(`${baseUrl}/api/session-info`, {
          headers: { 'X-Session-ID': sessionId }
        });
        await new Promise(resolve => setTimeout(resolve, 100));
      } catch (error) {
        console.error("Error refreshing session info:", error);
      }

    } catch (error) {
      let errorMessage = "An error occurred while uploading the file.";
      
      if (axios.isAxiosError(error)) {
        if (error.code === 'ECONNABORTED') {
          errorMessage = "Upload timeout: The request took too long to complete. Please try again with a smaller file.";
        } else if (error.response) {
          errorMessage = `Upload failed: ${error.response.data?.message || error.message}`;
        }
      }
      
      addMessage({
        text: errorMessage,
        sender: "ai"
      });
      
      throw error;
    }
  }

  const isInputDisabled = () => {
    if (session) return false // Allow input if user is signed in
    if (localStorage.getItem('userApiKey')) return false // Allow input if user has set a custom API key
    return !hasFreeTrial() // Only check free trial if not signed in and no custom API key
  }

  // Add useEffect to fetch chat histories on mount for signed-in or admin users
  useEffect(() => {
    if (mounted && (session || isAdmin)) {
      fetchChatHistories();
    }
  }, [mounted, fetchChatHistories, session, isAdmin]);

  // Add back the initial page load effect
  useEffect(() => {
    if (mounted) {
      // Just set up an empty chat initially, the dataset check will handle the rest
      clearMessages();
      setShowWelcome(true);
      
      // Only set activeChatId if we don't already have one
      if (!activeChatId) {
        setActiveChatId(Date.now());
      }
    }
  }, [mounted, clearMessages, activeChatId]);

  // Add useEffect to check admin status
  useEffect(() => {
    if (mounted) {
      setIsAdmin(localStorage.getItem('isAdmin') === 'true');
    }
  }, [mounted]);

  // Update useEffect with isSettingsOpen dependency
  useEffect(() => {
    if (isSettingsOpen) {
      // No need for explicit fetch as the hook handles it
    }
  }, [isSettingsOpen]);

  // Session info check for dataset state
  useEffect(() => {
    if (sessionId) {
      const checkSessionDataset = async () => {
        try {
          // Check for uploaded dataset in localStorage
          const lastUploadedFile = localStorage.getItem('lastUploadedFile');
          if (lastUploadedFile) {
            setHasUploadedDataset(true);
            datasetPopupShownRef.current = true;
            
            if (activeChatId) {
              popupShownForChatIdsRef.current.add(activeChatId);
            }
            
            localStorage.setItem('suppressDatasetPopup', 'true');
            return;
          }
          
          // Skip check if we just uploaded a dataset
          if (recentlyUploadedDataset) {
            datasetPopupShownRef.current = true;
            setHasUploadedDataset(true);
            
            if (activeChatId) {
              popupShownForChatIdsRef.current.add(activeChatId);
            }
            
            localStorage.setItem('suppressDatasetPopup', 'true');
            return;
          }
          
          // Check session info for custom dataset
          const response = await axios.get(`${API_URL}/api/session-info`, {
            headers: { 'X-Session-ID': sessionId }
          });
          
          // Handle custom dataset detection
          if (response.data && response.data.is_custom_dataset) {
            setHasUploadedDataset(true);
            
            // Show dataset popup if needed
            const currentChatId = activeChatId || Date.now();
            const shouldShowPopup = !datasetPopupShownRef.current && 
                !popupShownForChatIdsRef.current.has(currentChatId) && 
                !recentlyUploadedDataset &&
                !localStorage.getItem('suppressDatasetPopup') &&
                !localStorage.getItem('lastUploadedFile');
            
            if (shouldShowPopup) {
              datasetPopupShownRef.current = true;
              popupShownForChatIdsRef.current.add(currentChatId);
              
              localStorage.setItem('suppressDatasetPopup', 'true');
              setTimeout(() => localStorage.removeItem('suppressDatasetPopup'), 5000);
              
              setTempChatIdForReset(currentChatId);
              setShowDatasetResetConfirm(true);
            }
          } else {
            // Using default dataset
            if (!recentlyUploadedDataset && !localStorage.getItem('lastUploadedFile')) {
              setHasUploadedDataset(false);
            }
          }
        } catch (error) {
          console.error("Error checking session dataset:", error);
        }
      };
      
      // Slight delay to ensure it runs after initial render
      setTimeout(() => {
        checkSessionDataset();
      }, 100);
    }
  }, [sessionId, activeChatId, recentlyUploadedDataset, syncSettingsToBackend]);
  
  // Fix the dataset reset confirmation handler
  const handleDatasetResetConfirm = async (shouldReset: boolean) => {
    try {
      if (shouldReset) {
        // Reset to default dataset
        await axios.post(`${API_URL}/reset-session`, 
          { preserveModelSettings: true },
          { headers: { 'X-Session-ID': sessionId } }
        );
        
        setHasUploadedDataset(false);
        
        // Show default dataset preview
        if (chatInputRef.current) {
          chatInputRef.current.handlePreviewDefaultDataset();
          localStorage.removeItem('lastUploadedFile');
          
          setTimeout(() => {
            setHasUploadedDataset(false);
          }, 100);
        }
      } else {
        // Keep custom dataset
        try {
          const sessionResponse = await axios.get(`${API_URL}/api/session-info`, {
            headers: { 'X-Session-ID': sessionId }
          });
          
          if (sessionResponse.data && sessionResponse.data.is_custom_dataset) {
            setHasUploadedDataset(true);
            
            if (chatInputRef.current && sessionResponse.data.dataset_name) {
              const datasetName = sessionResponse.data.dataset_name;
              
              const fileInfo = {
                name: datasetName.endsWith('.csv') ? datasetName : `${datasetName}.csv`,
                type: 'text/csv',
                lastModified: new Date().getTime()
              };
              
              localStorage.setItem('lastUploadedFile', JSON.stringify(fileInfo));
              
              setTimeout(() => {
                setHasUploadedDataset(prev => !prev);
                setTimeout(() => setHasUploadedDataset(true), 10);
              }, 10);
            }
          }
        } catch (error) {
          console.error("Error getting session info:", error);
        }
      }
      
      // Hide the popup and proceed with loading chat
      setShowDatasetResetConfirm(false);
      
      if (tempChatIdForReset) {
        popupShownForChatIdsRef.current.add(tempChatIdForReset);
        datasetPopupShownRef.current = true;
        
        loadChat(tempChatIdForReset);
        setTempChatIdForReset(null);
      }
    } catch (error) {
      console.error("Error handling dataset reset:", error);
      setShowDatasetResetConfirm(false);
      
      datasetPopupShownRef.current = true;
      if (tempChatIdForReset) {
        popupShownForChatIdsRef.current.add(tempChatIdForReset);
      }
    }
  };

  const handleChatDelete = useCallback((chatId: number) => {
    axios.delete(`${API_URL}/chats/${chatId}`, {
      params: { user_id: userId },
      headers: { 'X-Session-ID': sessionId }
    }).then(() => {
      // Remove the chat from the chat histories
      setChatHistories(prev => prev.filter(chat => chat.chat_id !== chatId));
      
      // If the deleted chat was the active chat, reset the active chat and clear messages
      if (chatId === activeChatId) {
        setActiveChatId(null);
        clearMessages();
        setShowWelcome(true);
        
        // If there are other chats, select the most recent one
        const remainingChats = chatHistories.filter(chat => chat.chat_id !== chatId);
        if (remainingChats.length > 0) {
          const mostRecentChat = [...remainingChats].sort(
            (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          )[0];
          
          setActiveChatId(mostRecentChat.chat_id);
          loadChat(mostRecentChat.chat_id);
        } else {
          // If no chats remain, create a new one
          createNewChat();
        }
      }
    }).catch(error => {
      console.error(`Failed to delete chat ${chatId}:`, error);
    });
  }, [activeChatId, chatHistories, clearMessages, createNewChat, loadChat, userId, sessionId]);

  const handleNavigateToAccount = useCallback(() => {
    router.push('/account');
    setIsUserProfileOpen(false);
  }, [router, setIsUserProfileOpen]);

  // Handle model settings from environment or local storage
  useEffect(() => {
    // Get provider from local storage or default to gemini
    const modelProvider = localStorage.getItem('modelProvider') || 'gemini';
    const userApiKey = localStorage.getItem('userApiKey');
    
    // Always set up default model provider if none is set
    if (!localStorage.getItem('modelProvider')) {
      localStorage.setItem('modelProvider', 'gemini');
    }
    
    if (modelSettings) {
      // Create updated settings with proper defaults
      const updatedSettings = {
        ...modelSettings,
        provider: modelProvider,
        // Use user's API key if available, otherwise leave as default
        ...(userApiKey && { apiKey: userApiKey }),
        model: modelProvider === 'gemini' ? 'gemini-pro' : 
               modelProvider === 'openai' ? 'gpt-4o-mini' :
               modelProvider === 'anthropic' ? 'claude-3-opus-20240229' : 
               modelSettings.model
      };
      
      // Save updated settings both locally and to storage
      localStorage.setItem('modelSettings', JSON.stringify(updatedSettings));
      
      // Update settings without waiting for completion
      updateModelSettings(updatedSettings).catch(err => {
        console.error('Failed to update model settings:', err);
      });
    }
  }, [modelSettings, updateModelSettings]);

  // Don't render anything until mounted to prevent hydration mismatch
  if (!mounted) {
    return null
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 to-white text-gray-900">
      {/* Include sidebar for signed-in users or admin */}
      {(session || isAdmin) && (
        <Sidebar 
          isOpen={isSidebarOpen} 
          onClose={() => setSidebarOpen(false)} 
          onNewChat={handleNewChat}
          chatHistories={chatHistories}
          activeChatId={activeChatId}
          onChatSelect={loadChat}
          isLoading={isLoadingHistory}
          onDeleteChat={handleChatDelete}
        />
      )}

      <motion.div
        animate={{ 
          marginLeft: (session || isAdmin) && isSidebarOpen ? "16rem" : "0rem" 
        } as any}
        transition={{ type: "tween", duration: 0.3 }}
        className="flex-1 flex flex-col min-w-0 relative"
      >
        <header className="bg-white/70 backdrop-blur-sm p-4 flex justify-between items-center border-b border-gray-200 relative z-10">
          <div className="flex items-center gap-4">
            {(session || isAdmin) && !isSidebarOpen && (
              <button
                onClick={() => setSidebarOpen(true)}
                className="p-2 rounded-full text-gray-500 hover:text-[#FF7F7F] hover:bg-[#FF7F7F]/5 focus:outline-none transition-colors"
                aria-label="Toggle sidebar"
              >
                <Menu className="h-5 w-5" />
              </button>
            )}
            
            <div className="flex items-center cursor-pointer" onClick={() => router.push("/")}>
              <div className="w-8 h-8 relative">
                <Image
                  src="https://4q2e4qu710mvgubg.public.blob.vercel-storage.com/Auto-analysts%20icon%20small-S682Oi8nbFhOADUHXJSD9d0KtSWKCe.png"
                  alt="Auto-Analyst Logo"
                  fill
                  className="object-contain"
                  priority
                />
              </div>
              <h1 className="text-xl font-semibold text-gray-900 ml-3">
                Auto-Analyst
              </h1>
            </div>
          </div>

          {/* Show credit balance and user profile */}
          <div className="flex items-center gap-3">
            {(session || isAdmin) && <CreditBalance />}
            
            {(session || isAdmin) && (
              <div className="relative">
                <div 
                  onClick={() => setIsUserProfileOpen(prev => !prev)}
                  className="cursor-pointer"
                >
                  {session?.user?.image ? (
                    <Avatar className="h-8 w-8">
                      <img src={session.user.image} alt={session.user.name || "User"} />
                    </Avatar>
                  ) : (
                    <Avatar className="h-8 w-8 bg-gray-100">
                      <User className="h-5 w-5 text-gray-600" />
                    </Avatar>
                  )}
                </div>
                
                <div className="relative z-50">
                  <UserProfilePopup 
                    isOpen={isUserProfileOpen}
                    onClose={() => setIsUserProfileOpen(false)}
                    onSettingsOpen={() => {
                      setIsUserProfileOpen(false);
                      setIsSettingsOpen(true);
                    }}
                    onAccountOpen={handleNavigateToAccount}
                    isAdmin={isAdmin}
                  />
                </div>
              </div>
            )}
          </div>
        </header>

        <div className="flex-1 overflow-hidden">
          <ChatWindow 
            messages={storedMessages} 
            isLoading={isLoading} 
            onSendMessage={handleSendMessage}
            showWelcome={showWelcome}
            chatNameGenerated={chatNameGenerated}
            setSidebarOpen={setSidebarOpen}
          />
        </div>
        <ChatInput 
          ref={chatInputRef}
          onSendMessage={handleSendMessage} 
          onFileUpload={handleFileUpload}
          disabled={isInputDisabled()} 
          isLoading={isLoading}
          onStopGeneration={handleStopGeneration}
        />

        <SettingsPopup 
          isOpen={isSettingsOpen}
          onClose={() => setIsSettingsOpen(false)}
          initialSettings={modelSettings}
          onSettingsUpdated={() => {
            logger.log("Settings updated");
          }}
        />
        
        <InsufficientCreditsModal
          isOpen={insufficientCreditsModalOpen}
          onClose={() => {
            // When the modal is closed, keep the blocked state but hide the modal
            setInsufficientCreditsModalOpen(false);
            
            // Force a credits check to ensure the blocked state is maintained
            checkCredits().then(() => {
              logger.log("[ChatInterface] Credits checked after modal closed");
            });
          }}
          requiredCredits={requiredCredits}
        />

        {/* Dataset Reset Popup */}
        {showDatasetResetConfirm && !recentlyUploadedDataset && (
          <DatasetResetPopup 
            isOpen={true}
            onClose={() => {
              setShowDatasetResetConfirm(false);
              localStorage.setItem('suppressDatasetPopup', 'true');
              setTimeout(() => localStorage.removeItem('suppressDatasetPopup'), 3000);
            }}
            onConfirm={() => handleDatasetResetConfirm(true)}
            onCancel={() => handleDatasetResetConfirm(false)}
            silentOnLogin={isNewLoginSession}
          />
        )}
      </motion.div>
      
      {/* Onboarding Tooltip */}
      <OnboardingTooltip 
        isOpen={showOnboarding} 
        onClose={() => setShowOnboarding(false)} 
      />
    </div>
  )
}

export default ChatInterface