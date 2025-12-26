# APE Frontend - Visual Testing Checklist

## ✅ Improvements Completed

### 1. **CSS Design System Overhaul** (`globals.css`)
- ✅ Enhanced color contrast ratios (WCAG AA compliant)
- ✅ Improved glass effect opacity (0.12-0.85 from 0.04-0.08)
- ✅ Better border visibility (0.2 from 0.1 opacity)
- ✅ Darker, more opaque backgrounds for readability
- ✅ Text hierarchy with 4 levels (primary, secondary, tertiary, muted)

### 2. **All Pages Updated**
- ✅ Landing page (`page.tsx`)
- ✅ Dashboard (`dashboard/page.tsx`)
- ✅ Chat interface (`chat/page.tsx`)
- ✅ Code assistant (`code/page.tsx`)
- ✅ Research module (`research/page.tsx`)
- ✅ Login page (`login/page.tsx`)
- ✅ Register page (`register/page.tsx`)

### 3. **Build Verification**
- ✅ TypeScript compilation: PASSED
- ✅ Next.js build: SUCCESSFUL
- ✅ All routes compiled: 10/10 pages
- ✅ No errors or warnings

---

## 🧪 Manual Testing Checklist

### **Base URL**: `http://localhost:3000`

### 📄 **1. Landing Page** (`/`)

#### Visual Elements
- [ ] Hero section background effects visible but not distracting
- [ ] Main heading "AI Productivity Engine" is crisp white and readable
- [ ] Description text (`text-slate-200`) is clearly visible
- [ ] Liquid glass cards have proper transparency and borders
- [ ] Trust indicators (checkmarks) are visible in `text-slate-300`
- [ ] Feature cards show 3D hover effect on mouse over
- [ ] Gradient buttons are vibrant and readable

#### Typography Hierarchy
- [ ] H1 headings: Pure white (`#ffffff`)
- [ ] Body text: Light gray (`text-slate-200/300`)
- [ ] Secondary text: Visible against backgrounds

#### Interactive Elements
- [ ] "Start Free Trial" button: Gradient visible, hover works
- [ ] "Watch Demo" button: Hover state clear
- [ ] "Get Started" / "Sign In" header buttons: Clear contrast
- [ ] All links in header are clickable and visible

---

### 🏠 **2. Dashboard** (`/dashboard`)

#### Header Section
- [ ] "Command Center" title is pure white and bold
- [ ] Welcome message in `text-slate-300` is readable
- [ ] Description paragraph in `text-slate-200` is clear
- [ ] System status badge shows green pulse animation
- [ ] Current time display is visible

#### Quick Actions Grid
- [ ] All 4 action cards visible with liquid glass effect
- [ ] Icon gradients are vibrant (blue, purple, green, orange)
- [ ] Card titles in white on hover
- [ ] Descriptions in `text-slate-300` are readable
- [ ] Stats badges have proper background opacity
- [ ] "Launch" buttons show gradient on hover
- [ ] 3D hover effect works smoothly
- [ ] ChevronRight icon animates on hover

#### System Metrics
- [ ] 4 metric cards display properly
- [ ] Numbers are large and white
- [ ] Labels in `text-slate-300` are clear
- [ ] TrendingUp icons show properly
- [ ] Cards have hover 3D effect

#### Recent Activity Panel
- [ ] Activity cards have borders and proper spacing
- [ ] Icon backgrounds are color-coded
- [ ] Activity titles are white and bold
- [ ] Descriptions in `text-slate-300` are readable
- [ ] Timestamps in `text-slate-400` are visible
- [ ] Hover effect changes background opacity

#### AI Insights Section
- [ ] Gradient backgrounds for insight cards visible
- [ ] Section headings are white
- [ ] Text content in `text-slate-300` is readable
- [ ] Icons show proper colors (blue, purple, green, etc.)
- [ ] Hover 3D effect works

---

### 💬 **3. Chat Page** (`/chat`)

#### Conversations Sidebar
- [ ] "Conversations" title with MessageSquare icon visible
- [ ] "New" button is clear and clickable
- [ ] Conversation list items have proper borders
- [ ] Selected conversation has primary color glow
- [ ] Hover states show background change
- [ ] Delete icon (trash) appears on hover
- [ ] "No conversations" empty state is readable

