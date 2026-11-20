/**
 * Predefined campus placement target job roles.
 * Users can only select from these standardized industry job profiles.
 */
export const PREDEFINED_JOB_ROLES = [
  "Software Development Engineer (SDE)",
  "Frontend Developer",
  "Backend Developer",
  "Full Stack Developer",
  "Data Scientist / ML Engineer",
  "Data Analyst",
  "DevOps & Cloud Engineer",
  "Mobile App Developer (Android/iOS)",
  "QA / Test Automation Engineer",
  "Product & Systems Engineer",
] as const;

export type PredefinedJobRole = (typeof PREDEFINED_JOB_ROLES)[number];

