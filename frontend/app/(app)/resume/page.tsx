"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/components/layout/providers/auth-provider";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { PREDEFINED_JOB_ROLES } from "@/lib/constants";
import {
  Upload,
  FileText,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Download,
  Clock,
  ArrowRight,
  TrendingUp,
  FileCheck,
} from "lucide-react";

interface SectionScores {
  skills: number;
  projects: number;
  experience: number;
  education: number;
}

interface AnalysisData {
  resume_id: string;
  original_filename: string;
  target_role: string;
  ats_score: number;
  role_fit_percentage: number;
  strengths: string[];
  weaknesses: string[];
  ats_keywords_missing: string[];
  suggestions: string[];
  section_scores: SectionScores;
  parsed_skills: string[];
  uploaded_at: string;
  status: string;
}

interface ResumeListItem {
  id: string;
  original_filename: string;
  target_role: string;
  ats_score: number | null;
  status: string;
  uploaded_at: string;
}

export default function ResumePage() {
  const { user } = useAuth();

  const [targetRole, setTargetRole] = useState<string>(PREDEFINED_JOB_ROLES[0]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [activeAnalysis, setActiveAnalysis] = useState<AnalysisData | null>(null);
  const [pastResumes, setPastResumes] = useState<ResumeListItem[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);

  // Set default target role from user's profile if available
  useEffect(() => {
    if (user?.goals?.target_roles && user.goals.target_roles.length > 0) {
      setTargetRole(user.goals.target_roles[0]);
    }
  }, [user]);

  // Load past uploads
  useEffect(() => {
    async function loadHistory() {
      try {
        const list = await api.get<ResumeListItem[]>("/resume/list");
        setPastResumes(list);
        if (list.length > 0) {
          // Auto load latest scan
          const latest = await api.get<AnalysisData>(`/resume/${list[0].id}/analysis`);
          setActiveAnalysis(latest);
        }
      } catch (err) {
        console.error("Failed to load resume list:", err);
      } finally {
        setIsLoadingHistory(false);
      }
    }
    loadHistory();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setErrorMessage(null);
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.size > 5 * 1024 * 1024) {
        setErrorMessage("File exceeds maximum allowed limit of 5 MB.");
        return;
      }
      const ext = file.name.toLowerCase().split(".").pop();
      if (ext !== "pdf" && ext !== "docx") {
        setErrorMessage("Only PDF and DOCX formats are supported.");
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setErrorMessage("Please select a resume file to upload.");
      return;
    }

    setIsUploading(true);
    setErrorMessage(null);

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("target_role", targetRole);

    try {
      const result = await api.post<AnalysisData>("/resume/upload", formData);
      setActiveAnalysis(result);
      setSelectedFile(null);

      // Refresh list
      const list = await api.get<ResumeListItem[]>("/resume/list");
      setPastResumes(list);
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Failed to upload and analyze resume.");
      }
    } finally {
      setIsUploading(false);
    }
  };

  const loadPastScan = async (id: string) => {
    try {
      const data = await api.get<AnalysisData>(`/resume/${id}/analysis`);
      setActiveAnalysis(data);
    } catch (err) {
      console.error("Failed to load analysis:", err);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">Resume Scanner & ATS Role Analysis</h2>
        <p className="text-sm text-muted-foreground">
          Analyze resume keyword density, section strengths, and recruitment compatibility against specific job profiles.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Col: Upload & History (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <Card className="border-border shadow-xs">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Upload className="h-4 w-4 text-primary" />
                Upload New Resume
              </CardTitle>
              <CardDescription>Upload your latest CV in PDF or DOCX format (max 5 MB).</CardDescription>
            </CardHeader>

            <form onSubmit={handleUpload}>
              <CardContent className="space-y-4">
                {errorMessage && (
                  <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-md flex items-start gap-2">
                    <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-red-600" />
                    <span>{errorMessage}</span>
                  </div>
                )}

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-medium text-foreground">Target Career Role</label>
                    <span className="text-[11px] text-muted-foreground">Select from 10 standard roles</span>
                  </div>
                  <select
                    value={targetRole}
                    onChange={(e) => setTargetRole(e.target.value)}
                    disabled={isUploading}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-xs sm:text-sm text-foreground shadow-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  >
                    {PREDEFINED_JOB_ROLES.map((role) => (
                      <option key={role} value={role} className="bg-background text-foreground">
                        {role}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700">Resume Document</label>
                  <div className="border-2 border-dashed border-border rounded-lg p-5 text-center bg-slate-50 hover:bg-slate-100/50 transition-colors cursor-pointer relative">
                    <input
                      type="file"
                      accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                      onChange={handleFileChange}
                      disabled={isUploading}
                      className="absolute inset-0 opacity-0 cursor-pointer"
                    />
                    <div className="flex flex-col items-center justify-center space-y-2 pointer-events-none">
                      <FileText className="h-8 w-8 text-muted-foreground" />
                      <div className="text-xs">
                        <span className="font-semibold text-primary">Click to select file</span> or drag & drop
                      </div>
                      <p className="text-[11px] text-muted-foreground">PDF or DOCX up to 5 MB</p>
                    </div>
                  </div>

                  {selectedFile && (
                    <div className="text-xs text-slate-700 font-medium flex items-center gap-2 pt-1">
                      <FileCheck className="h-4 w-4 text-emerald-600" />
                      <span className="truncate">{selectedFile.name}</span>
                      <span className="text-muted-foreground font-mono">
                        ({(selectedFile.size / 1024).toFixed(0)} KB)
                      </span>
                    </div>
                  )}
                </div>
              </CardContent>

              <CardFooter className="pt-0 border-t border-slate-100">
                <Button type="submit" disabled={isUploading || !selectedFile} className="w-full gap-2 mt-4">
                  {isUploading ? (
                    <>
                      <div className="h-4 w-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                      <span>Scanning & Evaluating...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      <span>Scan & Score Resume</span>
                    </>
                  )}
                </Button>
              </CardFooter>
            </form>
          </Card>

          {/* Past Scans */}
          <Card className="border-border shadow-xs">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                Previous Scans ({pastResumes.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoadingHistory ? (
                <div className="space-y-2">
                  {[1, 2].map((i) => (
                    <div key={i} className="h-12 bg-slate-100 rounded animate-pulse" />
                  ))}
                </div>
              ) : pastResumes.length === 0 ? (
                <p className="text-xs text-muted-foreground italic py-3 text-center">No past scans recorded.</p>
              ) : (
                <div className="divide-y divide-border">
                  {pastResumes.map((item) => (
                    <div
                      key={item.id}
                      onClick={() => loadPastScan(item.id)}
                      className={`py-3 flex items-center justify-between cursor-pointer text-xs rounded-md px-2 -mx-2 transition-colors ${activeAnalysis?.resume_id === item.id ? "bg-indigo-50/70 font-medium" : "hover:bg-slate-50"
                        }`}
                    >
                      <div className="truncate max-w-[180px]">
                        <p className="truncate text-slate-900">{item.original_filename}</p>
                        <p className="text-[11px] text-muted-foreground">{item.target_role}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge
                          variant={
                            (item.ats_score || 0) >= 70
                              ? "success"
                              : (item.ats_score || 0) >= 50
                                ? "warning"
                                : "destructive"
                          }
                          className="text-[10px] font-mono"
                        >
                          {item.ats_score}% ATS
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Col: Analysis Report (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {!activeAnalysis ? (
            <Card className="border-border shadow-xs text-center py-20 px-6">
              <CardContent className="space-y-3">
                <div className="h-12 w-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400">
                  <FileText className="h-6 w-6" />
                </div>
                <h3 className="text-base font-semibold text-slate-900">No Resume Analyzed Yet</h3>
                <p className="text-xs text-muted-foreground max-w-sm mx-auto">
                  Upload your CV on the left to extract technical skills, check ATS compliance, and receive role-specific
                  keyword recommendations.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {/* ATS Score Card */}
              <Card className="border-border shadow-xs overflow-hidden">
                <div
                  className={`h-2 ${activeAnalysis.ats_score >= 75
                      ? "bg-emerald-500"
                      : activeAnalysis.ats_score >= 50
                        ? "bg-amber-500"
                        : "bg-red-500"
                    }`}
                />
                <CardHeader className="flex flex-row items-center justify-between pb-4">
                  <div>
                    <span className="text-xs font-mono uppercase text-muted-foreground tracking-wider">
                      Role-Fit Evaluation
                    </span>
                    <CardTitle className="text-lg pt-1">{activeAnalysis.target_role}</CardTitle>
                    <CardDescription className="text-xs truncate max-w-sm">
                      {activeAnalysis.original_filename} • Scanned on{" "}
                      {new Date(activeAnalysis.uploaded_at).toLocaleDateString()}
                    </CardDescription>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-center">
                      <div className="text-3xl font-extrabold text-slate-900 font-mono tracking-tight">
                        {activeAnalysis.ats_score}
                      </div>
                      <span className="text-[11px] text-muted-foreground">ATS Score / 100</span>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="border-t border-border pt-4">
                  {/* Section Scores */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                    <div className="p-2.5 rounded-md bg-slate-50 border border-slate-200">
                      <span className="text-[11px] text-muted-foreground block">Skills Match</span>
                      <span className="text-sm font-bold text-slate-900 font-mono">
                        {activeAnalysis.section_scores.skills}%
                      </span>
                    </div>
                    <div className="p-2.5 rounded-md bg-slate-50 border border-slate-200">
                      <span className="text-[11px] text-muted-foreground block">Projects</span>
                      <span className="text-sm font-bold text-slate-900 font-mono">
                        {activeAnalysis.section_scores.projects}%
                      </span>
                    </div>
                    <div className="p-2.5 rounded-md bg-slate-50 border border-slate-200">
                      <span className="text-[11px] text-muted-foreground block">Experience</span>
                      <span className="text-sm font-bold text-slate-900 font-mono">
                        {activeAnalysis.section_scores.experience}%
                      </span>
                    </div>
                    <div className="p-2.5 rounded-md bg-slate-50 border border-slate-200">
                      <span className="text-[11px] text-muted-foreground block">Academics</span>
                      <span className="text-sm font-bold text-slate-900 font-mono">
                        {activeAnalysis.section_scores.education}%
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Missing ATS Keywords */}
              {activeAnalysis.ats_keywords_missing.length > 0 && (
                <div className="p-4 rounded-lg border border-amber-200 bg-amber-50/70 space-y-2.5">
                  <div className="flex items-center gap-2 text-amber-900 font-semibold text-xs">
                    <AlertCircle className="h-4 w-4 text-amber-600 shrink-0" />
                    <span>Missing Industry ATS Keywords for {activeAnalysis.target_role}:</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {activeAnalysis.ats_keywords_missing.map((kw) => (
                      <Badge key={kw} variant="warning" className="text-xs">
                        + {kw}
                      </Badge>
                    ))}
                  </div>
                  <p className="text-[11px] text-amber-800 pt-1">
                    Recruiter search filters and ATS scanners flag resumes that contain these standard domain keywords.
                  </p>
                </div>
              )}

              {/* Strengths & Weaknesses */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="border-border shadow-xs">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xs uppercase tracking-wider font-semibold text-emerald-800 flex items-center gap-1.5">
                      <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                      Identified Strengths
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-1.5">
                    {activeAnalysis.strengths.map((s, idx) => (
                      <p key={idx} className="text-xs text-slate-700 flex items-start gap-2">
                        <span className="text-emerald-600 font-bold">•</span>
                        <span>{s}</span>
                      </p>
                    ))}
                  </CardContent>
                </Card>

                <Card className="border-border shadow-xs">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xs uppercase tracking-wider font-semibold text-red-800 flex items-center gap-1.5">
                      <AlertCircle className="h-4 w-4 text-red-600" />
                      Critical Gaps
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-1.5">
                    {activeAnalysis.weaknesses.map((w, idx) => (
                      <p key={idx} className="text-xs text-slate-700 flex items-start gap-2">
                        <span className="text-red-600 font-bold">•</span>
                        <span>{w}</span>
                      </p>
                    ))}
                  </CardContent>
                </Card>
              </div>

              {/* Actionable Suggestions */}
              <Card className="border-border shadow-xs">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-primary" />
                    Recommended Resume Iterations
                  </CardTitle>
                  <CardDescription>Concrete improvements to boost callback rates for this role.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-2.5">
                  {activeAnalysis.suggestions.map((sug, idx) => (
                    <div key={idx} className="p-3 rounded-md bg-slate-50 border border-slate-200 text-xs text-slate-800 flex items-start gap-2.5">
                      <div className="h-4 w-4 rounded-full bg-primary/10 text-primary flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                        {idx + 1}
                      </div>
                      <p className="leading-relaxed">{sug}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

