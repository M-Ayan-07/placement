"use client";

import React from "react";
import Link from "next/navigation";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  CheckCircle2,
  FileText,
  Target,
  Sparkles,
  ArrowRight,
  Code,
  Users,
  Compass,
  MessageSquare,
  AlertTriangle,
  Clock,
  Briefcase,
  TrendingUp,
} from "lucide-react";
import { DashboardSummary } from "@/types";

export default function DashboardPage() {
  const router = useRouter();

  const { data: dashboard, isLoading, isError } = useQuery<DashboardSummary>({
    queryKey: ["dashboard-summary"],
    queryFn: async () => {
      return api.get<DashboardSummary>("/dashboard/summary");
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] text-slate-500 text-sm">
        Compiling your placement preparation telemetry...
      </div>
    );
  }

  if (isError || !dashboard) {
    return (
      <div className="p-8 text-center bg-white border border-slate-200 rounded-xl space-y-3">
        <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto" />
        <h2 className="text-base font-semibold text-slate-900">Telemetry Unavailable</h2>
        <p className="text-sm text-slate-500">
          Unable to fetch placement analytics. Please verify backend connectivity.
        </p>
        <Button variant="outline" onClick={() => window.location.reload()} className="text-xs">
          Reload Dashboard
        </Button>
      </div>
    );
  }

  const { readiness } = dashboard;
  const compositeScore = readiness.composite_readiness_score;

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-2 gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground">
            Welcome back, {dashboard.full_name}
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Tracking your campus recruitment readiness across technical tests, resume evaluations, and interview rounds.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            onClick={() => router.push("/assessments")}
            className="text-xs gap-1.5"
          >
            <Code className="h-3.5 w-3.5" /> Take Test
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => router.push("/chat")}
            className="text-xs gap-1.5"
          >
            <MessageSquare className="h-3.5 w-3.5" /> Ask Coach
          </Button>
        </div>
      </div>

      {/* Placement Readiness Hero Card */}
      <Card className="border-slate-300 shadow-sm bg-gradient-to-br from-slate-900 to-slate-800 text-white overflow-hidden">
        <CardContent className="pt-6 pb-6">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Badge
                  variant="outline"
                  className="bg-white/10 text-white border-white/20 text-xs font-medium"
                >
                  {readiness.readiness_level}
                </Badge>
                <span className="text-xs text-slate-400">Target Role:</span>
                <span className="text-xs font-semibold text-white">
                  {dashboard.target_role || "Role Not Selected"}
                </span>
              </div>
              <h2 className="text-xl font-bold">Overall Placement Readiness</h2>
              <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
                {compositeScore >= 80
                  ? "Outstanding! Your profile, test accuracy, and interview scores demonstrate high campus recruitment competitiveness."
                  : compositeScore >= 60
                  ? "Good progress. Focus on weak topics identified in tests and refine resume keywords to boost shortlisting odds."
                  : "Preparation in progress. Complete screening tests and a mock interview to establish your benchmark."}
              </p>
            </div>

            {/* Circular / Large Score Display */}
            <div className="flex items-center gap-6 bg-white/5 border border-white/10 p-5 rounded-2xl">
              <div className="text-center">
                <div className="text-5xl font-extrabold tracking-tight text-white">{compositeScore}%</div>
                <div className="text-[11px] uppercase tracking-wider text-slate-400 mt-1 font-medium">
                  Readiness Index
                </div>
              </div>
            </div>
          </div>

          {/* Breakdown Pillars */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-5 border-t border-white/10 text-xs">
            <div className="bg-white/5 p-3 rounded-lg border border-white/10">
              <span className="text-slate-400 block text-[11px]">Academic Profile</span>
              <span className="text-base font-bold text-white mt-0.5 block">{readiness.profile_score}%</span>
              <span className="text-[10px] text-slate-400">Weight 15%</span>
            </div>
            <div className="bg-white/5 p-3 rounded-lg border border-white/10">
              <span className="text-slate-400 block text-[11px]">Screening Tests</span>
              <span className="text-base font-bold text-white mt-0.5 block">{readiness.assessment_score}%</span>
              <span className="text-[10px] text-slate-400">Weight 35%</span>
            </div>
            <div className="bg-white/5 p-3 rounded-lg border border-white/10">
              <span className="text-slate-400 block text-[11px]">Resume ATS Score</span>
              <span className="text-base font-bold text-white mt-0.5 block">{readiness.resume_score}%</span>
              <span className="text-[10px] text-slate-400">Weight 25%</span>
            </div>
            <div className="bg-white/5 p-3 rounded-lg border border-white/10">
              <span className="text-slate-400 block text-[11px]">Mock Interviews</span>
              <span className="text-base font-bold text-white mt-0.5 block">{readiness.interview_score}%</span>
              <span className="text-[10px] text-slate-400">Weight 25%</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 4 Core KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Assessments */}
        <Card className="hover:border-slate-300 transition-colors">
          <CardContent className="pt-5">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-medium">Screening Tests</span>
              <Code className="h-4 w-4 text-blue-600" />
            </div>
            <div className="text-2xl font-bold text-slate-900">
              {dashboard.total_tests_completed}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              {dashboard.assessment_average !== null
                ? `Average accuracy: ${dashboard.assessment_average}%`
                : "No tests taken yet"}
            </p>
          </CardContent>
        </Card>

        {/* KPI 2: Resume */}
        <Card className="hover:border-slate-300 transition-colors">
          <CardContent className="pt-5">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-medium">Best Resume ATS</span>
              <FileText className="h-4 w-4 text-emerald-600" />
            </div>
            <div className="text-2xl font-bold text-slate-900">
              {dashboard.best_ats_score !== null ? `${dashboard.best_ats_score}%` : "—"}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              {dashboard.best_ats_score !== null
                ? "Scanned & analyzed"
                : "Upload resume to scan"}
            </p>
          </CardContent>
        </Card>

        {/* KPI 3: Mock Interviews */}
        <Card className="hover:border-slate-300 transition-colors">
          <CardContent className="pt-5">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-medium">Mock Interviews</span>
              <Users className="h-4 w-4 text-indigo-600" />
            </div>
            <div className="text-2xl font-bold text-slate-900">
              {dashboard.total_interviews_completed}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              {dashboard.interview_average !== null
                ? `Average score: ${dashboard.interview_average}%`
                : "Practice behavioral / tech"}
            </p>
          </CardContent>
        </Card>

        {/* KPI 4: Target Goals */}
        <Card className="hover:border-slate-300 transition-colors">
          <CardContent className="pt-5">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-medium">Placement Goal</span>
              <Target className="h-4 w-4 text-amber-600" />
            </div>
            <div className="text-2xl font-bold text-slate-900">
              {dashboard.target_ctc_lpa ? `₹${dashboard.target_ctc_lpa} LPA` : "Not set"}
            </div>
            <p className="text-xs text-slate-500 mt-1 truncate">
              {dashboard.target_companies.length > 0
                ? dashboard.target_companies.slice(0, 2).join(", ")
                : "Set target dream companies"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Weak Areas Banner (if any detected) */}
      {dashboard.weak_topics.length > 0 && (
        <div className="bg-amber-50/70 border border-amber-200/80 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold text-amber-900">
                Weak Topics Requiring Attention
              </h3>
              <p className="text-xs text-amber-800 mt-0.5">
                Identified based on incorrect test responses:{" "}
                <span className="font-semibold">{dashboard.weak_topics.join(", ")}</span>
              </p>
            </div>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={() => router.push("/recommendations")}
            className="text-xs border-amber-300 text-amber-900 hover:bg-amber-100 flex-shrink-0"
          >
            View Study Plan
          </Button>
        </div>
      )}

      {/* Quick Action Launchpad */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wider">
          Preparation Modules
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={() => router.push("/assessments")}
            className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-400 hover:bg-slate-50/50 transition-all text-left flex flex-col justify-between h-32 group shadow-2xs"
          >
            <div>
              <div className="flex items-center justify-between">
                <Code className="h-5 w-5 text-blue-600" />
                <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-slate-900 transition-colors" />
              </div>
              <h3 className="font-semibold text-slate-900 text-sm mt-3">Screening Tests</h3>
              <p className="text-xs text-slate-500 mt-0.5">Quantitative, DSA & Core CS</p>
            </div>
          </button>

          <button
            onClick={() => router.push("/resume")}
            className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-400 hover:bg-slate-50/50 transition-all text-left flex flex-col justify-between h-32 group shadow-2xs"
          >
            <div>
              <div className="flex items-center justify-between">
                <FileText className="h-5 w-5 text-emerald-600" />
                <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-slate-900 transition-colors" />
              </div>
              <h3 className="font-semibold text-slate-900 text-sm mt-3">Resume Scanner</h3>
              <p className="text-xs text-slate-500 mt-0.5">ATS role match & suggestions</p>
            </div>
          </button>

          <button
            onClick={() => router.push("/interview")}
            className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-400 hover:bg-slate-50/50 transition-all text-left flex flex-col justify-between h-32 group shadow-2xs"
          >
            <div>
              <div className="flex items-center justify-between">
                <Users className="h-5 w-5 text-indigo-600" />
                <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-slate-900 transition-colors" />
              </div>
              <h3 className="font-semibold text-slate-900 text-sm mt-3">Mock Interviews</h3>
              <p className="text-xs text-slate-500 mt-0.5">Technical & HR behavioral practice</p>
            </div>
          </button>

          <button
            onClick={() => router.push("/recommendations")}
            className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-400 hover:bg-slate-50/50 transition-all text-left flex flex-col justify-between h-32 group shadow-2xs"
          >
            <div>
              <div className="flex items-center justify-between">
                <Compass className="h-5 w-5 text-purple-600" />
                <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-slate-900 transition-colors" />
              </div>
              <h3 className="font-semibold text-slate-900 text-sm mt-3">Study Roadmap</h3>
              <p className="text-xs text-slate-500 mt-0.5">Phased topics & curated resources</p>
            </div>
          </button>
        </div>
      </div>

      {/* Recent Activity Log */}
      <div className="space-y-4 pt-2">
        <h2 className="text-base font-semibold text-slate-900">Recent Preparation Activity</h2>
        {dashboard.recent_activities.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500 bg-white border border-slate-200 rounded-xl">
            No activity logged yet. Take a screening test, upload a resume, or practice a mock interview to start building your placement telemetry.
          </div>
        ) : (
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden divide-y divide-slate-100 shadow-2xs">
            {dashboard.recent_activities.map((act) => (
              <div key={act.id} className="p-3.5 sm:p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 sm:gap-4 text-xs">
                <div className="flex items-center gap-3">
                  <div className="h-2 w-2 rounded-full bg-primary/60 shrink-0" />
                  <div>
                    <div className="font-medium text-foreground">{act.description}</div>
                    <div className="text-[11px] text-muted-foreground capitalize mt-0.5">
                      {act.activity_type.replace(/_/g, " ")}
                    </div>
                  </div>
                </div>
                <div className="text-muted-foreground text-[11px] pl-5 sm:pl-0">
                  {new Date(act.created_at).toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

