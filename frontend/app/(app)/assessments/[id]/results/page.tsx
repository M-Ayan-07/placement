"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ArrowRight,
  RotateCcw,
  Sparkles,
  LayoutDashboard,
} from "lucide-react";

interface QuestionDetail {
  question_id: string;
  question: string;
  options: string[];
  selected_option: number;
  correct_option: number;
  is_correct: boolean;
  explanation?: string;
  tags: string[];
}

interface ResultData {
  session_id: string;
  category: string;
  subcategory: string;
  score: number;
  max_score: number;
  percentage: number;
  time_taken_seconds: number;
  weak_topics: string[];
  breakdown: QuestionDetail[];
}

export default function AssessmentResultsPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.id as string;

  const [result, setResult] = useState<ResultData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadResult() {
      try {
        const data = await api.get<ResultData>(`/assessments/sessions/${sessionId}/result`);
        setResult(data);
      } catch (err) {
        console.error("Failed to load result:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadResult();
  }, [sessionId]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <div className="h-4 w-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <span>Generating diagnostic assessment report...</span>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="text-center py-20">
        <p className="text-sm text-muted-foreground">Assessment results could not be located.</p>
        <Button onClick={() => router.push("/assessments")} className="mt-4">
          Back to Assessments
        </Button>
      </div>
    );
  }

  const isPassed = result.percentage >= 60;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Score Overview Card */}
      <Card className="border-border shadow-xs overflow-hidden">
        <div
          className={`h-2 ${
            result.percentage >= 75
              ? "bg-emerald-500"
              : result.percentage >= 50
              ? "bg-amber-500"
              : "bg-red-500"
          }`}
        />
        <CardHeader className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4">
          <div>
            <Badge variant="outline" className="text-xs uppercase font-mono tracking-wider mb-2">
              Diagnostic Report
            </Badge>
            <CardTitle className="text-lg sm:text-xl capitalize">
              {result.subcategory.replace("_", " ")} Assessment
            </CardTitle>
            <CardDescription>
              Completed in {Math.round(result.time_taken_seconds)} seconds
            </CardDescription>
          </div>

          <div className="text-left sm:text-right">
            <div className="text-2xl sm:text-3xl font-extrabold text-foreground tracking-tight font-mono">
              {result.score} / {result.max_score}
            </div>
            <span
              className={`text-xs font-semibold px-2 py-0.5 rounded inline-block mt-0.5 ${
                isPassed ? "bg-emerald-100 text-emerald-800" : "bg-red-100 text-red-800"
              }`}
            >
              {result.percentage}% Score
            </span>
          </div>
        </CardHeader>
      </Card>

      {/* Weak Areas Callout */}
      {result.weak_topics.length > 0 && (
        <div className="p-4 rounded-lg border border-amber-200 bg-amber-50/70 space-y-3">
          <div className="flex items-center gap-2 text-amber-900 font-semibold text-sm">
            <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0" />
            <span>Identified Revision Focus & Weak Topics:</span>
          </div>
          <p className="text-xs text-amber-800 leading-relaxed">
            Based on your answers, prioritizing these specific concepts will give you the highest score improvements in
            screening rounds:
          </p>
          <div className="flex flex-wrap gap-1.5">
            {result.weak_topics.map((topic) => (
              <Badge key={topic} variant="warning" className="text-xs font-medium">
                {topic}
              </Badge>
            ))}
          </div>
          <div className="pt-2">
            <Link href="/recommendations">
              <Button size="sm" className="gap-2 text-xs bg-indigo-600 hover:bg-indigo-700 text-white">
                <Sparkles className="h-3.5 w-3.5" />
                Generate Tailored Preparation Plan
              </Button>
            </Link>
          </div>
        </div>
      )}

      {/* Question Review Breakdown */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-slate-900 tracking-tight">Question-by-Question Review</h3>

        <div className="space-y-4">
          {result.breakdown.map((q, idx) => (
            <Card key={q.question_id} className="border-border shadow-xs">
              <CardHeader className="pb-3 flex flex-row items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">
                    {q.is_correct ? (
                      <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-600" />
                    )}
                  </div>
                  <div>
                    <span className="text-xs font-mono text-muted-foreground">Question {idx + 1}</span>
                    <p className="text-sm font-medium text-slate-900 pt-1 leading-relaxed">{q.question}</p>
                  </div>
                </div>

                <Badge variant={q.is_correct ? "success" : "destructive"} className="text-[10px] shrink-0">
                  {q.is_correct ? "+1 Mark" : "0 Marks"}
                </Badge>
              </CardHeader>

              <CardContent className="space-y-3 pt-0">
                {/* Options List */}
                <div className="space-y-1.5 pl-8">
                  {q.options.map((opt, optIdx) => {
                    const isSelected = q.selected_option === optIdx;
                    const isCorrect = q.correct_option === optIdx;

                    let rowStyle = "border-border text-slate-600 bg-white";
                    if (isCorrect) {
                      rowStyle = "border-emerald-300 bg-emerald-50 text-emerald-900 font-medium";
                    } else if (isSelected && !isCorrect) {
                      rowStyle = "border-red-300 bg-red-50 text-red-900 line-through";
                    }

                    return (
                      <div key={optIdx} className={`p-2.5 rounded-md border text-xs flex items-center justify-between ${rowStyle}`}>
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-[11px]">{String.fromCharCode(65 + optIdx)}.</span>
                          <span>{opt}</span>
                        </div>
                        {isCorrect && <span className="text-[10px] font-semibold text-emerald-700">Correct Answer</span>}
                        {isSelected && !isCorrect && (
                          <span className="text-[10px] font-semibold text-red-700">Your Selection</span>
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Explanation */}
                {q.explanation && (
                  <div className="ml-8 p-3 rounded-md bg-slate-50 border border-slate-200 text-xs text-slate-700 space-y-1">
                    <span className="font-semibold text-slate-900">Concept Explanation:</span>
                    <p>{q.explanation}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Footer Navigation */}
      <div className="flex items-center justify-between pt-6 border-t border-border">
        <Link href="/assessments">
          <Button variant="outline" size="sm" className="gap-2">
            <RotateCcw className="h-4 w-4" />
            Back to Assessments Catalog
          </Button>
        </Link>

        <Link href="/dashboard">
          <Button size="sm" className="gap-2">
            <LayoutDashboard className="h-4 w-4" />
            Go to Dashboard
          </Button>
        </Link>
      </div>
    </div>
  );
}

