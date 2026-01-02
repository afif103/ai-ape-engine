# 📱 Mobile UI/UX Testing Guide

**Platform**: APE (AI Productivity Engine)  
**Target**: iPhone 13 Pro Max (428px) + All Mobile Devices  
**Test Method**: Physical Device + Chrome DevTools

---

## 🎯 QUICK TEST (5 Minutes)

**Goal**: Verify all 5 pages load and hamburger menu works

### Pages to Test:
1. ✅ Chat: https://ai-ape-engine-vercel.vercel.app/chat
2. ✅ Code: https://ai-ape-engine-vercel.vercel.app/code
3. ✅ Research: https://ai-ape-engine-vercel.vercel.app/research
4. ✅ Extraction: https://ai-ape-engine-vercel.vercel.app/extraction
5. ✅ Batch: https://ai-ape-engine-vercel.vercel.app/batch

### For EACH Page:
- [ ] Page loads without errors
- [ ] Hamburger button visible at top-left
- [ ] Tap hamburger → drawer slides in from left
- [ ] Tap backdrop (dark area) → drawer closes
- [ ] Press ESC key → drawer closes
- [ ] No horizontal scroll (swipe left/right)
- [ ] Content is readable (no tiny text)

---

## 🔍 DETAILED TEST BY PAGE

### 1️⃣ CHAT PAGE - `/chat`

#### Hamburger & Drawer:
- [ ] Hamburger button at top-left
- [ ] Tap → drawer slides in smoothly
- [ ] "New" button visible in drawer
- [ ] Conversation list visible
- [ ] Search bar works
- [ ] Tap conversation → drawer closes automatically
- [ ] Tap backdrop → drawer closes

#### Main Interface:
- [ ] Chat uses full width
- [ ] Messages readable
- [ ] Input box at bottom
- [ ] Send button accessible
- [ ] No horizontal scroll

---

### 2️⃣ CODE PAGE - `/code`

#### Hamburger & Drawer:
- [ ] Hamburger button at top-left
- [ ] Tap → drawer opens
- [ ] 4 modes visible (Generate/Review/Explain/Fix)
- [ ] Tap mode → drawer closes automatically
- [ ] Active mode highlighted

#### Main Interface:
- [ ] Form inputs full-width
- [ ] Monaco editor works
- [ ] Generate button accessible
- [ ] Results display properly
- [ ] No horizontal scroll

---

### 3️⃣ RESEARCH PAGE - `/research`

#### Hamburger & Drawer:
- [ ] Hamburger button at top-left
- [ ] Tap → drawer opens
- [ ] 2 modes visible (Scrape/Research)
- [ ] Tap mode → drawer closes
- [ ] URL inputs full-width
- [ ] "Add URL" button works
- [ ] URL list scrollable

#### Main Interface:
- [ ] Results use full screen
- [ ] Citations readable
- [ ] No horizontal scroll

---

### 4️⃣ EXTRACTION PAGE - `/extraction`

#### Hamburger & Drawer:
- [ ] Hamburger button at top-left
- [ ] Tap → drawer opens
- [ ] Upload dropzone visible
- [ ] File preview shows properly
- [ ] Extract button visible

#### Main Interface:
- [ ] Upload works
- [ ] Results display
- [ ] Export buttons work
- [ ] No horizontal scroll

---

### 5️⃣ BATCH PAGE - `/batch`

#### Hamburger & Drawer:
- [ ] Hamburger button at top-left
- [ ] Tap → drawer opens
- [ ] Batch name input visible
- [ ] Files counter visible (0/10)
- [ ] Upload area accessible
- [ ] File list scrollable

#### Main Interface:
- [ ] Multi-file selection works
- [ ] Status indicators visible
- [ ] Progress displays
- [ ] No horizontal scroll

---

## 📱 DEVICE TESTING

### iPhone 13 Pro Max (428px):
- [ ] All pages tested
- [ ] Safe areas respected
- [ ] Dark keyboard
- [ ] No zoom on focus

### Chrome DevTools:
- [ ] iPhone SE (375px) - All pages work
- [ ] iPhone 13 (390px) - All pages work
- [ ] iPad (768px) - Desktop layout returns
- [ ] Desktop (1920px) - Full desktop experience

---

## ✅ PASS CRITERIA

### Must Pass:
- All 5 pages load
- Hamburger works on all pages
- No horizontal scroll
- Content readable
- Features still work

### Desktop Unchanged:
- Hamburger hidden (≥768px)
- Sidebar always visible
- 2-column layout
- All features work

---

## 🐛 ISSUE REPORTING

**Template**:
```
Page: [Chat/Code/Research/Extraction/Batch]
Device: [iPhone 13 Pro Max/Chrome DevTools]
Issue: [Description]
Expected: [What should happen]
Screenshot: [If applicable]
```

---

**Quick Start**: Test Chat and Code pages first (most used features)
