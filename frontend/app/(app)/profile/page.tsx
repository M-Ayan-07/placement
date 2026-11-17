"use client";

import React, { useEffect, useState } from "react";
import { useAuth, User } from "@/components/layout/providers/auth-provider";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Target, CheckCircle2, AlertCircle, X, Plus, Save } from "lucide-react";
import { PREDEFINED_JOB_ROLES } from "@/lib/constants";

export default function ProfilePage() {
  const { user, updateUser } = useAuth();

  // Tab selection
  const [activeTab, setActiveTab] = useState<"profile" | "goals">("profile");

  // Profile Form State
  const [fullName, setFullName] = useState("");
  const [college, setCollege] = useState("");
  const [branch, setBranch] = useState("");
  const [graduationYear, setGraduationYear] = useState<number | "">("");
  const [cgpa, setCgpa] = useState<number | "">("");
  const [bio, setBio] = useState("");
  const [skills, setSkills] = useState<string[]>([]);
  const [newSkillInput, setNewSkillInput] = useState("");

  // Goals Form State
  const [targetRoles, setTargetRoles] = useState<string[]>([]);
  const [selectedRoleDropdown, setSelectedRoleDropdown] = useState<string>(PREDEFINED_JOB_ROLES[0]);
  const [targetCompanies, setTargetCompanies] = useState<string[]>([]);
  const [newCompanyInput, setNewCompanyInput] = useState("");
  const [targetCtcLpa, setTargetCtcLpa] = useState<number | "">("");
  const [preferredLocations, setPreferredLocations] = useState<string[]>([]);
  const [newLocationInput, setNewLocationInput] = useState("");

  // UI state
  const [isSaving, setIsSaving] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Pre-fill on mount from user
  useEffect(() => {
    if (user) {
      if (user.profile) {
        setFullName(user.profile.full_name || "");
        setCollege(user.profile.college || "");
        setBranch(user.profile.branch || "");
        setGraduationYear(user.profile.graduation_year ?? "");
        setCgpa(user.profile.cgpa ?? "");
        setBio(user.profile.bio || "");
        setSkills(user.profile.skills || []);
      }
      if (user.goals) {
        setTargetRoles(user.goals.target_roles || []);
        setTargetCompanies(user.goals.target_companies || []);
        setTargetCtcLpa(user.goals.target_ctc_lpa ?? "");
        setPreferredLocations(user.goals.preferred_locations || []);
      }
    }
  }, [user]);

  // Skill management
  const addSkill = () => {
    const trimmed = newSkillInput.trim();
    if (trimmed && !skills.includes(trimmed)) {
      setSkills([...skills, trimmed]);
      setNewSkillInput("");
    }
  };

  const removeSkill = (skillToRemove: string) => {
    setSkills(skills.filter((s) => s !== skillToRemove));
  };

  // Role management
  const addRole = () => {
    if (selectedRoleDropdown && !targetRoles.includes(selectedRoleDropdown)) {
      setTargetRoles([...targetRoles, selectedRoleDropdown]);
    }
  };

  const removeRole = (roleToRemove: string) => {
    setTargetRoles(targetRoles.filter((r) => r !== roleToRemove));
  };

  // Company management
  const addCompany = () => {
    const trimmed = newCompanyInput.trim();
    if (trimmed && !targetCompanies.includes(trimmed)) {
      setTargetCompanies([...targetCompanies, trimmed]);
      setNewCompanyInput("");
    }
  };

  const removeCompany = (companyToRemove: string) => {
    setTargetCompanies(targetCompanies.filter((c) => c !== companyToRemove));
  };

  // Location management
  const addLocation = () => {
    const trimmed = newLocationInput.trim();
    if (trimmed && !preferredLocations.includes(trimmed)) {
      setPreferredLocations([...preferredLocations, trimmed]);
      setNewLocationInput("");
    }
  };

  const removeLocation = (locToRemove: string) => {
    setPreferredLocations(preferredLocations.filter((l) => l !== locToRemove));
  };

  // Save profile handler
  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setStatusMessage(null);

    try {
      const updatedProfile = await api.put<NonNullable<User["profile"]>>("/profile/me", {
        full_name: fullName,
        college: college || null,
        branch: branch || null,
        graduation_year: graduationYear === "" ? null : Number(graduationYear),
        cgpa: cgpa === "" ? null : Number(cgpa),
        skills,
        bio: bio || null,
      });

      if (user) {
        updateUser({ ...user, profile: updatedProfile });
      }
      setStatusMessage({ type: "success", text: "Profile details updated successfully." });
    } catch (err: unknown) {
      const msg = err instanceof ApiError ? err.message : "Failed to update profile details.";
      setStatusMessage({ type: "error", text: msg });
    } finally {
      setIsSaving(false);
    }
  };

  // Save goals handler
  const handleSaveGoals = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setStatusMessage(null);

    try {
      const updatedGoals = await api.put<NonNullable<User["goals"]>>("/profile/goals", {
        target_roles: targetRoles,
        target_companies: targetCompanies,
        target_ctc_lpa: targetCtcLpa === "" ? null : Number(targetCtcLpa),
        preferred_locations: preferredLocations,
      });

      if (user) {
        updateUser({ ...user, goals: updatedGoals });
      }
      setStatusMessage({ type: "success", text: "Placement goals saved successfully." });
    } catch (err: unknown) {
      const msg = err instanceof ApiError ? err.message : "Failed to save placement goals.";
      setStatusMessage({ type: "error", text: msg });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Page Heading */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">Student Profile & Placement Goals</h2>
        <p className="text-sm text-muted-foreground">
          Maintain your academic record, competencies, and company recruitment targets.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-border space-x-4 sm:space-x-6 text-xs sm:text-sm overflow-x-auto flex-nowrap">
        <button
          onClick={() => {
            setActiveTab("profile");
            setStatusMessage(null);
          }}
          className={`flex items-center gap-1.5 sm:gap-2 pb-3 font-medium transition-colors border-b-2 -mb-px whitespace-nowrap ${
            activeTab === "profile"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <User className="h-4 w-4" />
          Academic & Personal Details
        </button>

        <button
          onClick={() => {
            setActiveTab("goals");
            setStatusMessage(null);
          }}
          className={`flex items-center gap-1.5 sm:gap-2 pb-3 font-medium transition-colors border-b-2 -mb-px whitespace-nowrap ${
            activeTab === "goals"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Target className="h-4 w-4" />
          Placement Goals
        </button>
      </div>

      {/* Status Alert */}
      {statusMessage && (
        <div
          className={`p-3 rounded-md text-xs flex items-center gap-2 border ${statusMessage.type === "success"
              ? "bg-emerald-50 border-emerald-200 text-emerald-800"
              : "bg-red-50 border-red-200 text-red-800"
            }`}
        >
          {statusMessage.type === "success" ? (
            <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
          ) : (
            <AlertCircle className="h-4 w-4 text-red-600 shrink-0" />
          )}
          <span>{statusMessage.text}</span>
        </div>
      )}

      {/* Profile Tab */}
      {activeTab === "profile" && (
        <Card className="border-border shadow-xs bg-card">
          <CardHeader>
            <CardTitle className="text-base">Personal & Academic Profile</CardTitle>
            <CardDescription>
              Your academic background helps tailor mock interviews and diagnostic tests.
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleSaveProfile}>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700">Full Name</label>
                  <Input
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700">Email Address (Account)</label>
                  <Input value={user?.email || ""} disabled className="bg-slate-50 cursor-not-allowed" />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700">College / University</label>
                  <Input
                    placeholder="e.g. National Institute of Technology"
                    value={college}
                    onChange={(e) => setCollege(e.target.value)}
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700">Branch / Specialization</label>
                  <Input
                    placeholder="e.g. Computer Science & Engineering"
                    value={branch}
                    onChange={(e) => setBranch(e.target.value)}
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700">Graduation Year</label>
                  <Input
                    type="number"
                    min={2020}
                    max={2035}
                    placeholder="2026"
                    value={graduationYear}
                    onChange={(e) => setGraduationYear(e.target.value === "" ? "" : Number(e.target.value))}
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700">CGPA / Percentage</label>
                  <Input
                    type="number"
                    step="0.01"
                    min={0}
                    max={10}
                    placeholder="8.50"
                    value={cgpa}
                    onChange={(e) => setCgpa(e.target.value === "" ? "" : Number(e.target.value))}
                    disabled={isSaving}
                  />
                </div>
              </div>

              {/* Skills Tag Editor */}
              <div className="space-y-2 pt-2">
                <label className="text-xs font-medium text-slate-700">Technical Skills</label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Add a skill (e.g. Python, SQL, DSA, React)"
                    value={newSkillInput}
                    onChange={(e) => setNewSkillInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        addSkill();
                      }
                    }}
                    disabled={isSaving}
                  />
                  <Button type="button" variant="secondary" onClick={addSkill} disabled={isSaving} className="gap-1">
                    <Plus className="h-4 w-4" />
                    Add
                  </Button>
                </div>

                <div className="flex flex-wrap gap-1.5 pt-2 min-h-8">
                  {skills.length === 0 ? (
                    <span className="text-xs text-muted-foreground italic">No skills added yet.</span>
                  ) : (
                    skills.map((skill) => (
                      <Badge key={skill} variant="secondary" className="gap-1 pl-2.5 pr-1.5 py-1 text-xs">
                        {skill}
                        <button
                          type="button"
                          onClick={() => removeSkill(skill)}
                          className="hover:bg-slate-200 rounded-full p-0.5 text-muted-foreground hover:text-foreground"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </Badge>
                    ))
                  )}
                </div>
              </div>

              {/* Bio */}
              <div className="space-y-1.5 pt-2">
                <label className="text-xs font-medium text-slate-700">Professional Summary / Bio</label>
                <textarea
                  rows={3}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  placeholder="Brief summary of your career focus and technical interests..."
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  disabled={isSaving}
                />
              </div>

              <div className="flex justify-end pt-4">
                <Button type="submit" disabled={isSaving} className="gap-2">
                  <Save className="h-4 w-4" />
                  {isSaving ? "Saving..." : "Save Profile Details"}
                </Button>
              </div>
            </CardContent>
          </form>
        </Card>
      )}

      {/* Goals Tab */}
      {activeTab === "goals" && (
        <Card className="border-border shadow-xs bg-card">
          <CardHeader>
            <CardTitle className="text-base">Placement & Career Targets</CardTitle>
            <CardDescription>
              Set your target job roles, preferred recruiters, and compensation expectations.
            </CardDescription>
          </CardHeader>
          <form onSubmit={handleSaveGoals}>
            <CardContent className="space-y-5">
              {/* Target Roles */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-medium text-foreground">Target Job Roles</label>
                  <span className="text-[11px] text-muted-foreground">Select from 10 industry roles</span>
                </div>
                <div className="flex gap-2">
                  <select
                    value={selectedRoleDropdown}
                    onChange={(e) => setSelectedRoleDropdown(e.target.value)}
                    disabled={isSaving}
                    className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-xs sm:text-sm text-foreground shadow-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  >
                    {PREDEFINED_JOB_ROLES.map((role) => (
                      <option key={role} value={role} className="bg-background text-foreground">
                        {role}
                      </option>
                    ))}
                  </select>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={addRole}
                    disabled={isSaving || targetRoles.includes(selectedRoleDropdown)}
                    className="gap-1 text-xs shrink-0"
                  >
                    <Plus className="h-4 w-4" />
                    Add Role
                  </Button>
                </div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {targetRoles.length === 0 ? (
                    <span className="text-xs text-muted-foreground italic">No target roles selected. Pick from the list above.</span>
                  ) : (
                    targetRoles.map((role) => (
                      <Badge key={role} variant="default" className="gap-1 pl-2.5 pr-1.5 py-1 text-xs">
                        {role}
                        <button
                          type="button"
                          onClick={() => removeRole(role)}
                          className="hover:bg-primary-700 rounded-full p-0.5 text-primary-foreground"
                          aria-label={`Remove ${role}`}
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </Badge>
                    ))
                  )}
                </div>
              </div>

              {/* Target Companies */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-slate-700">Target Companies</label>
                <div className="flex gap-2">
                  <Input
                    placeholder="e.g. Google, Microsoft, Amazon, TCS, Infosys"
                    value={newCompanyInput}
                    onChange={(e) => setNewCompanyInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        addCompany();
                      }
                    }}
                    disabled={isSaving}
                  />
                  <Button type="button" variant="secondary" onClick={addCompany} disabled={isSaving} className="gap-1">
                    <Plus className="h-4 w-4" />
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {targetCompanies.length === 0 ? (
                    <span className="text-xs text-muted-foreground italic">No companies added yet.</span>
                  ) : (
                    targetCompanies.map((comp) => (
                      <Badge key={comp} variant="secondary" className="gap-1 pl-2.5 pr-1.5 py-1 text-xs">
                        {comp}
                        <button
                          type="button"
                          onClick={() => removeCompany(comp)}
                          className="hover:bg-slate-200 rounded-full p-0.5 text-muted-foreground hover:text-foreground"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </Badge>
                    ))
                  )}
                </div>
              </div>

              {/* CTC & Locations */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-700">Target CTC (LPA in ₹)</label>
                  <Input
                    type="number"
                    step="0.5"
                    min={0}
                    placeholder="e.g. 15.0"
                    value={targetCtcLpa}
                    onChange={(e) => setTargetCtcLpa(e.target.value === "" ? "" : Number(e.target.value))}
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-medium text-slate-700">Preferred Locations</label>
                  <div className="flex gap-2">
                    <Input
                      placeholder="e.g. Bangalore, Hyderabad, Remote"
                      value={newLocationInput}
                      onChange={(e) => setNewLocationInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          addLocation();
                        }
                      }}
                      disabled={isSaving}
                    />
                    <Button type="button" variant="secondary" onClick={addLocation} disabled={isSaving} className="gap-1">
                      <Plus className="h-4 w-4" />
                      Add
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {preferredLocations.map((loc) => (
                      <Badge key={loc} variant="outline" className="gap-1 pl-2.5 pr-1.5 py-1 text-xs">
                        {loc}
                        <button
                          type="button"
                          onClick={() => removeLocation(loc)}
                          className="hover:bg-slate-100 rounded-full p-0.5 text-muted-foreground hover:text-foreground"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <Button type="submit" disabled={isSaving} className="gap-2">
                  <Save className="h-4 w-4" />
                  {isSaving ? "Saving..." : "Save Placement Goals"}
                </Button>
              </div>
            </CardContent>
          </form>
        </Card>
      )}
    </div>
  );
}