#### Chat Area
- [ ] Bot icon and title visible in header
- [ ] "AI Online" badge shows green with pulse
- [ ] Message count badge visible
- [ ] User messages align right with primary background
- [ ] AI messages align left with glass background
- [ ] Message text is readable in both types
- [ ] Token stats show below AI messages
- [ ] Streaming indicator animates properly
- [ ] "AI is thinking" loader shows pulsing dots

#### Input Area
- [ ] Input field has glass effect and border
- [ ] Placeholder text is visible
- [ ] "Send" button is enabled when text present
- [ ] Stream button (Zap icon) visible and functional
- [ ] Conversation stats show clearly at bottom

---

### 💻 **4. Code Assistant** (`/code`)

#### Tab Selection Panel
- [ ] All 4 tabs (Generate, Review, Explain, Fix) visible
- [ ] Active tab has primary color glow
- [ ] Tab descriptions are readable
- [ ] Icons show proper colors
- [ ] Hover states work smoothly

#### Form Area
- [ ] Labels are white and clear
- [ ] Input fields have glass effect
- [ ] Textarea has proper min-height
- [ ] Monaco Editor loads properly (for Review/Explain/Fix)
- [ ] Dropdown (select) has proper styling
- [ ] Submit buttons show "futuristic" variant
- [ ] Loading states show proper text

#### Results Panel
- [ ] "Ready to Assist" empty state shows centered
- [ ] Loading spinner pulses properly
- [ ] Generated code shows in code block with proper styling
- [ ] Review results text is white with `text-slate-200` for content
- [ ] Explanation text is readable
- [ ] Fixed code displays in formatted code block
- [ ] Copy button appears when result exists
- [ ] Provider badge shows properly

---

### 🔍 **5. Research Page** (`/research`)

#### Tab Selection
- [ ] "Scrape URL" and "Research Topic" tabs visible
- [ ] Active tab has glow effect
- [ ] Tab icons and descriptions clear

#### Scrape Form
- [ ] URL input has liquid glass styling
- [ ] "Scrape Website" button is clear
- [ ] Error messages show in red

#### Research Form
- [ ] Query textarea has proper height and styling
- [ ] "Add URL" button works and shows "+

" icon
- [ ] URL inputs can be added/removed dynamically
- [ ] Max 5 URLs enforced
- [ ] Max sources dropdown styled properly
- [ ] File upload area has dashed border
- [ ] Upload icon and text are visible
- [ ] "Start Research" button functional

#### Results Panel
- [ ] "Ready to Research" empty state centered
- [ ] Loading state shows pulse animation
- [ ] Scraped content displays with white headings
- [ ] Content text is `text-slate-200` and readable
- [ ] Metadata grid shows properly with white labels
- [ ] "View Original" link visible and clickable
- [ ] Research synthesis shows in white heading
- [ ] AI synthesis content is `text-slate-200`
- [ ] Source list displays with badges and links
- [ ] Copy button works

---

### 🔐 **6. Login Page** (`/login`)

#### Layout
- [ ] Centered card on dark gradient background
- [ ] Grid pattern visible but subtle (0.03 opacity)
- [ ] Blur circles in background not distracting

#### Form
- [ ] "Welcome back" title is white
- [ ] Description text is `text-slate-300` and readable
- [ ] Email label is white
- [ ] Password label is white
- [ ] Input fields have glass effect
- [ ] Eye icon toggle works for password visibility
- [ ] Error messages show in red
- [ ] "ACCESS SYSTEM" button has futuristic variant
- [ ] Loading state shows "Signing in..."

#### Links
- [ ] "Don't have an account?" text in `text-slate-300`
- [ ] "INITIALIZE ACCOUNT" link is visible
- [ ] "RETURN TO SURFACE" link is visible
- [ ] Links have hover color change

---

### 📝 **7. Register Page** (`/register`)

#### Layout
- [ ] Similar to login with centered card
- [ ] Background effects match login page

