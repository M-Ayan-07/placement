"use client";

import { useAuth } from "@/components/layout/providers/auth-provider";
import { ThemeToggle } from "@/components/layout/providers/theme-provider";
import { Button } from "@/components/ui/button";
import { LogOut, UserCircle, Menu } from "lucide-react";

interface TopBarProps {
  title?: string;
  onMenuClick?: () => void;
}

export function TopBar({ title, onMenuClick }: TopBarProps) {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 border-b border-border bg-card/80 backdrop-blur-xs px-4 sm:px-6 lg:px-8 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-3">
        {/* Mobile Hamburger Menu Toggle */}
        <Button
          variant="outline"
          size="sm"
          onClick={onMenuClick}
          className="lg:hidden h-9 w-9 p-0 text-foreground border-border hover:bg-secondary"
          aria-label="Open navigation menu"
        >
          <Menu className="h-5 w-5" />
        </Button>

        <h1 className="text-sm sm:text-base font-semibold text-foreground tracking-tight truncate max-w-[200px] sm:max-w-md">
          {title || "Placement Coach"}
        </h1>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        <ThemeToggle />

        {user ? (
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="flex items-center gap-2 text-sm text-foreground">
              <UserCircle className="h-5 w-5 text-muted-foreground shrink-0" />
              <span className="font-medium hidden sm:inline max-w-[140px] md:max-w-[180px] truncate">
                {user.profile?.full_name || user.email}
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => logout()}
              className="gap-1.5 text-xs border-border hover:bg-secondary text-muted-foreground hover:text-foreground h-9 px-2.5 sm:px-3"
            >
              <LogOut className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Sign Out</span>
            </Button>
          </div>
        ) : null}
      </div>
    </header>
  );
}
