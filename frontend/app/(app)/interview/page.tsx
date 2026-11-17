"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Code,
  Users,
  Database,
  Layers,
  ArrowRight,
  Clock,
  CheckCircle2,
  HelpCircle,
  PlayCircle,
  FileText,
} from "lucide-react";
import { InterviewSession } from "@/types";

interface InterviewPack {
  type: "technical" | "hr";
  topic: string;
  categoryName: string;
  description: string;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  estimatedMinutes: number;
  icon: React.ReactNode;
}

const INTERVIEW_PACKS: InterviewPack[] = [
  {
    type: "technical",
    topic: "Data Structures & Algorithms",
    categoryName: "Core Algorithms & Complexity",
    description: "Multi-turn deep dive covering hash tables, graph traversals, and dynamic programming.",
    difficulty: "Intermediate",
    estimatedMinutes: 15,
    icon: <Code className="h-5 w-5 text-blue-600" />,
  },
  {
    type: "technical",
    topic: "System Design",
    categoryName: "Architecture & Scalability",
    description: "Evaluates horizontal scaling, caching strategies, load balancing, and storage schemas.",
    difficulty: "Advanced",
    estimatedMinutes: 20,
    icon: <Layers className="h-5 w-5 text-indigo-600" />,
  },
  {
    type: "technical",
    topic: "Database Management",
    categoryName: "DBMS & SQL Query Optimization",
    description: "Focuses on ACID properties, B-Tree indexing trade-offs, and complex joins.",
    difficulty: "Intermediate",
    estimatedMinutes: 15,
    icon: <Database className="h-5 w-5 text-emerald-600" />,
  },
  {
    type: "technical",
    topic: "Computer Networks & OS",
    categoryName: "CS Core Fundamentals",
    description: "Tests your comprehension of IPC, TCP/UDP protocols, DNS resolution, and virtual memory.",
    difficulty: "Intermediate",
    estimatedMinutes: 15,
    icon: <Code className="h-5 w-5 text-purple-600" />,
  },
  {
    type: "hr",
    topic: "Behavioral",
    categoryName: "STAR Method & Teamwork",
    description: "Practice answering situational conflict, technical roadblock, and leadership questions.",
    difficulty: "Beginner",
    estimatedMinutes: 12,
    icon: <Users className="h-5 w-5 text-amber-600" />,
  },
  {
    type: "hr",
    topic: "Situational",
    categoryName: "Workplace Adaptability",
    description: "Simulates high-pressure deadlines, rapid unlearned tech stacks, and priority conflicts.",
    difficulty: "Intermediate",
    estimatedMinutes: 12,
    icon: <HelpCircle className="h-5 w-5 text-rose-600" />,
  },
];

