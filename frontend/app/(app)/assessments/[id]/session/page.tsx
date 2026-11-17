"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Clock, AlertTriangle, ArrowRight, ArrowLeft, CheckCircle2 } from "lucide-react";

interface QuestionItem {
  id: string;
  category: string;
  subcategory: string;
  question: string;
  options: string[];
  difficulty: string;
}

interface SessionData {
  session_id: string;
  category: string;
  subcategory: string;
  time_limit_minutes: number;
  questions: QuestionItem[];
}

export default function AssessmentSessionPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.id as string;

  const [questions, setQuestions] = useState<QuestionItem[]>([]);
  const [subcategory, setSubcategory] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [secondsRemaining, setSecondsRemaining] = useState(15 * 60);
  const [startTime] = useState<number>(Date.now());
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  useEffect(() => {
    // If questions were saved or we load from backend
    // Since start_session returns questions, let's store them in sessionStorage or re-fetch
    const cachedData = sessionStorage.getItem(`exam_${sessionId}`);
    if (cachedData) {
      try {
        const parsed = JSON.parse(cachedData);
        setQuestions(parsed.questions || []);
        setSubcategory(parsed.subcategory || "");
        setIsLoading(false);
        return;
      } catch {
        // Fallback
      }
    }

    // If not cached, start session with same category or load
    async function loadFallback() {
      try {
        const res = await api.post<SessionData>("/assessments/sessions/start", {
          category: "technical",
          subcategory: "dsa",
          num_questions: 10,
        });
        setQuestions(res.questions);
        setSubcategory(res.subcategory);
      } catch (err) {
        console.error("Failed to load session:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadFallback();
  }, [sessionId]);

  // Countdown Timer
  useEffect(() => {
    if (isLoading || isSubmitting) return;

    const timer = setInterval(() => {
      setSecondsRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleSubmitTest();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isLoading, isSubmitting]);

  const currentQ = questions[currentIndex];
  const selectedOption = currentQ ? answers[currentQ.id] : undefined;

  const handleSelectOption = (idx: number) => {
    if (!currentQ) return;
    setAnswers((prev) => ({ ...prev, [currentQ.id]: idx }));
  };

  const handleSubmitTest = async () => {
    setIsSubmitting(true);
    const timeSpent = Math.round((Date.now() - startTime) / 1000);

    const answerPayload = questions.map((q) => ({
      question_id: q.id,
      selected_option: answers[q.id] !== undefined ? answers[q.id] : -1,
    }));

    try {
      await api.post(`/assessments/sessions/${sessionId}/submit`, {
        answers: answerPayload,
        time_taken_seconds: timeSpent,
      });

      router.push(`/assessments/${sessionId}/results`);
    } catch (err) {
      console.error("Failed to submit exam:", err);
      setIsSubmitting(false);
      setShowConfirmModal(false);
    }
  };

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const rem = secs % 60;
    return `${mins.toString().padStart(2, "0")}:${rem.toString().padStart(2, "0")}`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <div className="h-4 w-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <span>Setting up test environment...</span>
        </div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="text-center py-20">
        <p className="text-sm text-muted-foreground">No questions found for this session.</p>
        <Button onClick={() => router.push("/assessments")} className="mt-4">
          Back to Assessments
        </Button>
      </div>
    );
  }

  const answeredCount = Object.keys(answers).length;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Test Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-card border border-border rounded-lg p-4 shadow-xs">
        <div>
          <span className="text-xs uppercase font-mono tracking-wider text-muted-foreground">Screening Exam</span>
          <h2 className="text-base font-bold text-foreground capitalize">
            {subcategory ? subcategory.replace("_", " ") : "Diagnostic Assessment"}
          </h2>
        </div>

        {/* Timer */}
        <div
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md border font-mono text-sm font-semibold shrink-0 ${
            secondsRemaining < 120
              ? "bg-red-500/10 border-red-500/20 text-red-600 dark:text-red-400 animate-pulse"
              : secondsRemaining < 300
              ? "bg-amber-500/10 border-amber-500/20 text-amber-600 dark:text-amber-400"
              : "bg-muted border-border text-foreground"
          }`}
        >
          <Clock className="h-4 w-4" />
          <span>{formatTime(secondsRemaining)}</span>
        </div>
      </div>

      {/* Main Question View */}
      <Card className="border-border shadow-xs">
        <CardHeader className="pb-3 border-b border-border flex flex-row items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-mono text-muted-foreground">
              Question {currentIndex + 1} of {questions.length}
            </span>
          </div>
          <Badge variant="outline" className="text-[11px] capitalize">
            {currentQ.difficulty}
          </Badge>
        </CardHeader>

        <CardContent className="pt-6 space-y-6">
          <p className="text-base font-medium text-slate-900 leading-relaxed">{currentQ.question}</p>

          {/* Options */}
          <div className="space-y-2.5">
            {currentQ.options.map((opt, idx) => {
              const isSelected = selectedOption === idx;
              return (
                <div
                  key={idx}
                  onClick={() => handleSelectOption(idx)}
                  className={`flex items-center gap-3 p-3.5 rounded-lg border text-sm cursor-pointer transition-colors ${
                    isSelected
                      ? "border-primary bg-primary-50/50 text-slate-900 font-medium"
                      : "border-border hover:bg-slate-50 text-slate-800"
                  }`}
                >
                  <div
                    className={`h-5 w-5 rounded-full border flex items-center justify-center text-xs font-mono shrink-0 ${
                      isSelected
                        ? "border-primary bg-primary text-primary-foreground font-bold"
                        : "border-slate-300 text-slate-500"
                    }`}
                  >
                    {String.fromCharCode(65 + idx)}
                  </div>
                  <span>{opt}</span>
                </div>
              );
            })}
          </div>
        </CardContent>

        <CardFooter className="border-t border-border pt-4 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
            disabled={currentIndex === 0}
            className="gap-2 justify-center"
          >
            <ArrowLeft className="h-4 w-4" />
            Previous
          </Button>

          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            {currentIndex < questions.length - 1 ? (
              <Button
                size="sm"
                onClick={() => setCurrentIndex((prev) => Math.min(questions.length - 1, prev + 1))}
                className="gap-2 w-full sm:w-auto justify-center"
              >
                Next
                <ArrowRight className="h-4 w-4" />
              </Button>
            ) : (
              <Button
                size="sm"
                onClick={() => setShowConfirmModal(true)}
                className="gap-2 bg-emerald-600 hover:bg-emerald-700 text-white w-full sm:w-auto justify-center"
              >
                <CheckCircle2 className="h-4 w-4" />
                Submit Assessment
              </Button>
            )}
          </div>
        </CardFooter>
      </Card>

      {/* Question Palette */}
      <div className="p-4 bg-card border border-border rounded-lg shadow-xs space-y-3">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Question Navigation</span>
          <span>
            {answeredCount} of {questions.length} answered
          </span>
        </div>

        <div className="flex flex-wrap gap-2">
          {questions.map((q, idx) => {
            const isAnswered = answers[q.id] !== undefined;
            const isCurrent = idx === currentIndex;
            return (
              <button
                key={q.id}
                onClick={() => setCurrentIndex(idx)}
                className={`h-8 w-8 rounded text-xs font-mono font-medium transition-colors border ${
                  isCurrent
                    ? "border-primary bg-primary text-primary-foreground font-bold ring-2 ring-primary/20"
                    : isAnswered
                    ? "border-emerald-300 bg-emerald-50 text-emerald-800"
                    : "border-border bg-slate-50 text-slate-600 hover:bg-slate-100"
                }`}
              >
                {idx + 1}
              </button>
            );
          })}
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-md border-border shadow-lg">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-500" />
                Ready to submit?
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              <p>
                You have answered <strong className="text-foreground">{answeredCount}</strong> out of{" "}
                <strong className="text-foreground">{questions.length}</strong> questions.
              </p>
              {answeredCount < questions.length && (
                <p className="text-amber-700 text-xs bg-amber-50 p-2 rounded border border-amber-200">
                  Unanswered questions will be scored as 0 marks.
                </p>
              )}
            </CardContent>
            <CardFooter className="flex justify-end gap-3 pt-4 border-t border-border">
              <Button variant="outline" size="sm" onClick={() => setShowConfirmModal(false)} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button size="sm" onClick={handleSubmitTest} disabled={isSubmitting} className="bg-emerald-600 hover:bg-emerald-700 text-white">
                {isSubmitting ? "Scoring..." : "Yes, Submit Test"}
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}
    </div>
  );
}

