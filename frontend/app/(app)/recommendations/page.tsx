"use client";

import React, { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Sparkles,
  Calendar,
  Clock,
  ExternalLink,
  BookOpen,
  Code2,
  Video,
  FileCode,
  RotateCcw,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";

interface StudyPhase {
  phase: string;
  topic: string;
  priority: string;
  objective: string;
  recommended_hours: number;
}

interface ResourceItem {
  title: string;
  type: string;
  url: string;
  topics: string[];
  description: string;
}

interface RecommendationData {
  id: string;
  user_id: string;
  study_plan: StudyPhase[];
  resources: ResourceItem[];
  generated_at: string;
}

export default function RecommendationsPage() {
  const [data, setData] = useState<RecommendationData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [activeFilter, setActiveFilter] = useState<string>("all");
  const [feedbackMsg, setFeedbackMsg] = useState<string | null>(null);

  const loadRecommendations = async () => {
    try {
      const res = await api.get<RecommendationData>("/recommendations/latest");
      setData(res);
    } catch (err) {
      console.error("Failed to load recommendations:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadRecommendations();
  }, []);

  const handleRegenerate = async () => {
    setIsRegenerating(true);
    setFeedbackMsg(null);
    try {
      const res = await api.post<RecommendationData>("/recommendations/generate");
      setData(res);
      setFeedbackMsg("Preparation roadmap refreshed using your latest test attempts and goals.");
      setTimeout(() => setFeedbackMsg(null), 4000);
    } catch (err) {
      console.error("Failed to regenerate:", err);
    } finally {
      setIsRegenerating(false);
    }
  };

  const filteredResources =
    data?.resources.filter((r) => {
      if (activeFilter === "all") return true;
      return r.type.toLowerCase() === activeFilter;
    }) || [];

  const getResourceIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "practice":
        return <Code2 className="h-4 w-4 text-emerald-600" />;
      case "video":
        return <Video className="h-4 w-4 text-rose-600" />;
      case "documentation":
        return <BookOpen className="h-4 w-4 text-sky-600" />;
      default:
        return <FileCode className="h-4 w-4 text-indigo-600" />;
    }
  };

  return (
    <div className="space-y-8 max-w-5xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Personalized Preparation Roadmap</h2>
          <p className="text-sm text-muted-foreground">
            Structured study schedule and curated learning resources tailored to your diagnostic weak spots and recruitment goals.
          </p>
        </div>

        <Button onClick={handleRegenerate} disabled={isRegenerating || isLoading} className="gap-2 shrink-0">
          <Sparkles className="h-4 w-4" />
          {isRegenerating ? "Generating Roadmap..." : "Refresh Roadmap"}
        </Button>
      </div>

      {feedbackMsg && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-md flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
          <span>{feedbackMsg}</span>
        </div>
      )}

      {/* Loading Skeleton */}
      {isLoading && (
        <div className="space-y-4">
          <div className="h-48 rounded-lg border border-border bg-slate-100 animate-pulse" />
          <div className="h-64 rounded-lg border border-border bg-slate-100 animate-pulse" />
        </div>
      )}

      {!isLoading && data && (
        <>
          {/* Section 1: Preparation Roadmap */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold text-slate-900 tracking-tight flex items-center gap-2">
                <Calendar className="h-4 w-4 text-primary" />
                Phased Study Schedule
              </h3>
              <span className="text-xs text-muted-foreground font-mono">
                Updated on {new Date(data.generated_at).toLocaleDateString()}
              </span>
            </div>

            <div className="space-y-3">
              {data.study_plan.map((phase, idx) => (
                <Card key={idx} className="border-border shadow-xs hover:border-slate-300 transition-colors">
                  <CardHeader className="pb-2 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 sm:gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2.5">
                        <span className="text-xs font-mono font-bold text-primary px-2 py-0.5 rounded bg-primary-50 dark:bg-primary/10">
                          {phase.phase}
                        </span>
                        <h4 className="text-sm font-semibold text-foreground">{phase.topic}</h4>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <Badge
                        variant={
                          phase.priority.toLowerCase() === "high"
                            ? "destructive"
                            : phase.priority.toLowerCase() === "medium"
                              ? "warning"
                              : "secondary"
                        }
                        className="text-[10px] font-bold capitalize "
                      >
                        {phase.priority} Priority
                      </Badge>

                      <div className="flex items-center gap-1 text-xs text-muted-foreground  bg-slate-50 px-2 py-1 rounded border border-slate-200">
                        <Clock className="h-3 w-3" />
                        <span>~{phase.recommended_hours} hrs</span>
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="pt-1">
                    <p className="text-xs text-slate-700 leading-relaxed">{phase.objective}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Section 2: Curated Learning Resources */}
          <div className="space-y-4 pt-4 border-t border-border">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <h3 className="text-base font-semibold text-slate-900 tracking-tight flex items-center gap-2">
                <BookOpen className="h-4 w-4 text-primary" />
                Curated Placement Resources ({filteredResources.length})
              </h3>

              {/* Filter Tabs */}
              <div className="flex gap-1.5 p-1 bg-slate-100 rounded-lg text-xs font-medium border border-border">
                {["all", "practice", "documentation", "video"].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveFilter(tab)}
                    className={`px-3 py-1 rounded-md capitalize transition-colors ${activeFilter === tab ? "bg-white text-slate-900 shadow-xs font-semibold" : "text-muted-foreground hover:text-slate-900"
                      }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredResources.map((res, idx) => (
                <Card key={idx} className="border-border shadow-xs hover:border-slate-300 transition-colors flex flex-col justify-between">
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <div className="p-1.5 rounded bg-slate-50 border border-slate-200">
                          {getResourceIcon(res.type)}
                        </div>
                        <CardTitle className="text-sm font-semibold leading-snug">{res.title}</CardTitle>
                      </div>
                      <Badge variant="outline" className="text-[10px] capitalize font-mono shrink-0">
                        {res.type}
                      </Badge>
                    </div>
                    <CardDescription className="text-xs pt-1.5 leading-relaxed">{res.description}</CardDescription>
                  </CardHeader>

                  <CardContent className="space-y-3 pt-2">
                    <div className="flex flex-wrap gap-1">
                      {res.topics.map((t) => (
                        <span key={t} className="text-[10px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200 font-mono">
                          {t}
                        </span>
                      ))}
                    </div>

                    <a
                      href={res.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 text-xs text-primary font-medium hover:underline pt-1"
                    >
                      <span>Open Learning Material</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

