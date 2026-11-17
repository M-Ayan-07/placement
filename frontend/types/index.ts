export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ChatSession {
  id: string;
  title: string;
  started_at: string;
  messages: ChatMessage[];
}

export interface InterviewExchange {
  id: string;
  turn_order: number;
  question: string;
  student_answer: string | null;
  ai_feedback: string | null;
  score: number | null;
}

export interface InterviewSession {
  id: string;
  interview_type: "technical" | "hr";
  topic: string;
  score: number | null;
  overall_feedback: string | null;
  status: "in_progress" | "completed";
  started_at: string;
  completed_at: string | null;
  exchanges: InterviewExchange[];
}

export interface InterviewAnswerResponse {
  turn_order: number;
  score: number;
  feedback: string;
  strengths: string[];
  improvements: string[];
  model_answer: string;
  next_question: string | null;
  is_complete: boolean;
  overall_score: number | null;
  overall_feedback: string | null;
}

export interface ReadinessBreakdown {
  profile_score: number;
  assessment_score: number;
  resume_score: number;
  interview_score: number;
  composite_readiness_score: number;
  readiness_level: string;
}

export interface ActivityItem {
  id: string;
  activity_type: string;
  description: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface DashboardSummary {
  full_name: string;
  email: string;
  target_role: string | null;
  target_companies: string[];
  target_ctc_lpa: number | null;
  readiness: ReadinessBreakdown;
  total_tests_completed: number;
  assessment_average: number | null;
  best_ats_score: number | null;
  total_interviews_completed: number;
  interview_average: number | null;
  weak_topics: string[];
  recent_activities: ActivityItem[];
}
