"use client";

import React, { useState, useEffect, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bot, User, Send, Plus, Sparkles, MessageSquare, AlertCircle, List, ArrowLeft } from "lucide-react";
import { ChatSession, ChatMessage } from "@/types";

const QUICK_PROMPTS = [
  "What are the top 5 high-frequency DSA patterns for campus placements?",
  "How should I structure my answer to 'Tell me about yourself'?",
  "Explain the difference between SQL and NoSQL for system design rounds.",
  "Give me an example of answering a behavioral question using the STAR method.",
];

export default function ChatPage() {
  const queryClient = useQueryClient();
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [inputMessage, setInputMessage] = useState("");
  const [showMobileList, setShowMobileList] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 1. Fetch user's chat sessions
  const { data: sessions = [], isLoading: isLoadingSessions } = useQuery<ChatSession[]>({
    queryKey: ["chat-sessions"],
    queryFn: async () => {
      return api.get<ChatSession[]>("/chat/sessions");
    },
  });

  // Set default selected session once loaded
  useEffect(() => {
    if (sessions.length > 0 && !selectedSessionId) {
      setSelectedSessionId(sessions[0].id);
    }
  }, [sessions, selectedSessionId]);

  // 2. Fetch active session details
  const { data: activeSession, isLoading: isLoadingSession } = useQuery<ChatSession>({
    queryKey: ["chat-session", selectedSessionId],
    queryFn: async () => {
      if (!selectedSessionId) throw new Error("No session selected");
      return api.get<ChatSession>(`/chat/sessions/${selectedSessionId}`);
    },
    enabled: !!selectedSessionId,
  });

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeSession?.messages]);

  // 3. Create session mutation
  const createSessionMutation = useMutation({
    mutationFn: async (title: string) => {
      return api.post<ChatSession>("/chat/sessions", { title });
    },
    onSuccess: (newSession) => {
      queryClient.invalidateQueries({ queryKey: ["chat-sessions"] });
      setSelectedSessionId(newSession.id);
      setShowMobileList(false);
    },
  });

  // 4. Send message mutation with instant optimistic UI update
  const sendMessageMutation = useMutation({
    mutationFn: async (content: string) => {
      if (!selectedSessionId) throw new Error("No active session");
      return api.post<{ user_message: ChatMessage; assistant_message: ChatMessage }>(
        `/chat/sessions/${selectedSessionId}/messages`,
        { content }
      );
    },
    onMutate: async (content: string) => {
      await queryClient.cancelQueries({ queryKey: ["chat-session", selectedSessionId] });
      const previousSession = queryClient.getQueryData<ChatSession>(["chat-session", selectedSessionId]);

      if (previousSession) {
        const optimisticUserMsg: ChatMessage = {
          id: `temp-${Date.now()}`,
          role: "user",
          content,
          created_at: new Date().toISOString(),
        };
        queryClient.setQueryData<ChatSession>(["chat-session", selectedSessionId], {
          ...previousSession,
          messages: [...previousSession.messages, optimisticUserMsg],
        });
      }
      return { previousSession };
    },
    onError: (_err, _content, context) => {
      if (context?.previousSession) {
        queryClient.setQueryData(["chat-session", selectedSessionId], context.previousSession);
      }
    },
    onSuccess: (data) => {
      queryClient.setQueryData<ChatSession>(["chat-session", selectedSessionId], (old) => {
        if (!old) return old;
        const nonOptimistic = old.messages.filter((m) => !m.id.startsWith("temp-"));
        return {
          ...old,
          messages: [...nonOptimistic, data.user_message, data.assistant_message],
        };
      });
      queryClient.invalidateQueries({ queryKey: ["chat-sessions"] });
    },
  });

  const handleSendMessage = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const text = inputMessage.trim();
    if (!text || sendMessageMutation.isPending) return;
    setInputMessage("");
    sendMessageMutation.mutate(text);
  };

  const handleQuickPrompt = (prompt: string) => {
    if (sendMessageMutation.isPending) return;
    sendMessageMutation.mutate(prompt);
  };

  const handleCreateNewSession = () => {
    createSessionMutation.mutate("New Placement Coaching Session");
  };

  return (
    <div className="flex h-[calc(100vh-8.5rem)] gap-4 sm:gap-6 relative">
      {/* Sessions Sidebar (collapsible drawer on mobile, static on md+) */}
      <div
        className={`w-full md:w-80 flex-shrink-0 flex flex-col bg-card border border-border rounded-xl overflow-hidden shadow-xs ${
          showMobileList ? "flex absolute inset-0 z-20" : "hidden md:flex"
        }`}
      >
        <div className="p-4 border-b border-border flex items-center justify-between bg-muted/30">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4 text-primary" />
            <h2 className="font-semibold text-foreground text-sm">Discussions</h2>
          </div>
          <div className="flex items-center gap-1.5">
            <Button
              size="sm"
              variant="outline"
              onClick={handleCreateNewSession}
              disabled={createSessionMutation.isPending}
              className="h-8 gap-1 text-xs"
            >
              <Plus className="h-3.5 w-3.5" /> New
            </Button>
            {showMobileList && (
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setShowMobileList(false)}
                className="md:hidden h-8 text-xs"
              >
                Close
              </Button>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          {isLoadingSessions && (
            <div className="p-4 text-xs text-muted-foreground text-center">Loading conversations...</div>
          )}

          {!isLoadingSessions && sessions.length === 0 && (
            <div className="p-6 text-center text-xs text-muted-foreground">
              <p>No chat history yet.</p>
              <Button
                size="sm"
                variant="outline"
                onClick={handleCreateNewSession}
                className="mt-3 text-xs w-full"
              >
                Start First Session
              </Button>
            </div>
          )}

          {sessions.map((s) => {
            const isSelected = s.id === selectedSessionId;
            return (
              <button
                key={s.id}
                onClick={() => {
                  setSelectedSessionId(s.id);
                  setShowMobileList(false);
                }}
                className={`w-full text-left p-3 rounded-lg text-xs transition-colors flex flex-col gap-1 border ${
                  isSelected
                    ? "bg-primary-50 dark:bg-primary/10 border-primary/30 font-medium text-foreground"
                    : "border-transparent text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                <div className="truncate font-medium">{s.title}</div>
                <div className="text-[11px] text-muted-foreground">
                  {new Date(s.started_at).toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Conversation Thread */}
      <div className="flex-1 flex flex-col bg-card border border-border rounded-xl overflow-hidden shadow-xs w-full">
        {/* Header */}
        <div className="p-3 sm:p-4 border-b border-border flex items-center justify-between bg-muted/20 gap-3">
          <div className="flex items-center gap-2.5 min-w-0">
            {/* Mobile switch conversation button */}
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowMobileList(true)}
              className="md:hidden h-8 px-2.5 text-xs gap-1 shrink-0"
              title="View all chats"
            >
              <List className="h-3.5 w-3.5" />
              <span>Chats</span>
            </Button>

            <div className="min-w-0">
              <h1 className="font-semibold text-foreground text-sm sm:text-base truncate">
                {activeSession?.title || "Placement Coach Assistant"}
              </h1>
              <p className="text-[11px] sm:text-xs text-muted-foreground truncate hidden sm:block">
                Targeted assistance for campus placements, technical questions, and interview strategy.
              </p>
            </div>
          </div>

          <Badge variant="outline" className="gap-1.5 py-1 text-foreground font-medium shrink-0 text-[11px]">
            <Sparkles className="h-3.5 w-3.5 text-blue-500" />
            <span className="hidden sm:inline">AI Coach Ready</span>
          </Badge>
        </div>

        {/* Message scroll container */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 sm:space-y-5">
          {isLoadingSession && (
            <div className="flex items-center justify-center h-full text-sm text-muted-foreground">
              Loading conversation transcript...
            </div>
          )}

          {!isLoadingSession && activeSession?.messages?.map((msg) => {
            const isUser = msg.role === "user";
            return (
              <div
                key={msg.id}
                className={`flex gap-2.5 sm:gap-3 max-w-3xl ${isUser ? "ml-auto flex-row-reverse" : "mr-auto"}`}
              >
                <div
                  className={`h-7 w-7 sm:h-8 sm:w-8 rounded-full flex items-center justify-center shrink-0 text-xs font-semibold ${
                    isUser
                      ? "bg-primary text-primary-foreground"
                      : "bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300 border border-blue-200 dark:border-blue-800"
                  }`}
                >
                  {isUser ? <User className="h-3.5 w-3.5 sm:h-4 sm:w-4" /> : <Bot className="h-3.5 w-3.5 sm:h-4 sm:w-4" />}
                </div>

                <div
                  className={`rounded-xl p-3 sm:p-4 text-xs sm:text-sm leading-relaxed ${
                    isUser
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted/50 border border-border text-foreground"
                  }`}
                >
                  <p className="whitespace-pre-line">{msg.content}</p>
                  <div
                    className={`mt-1.5 text-[10px] ${
                      isUser ? "text-primary-foreground/70 text-right" : "text-muted-foreground"
                    }`}
                  >
                    {new Date(msg.created_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </div>
                </div>
              </div>
            );
          })}

          {sendMessageMutation.isPending && (
            <div className="flex gap-2.5 sm:gap-3 max-w-2xl mr-auto">
              <div className="h-7 w-7 sm:h-8 sm:w-8 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300 border border-blue-200 dark:border-blue-800 flex items-center justify-center shrink-0">
                <Bot className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
              </div>
              <div className="rounded-xl p-3 sm:p-4 text-xs sm:text-sm bg-muted border border-border text-muted-foreground flex items-center gap-2">
                <span className="inline-block w-2 h-2 rounded-full bg-foreground/40 animate-pulse" />
                <span className="inline-block w-2 h-2 rounded-full bg-foreground/40 animate-pulse [animation-delay:0.2s]" />
                <span className="inline-block w-2 h-2 rounded-full bg-foreground/40 animate-pulse [animation-delay:0.4s]" />
                <span className="ml-1 text-xs">Formulating coaching guidance...</span>
              </div>
            </div>
          )}

          {sendMessageMutation.isError && (
            <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-xs flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>Failed to send message. Please verify your connection or try again.</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick prompt suggestions (shown if session has few messages) */}
        {activeSession && activeSession.messages.length <= 2 && (
          <div className="px-4 sm:px-6 pb-3 pt-1 border-t border-border bg-muted/20">
            <p className="text-[11px] font-medium text-muted-foreground mb-1.5">Recommended placement prompts:</p>
            <div className="flex flex-wrap gap-1.5 sm:gap-2">
              {QUICK_PROMPTS.map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => handleQuickPrompt(prompt)}
                  disabled={sendMessageMutation.isPending}
                  className="text-[11px] sm:text-xs bg-card border border-border hover:bg-muted text-foreground px-2.5 py-1 sm:py-1.5 rounded-md transition-colors text-left"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Chat input box */}
        <form onSubmit={handleSendMessage} className="p-3 sm:p-4 border-t border-border bg-card flex gap-2 sm:gap-3">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask about placement preparation, algorithms, resume tips..."
            disabled={sendMessageMutation.isPending || !selectedSessionId}
            className="flex-1 rounded-lg border border-border bg-background px-3 sm:px-4 py-2 sm:py-2.5 text-xs sm:text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
          />
          <Button
            type="submit"
            disabled={sendMessageMutation.isPending || !inputMessage.trim() || !selectedSessionId}
            className="gap-1.5 px-3.5 sm:px-5 h-9 sm:h-10 text-xs sm:text-sm shrink-0"
          >
            <Send className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
            <span className="hidden sm:inline">Send</span>
          </Button>
        </form>
      </div>
    </div>
  );
}
