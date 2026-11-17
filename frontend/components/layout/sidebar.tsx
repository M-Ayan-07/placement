"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  CheckSquare,
  Sparkles,
  MessageSquare,
  FileText,
  Mic,
  User,
  GraduationCap,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Assessments", href: "/assessments", icon: CheckSquare },
  { name: "Preparation Plan", href: "/recommendations", icon: Sparkles },
  { name: "Placement Chatbot", href: "/chat", icon: MessageSquare },
  { name: "Resume Scanner", href: "/resume", icon: FileText },
  { name: "Interview Practice", href: "/interview", icon: Mic },
  { name: "Profile & Goals", href: "/profile", icon: User },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "w-64 border-r border-border bg-card flex flex-col h-screen fixed left-0 top-0 z-50 select-none transition-transform duration-300 ease-in-out lg:translate-x-0",
        isOpen ? "translate-x-0 shadow-2xl" : "-translate-x-full"
      )}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-5 border-b border-border">
        <div className="flex items-center gap-2.5">
          <div className="h-9 w-9 rounded-lg bg-primary flex items-center justify-center text-primary-foreground shadow-sm shrink-0">
            <GraduationCap className="h-5 w-5" />
          </div>
          <div className="flex flex-col">
            <span className="font-semibold text-sm tracking-tight text-foreground truncate" title="AI-Powered Placement Coach">
              AI Placement Coach
            </span>
            <span className="text-[11px] text-muted-foreground font-mono">v1.0 • AI Campus Prep</span>
          </div>
        </div>

        {/* Mobile close button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          className="lg:hidden h-8 w-8 p-0 text-muted-foreground hover:text-foreground"
          aria-label="Close navigation"
        >
          <X className="h-5 w-5" />
        </Button>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onClose}
              className={cn(
                "flex items-center gap-3 px-3.5 py-2.5 rounded-md text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary-50 dark:bg-primary/10 text-primary font-semibold shadow-xs"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              )}
            >
              <Icon className={cn("h-4 w-4 shrink-0", isActive ? "text-primary" : "text-muted-foreground")} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-border bg-muted/40">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Campus Readiness</span>
          <span className="font-mono text-[10px] bg-background px-1.5 py-0.5 rounded border border-border">
            100% Free Tier
          </span>
        </div>
      </div>
    </aside>
  );
}
