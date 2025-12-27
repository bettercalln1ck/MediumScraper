# 💜 Lovable Quick Start - Copy & Paste Prompts

## 🚀 Instant App Prompts

Copy any of these prompts directly into Lovable.dev to build an app in 60 seconds!

---

### 1️⃣ Simple Q&A Browser (Beginner)

```
Build an iOS Q&A browser:

- Single page app
- "Load Questions" button that fetches from:
  GET https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/api/qa?limit=20
- Display Q&A in clean cards
- Each card shows question, answer, and source link
- Use Tailwind CSS with blue color scheme
- Add loading spinner
- Mobile responsive
```

---

### 2️⃣ Random Question Generator (Beginner)

```
Create a random iOS question generator:

- Landing page with big "Get Random Question" button
- Clicking calls:
  POST https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/api/scrape/random?count=1
- Show loading state while processing
- Poll job status every 2 seconds:
  GET https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/api/jobs/{job_id}
- When complete, display the Q&A
- "Get Another" button
- Minimalist design
- Use React Query for API calls
```

---

### 3️⃣ Flashcard Study App (Beginner)

```
Build an iOS interview flashcard app:

FEATURES:
- Fetch 50 questions on load from:
  GET https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/api/qa?limit=50
- Show one question at a time in a large card
- "Reveal Answer" button with flip animation
- "Next" and "Previous" navigation buttons
- Progress indicator (Question 5/50)
- Keyboard shortcuts: Space = reveal, Arrow keys = navigate
- Clean, minimal design with large readable fonts
- Use Tailwind CSS
```

---

### 4️⃣ Interview Prep Dashboard (Intermediate)

```
Create an iOS interview prep dashboard:

PAGES:
1. Home - Hero with stats
2. Discover - Scrape random articles
3. Browse - View all Q&A
4. Practice - Flashcard mode

DISCOVER PAGE:
- Input for count (1-10)
- "Discover Random Articles" button
- Calls: POST https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/api/scrape/random?count=X
- Show job queue with real-time status
- Use React Query for polling

BROWSE PAGE:
- Fetch from: GET https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/api/qa?limit=50&offset=0
- Search bar to filter questions
- Pagination
- "Copy to Clipboard" button per Q&A

PRACTICE PAGE:
- Flashcard interface
- Track which questions practiced

Use Tailwind CSS, Lucide icons, React Query, dark mode toggle
```

---

### 5️⃣ Article Scraper UI (Intermediate)

```
Build a Medium article scraper interface:

FEATURES:
1. URL input form
2. "Scrape Article" button that calls:
   POST https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/api/scrape
   Body: {"url": "entered-url"}
3. Job status tracker with progress indicator
4. Real-time status updates (poll every 2 seconds)
5. Display extracted Q&A when complete
6. Job history list
7. Export results as JSON
8. Stats: Total jobs, success rate, Q&A collected

Use React Query, Tailwind CSS, Radix UI components
Add toast notifications for success/errors
```

---

### 6️⃣ Full Knowledge Base (Advanced)

```
Create a comprehensive iOS knowledge base platform:

LAYOUT:
- Sidebar navigation
- Header with stats and dark mode toggle
- Main content area

PAGES:

HOME:
- Hero section
- Feature cards
- Recent Q&A feed
- System stats

DISCOVER:
- Form to scrape custom URL
- "Random Articles" button (1-10 count)
- Job queue with status badges
- Real-time progress
- API: POST https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/api/scrape/random?count=X

BROWSE:
- Advanced search (filters by question text)
- Multi-select category tags
- Sort options (date, source, relevance)
- Infinite scroll
- Export buttons (JSON, CSV)
- Share on social media
- API: GET https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/api/qa?limit=50&offset=X

ANALYTICS:
- Charts: Q&A over time, success rate, top sources
- Statistics cards
- Activity timeline
- Use Recharts for visualizations
- API: GET https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/api/stats

PRACTICE:
- Flashcard mode
- Quiz mode
- Track progress
- Spaced repetition

SETTINGS:
- Theme customization
- Notification preferences
- Data export

TECH STACK:
- React Query for API calls
- Zustand for state management
- Recharts for analytics
- Radix UI for components
- Tailwind CSS for styling
- Lucide React for icons

Make it professional, modern, and fully responsive
```

---

## 🎯 Copy-Paste API Info

**Base URL:**
```
https://misleading-aile-personalnikhil-27cb1e20.koyeb.app
```

**Key Endpoints:**
```
GET  /api/discover?count=5
POST /api/scrape/random?count=3
POST /api/scrape (body: {"url": "..."})
GET  /api/jobs/{job_id}
GET  /api/jobs/{job_id}/results
GET  /api/qa?limit=50&offset=0
GET  /api/stats
```

---

## 💡 Iteration Prompts

After Lovable builds your app, use these to improve it:

```
Add dark mode toggle in the header
```

```
Make all cards have hover effects and shadows
```

```
Add a search bar that filters questions in real-time
```

```
Show loading skeletons while data is fetching
```

```
Add toast notifications for success and errors
```

```
Make it more colorful with gradient backgrounds
```

```
Add "Copy to Clipboard" button for each Q&A
```

```
Show a confetti animation when questions load
```

```
Add keyboard shortcuts for navigation
```

```
Make the layout more spacious with better padding
```

---

## 🎨 Style Variations

### iOS Blue Theme
```
Change the color scheme to iOS blue (#007AFF) as primary color
and iOS purple (#5856D6) as secondary
```

### Dark Professional
```
Make it dark mode by default with a professional color scheme:
background #1F2937, cards #374151, text white, accent purple #8B5CF6
```

### Minimal Clean
```
Make the design more minimal: remove borders, use subtle shadows,
increase whitespace, use system fonts
```

### Vibrant Modern
```
Make it vibrant and modern with gradients, glassmorphism effects,
animated transitions, and bold colors
```

---

## 🚀 How to Use

1. **Go to:** https://lovable.dev
2. **Click:** "New Project"
3. **Copy:** Any prompt above
4. **Paste:** Into Lovable
5. **Wait:** 60 seconds
6. **Enjoy:** Your new app! 🎉

Then iterate with the improvement prompts above!

---

## 📚 Full Guide

For detailed examples, code snippets, and tutorials:
**See:** `LOVABLE_GUIDE.md`

---

## 🔗 Resources

- **Your API:** https://misleading-aile-personalnikhil-27cb1e20.koyeb.app
- **Swagger Docs:** https://misleading-aile-personalnikhil-27cb1e20.koyeb.app/docs
- **Lovable:** https://lovable.dev

---

**Ready? Start building in 60 seconds!** 💜✨

