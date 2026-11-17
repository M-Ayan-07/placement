"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/layout/providers/auth-provider";
import { ThemeToggle } from "@/components/layout/providers/theme-provider";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  GraduationCap,
  ArrowRight,
  Code,
  FileText,
  Users,
  Compass,
  CheckCircle2,
  Sparkles,
  Mic,
  BarChart3,
  ShieldCheck,
  Target,
  Zap,
} from "lucide-react";

export default function LandingPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  // If already authenticated, route directly to personal dashboard
  useEffect(() => {
    if (!isLoading && user) {
      router.replace("/dashboard");
    }
  }, [user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-foreground">
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <div className="h-4 w-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          <span>Loading workspace...</span>
        </div>
      </div>
    );
  }

  // If authenticated, render nothing while redirecting
  if (user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col selection:bg-primary/20 selection:text-primary transition-colors duration-200">
      {/* Top Navigation */}
      <header className="border-b border-border bg-background/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 sm:gap-2.5 min-w-0">
            <div className="h-8 w-8 sm:h-9 sm:w-9 rounded-lg bg-primary text-primary-foreground flex items-center justify-center font-bold shadow-xs shrink-0">
              <GraduationCap className="h-4 w-4 sm:h-5 sm:w-5" />
            </div>
            <span className="font-bold text-sm sm:text-base tracking-tight text-foreground truncate">
              AI-Powered Placement Coach
            </span>
          </div>

          {/* Controls: Theme Toggle + Only Login and Register actions */}
          <div className="flex items-center gap-1.5 sm:gap-3 shrink-0">
            <ThemeToggle />
            <Link href="/login">
              <Button
                variant="ghost"
                size="sm"
                className="text-muted-foreground hover:text-foreground text-xs px-2.5 sm:px-3.5"
              >
                Sign In
              </Button>
            </Link>
            <Link href="/register">
              <Button
                size="sm"
                className="text-xs font-semibold px-3 sm:px-4 shadow-xs"
              >
                Register
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center">
        {/* Hero Section */}
        <section className="w-full max-w-5xl mx-auto px-6 pt-16 pb-14 text-center">


          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-foreground max-w-4xl mx-auto leading-[1.15]">
            AI-Powered Placement Coach
          </h1>

          <p className="mt-5 text-base sm:text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed font-normal">
            Master every stage of campus recruitment. Diagnose algorithmic gaps with 10-question screening tests,
            practice multi-turn voice mock interviews, and optimize your resume for applicant tracking systems.
          </p>

          {/* Primary Action Buttons — ONLY Register or Sign In */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3.5">
            <Link href="/register">
              <Button
                size="lg"
                className="font-semibold text-sm px-6 h-11 gap-2 shadow-sm"
              >
                Create Student Account
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/login">
              <Button
                variant="outline"
                size="lg"
                className="text-sm px-6 h-11"
              >
                Sign In to Workspace
              </Button>
            </Link>
          </div>

          {/* Quick Pillars Badge */}
          {/* <div className="mt-8 flex flex-wrap items-center justify-center gap-3 text-xs text-muted-foreground">
            <span className="flex items-center gap-1.5 bg-muted/50 px-3 py-1 rounded-full border border-border">
              <Zap className="h-3.5 w-3.5 text-blue-500" /> 10-Question Assessments
            </span>
            <span className="flex items-center gap-1.5 bg-muted/50 px-3 py-1 rounded-full border border-border">
              <Mic className="h-3.5 w-3.5 text-purple-500" /> Voice-to-Text Mock Interviews
            </span>
            <span className="flex items-center gap-1.5 bg-muted/50 px-3 py-1 rounded-full border border-border">
              <FileText className="h-3.5 w-3.5 text-emerald-500" /> ATS Resume Scanner
            </span>
            <span className="flex items-center gap-1.5 bg-muted/50 px-3 py-1 rounded-full border border-border">
              <ShieldCheck className="h-3.5 w-3.5 text-amber-500" /> 100% Free Tier ($0 Cost)
            </span>
          </div> */}
        </section>

        {/* Product Preview / Telemetry Architecture Showcase */}
        <section className="w-full max-w-5xl mx-auto px-6 pb-16">
          <div className="rounded-2xl border border-border bg-card p-4 sm:p-6 shadow-xl">
            <div className="rounded-xl border border-border/80 bg-background/50 p-6 sm:p-8">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-border gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs uppercase font-semibold tracking-wider text-muted-foreground">
                      Student Readiness Telemetry
                    </span>
                    <Badge variant="outline" className="text-[11px]">
                      Live Aggregate Index
                    </Badge>
                  </div>
                  <h3 className="text-lg font-bold text-foreground mt-1">
                    Placement Readiness Benchmark
                  </h3>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <span className="text-3xl font-extrabold text-foreground">84%</span>
                    <span className="text-[11px] text-emerald-600 dark:text-emerald-400 block font-semibold">
                      Placement Ready
                    </span>
                  </div>
                </div>
              </div>

              {/* 4 Pillars Breakdown Preview */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5 mt-6 text-xs">
                <div className="p-4 rounded-xl border border-border bg-muted/40">
                  <span className="text-muted-foreground block text-[11px]">Academic Profile</span>
                  <span className="text-lg font-bold text-foreground mt-1 block">100%</span>
                  <span className="text-[10px] text-muted-foreground">Weight 15%</span>
                </div>
                <div className="p-4 rounded-xl border border-border bg-muted/40">
                  <span className="text-muted-foreground block text-[11px]">10-Q Screening Tests</span>
                  <span className="text-lg font-bold text-foreground mt-1 block">88%</span>
                  <span className="text-[10px] text-muted-foreground">Weight 35%</span>
                </div>
                <div className="p-4 rounded-xl border border-border bg-muted/40">
                  <span className="text-muted-foreground block text-[11px]">Resume ATS Score</span>
                  <span className="text-lg font-bold text-foreground mt-1 block">82%</span>
                  <span className="text-[10px] text-muted-foreground">Weight 25%</span>
                </div>
                <div className="p-4 rounded-xl border border-border bg-muted/40">
                  <span className="text-muted-foreground block text-[11px]">Mock Interviews</span>
                  <span className="text-lg font-bold text-foreground mt-1 block">80%</span>
                  <span className="text-[10px] text-muted-foreground">Weight 25%</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 4 Core Capabilities */}
        <section className="w-full max-w-5xl mx-auto px-6 py-14 border-t border-border">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-foreground">
              Built for campus placement success
            </h2>
            <p className="text-sm text-muted-foreground mt-2">
              Every round of the placement funnel covered with objective evaluations and actionable feedback.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Feature 1 */}
            <div className="rounded-xl border border-border bg-card p-6 flex flex-col justify-between shadow-xs hover:border-primary/40 transition-colors">
              <div>
                <div className="h-10 w-10 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-500 flex items-center justify-center mb-4">
                  <Code className="h-5 w-5" />
                </div>
                <h3 className="text-base font-semibold text-foreground">10-Question Assessments</h3>
                <p className="text-xs text-muted-foreground leading-relaxed mt-2">
                  Timer-assisted diagnostic evaluations in Quantitative Aptitude, Logical Reasoning, DSA, and Core CS Fundamentals with weak-topic diagnosis.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-border text-[11px] text-muted-foreground flex items-center gap-1.5">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                <span>10 In-Depth Questions Per Session</span>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="rounded-xl border border-border bg-card p-6 flex flex-col justify-between shadow-xs hover:border-primary/40 transition-colors">
              <div>
                <div className="h-10 w-10 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-500 flex items-center justify-center mb-4">
                  <Mic className="h-5 w-5" />
                </div>
                <h3 className="text-base font-semibold text-foreground">Speech-to-Text Mock Interviews</h3>
                <p className="text-xs text-muted-foreground leading-relaxed mt-2">
                  10-turn multi-turn technical & behavioral mock interviews. Speak your responses out loud with live speech recognition or type answers.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-border text-[11px] text-muted-foreground flex items-center gap-1.5">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                <span>Real-Time Voice Dictation & Scoring</span>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="rounded-xl border border-border bg-card p-6 flex flex-col justify-between shadow-xs hover:border-primary/40 transition-colors">
              <div>
                <div className="h-10 w-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 flex items-center justify-center mb-4">
                  <FileText className="h-5 w-5" />
                </div>
                <h3 className="text-base font-semibold text-foreground">Role-Specific ATS Scanner</h3>
                <p className="text-xs text-muted-foreground leading-relaxed mt-2">
                  Upload PDF or DOCX resumes. Receive automated parsing, ATS compatibility scoring, keyword gap analysis, and section rewrites.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-border text-[11px] text-muted-foreground flex items-center gap-1.5">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                <span>Secure In-Memory Storage & Scoring</span>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA Banner */}
        <section className="w-full max-w-5xl mx-auto px-6 py-14 border-t border-border text-center">
          <div className="rounded-2xl border border-border bg-muted/30 p-8 sm:p-10 shadow-xs">
            <h2 className="text-2xl sm:text-3xl font-bold text-foreground">
              Ready to accelerate your placement preparation?
            </h2>
            <p className="text-sm text-muted-foreground mt-2 max-w-lg mx-auto">
              Create your account to start benchmarking your composite readiness score today.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link href="/register">
                <Button
                  size="lg"
                  className="font-semibold text-sm px-6 h-11 gap-2 shadow-xs"
                >
                  Register Now
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link href="/login">
                <Button
                  variant="outline"
                  size="lg"
                  className="text-sm px-6 h-11"
                >
                  Sign In
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* Minimal Footer */}
      <footer className="border-t border-border py-8 bg-background">
        <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between text-xs text-muted-foreground gap-4">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-4 w-4 text-primary" />
            <span className="font-medium text-foreground">AI-Powered Placement Coach</span>
            <span>• Full-Stack Campus Recruitment Intelligence</span>
          </div>
          <div>All preparation modules active • 100% Free Tier</div>
        </div>
      </footer>
    </div>
  );
}