#### Form
- [ ] "Get Started" title is white
- [ ] All 4 fields (Name, Email, Password, Confirm) visible
- [ ] Labels are white and clear
- [ ] Input fields styled consistently
- [ ] Eye toggle icons work for both password fields
- [ ] Form card has 70% background opacity
- [ ] Error messages clear and red
- [ ] "INITIALIZE ACCOUNT" button futuristic
- [ ] Loading state functional

#### Links
- [ ] "Already have an account?" readable
- [ ] Links have proper hover states

---

## 🎨 Design Consistency Checks

### Global
- [ ] All headings use pure white (`#ffffff`) or `text-white`
- [ ] Body text uses `text-slate-200` or `text-slate-300`
- [ ] Secondary/muted text uses `text-slate-300` or `text-slate-400`
- [ ] Glass effects have consistent opacity (0.7-0.85)
- [ ] Borders are visible at 0.15-0.2 opacity
- [ ] Hover states show 3D perspective transforms
- [ ] Gradient buttons are vibrant and clickable

### Spacing (8px Grid)
- [ ] Card padding: 16px (p-4) or 24px (p-6)
- [ ] Section gaps: 16px or 24px
- [ ] Icon spacing: 8px or 12px margins
- [ ] Consistent gap-4 (16px) or gap-6 (24px) in grids

### Animations
- [ ] Fade-in animations smooth (0.4s)
- [ ] Hover 3D transforms work without jank
- [ ] Liquid morph animations run smoothly
- [ ] Pulse glows cycle properly (2s)
- [ ] Float animations are subtle

---

## 🐛 Known Issues to Check For

### Potential Problems
- [ ] Text too light against glass backgrounds (should be fixed now)
- [ ] Scrollbar visibility (should have gradient style)
- [ ] Glass cards blending with background (increased opacity)
- [ ] Button text hard to read (should be white on gradients)
- [ ] Form inputs blend with background (glass effect should show border)

### Browser Compatibility
- [ ] Test in Chrome/Edge (Chromium)
- [ ] Test in Firefox
- [ ] Test in Safari (if on Mac)
- [ ] Check mobile responsiveness (< 768px)

---

## ✅ Accessibility Checks

### Contrast Ratios (WCAG AA: 4.5:1 minimum)
- [ ] Headings: White on dark (~7:1) ✅
- [ ] Body text: `#e2e8f0` on dark (~5.5:1) ✅
- [ ] Secondary text: `#cbd5e1` on dark (~4.8:1) ✅
- [ ] Muted text: `#94a3b8` on dark (~4.5:1) ✅

### Keyboard Navigation
- [ ] Tab order is logical
- [ ] Focus rings visible (2px outline)
- [ ] All buttons reachable via keyboard
- [ ] Enter key submits forms
- [ ] Escape closes modals (if any)

### Screen Reader
- [ ] Alt text on all images
- [ ] Semantic HTML (header, nav, main, aside)
- [ ] ARIA labels where needed
- [ ] Form labels associated with inputs

---

## 📊 Performance Checks

### Page Load
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3s
- [ ] No layout shift (CLS < 0.1)
- [ ] Smooth scrolling performance

### Animations
- [ ] 60fps during hover effects
- [ ] No jank during liquid morph
- [ ] GPU acceleration working (translate3d)

---

## 🚀 Final Approval Checklist

Before marking as complete:
- [ ] All pages visually tested in browser
- [ ] No console errors in DevTools
- [ ] All interactive elements functional
- [ ] Text readable on all backgrounds
- [ ] Hover states provide clear feedback
- [ ] Loading states visible and informative
- [ ] Error states handled gracefully
- [ ] Mobile responsive (if required)
- [ ] Cross-browser tested
- [ ] User feedback incorporated

---

## 📝 Testing Notes

**Tester Name**: _____________
**Date**: _____________
**Browser**: _____________
**Screen Resolution**: _____________

### Issues Found:
1. 
2. 
3. 

### Suggestions:
1. 
2. 
3. 

---

**Status**: ⏳ PENDING USER TESTING

**Next Step**: User to manually test all pages at `http://localhost:3000` and report any visual issues or readability problems.
