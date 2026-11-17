# UI Design System — AI-Powered Placement Coach

> **Stack:** Next.js 14+ (App Router) · Tailwind CSS · shadcn/ui (Radix UI) · lucide-react · TanStack Query

---

## 0. Product Design Philosophy & Visual Standards

The application must look and feel like an authentic, high-craft, professional SaaS workspace — never an AI-generated template or generic hackathon demo.

### 0.1 Strict Anti-Patterns (Banned)
- ❌ **No excessive gradients or multicolor backdrops**: No rainbow sweeps or multi-stop gradients across page backgrounds.
- ❌ **No glassmorphism or blur gimmicks**: No `backdrop-blur-md` panels with semi-transparent white borders mimicking futuristic frosted glass.
- ❌ **No neon glows or pulsating halos**: No pulsing colored rings around cards, buttons, or AI chat bubbles.
- ❌ **No meaningless animations**: No floating particles, bouncy layout transitions, or distracting micro-animations. Animations are restricted to fast, functional state shifts (e.g. 150ms ease-out dropdown/modal reveals).
- ❌ **No repetitive cookie-cutter card grids**: Avoid landing-page style rows of 3 identical rectangular cards with huge icons and 2 lines of text. Content structure must dictate layout.
- ❌ **No fake statistics or placeholder vanity metrics**: No static counters reading "98% placement rate" or "10,000+ active recruiters". Every metric displayed on the dashboard must be derived from genuine user test sessions, resume analyses, and interview logs.
- ❌ **No decorative or non-functional interactions**: Every button, chip, and dropdown must perform a real action. No dummy "Share" or "Filter" buttons that do nothing.

### 0.2 Required Standards
- ✅ **Restrained, purpose-driven visual identity**: Crisp neutral backgrounds (`#F8FAFC` slate-50), subtle borders (`#E2E8F0` slate-200), and deep high-contrast text (`#0F172A` slate-900).
- ✅ **Purposeful semantic color accents**: Colors are used strictly to communicate status or category (Emerald for completed/strong areas, Amber for revision needed, Crimson for weak topics, Indigo for primary actions).
- ✅ **Clear typographic hierarchy**: Dense, readable interface typography using `Inter` with strict sizing and line-height scales. Code blocks and technical terms use `JetBrains Mono`.
- ✅ **Four-state completeness**: Every view and interactive component must define all four UI states:
  1. **Loading state**: Structural skeleton placeholders matching actual content dimensions (no generic full-screen spinners).
  2. **Empty state**: Informative explanation of why the view is empty, what will appear once used, and a primary CTA (e.g., "No assessments taken yet. Start a 15-minute diagnostic test to unlock your readiness score.").
  3. **Success state**: Unobtrusive confirmation (crisp toast or inline status badge) with updated data.
  4. **Error state**: Clear, human-readable error description with an immediate retry button (especially crucial for AI rate limits).

---

## Table of Contents

