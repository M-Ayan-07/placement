"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Clock,
  HelpCircle,
  ArrowRight,
  Calculator,
  Brain,
  BookOpen,
  Code2,
  Cpu,
  History,
  CheckCircle2,
} from "lucide-react";

interface SubcategoryInfo {
  name: string;
  category: string;
  question_count: number;
  duration_minutes: number;
  description: string;
}

interface CategoriesData {
  categories: {
    aptitude: SubcategoryInfo[];
    technical: SubcategoryInfo[];
  };
}

interface HistoryItem {
  session_id: string;
  category: string;
  subcategory: string;
  score: number;
  max_score: number;
  percentage: number;
  time_taken_seconds: number;
  completed_at: string;
  status: string;
}

export default function AssessmentsPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<"aptitude" | "technical" | "history">("technical");
  const [categoriesData, setCategoriesData] = useState<CategoriesData | null>(null);
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [startingSubcat, setStartingSubcat] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        const catRes = await api.get<CategoriesData>("/assessments/categories");
        setCategoriesData(catRes);
        const histRes = await api.get<HistoryItem[]>("/assessments/history");
        setHistoryItems(histRes);
      } catch (err) {
        console.error("Failed to load assessments:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  const handleStartSession = async (category: string, subcategory: string) => {
    setStartingSubcat(subcategory);
    try {
      const res = await api.post<{ session_id: string }>("/assessments/sessions/start", {
        category,
        subcategory,
        num_questions: 10,
      });
      router.push(`/assessments/${res.session_id}/session`);
    } catch (err) {
      console.error("Failed to start session:", err);
      setStartingSubcat(null);
    }
  };

  const getSubcatKey = (name: string): string => {
    const map: Record<string, string> = {
      "Quantitative Aptitude": "quantitative",
      "Logical Reasoning": "logical",
      "Verbal Ability": "verbal",
      "Data Structures & Algorithms": "dsa",
      "CS Core Fundamentals": "cs_fundamentals",
    };
    return map[name] || "dsa";
  };

  const getSubcatIcon = (name: string) => {
    switch (name) {
      case "Quantitative Aptitude":
        return <Calculator className="h-5 w-5 text-indigo-600" />;
      case "Logical Reasoning":
        return <Brain className="h-5 w-5 text-indigo-600" />;
      case "Verbal Ability":
        return <BookOpen className="h-5 w-5 text-indigo-600" />;
      case "Data Structures & Algorithms":
        return <Code2 className="h-5 w-5 text-indigo-600" />;
      case "CS Core Fundamentals":
        return <Cpu className="h-5 w-5 text-indigo-600" />;
      default:
        return <HelpCircle className="h-5 w-5 text-indigo-600" />;
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">Diagnostic Assessments</h2>
        <p className="text-sm text-muted-foreground">
          Timed screening tests designed to match campus recruitment rounds and identify your weak topics.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-border space-x-4 sm:space-x-6 text-xs sm:text-sm overflow-x-auto flex-nowrap">
        <button
          onClick={() => setActiveTab("technical")}
          className={`flex items-center gap-1.5 sm:gap-2 pb-3 font-medium transition-colors border-b-2 -mb-px whitespace-nowrap ${
            activeTab === "technical"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Code2 className="h-4 w-4" />
          Technical Tests
        </button>

        <button
          onClick={() => setActiveTab("aptitude")}
          className={`flex items-center gap-1.5 sm:gap-2 pb-3 font-medium transition-colors border-b-2 -mb-px whitespace-nowrap ${
            activeTab === "aptitude"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Brain className="h-4 w-4" />
          Aptitude Screening
        </button>

        <button
          onClick={() => setActiveTab("history")}
          className={`flex items-center gap-1.5 sm:gap-2 pb-3 font-medium transition-colors border-b-2 -mb-px whitespace-nowrap ${
            activeTab === "history"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <History className="h-4 w-4" />
          Attempt History ({historyItems.length})
        </button>
      </div>

      {/* Loading Skeleton */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-44 rounded-lg border border-border bg-slate-100 animate-pulse" />
          ))}
        </div>
      )}

      {/* Technical Grid */}
      {!isLoading && activeTab === "technical" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {categoriesData?.categories.technical.map((subcat) => {
            const subcatKey = getSubcatKey(subcat.name);
            const isStarting = startingSubcat === subcatKey;
            return (
              <Card key={subcat.name} className="border-border shadow-xs hover:border-slate-300 transition-colors flex flex-col justify-between">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="p-2.5 rounded-lg bg-indigo-50 border border-indigo-100 w-fit">
                      {getSubcatIcon(subcat.name)}
                    </div>
                    <Badge variant="secondary" className="text-[11px] font-mono">
                      Technical
                    </Badge>
                  </div>
                  <CardTitle className="text-base pt-2">{subcat.name}</CardTitle>
                  <CardDescription className="text-xs line-clamp-2">{subcat.description}</CardDescription>
                </CardHeader>

                <CardContent className="pb-4">
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1.5">
                      <Clock className="h-3.5 w-3.5" />
                      <span>{subcat.duration_minutes} mins</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <HelpCircle className="h-3.5 w-3.5" />
                      <span>5 Questions per test</span>
                    </div>
                  </div>
                </CardContent>

                <CardFooter className="pt-0 border-t border-slate-100">
                  <Button
                    onClick={() => handleStartSession("technical", subcatKey)}
                    disabled={isStarting}
                    className="w-full gap-2 mt-4"
                  >
                    {isStarting ? "Starting Test..." : "Start Diagnostic Test"}
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </CardFooter>
              </Card>
            );
          })}
        </div>
      )}

      {/* Aptitude Grid */}
      {!isLoading && activeTab === "aptitude" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {categoriesData?.categories.aptitude.map((subcat) => {
            const subcatKey = getSubcatKey(subcat.name);
            const isStarting = startingSubcat === subcatKey;
            return (
              <Card key={subcat.name} className="border-border shadow-xs hover:border-slate-300 transition-colors flex flex-col justify-between">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="p-2.5 rounded-lg bg-indigo-50 border border-indigo-100 w-fit">
                      {getSubcatIcon(subcat.name)}
                    </div>
                    <Badge variant="outline" className="text-[11px] font-mono">
                      Aptitude
                    </Badge>
                  </div>
                  <CardTitle className="text-base pt-2">{subcat.name}</CardTitle>
                  <CardDescription className="text-xs line-clamp-2">{subcat.description}</CardDescription>
                </CardHeader>

                <CardContent className="pb-4">
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1.5">
                      <Clock className="h-3.5 w-3.5" />
                      <span>{subcat.duration_minutes} mins</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <HelpCircle className="h-3.5 w-3.5" />
                      <span>5 Questions per test</span>
                    </div>
                  </div>
                </CardContent>

                <CardFooter className="pt-0 border-t border-slate-100">
                  <Button
                    onClick={() => handleStartSession("aptitude", subcatKey)}
                    disabled={isStarting}
                    className="w-full gap-2 mt-4"
                  >
                    {isStarting ? "Starting Test..." : "Start Diagnostic Test"}
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </CardFooter>
              </Card>
            );
          })}
        </div>
      )}

      {/* History Tab */}
      {!isLoading && activeTab === "history" && (
        <Card className="border-border shadow-xs">
          <CardHeader>
            <CardTitle className="text-base">Your Assessment Attempts</CardTitle>
            <CardDescription>Review scores and diagnostic feedback from past practice sessions.</CardDescription>
          </CardHeader>
          <CardContent>
            {historyItems.length === 0 ? (
              <div className="text-center py-10 space-y-2">
                <History className="h-8 w-8 text-muted-foreground mx-auto" />
                <p className="text-sm font-medium text-slate-800">No assessments taken yet</p>
                <p className="text-xs text-muted-foreground">
                  Take a 15-minute diagnostic test to establish your baseline readiness score.
                </p>
              </div>
            ) : (
              <div className="divide-y divide-border">
                {historyItems.map((item) => (
                  <div key={item.session_id} className="py-3.5 flex items-center justify-between">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-slate-900 capitalize">
                          {item.subcategory.replace("_", " ")}
                        </span>
                        <Badge
                          variant={item.percentage >= 70 ? "success" : item.percentage >= 40 ? "warning" : "destructive"}
                          className="text-[10px]"
                        >
                          {item.score} / {item.max_score} ({item.percentage}%)
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {item.completed_at ? new Date(item.completed_at).toLocaleDateString() : "In progress"} • Duration: {Math.round(item.time_taken_seconds)}s
                      </p>
                    </div>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => router.push(`/assessments/${item.session_id}/results`)}
                      className="text-xs"
                    >
                      View Report
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