export default function InterviewCatalogPage() {
  const router = useRouter();
  const [selectedTab, setSelectedTab] = useState<"all" | "technical" | "hr">("all");

  // Fetch past interview sessions
  const { data: history = [], isLoading: isLoadingHistory } = useQuery<InterviewSession[]>({
    queryKey: ["interview-history"],
    queryFn: async () => {
      return api.get<InterviewSession[]>("/interview/history");
    },
  });

  // Start interview mutation
  const startMutation = useMutation({
    mutationFn: async (payload: { interview_type: string; topic: string }) => {
      return api.post<InterviewSession>("/interview/start", payload);
    },
    onSuccess: (session) => {
      router.push(`/interview/${session.id}`);
    },
  });

  const filteredPacks = INTERVIEW_PACKS.filter((pack) => {
    if (selectedTab === "all") return true;
    return pack.type === selectedTab;
  });

  return (
    <div className="space-y-10">
      {/* Hero Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Mock Interview Practice</h1>
        <p className="mt-1 text-sm text-slate-600">
          Simulate realistic multi-turn technical and behavioral placement rounds with AI-powered instant feedback,
          strengths analysis, and exemplary model answers.
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 border-b border-border pb-3 overflow-x-auto flex-nowrap sm:flex-wrap">
        <button
          onClick={() => setSelectedTab("all")}
          className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium whitespace-nowrap transition-colors ${
            selectedTab === "all"
              ? "bg-primary text-primary-foreground font-semibold"
              : "bg-transparent text-muted-foreground hover:text-foreground hover:bg-muted"
          }`}
        >
          All Practice Packs ({INTERVIEW_PACKS.length})
        </button>
        <button
          onClick={() => setSelectedTab("technical")}
          className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium whitespace-nowrap transition-colors ${
            selectedTab === "technical"
              ? "bg-primary text-primary-foreground font-semibold"
              : "bg-transparent text-muted-foreground hover:text-foreground hover:bg-muted"
          }`}
        >
          Technical Rounds
        </button>
        <button
          onClick={() => setSelectedTab("hr")}
          className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium whitespace-nowrap transition-colors ${
            selectedTab === "hr"
              ? "bg-primary text-primary-foreground font-semibold"
              : "bg-transparent text-muted-foreground hover:text-foreground hover:bg-muted"
          }`}
        >
          HR & Behavioral
        </button>
      </div>

      {/* Interview Packs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPacks.map((pack, idx) => (
          <Card key={idx} className="flex flex-col justify-between hover:border-slate-300 transition-colors">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between mb-2">
                <div className="p-2.5 rounded-lg bg-slate-100">{pack.icon}</div>
                <div className="flex gap-1.5">
                  <Badge variant="outline" className="text-xs capitalize">
                    {pack.type}
                  </Badge>
                  <Badge variant="secondary" className="text-xs">
                    {pack.difficulty}
                  </Badge>
                </div>
              </div>
              <CardTitle className="text-base text-slate-900">{pack.topic}</CardTitle>
              <div className="text-xs font-medium text-slate-500">{pack.categoryName}</div>
              <CardDescription className="text-xs text-slate-600 leading-relaxed mt-2">
                {pack.description}
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-2">
              <div className="flex items-center justify-between text-xs text-slate-500 mb-4 pt-3 border-t border-slate-100">
                <span className="flex items-center gap-1.5">
                  <Clock className="h-3.5 w-3.5" /> ~{pack.estimatedMinutes} mins
                </span>
                <span>10 In-Depth Questions</span>
              </div>
              <Button
                className="w-full gap-2 text-xs"
                disabled={startMutation.isPending}
                onClick={() =>
                  startMutation.mutate({
                    interview_type: pack.type,
                    topic: pack.topic,
                  })
                }
              >
                <PlayCircle className="h-4 w-4" />
                Start Mock Interview
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Past Mock Interviews Attempt History */}
      <div className="pt-4 space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">Your Interview History</h2>
        {isLoadingHistory ? (
          <div className="p-8 text-center text-sm text-slate-500 bg-white border border-slate-200 rounded-xl">
            Loading previous interview records...
          </div>
        ) : history.length === 0 ? (
          <div className="p-8 text-center text-sm text-slate-500 bg-white border border-slate-200 rounded-xl">
            You have not completed any mock interviews yet. Pick any module above to simulate your first interview round!
          </div>
        ) : (
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs divide-y divide-slate-100">
            {history.map((item) => (
              <div key={item.id} className="p-4 flex items-center justify-between hover:bg-slate-50/50 transition-colors">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-slate-900 text-sm">{item.topic}</span>
                    <Badge variant="outline" className="text-[11px] uppercase tracking-wider">
                      {item.interview_type}
                    </Badge>
                    <Badge
                      variant={item.status === "completed" ? "default" : "secondary"}
                      className="text-[11px]"
                    >
                      {item.status === "completed" ? "Completed" : "In Progress"}
                    </Badge>
                  </div>
                  <div className="text-xs text-slate-500">
                    Started on{" "}
                    {new Date(item.started_at).toLocaleDateString(undefined, {
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  {item.score !== null && (
                    <div className="text-right">
                      <div className="text-sm font-bold text-slate-900">{item.score}%</div>
                      <div className="text-[10px] text-slate-500">Score</div>
                    </div>
                  )}

                  {item.status === "completed" ? (
                    <Button
                      variant="outline"
                      size="sm"
                      className="gap-1.5 text-xs"
                      onClick={() => router.push(`/interview/${item.id}/report`)}
                    >
                      <FileText className="h-3.5 w-3.5" /> View Report
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      className="gap-1.5 text-xs"
                      onClick={() => router.push(`/interview/${item.id}`)}
                    >
                      Resume <ArrowRight className="h-3.5 w-3.5" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