0. [Product Design Philosophy & Visual Standards](#0-product-design-philosophy--visual-standards)
1. [Design Tokens](#1-design-tokens)
2. [shadcn/ui Component Usage](#2-shadcnui-component-usage)
3. [Page Layout Structure](#3-page-layout-structure)
4. [Key Component Specifications](#4-key-component-specifications)
5. [Responsive Breakpoints](#5-responsive-breakpoints)
6. [Next.js App Router Page Map](#6-nextjs-app-router-page-map)

---

## 1. Design Tokens

All tokens are defined in `tailwind.config.ts` under `theme.extend`. Import the config in `app/globals.css` using CSS custom properties so shadcn/ui can consume them.

### 1.1 Color Palette

```ts
// tailwind.config.ts → theme.extend.colors
colors: {
  primary: {
    DEFAULT: '#4F46E5', // Indigo-600 — primary actions, active nav
    foreground: '#FFFFFF',
    50:  '#EEF2FF',
    100: '#E0E7FF',
    200: '#C7D2FE',
    300: '#A5B4FC',
    400: '#818CF8',
    500: '#6366F1',
    600: '#4F46E5',
    700: '#4338CA',
    800: '#3730A3',
    900: '#312E81',
  },
  secondary: {
    DEFAULT: '#0EA5E9', // Sky-500 — highlights, links, info chips
    foreground: '#FFFFFF',
    50:  '#F0F9FF',
    500: '#0EA5E9',
    700: '#0369A1',
  },
  accent: {
    DEFAULT: '#8B5CF6', // Violet-500 — AI/chatbot identity colour
    foreground: '#FFFFFF',
    50:  '#F5F3FF',
    500: '#8B5CF6',
    700: '#6D28D9',
  },
  success: {
    DEFAULT: '#10B981', // Emerald-500
    foreground: '#FFFFFF',
    light: '#D1FAE5',
  },
  warning: {
    DEFAULT: '#F59E0B', // Amber-500
    foreground: '#1C1917',
    light: '#FEF3C7',
  },
  error: {
    DEFAULT: '#EF4444', // Red-500
    foreground: '#FFFFFF',
    light: '#FEE2E2',
  },
  neutral: {
    0:   '#FFFFFF',
    50:  '#F8FAFC',
    100: '#F1F5F9',
    200: '#E2E8F0',
    300: '#CBD5E1',
    400: '#94A3B8',
    500: '#64748B',
    600: '#475569',
    700: '#334155',
    800: '#1E293B',
    900: '#0F172A',
    950: '#020617',
  },
}
```

**Semantic aliases** (set as CSS variables in `globals.css`, consumed by shadcn/ui):

```css
/* app/globals.css */
:root {
  --background:         #F8FAFC;   /* neutral-50  */
  --foreground:         #0F172A;   /* neutral-900 */
  --card:               #FFFFFF;
  --card-foreground:    #1E293B;
  --popover:            #FFFFFF;
  --popover-foreground: #0F172A;
  --muted:              #F1F5F9;   /* neutral-100 */
  --muted-foreground:   #64748B;   /* neutral-500 */
  --border:             #E2E8F0;   /* neutral-200 */
  --input:              #E2E8F0;
  --ring:               #4F46E5;   /* primary     */
}
.dark {
  --background:         #0F172A;
  --foreground:         #F8FAFC;
  --card:               #1E293B;
  --card-foreground:    #F1F5F9;
  --popover:            #1E293B;
  --popover-foreground: #F8FAFC;
  --muted:              #1E293B;
  --muted-foreground:   #94A3B8;
  --border:             #334155;
  --input:              #334155;
  --ring:               #818CF8;
}
```

---

### 1.2 Typography

```ts
// tailwind.config.ts → theme.extend
fontFamily: {
  sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
  mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'monospace'],
},
fontSize: {
  xs:   ['12px', { lineHeight: '16px' }],
  sm:   ['14px', { lineHeight: '20px' }],
  base: ['16px', { lineHeight: '24px' }],
  lg:   ['18px', { lineHeight: '28px' }],
  xl:   ['20px', { lineHeight: '28px' }],
  '2xl':['24px', { lineHeight: '32px' }],
  '3xl':['30px', { lineHeight: '36px' }],
  '4xl':['36px', { lineHeight: '40px' }],
},
fontWeight: {
  normal:   '400',
  medium:   '500',
  semibold: '600',
  bold:     '700',
},
```

**Usage rules:**
- Page headings: `font-sans font-bold text-2xl text-neutral-900`
- Section headings: `font-sans font-semibold text-xl text-neutral-800`
- Body text: `font-sans font-normal text-base text-neutral-700`
- Code / monospaced output: `font-mono text-sm text-neutral-800 bg-neutral-100`
- Labels & captions: `font-sans font-medium text-xs text-neutral-500`

Load fonts in `app/layout.tsx` via `next/font/google`:

```ts
import { Inter, JetBrains_Mono } from 'next/font/google'

const inter         = Inter({ subsets: ['latin'], variable: '--font-sans' })
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono' })
```

---

### 1.3 Spacing Scale

Uses Tailwind's default 4 px base unit (1 unit = 4 px). Key named steps used throughout the app:

| Token      | Value | Use case                            |
|------------|-------|-------------------------------------|
| `space-1`  | 4 px  | Icon padding, tight inline gaps     |
| `space-2`  | 8 px  | Between badge and text              |
| `space-3`  | 12 px | Form field internal padding         |
| `space-4`  | 16 px | Card padding (mobile)               |
| `space-5`  | 20 px | Section gap                         |
| `space-6`  | 24 px | Card padding (desktop)              |
| `space-8`  | 32 px | Section vertical rhythm             |
| `space-12` | 48 px | Page section separation             |
| `space-16` | 64 px | Large hero gap                      |

Sidebar width: `w-64` (256 px desktop), `w-16` (64 px collapsed).  
Top bar height: `h-16` (64 px).  
Bottom nav height: `h-16` (64 px mobile).

---

### 1.4 Border Radius Tokens

```ts
borderRadius: {
  none:    '0',
  sm:      '4px',
  DEFAULT: '8px',
  md:      '8px',
  lg:      '12px',
  xl:      '16px',
  '2xl':   '20px',
  full:    '9999px',
},
```

| Element                       | Token        |
|-------------------------------|--------------|
| Buttons                       | `rounded-md` |
| Cards                         | `rounded-xl` |
| Badges / chips                | `rounded-full` |
| Input fields                  | `rounded-md` |
| Modals / desktop dialogs      | `rounded-xl` |
| Mobile bottom sheets (top)    | `rounded-2xl` |
| Avatars                       | `rounded-full` |
| Code blocks                   | `rounded-lg` |

---

### 1.5 Shadow Tokens

```ts
boxShadow: {
  sm:             '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  DEFAULT:        '0 1px 3px 0 rgb(0 0 0 / 0.10), 0 1px 2px -1px rgb(0 0 0 / 0.10)',
  md:             '0 4px 6px -1px rgb(0 0 0 / 0.10), 0 2px 4px -2px rgb(0 0 0 / 0.10)',
  lg:             '0 10px 15px -3px rgb(0 0 0 / 0.10), 0 4px 6px -4px rgb(0 0 0 / 0.10)',
  xl:             '0 20px 25px -5px rgb(0 0 0 / 0.10), 0 8px 10px -6px rgb(0 0 0 / 0.10)',
  inner:          'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
  'primary-glow': '0 4px 24px 0 rgb(79 70 229 / 0.18)',
  'accent-glow':  '0 4px 24px 0 rgb(139 92 246 / 0.18)',
  none:           'none',
},
```

| Element                          | Token                |
|----------------------------------|----------------------|
| Default card                     | `shadow-md`          |
| Active / focused card            | `shadow-lg`          |
| Top bar                          | `shadow-sm`          |
| Floating action button           | `shadow-xl`          |
| AI chatbot bubble highlight      | `shadow-accent-glow` |

---

## 2. shadcn/ui Component Usage

Install components with `npx shadcn-ui@latest add <name>`. All components live in `components/ui/`.

### 2.1 Feature → Component Matrix

| Feature | Page(s) | shadcn/ui Components |
|---------|---------|----------------------|
| **Student Profile & Goals** | `/profile`, `/goals` | `Avatar`, `Card`, `Input`, `Textarea`, `Select`, `Button`, `Badge`, `Separator`, `Form` (react-hook-form) |
| **Aptitude & Technical Assessments** | `/assessments`, `/assessments/[id]`, `/assessments/[id]/results` | `Card`, `Badge`, `Button`, `Progress`, `RadioGroup`, `Checkbox`, `Tabs`, `Alert`, `Skeleton`, `Separator` |
| **Personalised Recommendations** | `/recommendations` | `Card`, `Badge`, `Button`, `Accordion`, `Tabs`, `Progress`, `HoverCard`, `Tooltip` |
| **AI Chatbot** | `/chat`, `/chat/[sessionId]` | `ScrollArea`, `Input`, `Button`, `Avatar`, `Badge`, `Separator`, `Sheet` (mobile session switcher), `DropdownMenu` |
| **Resume Scanner** | `/resume` | `Card`, `Button`, `Badge`, `Progress`, `Alert`, `Select`, `Separator`, `Tooltip`, `Table` |
| **Interview Practice** | `/interview`, `/interview/[sessionId]`, `/interview/[sessionId]/report` | `Card`, `Button`, `Badge`, `Progress`, `Tabs`, `Accordion`, `Alert`, `Separator`, `Dialog` (end-session confirm) |
| **Progress Dashboard** | `/dashboard` | `Card`, `Progress`, `Badge`, `Tabs`, `Button`, `Table`, `Skeleton`, `Separator`, `Tooltip` |

### 2.2 Component Customisations

#### `Button`

Add two extra variants in `components/ui/button.tsx`:

```ts
// variant: "ai"  — used for AI-initiated actions
ai: 'bg-accent text-white hover:bg-accent/90 shadow-accent-glow',

// variant: "ghost-danger"  — destructive ghost (e.g., end session)
'ghost-danger': 'text-error hover:bg-error/10 hover:text-error',
```

#### `Badge`

Add variant `"score"` for readiness score chips:

```ts
score: 'bg-primary/10 text-primary border border-primary/20 font-semibold',
```

Add variant `"difficulty"` — apply colour via additional className in JSX:

| Level  | Classes applied to badge                            |
|--------|-----------------------------------------------------|
| Easy   | `bg-success/10 text-success border-success/20`      |
| Medium | `bg-warning/10 text-warning border-warning/20`      |
| Hard   | `bg-error/10 text-error border-error/20`            |

#### `Card`

Register a utility class `placement-card` in `globals.css`:

```css
.placement-card {
  @apply rounded-xl border border-neutral-200 bg-white shadow-md
         dark:border-neutral-700 dark:bg-neutral-800;
}
```

#### `Progress`

Override the indicator colour via the CSS variable `--progress-indicator` to support state-aware colouring:

| Score range | Indicator colour |
|-------------|-----------------|
| ≥ 80        | `bg-success`    |
| 40–79       | `bg-warning`    |
| < 40        | `bg-error`      |
| Default     | `bg-primary`    |

#### `ScrollArea`

Set `type="auto"` and style the scrollbar thumb in chat and result panels:

```html
<ScrollArea
  type="auto"
  className="[&>div]:scrollbar-thin [&>div]:scrollbar-thumb-neutral-300"
>
```

---

## 3. Page Layout Structure

### 3.1 App Shell

The root layout (`app/(app)/layout.tsx`) renders the shell for all authenticated pages.

```
┌──────────────────────────────────────────────────────┐
│  TopBar  (h-16, sticky top-0, z-40)                  │
├─────────────────┬────────────────────────────────────┤
│                 │                                    │
│  Sidebar        │   <main>                           │
│  (w-64, fixed)  │   px-6 py-8                        │
│  (lg: visible)  │   max-w-7xl mx-auto                │
│                 │                                    │
└─────────────────┴────────────────────────────────────┘
│  BottomNav  (h-16, fixed bottom-0, lg:hidden)        │
└──────────────────────────────────────────────────────┘
```

- **Sidebar** — `fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 hidden lg:flex flex-col`.
- **Main content** — `lg:pl-64 pb-16 lg:pb-0` (bottom padding clears mobile BottomNav).
- **BottomNav** — `fixed bottom-0 inset-x-0 h-16 lg:hidden z-40`.

### 3.2 Sidebar Navigation

**File:** `components/layout/Sidebar.tsx`

```tsx
import {
  LayoutDashboard, ClipboardList, Lightbulb,
  MessageSquare, FileText, Mic, UserCircle,
} from 'lucide-react'

const navItems = [
  { label: 'Dashboard',       href: '/dashboard',       icon: LayoutDashboard },
  { label: 'Assessments',     href: '/assessments',     icon: ClipboardList   },
  { label: 'Recommendations', href: '/recommendations', icon: Lightbulb       },
  { label: 'Chat',            href: '/chat',            icon: MessageSquare   },
  { label: 'Resume',          href: '/resume',          icon: FileText        },
  { label: 'Interview',       href: '/interview',       icon: Mic             },
  { label: 'Profile',         href: '/profile',         icon: UserCircle      },
]
```

Active state (detected with `usePathname()`):
```
bg-primary/10 text-primary font-semibold rounded-lg
```

Inactive state:
```
text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 rounded-lg
```

Each item: `flex items-center gap-3 px-3 py-2.5 text-sm transition-colors`.

**Sidebar footer:** user `<Avatar>` (32 px) + display name (`text-sm font-medium`) + `<LogOut>` icon `<Button variant="ghost" size="icon">`.

#### Collapsed Sidebar (tablet 640–1023 px)

Width shrinks to `w-16`; only icons are rendered. Each icon is wrapped in a `<Tooltip>` (shadcn/ui, `side="right"`) displaying the label. A `<ChevronRight>` / `<ChevronLeft>` toggle button is pinned at `top-4 -right-3` to expand/collapse.

### 3.3 Top Bar

**File:** `components/layout/TopBar.tsx`

```
┌────────────────────────────────────────────────────────────┐
│ [≡ Menu]   PlacementAI logo + wordmark    [🔔]  [Avatar ▾] │
└────────────────────────────────────────────────────────────┘
```

- **Left:** `<Button variant="ghost" size="icon">` with `<Menu>` icon — visible `lg:hidden` — opens `<Sheet side="left">` containing full nav. Logo `<Image>` + `"PlacementAI"` wordmark visible on `lg:`.
- **Centre (mobile only):** Current page title derived from `usePathname()`.
- **Right:**
  - `<Bell>` icon button with an absolute-positioned 8 px `bg-error rounded-full` dot for unread notifications.
  - `<DropdownMenu>` triggered by user avatar: items = View Profile, Settings, Divider, Sign Out.

### 3.4 Bottom Navigation (Mobile)

**File:** `components/layout/BottomNav.tsx`

Displays 5 primary nav items. All 7 items accessible via the hamburger `<Sheet>`.

```
┌──────────────────────────────────────────────┐
│ Dashboard  Assessments  Chat  Interview  Profile │
└──────────────────────────────────────────────┘
```

Each item: `flex flex-col items-center gap-0.5 pt-2 text-[10px]`.  
Active: `text-primary`.  Inactive: `text-neutral-400`.

---

## 4. Key Component Specifications

### 4.1 `<AssessmentTimer />`

**File:** `components/assessment/AssessmentTimer.tsx`

```ts
interface AssessmentTimerProps {
  totalSeconds:     number          // full duration of the assessment
  remainingSeconds: number          // controlled externally via useTimer hook
  onExpire:         () => void      // fires when remainingSeconds reaches 0
  variant?:         'compact' | 'full'
  // compact = Clock icon + "mm:ss" inline text
  // full    = SVG ring + centred mm:ss + caption
}
```

**Warning state thresholds:**

| Remaining        | Ring / text colour | Extra behaviour               |
|------------------|--------------------|-------------------------------|
| > 50 %           | `text-success`     | —                             |
| 25 – 50 %        | `text-warning`     | —                             |
| < 25 %           | `text-error`       | `animate-pulse` on text       |
| 0                | —                  | `onExpire()` → auto-submit    |

**Full variant layout:**

```
     ╭──────────╮
    ╱   12:34    ╲    ← SVG circle (r=20, strokeWidth=3)
   │  Time Left   │   ← caption  text-xs text-neutral-500
    ╲            ╱
     ╰──────────╯
```

SVG circle: `stroke-dasharray = 2πr`, `stroke-dashoffset` interpolated from `remainingSeconds / totalSeconds`. Animated with `transition-all duration-1000 ease-linear`.

**Compact variant:** `<Clock className="w-4 h-4 mr-1" /> 12:34` — inline, used inside `<QuestionCard />` header.

---

### 4.2 `<ChatWindow />`

**File:** `components/chat/ChatWindow.tsx`

```ts
interface ChatSession {
  id:        string
  title:     string
  createdAt: string
  preview:   string   // last message snippet
}

interface ChatWindowProps {
  sessionId:       string
  sessions:        ChatSession[]
  onNewSession:    () => void
  onSelectSession: (id: string) => void
}
```

**Layout:**

```
┌──────────────────────────────────────────────────────┐
│ [◀ Sessions]  "Placement Prep · Session 3"  [⋮]      │  h-14, border-b
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌─[AI]─────────────────────────────────────────┐   │
│  │ How can I help you prepare today?             │   │
│  └───────────────────────────────────────────────┘   │
│                                                      │
│          ┌─────────────────────────────────[U]─┐     │
│          │  What topics should I focus on?      │     │
│          └─────────────────────────────────────┘     │
│                                                      │
│  ┌─[AI]─────────────────────────────────────────┐   │
│  │ Based on your profile, focus on …            │   │
│  └───────────────────────────────────────────────┘   │
│                   ● ● ●  (loading indicator)          │
├──────────────────────────────────────────────────────┤
│ [📎]  [ Type a message…                   ]  [Send ➤] │  h-14
└──────────────────────────────────────────────────────┘
```

- **Message list:** `<ScrollArea className="flex-1">` — auto-scrolls to bottom (`useEffect` on message array change).
- **AI bubble:** `bg-accent/10 text-neutral-800 rounded-xl rounded-tl-none max-w-[75%]` + 32 px `<Avatar>` with robot icon.
- **User bubble:** `bg-primary text-white rounded-xl rounded-tr-none max-w-[75%] self-end`.
- **Timestamps:** `text-xs text-neutral-400 opacity-0 group-hover:opacity-100 transition-opacity`.
- **Loading indicator:** Three dots (`●●●`) inside an AI bubble, using `animate-bounce` with staggered `animation-delay`.

**Session Switcher:**
- `<Sheet side="left" className="w-72">` containing a search `<Input>` at the top and a list of `ChatSession` cards. Each card: title, date, preview truncated to 1 line.
- Triggered by `◀ Sessions` button (desktop + mobile).

**InputBar:**
- `<Textarea rows={1}` auto-resizes up to 4 rows via `onInput` height adjustment.
- `Enter` sends the message; `Shift+Enter` inserts a newline.
- Attachment `<Button variant="ghost" size="icon">` with `<Paperclip>` icon — reserved for injecting resume context into the session.

---

### 4.3 `<ResumeUploadCard />`

**File:** `components/resume/ResumeUploadCard.tsx`

```ts
interface ResumeUploadCardProps {
  onFileAccepted: (file: File) => void
  targetRole:     string
  onRoleChange:   (role: string) => void
  isAnalysing:    boolean
}
```

**Layout:**

```
┌─────────────────────────────────────────────────────┐
│  Target Role:  [ Select role…                  ▾ ]  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐  │
│  |   ☁  Drag & drop your resume here            |  │
│  |      or click to browse                      |  │
│  |      Accepts PDF · DOCX — max 5 MB           |  │
│  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘  │
│                                                     │
│  [ Analyse Resume ]                                 │
└─────────────────────────────────────────────────────┘
```

**Role selector options (`<Select>`):**

Software Engineer · Data Analyst · Product Manager · DevOps Engineer ·  
Business Analyst · Frontend Developer · Backend Developer ·  
Full-Stack Developer · ML Engineer

**Drop zone states:**

| State           | Classes                                               |
|-----------------|-------------------------------------------------------|
| Idle            | `border-2 border-dashed border-neutral-300 rounded-xl p-10` |
| Drag-over       | `border-primary bg-primary/5`                         |
| File accepted   | `border-success bg-success/5` + filename + `<CheckCircle className="text-success">` |
| Error (type/size) | `border-error bg-error/5` + `<Alert variant="destructive">` |

- Implemented via native `onDragOver`, `onDragLeave`, `onDrop` + hidden `<input type="file" accept=".pdf,.docx">`.
- `isAnalysing=true`: renders `<Progress>` bar beneath the drop zone with animated label `"Analysing your resume…"`.

---

### 4.4 `<ProgressRing />`

**File:** `components/shared/ProgressRing.tsx`

```ts
interface ProgressRingProps {
  value:        number        // 0–100 readiness score
  size?:        number        // SVG diameter in px, default 120
  strokeWidth?: number        // default 10
  label?:       string        // e.g. "Readiness Score"
  showValue?:   boolean       // default true
}
```

**Visual:**

```
       ╭──────────╮
      ╱    78 %    ╲   ← score, text-2xl font-bold  (colour matches stroke)
     │  Readiness   │  ← label, text-xs text-neutral-500
      ╲  Score     ╱
       ╰──────────╯
```

**SVG construction:**

```
cx = cy = size / 2
r  = (size - strokeWidth) / 2
circumference = 2 * Math.PI * r
dashoffset    = circumference * (1 - value / 100)
```

- Track circle: `stroke="var(--border)" fill="none"`.
- Indicator circle: `stroke={indicatorColour} fill="none" strokeLinecap="round"` + `transition-all duration-700 ease-out`.
- `transform="rotate(-90 cx cy)"` so progress starts from 12 o'clock.

**Indicator colour thresholds:**

| `value` | `stroke` colour |
|---------|----------------|
| ≥ 75    | `#10B981` (success) |
| 50–74   | `#4F46E5` (primary) |
| 25–49   | `#F59E0B` (warning) |
| < 25    | `#EF4444` (error)   |

Used on: Dashboard hero card (size=140), Profile page sidebar (size=100), Recommendations card (size=80).

---

### 4.5 `<QuestionCard />`

**File:** `components/assessment/QuestionCard.tsx`

```ts
interface QuestionOption {
  id:   string
  text: string
}

interface Question {
  id:         string
  index:      number               // 1-based display number
  total:      number
  text:       string
  options:    QuestionOption[]
  topic?:     string               // e.g. "Arrays"
  difficulty: 'easy' | 'medium' | 'hard'
}

interface QuestionCardProps {
  question:        Question
  selectedOption:  string | null
  onSelect:        (optionId: string) => void
  onNext:          () => void
  onPrevious:      () => void
  remainingSeconds: number
  totalSeconds:    number
}
```

**Layout:**

```
┌──────────────────────────────────────────────────────────┐
│  Q 4 / 20   [Arrays]  [Medium]              ⏱ 08:45     │  ← Header
├──────────────────────────────────────────────────────────┤
│                                                          │
│  What is the time complexity of binary search            │
│  on a sorted array of n elements?                        │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  ○  A.  O(n)                                             │
│  ●  B.  O(log n)          ← selected: bg-primary/10      │
│  ○  C.  O(n log n)                                       │
│  ○  D.  O(1)                                             │
├──────────────────────────────────────────────────────────┤
│  [ ← Previous ]                    [ Next Question → ]  │
└──────────────────────────────────────────────────────────┘
```

**Header row:** `flex items-center justify-between px-6 py-4 border-b`.  
- `Q {index} / {total}` — `text-sm font-semibold text-neutral-600`.
- Topic: `<Badge variant="secondary">`.
- Difficulty: `<Badge variant="difficulty" className={difficultyColour}>`.
- Timer: `<AssessmentTimer variant="compact" />`.

**Options (`<RadioGroup>`):**

Each `<label>` wraps `<RadioGroupItem>` + option text. Unselected:
```
border border-neutral-200 rounded-lg px-4 py-3 cursor-pointer hover:bg-neutral-50
```
Selected:
```
border-primary bg-primary/10 text-primary
```

**Navigation (`flex justify-between px-6 py-4 border-t`):**

- Previous: `<Button variant="outline" onClick={onPrevious} disabled={index === 1}>`.
- Next: `<Button variant="default" onClick={onNext}>Next Question</Button>`.
- On last question: Next button label becomes `"Submit Assessment"` and triggers `<Dialog>` confirmation before calling `onSubmit`.

---

## 5. Responsive Breakpoints

| Breakpoint | Viewport      | Tailwind prefix |
|------------|---------------|-----------------|
| Mobile     | < 640 px      | *(default)*     |
| Tablet     | 640–1023 px   | `sm:`           |
| Desktop    | ≥ 1024 px     | `lg:`           |

### 5.1 Navigation Behaviour

| Breakpoint | Behaviour |
|------------|-----------|
| **Mobile** (< 640 px) | Sidebar hidden entirely. BottomNav (`fixed bottom-0`) shows 5 icons with labels. Hamburger button in TopBar opens a `<Sheet side="left">` containing all 7 nav items + user info card. |
| **Tablet** (640–1023 px) | BottomNav hidden. Sidebar shown in icon-only collapsed state (`w-16`). Each icon has a `<Tooltip side="right">` label. A toggle button at `top-4 -right-3` of the sidebar expands it to `w-64`. |
| **Desktop** (≥ 1024 px) | Full sidebar (`w-64`) always visible with labels. BottomNav hidden. TopBar hamburger hidden. |

### 5.2 Content Grid Behaviour

| Area | Mobile | Tablet | Desktop |
|------|--------|--------|---------|
| Dashboard stat cards | 1 col | 2 cols | 3 cols |
| Assessment browse grid | 1 col | 2 cols | 3 cols |
| Chat layout | Full-width, no side panel | Full-width, no side panel | Split: session list `w-72` + chat panel `flex-1` |
| Resume page | Single column stacked | Single column stacked | Two columns — upload left (`w-2/5`) · results right (`w-3/5`) |
| Interview report | Single column | 2 cols | 2 cols |
| Recommendations | 1 col | 1 col | 2 cols |

Page container: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`.

---

## 6. Next.js App Router Page Map

`middleware.ts` guards all `(app)` routes. Unauthenticated requests redirect to `/login`; authenticated requests to `/login` or `/register` redirect to `/dashboard`.

### Auth Routes — `app/(auth)/`

Layout: `app/(auth)/layout.tsx` — clean, centred card on subtle neutral background (`bg-slate-50`).

| Route              | File                                    | Description |
|--------------------|-----------------------------------------|-------------|
| `/login`           | `app/(auth)/login/page.tsx`             | Email + password sign-in form; Google OAuth button; link to `/register`. |
| `/register`        | `app/(auth)/register/page.tsx`          | Name, email, password, institution, role (Student) fields. |
| `/forgot-password` | `app/(auth)/forgot-password/page.tsx`   | Email input; submits OTP request. |
| `/reset-password`  | `app/(auth)/reset-password/page.tsx`    | OTP entry + new password fields. Reads `?token=` from query string. |

---

### App Routes — `app/(app)/`

Layout: `app/(app)/layout.tsx` — renders `<TopBar />`, `<Sidebar />`, `<main>{children}</main>`, `<BottomNav />`.

| Route | File | Description |
|-------|------|-------------|
| `/` | `app/page.tsx` | Server component — redirects to `/dashboard` (authenticated) or `/login` (unauthenticated). |
| `/dashboard` | `app/(app)/dashboard/page.tsx` | Hero card with `<ProgressRing />` (readiness score), upcoming assessments list, recent activity feed, quick-action buttons (Start Assessment, Practice Interview, Open Chat). |
| `/profile` | `app/(app)/profile/page.tsx` | Avatar upload, personal info form (name, email, phone, institution, graduation year), skills multi-tag input, LinkedIn/GitHub URLs, save button. |
| `/goals` | `app/(app)/goals/page.tsx` | Target company cards (add/remove), target role selector, placement timeline date picker, per-company goal cards with inline `<ProgressRing />`. |
| `/assessments` | `app/(app)/assessments/page.tsx` | Filter bar (topic `<Select>`, difficulty `<RadioGroup>`, type `<Tabs>`), `<AssessmentCard />` grid with title, topic badge, difficulty badge, duration, attempt count. |
| `/assessments/[id]` | `app/(app)/assessments/[id]/page.tsx` | Assessment detail: description, syllabus `<Accordion>`, difficulty/duration/mark info, start button, previous attempts `<Table>` with score and date. |
| `/assessments/[id]/session` | `app/(app)/assessments/[id]/session/page.tsx` | Full-screen test session (uses its own layout — see below): `<QuestionCard />`, question palette sidebar (numbered grid, colour-coded: unanswered/answered/flagged), `<AssessmentTimer />` in header. |
| `/assessments/[id]/results` | `app/(app)/assessments/[id]/results/page.tsx` | Score card with `<ProgressRing />`, section-wise bar chart (`<Progress>`), per-question review accordion (selected answer, correct answer, explanation), share score button. |
| `/recommendations` | `app/(app)/recommendations/page.tsx` | Domain `<Tabs>` (DSA, System Design, Communication, Domain Knowledge). Per-domain learning path cards: topic name, `<Progress>`, resource links, estimated hours. `<Accordion>` for sub-topic details. |
| `/chat` | `app/(app)/chat/page.tsx` | Session list page: "New Chat" button, list of past `ChatSession` cards (title, date, preview). Selecting one navigates to `/chat/[sessionId]`. |
| `/chat/[sessionId]` | `app/(app)/chat/[sessionId]/page.tsx` | Full `<ChatWindow />` for the given session. Loads paginated message history server-side via `generateMetadata` + client-side streaming. |
| `/resume` | `app/(app)/resume/page.tsx` | Left/top: `<ResumeUploadCard />`. Right/bottom (after analysis): ATS score `<ProgressRing />`, keyword match `<Table>`, improvement suggestions list, detected skills `<Badge>` cloud, download-report button. |
| `/interview` | `app/(app)/interview/page.tsx` | Practice pack browse: `<Tabs>` (Technical, HR, Domain). Each tab lists packs as cards: title, description, question count, average duration, difficulty badge, start button. |
| `/interview/[sessionId]` | `app/(app)/interview/[sessionId]/page.tsx` | Interview session: question prompt, text `<Textarea>` response input, optional audio record toggle (`<Mic>` icon button), submit answer, next question. Per-question `<AssessmentTimer />`. |
| `/interview/[sessionId]/report` | `app/(app)/interview/[sessionId]/report/page.tsx` | Post-interview report: overall score, per-question feedback cards, model-answer `<Accordion>`, AI-generated strengths/improvements summary, retry button. |

---

### Special Files

| File | Purpose |
|------|---------|
| `app/layout.tsx` | Root layout — sets `<html lang="en" suppressHydrationWarning>`, injects Inter + JetBrains Mono font CSS variables, wraps content in `ThemeProvider`. |
| `app/(app)/assessments/[id]/session/layout.tsx` | Overrides the app shell for test sessions — no sidebar, no bottom nav, no top bar hamburger. Renders a minimal bar: logo + `<AssessmentTimer variant="full" />` + submit button. |
| `app/not-found.tsx` | Custom 404 — illustration, "Page not found" heading, "Go to Dashboard" `<Button>`. |
| `app/error.tsx` | Global error boundary — error message, "Try Again" button calling `reset()`. |
| `middleware.ts` | Auth guard via access/refresh token cookie. Public paths: `/login`, `/register`. Protects all `/(app)/**` routes. |
| `lib/api.ts` | Centralized Axios/fetch client communicating with FastAPI backend (`NEXT_PUBLIC_API_URL`). Handles JWT injection and refresh token rotation. |
| `hooks/*` | Dedicated TanStack Query hooks for all backend interactions (`useProfile`, `useAssessments`, `useChat`, `useResume`, `useInterview`, `useDashboard`). |

---

*PlacementAI Design System v1.0 — last updated 2026-10-31*
