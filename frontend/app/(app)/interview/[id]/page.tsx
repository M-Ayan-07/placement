"use client";

import React, { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Bot,
  User,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  HelpCircle,
  FileCheck,
  Mic,
  Radio,
} from "lucide-react";
import { InterviewSession, InterviewAnswerResponse } from "@/types";

export default function MockInterviewLivePage() {
  const params = useParams();
  const sessionId = params.id as string;
  const router = useRouter();
  const queryClient = useQueryClient();

  const [studentAnswer, setStudentAnswer] = useState("");
  const [lastTurnFeedback, setLastTurnFeedback] = useState<InterviewAnswerResponse | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [transcriptNotice, setTranscriptNotice] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        setSpeechSupported(true);
      }
    }
  }, []);

  const toggleListening = () => {
    if (!speechSupported) return;

    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
      return;
    }

    try {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = "en-US";

      recognition.onstart = () => {
        setIsListening(true);
        setTranscriptNotice("Listening... Speak your answer clearly.");
      };

      recognition.onresult = (event: any) => {
        let finalChunk = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalChunk += event.results[i][0].transcript + " ";
          }
        }
        if (finalChunk) {
          setStudentAnswer((prev) => {
            const separator = prev.length > 0 && !prev.endsWith(" ") ? " " : "";
            return prev + separator + finalChunk.trim();
          });
        }
      };

      recognition.onerror = (event: any) => {
        console.warn("Speech recognition error:", event.error);
        if (event.error === "not-allowed") {
          setTranscriptNotice("Microphone permission denied. Please allow microphone access.");
        } else {
          setTranscriptNotice(`Speech recognition error: ${event.error}`);
        }
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error("Speech recognition startup error:", err);
      setIsListening(false);
    }
  };

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch {
          // ignore
        }
      }
    };
  }, []);

  // 1. Fetch current interview session state
  const { data: session, isLoading, isError } = useQuery<InterviewSession>({
    queryKey: ["interview-session", sessionId],
    queryFn: async () => {
      return api.get<InterviewSession>(`/interview/${sessionId}`);
    },
  });

  // If already completed and user refreshed, show link to report
  const isCompleted = session?.status === "completed";

  // Active question is the last exchange without a student answer
  const pendingExchange = session?.exchanges?.find((ex) => ex.student_answer === null);
  const currentTurn = pendingExchange?.turn_order ?? (session?.exchanges.length || 1);

  // 2. Submit answer mutation
  const submitAnswerMutation = useMutation({
    mutationFn: async (answerText: string) => {
      return api.post<InterviewAnswerResponse>(`/interview/${sessionId}/answer`, {
        answer: answerText,
      });
    },
    onSuccess: (data) => {
      if (isListening && recognitionRef.current) {
        recognitionRef.current.stop();
        setIsListening(false);
      }
      setLastTurnFeedback(data);
      setStudentAnswer("");
      queryClient.invalidateQueries({ queryKey: ["interview-session", sessionId] });
      queryClient.invalidateQueries({ queryKey: ["interview-history"] });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!studentAnswer.trim() || studentAnswer.trim().length < 10) return;
    submitAnswerMutation.mutate(studentAnswer.trim());
  };

  const handleNextQuestion = () => {
    setLastTurnFeedback(null);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh] text-muted-foreground text-sm">
        Setting up interview environment...
      </div>
    );
  }

  if (isError || !session) {
    return (
      <div className="p-8 text-center bg-card border border-border rounded-xl space-y-3">
        <AlertCircle className="h-8 w-8 text-destructive mx-auto" />
        <h2 className="text-base font-semibold text-foreground">Session Not Found</h2>
        <p className="text-sm text-muted-foreground">The requested mock interview could not be loaded.</p>
        <Button variant="outline" onClick={() => router.push("/interview")} className="text-xs">
          Return to Interview Catalog
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Session Top Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-border gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs uppercase tracking-wider">
              {session.interview_type}
            </Badge>
            <span className="text-xs text-muted-foreground">•</span>
            <span className="text-xs font-medium text-foreground">Question {currentTurn} of 10</span>
          </div>
          <h1 className="text-xl font-bold text-foreground mt-1">{session.topic}</h1>
        </div>

        <div className="flex items-center gap-3">
          {isCompleted && (
            <Button
              size="sm"
              className="gap-1.5 text-xs"
              onClick={() => router.push(`/interview/${sessionId}/report`)}
            >
              <FileCheck className="h-4 w-4" /> View Full Report
            </Button>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={() => router.push("/interview")}
            className="text-xs"
          >
            Exit Session
          </Button>
        </div>
      </div>

      {/* If Turn Feedback is available, show evaluation review */}
      {lastTurnFeedback ? (
        <div className="space-y-6">
          <Card className="border-border shadow-xs">
            <CardHeader className="border-b border-border bg-muted/40 pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-blue-500" />
                  <CardTitle className="text-base">Turn {lastTurnFeedback.turn_order} Evaluation</CardTitle>
                </div>
                <Badge
                  variant={lastTurnFeedback.score >= 7 ? "default" : "secondary"}
                  className="text-xs"
                >
                  Score: {lastTurnFeedback.score}/10
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="pt-6 space-y-5">
              {/* Evaluator Notes */}
              <div>
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">
                  Interviewer Assessment
                </h4>
                <p className="text-sm text-foreground leading-relaxed">{lastTurnFeedback.feedback}</p>
              </div>

              {/* Strengths & Improvements */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div className="bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800 p-4 rounded-xl">
                  <span className="text-xs font-semibold text-emerald-800 dark:text-emerald-400 uppercase tracking-wider block mb-2">
                    Key Strengths
                  </span>
                  <ul className="text-xs text-emerald-900 dark:text-emerald-300 space-y-1.5 list-disc list-inside">
                    {lastTurnFeedback.strengths.map((str, idx) => (
                      <li key={idx}>{str}</li>
                    ))}
                  </ul>
                </div>

                <div className="bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 p-4 rounded-xl">
                  <span className="text-xs font-semibold text-amber-800 dark:text-amber-400 uppercase tracking-wider block mb-2">
                    Areas for Improvement
                  </span>
                  <ul className="text-xs text-amber-900 dark:text-amber-300 space-y-1.5 list-disc list-inside">
                    {lastTurnFeedback.improvements.map((imp, idx) => (
                      <li key={idx}>{imp}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Exemplary Model Answer */}
              <div>
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
                  Exemplary Benchmark Answer
                </h4>
                <p className="text-xs text-foreground bg-muted p-3.5 rounded-lg border border-border leading-relaxed font-mono">
                  {lastTurnFeedback.model_answer}
                </p>
              </div>

              {/* Navigation Action */}
              <div className="pt-3 flex justify-end">
                {lastTurnFeedback.is_complete ? (
                  <Button
                    onClick={() => router.push(`/interview/${sessionId}/report`)}
                    className="gap-2"
                  >
                    View Final Performance Report <ArrowRight className="h-4 w-4" />
                  </Button>
                ) : (
                  <Button onClick={handleNextQuestion} className="gap-2">
                    Proceed to Question {lastTurnFeedback.turn_order + 1} <ArrowRight className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        /* Active Question & Answer Prompt */
        <div className="space-y-6">
          {pendingExchange && (
            <Card className="border-border bg-card">
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <div className="h-8 w-8 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300 flex items-center justify-center flex-shrink-0 font-semibold text-xs">
                    <Bot className="h-4 w-4" />
                  </div>
                  <div className="space-y-2 flex-1">
                    <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Interviewer Question {pendingExchange.turn_order} of 10
                    </div>
                    <p className="text-base font-medium text-foreground leading-relaxed">
                      {pendingExchange.question}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Student Response Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <div className="flex flex-wrap justify-between items-center gap-2 text-xs">
                <label className="font-semibold text-foreground">Your Response</label>
                <div className="flex items-center gap-2.5">
                  {/* Speech-to-Text Button */}
                  {speechSupported ? (
                    <Button
                      type="button"
                      variant={isListening ? "destructive" : "outline"}
                      size="sm"
                      onClick={toggleListening}
                      className="h-8 text-xs gap-1.5"
                    >
                      {isListening ? (
                        <>
                          <Radio className="h-3.5 w-3.5 animate-pulse text-red-500" />
                          <span>Stop Recording</span>
                        </>
                      ) : (
                        <>
                          <Mic className="h-3.5 w-3.5 text-blue-500" />
                          <span>Speak Answer</span>
                        </>
                      )}
                    </Button>
                  ) : (
                    <span className="text-[11px] text-muted-foreground hidden sm:inline">
                      Voice typing available in Chrome/Edge
                    </span>
                  )}
                  <span className="text-muted-foreground">
                    {studentAnswer.trim().split(/\s+/).filter(Boolean).length} words
                  </span>
                </div>
              </div>

              {isListening && (
                <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900 rounded-lg text-xs text-blue-700 dark:text-blue-300">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-600"></span>
                  </span>
                  <span>{transcriptNotice || "Listening... Speak your answer into the microphone."}</span>
                </div>
              )}

              <textarea
                value={studentAnswer}
                onChange={(e) => setStudentAnswer(e.target.value)}
                placeholder="Type or speak your interview response. For technical rounds, explain your approach, data structures, complexity, and trade-offs. For behavioral questions, use the STAR format (Situation, Task, Action, Result)."
                rows={8}
                disabled={submitAnswerMutation.isPending}
                className="w-full rounded-xl border border-border bg-background p-3.5 sm:p-4 text-xs sm:text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring leading-relaxed resize-none disabled:opacity-50"
              />
            </div>

            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-2">
              <span className="text-xs text-muted-foreground">
                Minimum 10 characters. Speak concisely and clearly.
              </span>
              <Button
                type="submit"
                disabled={submitAnswerMutation.isPending || studentAnswer.trim().length < 10}
                className="gap-2 px-6 w-full sm:w-auto"
              >
                {submitAnswerMutation.isPending ? "Evaluating Response..." : "Submit Answer"}
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
