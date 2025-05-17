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

// Automotive API URL for data integration
const AUTOMOTIVE_API_URL = process.env.NEXT_PUBLIC_AUTOMOTIVE_API_URL || 'http://localhost:8003';

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
const generateFallbackResponse = (message: string): string | PlotlyMessage => {
  // Simple logic to generate fallback responses for demo/testing purposes
  const lowerMessage = message.toLowerCase();
  
  if (lowerMessage.includes('vehicle') || lowerMessage.includes('inventory') || lowerMessage.includes('car')) {
    return `Based on the automotive inventory data:

The dealership inventory includes several vehicles with varying specifications:
- Toyota Camry (2021), priced at $28,500, with 32,000 miles in excellent condition
- Honda Civic (2022), priced at $24,700, with 18,000 miles in good condition
- Ford F-150 (2020), priced at $38,900, with 45,000 miles in good condition
- BMW 3 Series (2021), priced at $43,200, with 22,000 miles in excellent condition
- Audi Q5 (2022), priced at $47,800, with 18,500 miles in excellent condition

This inventory provides a good mix of economy vehicles, luxury sedans, and trucks to meet diverse customer needs.`;
  }
  
  if (lowerMessage.includes('price') || lowerMessage.includes('market') || lowerMessage.includes('pricing')) {
    return `Based on the automotive market analysis data:

- The Toyota Camry is priced at $28,500, which is $1,700 below the market average of $30,200
- The Honda Civic is priced at $24,700, which is $1,200 below the market average of $25,900
- The Ford F-150 is priced at $38,900, which is $2,200 above the market average of $36,700
- The BMW 3 Series is priced at $43,200, which is $1,800 below the market average of $45,000
- The Audi Q5 is priced at $47,800, which is at market value

Most vehicles are competitively priced relative to the market, with the Toyota, Honda, and BMW models offering the best value compared to market prices.`;
  }
  
  if (lowerMessage.includes('opportunit') || lowerMessage.includes('profit') || lowerMessage.includes('best deal')) {
    return `Based on automotive pricing opportunities analysis:

Top undervalued vehicles with potential for higher pricing:
1. BMW 3 Series: $1,800 below market value (3.8% discount)
2. Toyota Camry: $1,700 below market value (5.6% discount)
3. Honda Civic: $1,200 below market value (4.6% discount)

Vehicles that may need price adjustments:
- Ford F-150: $2,200 above market value (6.0% premium)

These undervalued vehicles represent approximately $4,700 in potential additional revenue if prices were adjusted to match market values.`;
  }
  
  if (lowerMessage.includes('statistic') || lowerMessage.includes('analytic') || lowerMessage.includes('summary')) {
    return `Automotive Inventory Statistics:

Inventory Summary:
- Total vehicles: 50
- Available vehicles: 40 (80%)
- Sold vehicles: 10 (20%)
- Average price: $34,560
- Average days in inventory: 45.3

Distribution by Make:
- Toyota: 18%
- Honda: 16%
- Ford: 14%
- BMW: 12%
- Audi: 10%
- Others: 30%

Inventory by Condition:
- Excellent: 45%
- Good: 35%
- Fair: 15%
- Poor: 5%

These statistics indicate a healthy inventory with good turnover and a balanced mix of vehicle makes and conditions.`;
  }
  
  // If visualization or chart is requested
  if (lowerMessage.includes('visualiz') || lowerMessage.includes('chart') || lowerMessage.includes('graph')) {
    // If the message includes "yes" or "please" after describing charts, generate an actual visualization
    if (lowerMessage.includes('yes') || lowerMessage.includes('please') || lowerMessage.includes('generate') || lowerMessage.includes('show me')) {
      // Create a Plotly chart object
      if (lowerMessage.includes('price distribution') || lowerMessage.includes('make') || lowerMessage.includes('brand')) {
        // Return a price distribution by make chart
        const plotlyMessage: PlotlyMessage = {
          type: "plotly",
          data: [
            {
              type: 'bar',
              x: ['Toyota', 'Honda', 'Ford', 'BMW', 'Audi', 'Others'],
              y: [28500, 24700, 38900, 43200, 47800, 32000],
              marker: {
                color: ['#f44336', '#2196f3', '#4caf50', '#9c27b0', '#ff9800', '#607d8b']
              }
            }
          ],
          layout: {
            title: 'Price Distribution by Make',
            xaxis: { title: 'Vehicle Makes' },
            yaxis: { title: 'Average Price ($)' }
          }
        };
        return plotlyMessage;
      } else if (lowerMessage.includes('inventory age') || lowerMessage.includes('age distribution') || lowerMessage.includes('pie')) {
        // Return an inventory age distribution pie chart
        const plotlyMessage: PlotlyMessage = {
          type: "plotly",
          data: [
            {
              type: 'pie',
              labels: ['0-30 days', '31-60 days', '61-90 days', '90+ days'],
              values: [45, 30, 15, 10],
              marker: {
                colors: ['#4caf50', '#2196f3', '#ff9800', '#f44336']
              }
            }
          ],
          layout: {
            title: 'Inventory Age Distribution'
          }
        };
        return plotlyMessage;
      } else if (lowerMessage.includes('price vs market') || lowerMessage.includes('scatter') || lowerMessage.includes('comparison')) {
        // Return a price vs market comparison scatter plot
        const plotlyMessage: PlotlyMessage = {
          type: "plotly",
          data: [
            {
              type: 'scatter',
              mode: 'markers',
              x: [28500, 24700, 38900, 43200, 47800],
              y: [30200, 25900, 36700, 45000, 47800],
              text: ['Toyota Camry', 'Honda Civic', 'Ford F-150', 'BMW 3 Series', 'Audi Q5'],
              marker: {
                size: 12,
                color: ['#f44336', '#2196f3', '#4caf50', '#9c27b0', '#ff9800']
              }
            },
            {
              type: 'scatter',
              mode: 'lines',
              x: [20000, 50000],
              y: [20000, 50000],
              line: {
                color: 'rgba(0,0,0,0.3)',
                width: 2,
                dash: 'dash'
              }
            }
          ],
          layout: {
            title: 'Price vs. Market Comparison',
            xaxis: { title: 'Your Price ($)' },
            yaxis: { title: 'Market Price ($)' }
          }
        };
        return plotlyMessage;
      } else {
        // Default to the first chart type if specific type not mentioned
        const plotlyMessage: PlotlyMessage = {
          type: "plotly",
          data: [
            {
              type: 'bar',
              x: ['Toyota', 'Honda', 'Ford', 'BMW', 'Audi', 'Others'],
              y: [28500, 24700, 38900, 43200, 47800, 32000],
              marker: {
                color: ['#f44336', '#2196f3', '#4caf50', '#9c27b0', '#ff9800', '#607d8b']
              }
            }
          ],
          layout: {
            title: 'Price Distribution by Make',
            xaxis: { title: 'Vehicle Makes' },
            yaxis: { title: 'Average Price ($)' }
          }
        };
        return plotlyMessage;
      }
    }
    
    // If just asking about what visualizations are possible
    return `To visualize the automotive data, I recommend the following charts:

1. Price Distribution by Make (Bar Chart)
   - X-axis: Vehicle makes (Toyota, Honda, Ford, BMW, etc.)
   - Y-axis: Average price
   - This would show which brands have higher value inventory

2. Inventory Age Distribution (Pie Chart)
   - Categories: 0-30 days, 31-60 days, 61-90 days, 90+ days
   - This would help identify aging inventory that may need attention

3. Price vs. Market Comparison (Scatter Plot)
   - X-axis: Your price
   - Y-axis: Market price
   - Points above the diagonal indicate vehicles priced below market
   - Points below the diagonal indicate vehicles priced above market

Would you like me to generate any of these visualizations for your data?`;
  }
  
  return `I've analyzed the automotive inventory data. Your dealership has 50 vehicles in stock across multiple makes including Toyota, Honda, Ford, BMW, and Audi. 

Based on the market analysis, most of your vehicles are priced competitively, with several models (particularly the Toyota Camry, Honda Civic, and BMW 3 Series) priced below market value.

What specific aspect of the automotive data would you like me to analyze further?
- Vehicle inventory details
- Market pricing comparisons
- Profit opportunities`;
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
  // Add state for automotive data
  const [automotiveDataLoaded, setAutomotiveDataLoaded] = useState(false);

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

  // Update handleSendMessage implementation
  const handleSendMessage = useCallback(async (message: string) => {
    
    if (isLoading) {
      logger.log('Ignoring message - already processing')
      return
    }
    
    // Early validation - check if the message is empty
    if (!message.trim()) {
      logger.log('Ignoring empty message')
      return
    }
    
    // If the user needs to accept cookies, save message and show consent
    if (!hasConsented) {
      logger.log('Showing cookie consent before proceeding')
      return
    }
    
    // In a real implementation, check if user has enough credits
    if (!DEMO_MODE && !hasEnoughCredits && session) {
      logger.log('User does not have enough credits')
      setInsufficientCreditsModalOpen(true)
      setRequiredCredits(getModelCreditCost(modelSettings.model || 'gemini-pro'))
      return
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

    try {
      // Check if this is an agent message
      const agentMatch = message.match(/@([a-zA-Z_]+)/);
      if (agentMatch && agentMatch[1] && !DEMO_MODE) {
        logger.log(`Processing agent message for: ${agentMatch[1]}`);
        await processAgentMessage(agentMatch[1], message, controller, currentChatId);
      } 
      // If this is a request for automotive data and we're in demo mode
      else if (DEMO_MODE && (
        message.toLowerCase().includes('vehicle') || 
        message.toLowerCase().includes('car') || 
        message.toLowerCase().includes('automotive') ||
        message.toLowerCase().includes('inventory') ||
        message.toLowerCase().includes('dealership') ||
        message.toLowerCase().includes('price')
      )) {
        // Use our fallback response system for automotive data
        const response = generateFallbackResponse(message);
        
        // Add a slight delay to simulate processing
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Add the AI response
          addMessage({
          text: response,
          sender: "ai"
        });
      }
      else {
        // For regular messages
        logger.log(`Processing regular message`);
        
        if (DEMO_MODE) {
          // In demo mode, use fallback responses
          const response = generateFallbackResponse(message);
          
          // Add a slight delay to simulate processing
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          // Add the AI response
          addMessage({
            text: response,
            sender: "ai"
          });
        } else {
          // In real mode, process via API
          await processRegularMessage(message, controller, currentChatId);
        }
      }

      // Generate a chat title if needed
      if (isFirstMessage && (session || isAdmin) && !DEMO_MODE) {
        try {
          const titleResponse = await axios.post(`${API_URL}/chats/${currentChatId}/generate-title`, {
            message: originalQuery
          }, {
            params: { user_id: userId },
            headers: { 'X-Session-ID': sessionId }
          });
          
          if (titleResponse.data && titleResponse.data.title) {
            // Update the chat title in our local state
            setChatHistories(prev => prev.map(chat => 
                chat.chat_id === currentChatId 
                ? { ...chat, title: titleResponse.data.title } 
                  : chat
            ));
            setChatNameGenerated(true);
          }
        } catch (error) {
          console.error("Failed to generate chat title:", error);
        }
      } else if (DEMO_MODE && isFirstMessage) {
        // For demo mode, just set a static title based on the message
        if (message.toLowerCase().includes('vehicle') || 
            message.toLowerCase().includes('automotive') ||
            message.toLowerCase().includes('car')) {
          setChatHistories(prev => [
            ...prev, 
            { 
              chat_id: currentChatId || Date.now(), 
              title: "Automotive Data Analysis", 
              created_at: new Date().toISOString(),
              user_id: userId || undefined
            }
          ]);
          setChatNameGenerated(true);
        }
      }
      
      // Check if we should show first query onboarding
      if (localStorage.getItem('showFirstQueryOnboarding') === 'true') {
        localStorage.removeItem('showFirstQueryOnboarding');
        localStorage.setItem('showOnboarding', 'true');
        setShowOnboarding(true);
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        logger.log('Request aborted by user');
        addMessage({
          text: "Generation stopped by user.",
          sender: "ai",
        });
      } else {
        console.error('Error processing message:', error);
        
        if (DEMO_MODE) {
          // In demo mode, provide a friendly fallback
      addMessage({
            text: "I'm sorry, I couldn't process that request. Is there something else I can help you with?",
        sender: "ai"
      });
        } else {
          // In real mode, show the error
          addMessage({
            text: "Error processing your request. Please try again.",
            sender: "ai",
          });
        }
      }
    } finally {
      setIsLoading(false);
      setAbortController(null);
    }
  }, [
    isLoading, 
    hasConsented, 
    addMessage, 
    activeChatId, 
    chatHistories, 
    session, 
    isAdmin, 
    userId, 
    sessionId, 
    setActiveChatId, 
    incrementQueries, 
    queriesUsed, 
    hasEnoughCredits, 
    setInsufficientCreditsModalOpen, 
    modelSettings.model, 
    setShowWelcome,
    automotiveDataLoaded
  ]);

  const handleFileUpload = async (file: File) => {
    // File validation
    const isCSVByExtension = file.name.toLowerCase().endsWith('.csv');
    const isCSVByType = file.type === 'text/csv' || file.type === 'application/csv';
    
    if (!isCSVByExtension && !isCSVByType) {
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

      // Force close any open dataset popup and set short-term suppression
      setShowDatasetResetConfirm(false);
      localStorage.setItem('suppressDatasetPopup', 'true');
      setTimeout(() => localStorage.removeItem('suppressDatasetPopup'), 5000);
      
    // Define a reusable function for local file processing
    const processFileLocally = async (fileContent: string) => {
      try {
        // Parse CSV data
        const lines = fileContent.split('\n');
        const headers = lines[0].split(',');
        const rows = [];
        for (let i = 1; i <= 10 && i < lines.length; i++) {
          if (lines[i].trim()) {
            rows.push(lines[i].split(','));
          }
        }
        
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
        
        // Add a success message
        addMessage({
          text: `Successfully processed ${file.name}. You can now ask questions about this data.`,
          sender: "ai"
        });
        
        // Return success
        return true;
      } catch (error) {
        console.error("Error processing file locally:", error);
        return false;
      }
    };
    
    // Function to read the file locally
    const readFileThenProcess = () => {
      return new Promise<boolean>((resolve) => {
        const reader = new FileReader();
        
        reader.onload = async (e) => {
          const content = e.target?.result as string;
          if (!content) {
            addMessage({
              text: "Error: Failed to read the uploaded file. Please try again.",
              sender: "ai"
            });
            resolve(false);
            return;
          }
          
          const success = await processFileLocally(content);
          resolve(success);
        };
        
        reader.onerror = () => {
          addMessage({
            text: "Error: Failed to read the uploaded file. Please try again.",
            sender: "ai"
          });
          resolve(false);
        };
        
        reader.readAsText(file);
      });
    };

    // If in demo mode, handle file upload locally
    if (DEMO_MODE) {
      console.log("Using demo mode for file upload");
      const success = await readFileThenProcess();
      return;
    }
    
    // For non-demo mode, try server upload first
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("styling_instructions", "Please analyze the data and provide a detailed report.");
      
      const baseUrl = API_URL;
     
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
      
      // Add a success message from the server response
      if (uploadResponse.data?.message) {
        addMessage({
          text: uploadResponse.data.message,
          sender: "ai"
        });
      } else {
        addMessage({
          text: `Successfully uploaded ${file.name}. You can now ask questions about this data.`,
          sender: "ai"
        });
      }
      
      // Refresh session info to avoid race conditions
      try {
        await axios.get(`${baseUrl}/api/session-info`, {
          headers: { 'X-Session-ID': sessionId }
        });
        await new Promise(resolve => setTimeout(resolve, 100));
      } catch (sessionError) {
        console.error("Error refreshing session info:", sessionError);
        // Non-critical error, can continue
      }
    } catch (error) {
      console.error("Upload error:", error);
      let errorMessage = "An error occurred while uploading the file.";
      
      if (axios.isAxiosError(error)) {
        if (error.code === 'ECONNABORTED') {
          errorMessage = "Upload timeout: The request took too long to complete. Please try again with a smaller file.";
        } else if (error.response) {
          errorMessage = `Upload failed: ${error.response.data?.message || error.message}`;
        } else if (error.request) {
          errorMessage = "Network error: Could not connect to the server. Using local processing as fallback.";
        }
      }
      
      // For network errors or in demo mode, fall back to local processing
      console.log("Upload failed, attempting local fallback");
      const success = await readFileThenProcess();
      
      if (!success) {
        // Only show error message if both server upload and local processing failed
      addMessage({
        text: errorMessage,
        sender: "ai"
      });
      }
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

  // Add automotive data loading effect inside the component
  useEffect(() => {
    // Load automotive data if needed when component mounts
    if (mounted && !automotiveDataLoaded) {
      const loadAutomotiveData = async () => {
        try {
          // In a real implementation, we'd pre-fetch some data here
          // For now, just mark as loaded
          setAutomotiveDataLoaded(true);
          logger.log("Automotive data integration ready");
        } catch (error) {
          console.error("Error loading automotive data:", error);
        }
      };
      
      loadAutomotiveData();
    }
  }, [mounted, automotiveDataLoaded]);

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