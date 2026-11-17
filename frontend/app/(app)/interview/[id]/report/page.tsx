"use client";

import React from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  FileCheck,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Sparkles,
  RotateCcw,
  LayoutDashboard,
} from "lucide-react";
import { InterviewSession } from "@/types";

export default function InterviewReportPage() {
  const params = useParams();
  const sessionId = params.id as string;
  const router = useRouter();

  const { data: session, isLoading, isError } = useQuery<InterviewSession>({
    queryKey: ["interview-session", sessionId],
    queryFn: async () => {
      return api.get<InterviewSession>(`/interview/${sessionId}`);
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh] text-slate-500 text-sm">
        Generating comprehensive interview report...
      </div>
    );
  }

  if (isError || !session) {
    return (
      <div className="p-8 text-center bg-white border border-slate-200 rounded-xl space-y-3">
        <AlertCircle className="h-8 w-8 text-red-500 mx-auto" />
        <h2 className="text-base font-semibold text-slate-900">Report Not Found</h2>
        <Button variant="outline" onClick={() => router.push("/interview")} className="text-xs">
          Return to Interviews
        </Button>
      </div>
    );
  }

  const overallScore = session.score ?? 0;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-border gap-3">
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => router.push("/interview")}
            className="gap-1 text-xs shrink-0"
          >
            <ArrowLeft className="h-3.5 w-3.5" /> Back
          </Button>
          <div>
            <h1 className="text-lg sm:text-xl font-bold text-foreground">Mock Interview Report</h1>
            <p className="text-xs text-muted-foreground">
              {session.topic} • {session.interview_type.toUpperCase()} Round
            </p>
          </div>
        </div>
        <Badge
          variant={overallScore >= 75 ? "default" : "secondary"}
          className="text-xs font-semibold py-1 px-3 self-start sm:self-auto"
        >
          Overall: {overallScore}%
        </Badge>
      </div>

      {/* Score Summary Card */}
      <Card className="border-slate-300 shadow-sm bg-gradient-to-br from-slate-50 to-white">
        <CardContent className="pt-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Performance Evaluation
              </span>
              <h2 className="text-2xl font-bold text-slate-900 mt-1">
                {overallScore >= 80
                  ? "Placement Ready — Strong Candidate"
                  : overallScore >= 60
                  ? "Competent Foundation — Needs Polish"
                  : "Requires Targeted Preparation"}
              </h2>
            </div>
            <div className="text-right">
              <div className="text-4xl font-extrabold text-slate-900">{overallScore}%</div>
              <div className="text-xs text-slate-500">Composite Score</div>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Executive Feedback
            </h4>
            <p className="text-sm text-slate-800 leading-relaxed">
              {session.overall_feedback || "The candidate displayed foundational grasp of the concepts tested."}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Turn-by-Turn Transcript & Feedback Breakdown */}
      <div className="space-y-4">
        <h3 className="text-base font-semibold text-slate-900">Question-by-Question Transcript</h3>

        {session.exchanges.map((ex) => (
          <Card key={ex.id} className="border-slate-200 shadow-2xs">
            <CardHeader className="pb-3 bg-slate-50/70 border-b border-slate-100 flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-semibold text-slate-900">
                Question {ex.turn_order}
              </CardTitle>
              {ex.score !== null && (
                <Badge variant="outline" className="text-xs">
                  Score: {ex.score} / 10
                </Badge>
              )}
            </CardHeader>
            <CardContent className="pt-4 space-y-4 text-xs">
              {/* Question */}
              <div>
                <span className="font-semibold text-slate-500 block mb-1">Interviewer Prompt:</span>
                <p className="text-sm font-medium text-slate-900">{ex.question}</p>
              </div>

              {/* Student Answer */}
              <div>
                <span className="font-semibold text-slate-500 block mb-1">Your Response:</span>
                <p className="text-xs text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-200 leading-relaxed whitespace-pre-line">
                  {ex.student_answer || "No response provided."}
                </p>
              </div>

              {/* AI Feedback */}
              {ex.ai_feedback && (
                <div>
                  <span className="font-semibold text-slate-500 block mb-1">Evaluator Feedback:</span>
                  <p className="text-xs text-slate-800 bg-blue-50/50 p-3 rounded-lg border border-blue-200/60 leading-relaxed">
                    {ex.ai_feedback}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Action Navigation */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-slate-200">
        <Button
          variant="outline"
          onClick={() => router.push("/interview")}
          className="gap-2 text-xs"
        >
          <RotateCcw className="h-4 w-4" /> Practice Another Module
        </Button>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={() => router.push("/recommendations")}
            className="text-xs"
          >
            View Study Roadmap
          </Button>
          <Button
            onClick={() => router.push("/dashboard")}
            className="gap-2 text-xs"
          >
            <LayoutDashboard className="h-4 w-4" /> Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}

