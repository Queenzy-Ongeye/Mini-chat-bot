import { useState, useEffect } from "react";
import { useToast } from "./use-toast";

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

interface ApiStatus {
  available_topics: string[];
  message: string;
}

const API_BASE_URL = "https://mini-chat-bot-3o3u.onrender.com";

export const useChatbot = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<"connected" | "connecting" | "disconnected">("connecting");
  const [availableTopics, setAvailableTopics] = useState<string[]>([]);
  const { toast } = useToast();

  // Check API status on mount
  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        setConnectionStatus("connecting");
        const response = await fetch(API_BASE_URL);
        
        if (!response.ok) {
          throw new Error("API is not responding");
        }

        const data: ApiStatus = await response.json();
        setAvailableTopics(data.available_topics || []);
        setConnectionStatus("connected");
        
        // Add welcome message
        setMessages([
          {
            id: "welcome",
            text: `👋 Welcome to Omnivoltaic Notion RAG Chatbot!\n\nI can help you with the following topics:\n${data.available_topics.map(topic => `• ${topic}`).join('\n')}\n\nFeel free to ask me anything or click a topic to get started!`,
            isUser: false,
            timestamp: new Date(),
          },
        ]);

        toast({
          title: "Connected Successfully",
          description: "Chatbot is ready to assist you!",
        });
      } catch (error) {
        console.error("Failed to connect to API:", error);
        setConnectionStatus("disconnected");
        toast({
          title: "Connection Failed",
          description: "Unable to connect to the chatbot API. Please try again later.",
          variant: "destructive",
        });
      }
    };

    checkApiStatus();
  }, [toast]);

  const sendMessage = async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: text }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response from chatbot");
      }

      const data = await response.json();
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response || "I apologize, but I couldn't generate a response. Please try again.",
        isUser: false,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I encountered an error processing your request. Please try again.",
        isUser: false,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
      
      toast({
        title: "Error",
        description: "Failed to send message. Please check your connection.",
        variant: "destructive",
      });
    } finally {
      setIsTyping(false);
    }
  };

  const selectTopic = (topic: string) => {
    sendMessage(`Tell me about ${topic}`);
  };

  const resetChat = () => {
    setMessages([
      {
        id: "welcome",
        text: `👋 Welcome to Omnivoltaic Notion RAG Chatbot!\n\nI can help you with the following topics:\n${availableTopics.map(topic => `• ${topic}`).join('\n')}\n\nFeel free to ask me anything or click a topic to get started!`,
        isUser: false,
        timestamp: new Date(),
      },
    ]);
  };

  return {
    messages,
    isTyping,
    connectionStatus,
    availableTopics,
    sendMessage,
    selectTopic,
    resetChat,
  };
};
