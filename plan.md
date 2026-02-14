# Dental Cavity Prep Simulator — Updated Integration Plan

## Context

We have three sources to reconcile:
1. **Current implementation** — Vanilla JS, 7 steps, 3-view SVG, simple checklist
2. **React alternative** — 8 steps, quiz, weighted assessment, duration estimates
3. **Full project spec** — 16-step guided mode, free practice mode, auto-fail system, 5 camera views, bur selection, progress tracking, gamification

The full spec is the target vision. This plan bridges the current implementation toward that vision in a single pass, prioritizing the P0 (must-have) items that are achievable in the current vanilla JS architecture.

---

## What's Feasible vs Not in Current Architecture

| Spec Feature | Feasible Now? | Notes |
|---|---|---|
| 16-step guided mode | YES | Replace current 7 steps with full 16-step sequence |
| Auto-fail detection | YES | Critical criteria flagging in checklist |
| 4-point grading system | YES | Weighted scoring with Excellent/Good/Needs Work/Poor |
| Occlusal + Proximal + Buccal views | ALREADY DONE | Current SVG system |
| Cross-sectional view | YES | Add as 4th SVG view (depth/wall visualization) |
| Lingual view | YES | Add as 5th SVG view |
| Depth indicators in SVG | PARTIALLY DONE | Extend with more measurement annotations |
| Bur selection interface | YES | Add bur picker per step with validation |
| Adjacent tooth damage warnings | YES | Highlight in criteria + SVG danger zones |
| Interactive quiz | YES | 10+ questions with scoring |
| Free practice mode | YES | Toggle that hides step guidance, shows only SVG + final grading |
| Progress tracking (localStorage) | YES | Store completed preps, scores, weak areas |
| Haptic feedback | NO | Requires hardware/native APIs |
| Video tutorials | NO | Would need external video hosting |
| Physics-based material removal | NO | Would need WebGL/3D engine |
| Recording/replay | NO | Would need complex state serialization |
| Gamification | PARTIAL | Badges and streak tracking via localStorage |

---

## Implementation Plan — 10 Sections

### 1. Replace 7 Steps with 16-Step Guided Sequence

**Current:** 7 steps (Assessment → Margins & Finishing)
**New:** 16 steps matching the full spec sequence

Each step in the `STEPS` array gets these fields:
```
{
  id, title, phase, duration,
  description,        // HTML content with detailed instructions
  instruments,        // Array of instrument names
  recommendedBur,     // Primary bur for this step (for bur selection feature)
  tips,               // Exam tips array
  criteria,           // Array of { text, critical: bool }
  commonMistakes,     // Array of strings
  view,               // Recommended SVG view
  validations         // Array of { check, feedback } for the step
}
```

**The 16 steps:**

| # | Title | Phase | Duration | View |
|---|-------|-------|----------|------|
| 1 | Isolation & Protection | Pre-Procedure | 2-3 min | occlusal |
| 2 | Marking with Pencil | Pre-Procedure | 2-3 min | occlusal |
| 3 | Punch Cut in Proximal Pit | Initial Access | 1-2 min | occlusal |
| 4 | Occlusal Extension | Outline Form | 2-3 min | occlusal |
| 5 | Proximal Extension | Outline Form | 2-3 min | proximal |
| 6 | Buccolingual Extension (T-Shape) | Outline Form | 2-3 min | occlusal |
| 7 | Drop the Bur (Proximal Depth) | Proximal Box | 2-3 min | proximal |
| 8 | Join the Two Ditches | Proximal Box | 2-3 min | proximal |
| 9 | Protect Adjacent Tooth | Proximal Box | 1-2 min | proximal |
| 10 | Break the Wall | Proximal Box | 2-3 min | proximal |
| 11 | Check Clearance | Verification | 1-2 min | cross-section |
| 12 | Prep the Bird Beaks | Refinement | 2-3 min | proximal |
| 13 | Smoothen Gingival Seat | Refinement | 2-3 min | proximal |
| 14 | Smoothen Occlusal Floor & Walls | Refinement | 2-3 min | cross-section |
| 15 | Make the S-Curve / Funnel | Refinement | 1-2 min | proximal |
| 16 | Final Verification & Inspection | Quality Check | 2-3 min | occlusal |

**Clinical content for each step** will be drawn from the full spec (detailed descriptions, validation criteria, feedback messages). Duration estimates from the spec are included per step. Total: ~30-42 min.

**Note:** The React version's "Matrix & Restoration" step (Step 8 in React) is NOT included in the 16-step spec — the spec focuses on the preparation only, which matches the bench test scope. We will add it as an optional bonus Step 17 that users can toggle to see, since understanding restoration context is educational. It will not be part of the main 16-step guided flow or scoring.

---

### 2. Add 2 New SVG Views (Cross-Sectional + Lingual)

**Current:** 3 views (Occlusal, Proximal, Buccal)
**New:** 5 views

**Cross-Sectional View (`drawCrossSectionView`):**
- Buccolingual cross-section through the occlusal preparation
- Shows: enamel shell thickness, dentin, pulp chamber, prep cavity profile
- Step-specific overlays: depth measurements, wall angles, floor flatness
- Critical for Steps 11, 14 (verification of depths)

**Lingual View (`drawLingualView`):**
- Mirror of buccal view showing lingual aspect
- Shows: lingual wall of proximal box, lingual margin, lingual cusp
- Step-specific: lingual wall convergence, bird beak preparation
- Used for Steps 12, verification

**Changes to `index.html`:**
- Add 2 new `<button class="view-tab">` elements for Cross-Section and Lingual

**Changes to `app.js`:**
- Add `drawCrossSectionView(stepId)` and `drawLingualView(stepId)` functions
- Update `renderSVG()` switch to include new views
- Update step `view` recommendations to reference new views where appropriate

**Changes to `styles.css`:**
- View tabs may need to wrap on mobile (flex-wrap)

---

### 3. Bur Selection Interface

**New feature:** Each step that involves cutting has a recommended bur. The user picks which bur to use, and gets feedback.

**Changes to `index.html`:**
- Add `<div id="bur-selector">` inside the step details panel, below the step description
- Shows 4-6 bur options as clickable cards with bur name + image/icon
- Correct bur highlights green, wrong bur shows warning with explanation

**Changes to `app.js`:**
- Add `BURS` data array:
  ```
  [
    { id: 'fg330', name: 'FG 330', type: 'Pear-shaped carbide', use: 'Initial access, outline form' },
    { id: '245', name: '245', type: 'Pear-shaped carbide (3mm)', use: 'Depth cuts, proximal box, finishing' },
    { id: 'sf-diamond', name: 'SF Diamond', type: 'Super-fine diamond', use: 'Smoothing, gingival seat' },
    { id: 'thin-taper', name: 'Thin Taper', type: 'Tapered fissure', use: 'Bird beaks, wall refinement' },
    { id: 'round-small', name: '¼ Round', type: 'Small round', use: 'Rounding line angles' },
  ]
  ```
- Each step gets a `recommendedBur` field (or array for steps that accept multiple)
- Add `selectBur()`, `validateBur()` functions
- Show validation feedback inline

**Changes to `styles.css`:**
- Bur card styles with selected/correct/incorrect states

---

### 4. Interactive Quiz System (Expanded to 15+ Questions)

Same as previous plan but expanded to cover the 16-step sequence:

**Questions (15):**
1. First step before cutting → Isolation & protection
2. Purpose of pencil marking → Conservative outline, cannot correct over-extension
3. Initial punch cut depth → 1.5mm (accounting for 0.5mm finishing loss)
4. Why avoid transverse ridge → Structural integrity
5. When to stop proximal extension → 0.5mm enamel lip remaining
6. What shape before wall break → T-shape
7. Why drop bur to full length → Consistent proximal box depth
8. Why protect adjacent tooth before wall break → Prevent iatrogenic damage
9. Wall break technique → Enamel hatchet sloped toward axial wall
10. Minimum clearance from adjacent tooth → 0.5mm
11. Bird beak cavosurface angle → 90°
12. When to smoothen floor vs make S-curve → Floor BEFORE S-curve
13. Max reduction in isthmus → Minimal (1-2 bur passes)
14. Auto-fail criteria → Adjacent tooth damage / depth >3mm / no tooth above gingiva
15. Final occlusal depth → ~2mm

**UI:** Same as previous plan — quiz section in HTML, question cards, scoring, explanations.

---

### 5. Assessment System with Auto-Fail + 4-Point Grading

**Replaces** the old simple checklist and the React version's weighted percentages.

**Auto-Fail Criteria (UNACCEPTABLE — shown in red):**
- Adjacent tooth damage
- Cavity too deep (>3mm)
- No tooth structure above gingiva (<1mm)

**Grading Categories (4-point scale per category):**

| Category | Weight | What's Assessed |
|----------|--------|----------------|
| Outline Form | 20% | Conservative extension, T-shape, lesion boundaries |
| Walls & Margins | 20% | Smoothness, 90° cavosurface, no over-extension |
| Enamel Support | 15% | No unsupported enamel, conservative decisions |
| Depths | 20% | Occlusal ~2mm, proximal box height, isthmus control |
| Proximal Box | 15% | Clearance 0.5mm, gingival extension 1mm above gingiva, bird beaks |
| S-Curve / Funnel | 10% | Present, not over-reduced, smooth transition |

**Each item has:**
- Checkbox (done/not done)
- Critical flag (red badge) for auto-fail items
- Category weight shown as visual bar
- 4-point selector: Excellent / Good / Needs Work / Poor

**Live score calculation:**
- Weighted average across categories
- If ANY auto-fail item is checked → score shows "FAIL" regardless of other scores
- Overall grade: Excellent (≥85%), Good (70-84%), Needs Work (50-69%), Poor (<50%)

**Changes across files:**
- `app.js`: `ASSESSMENT_SECTIONS` array, `calculateScore()`, grade computation, auto-fail logic
- `index.html`: Rebuilt checklist section with weight bars, 4-point selectors, auto-fail banner, score display
- `styles.css`: Grade colors, weight bars, auto-fail alert styles, 4-point button group

---

### 6. Free Practice Mode

**New feature:** Toggle between Guided Mode and Free Practice Mode.

**Changes to `index.html`:**
- Add mode toggle buttons at top of simulator: `[Guided Mode] [Free Practice]`
- In free practice mode:
  - Step nav sidebar hides step descriptions (shows only step titles as a reference)
  - No automatic view switching
  - No tips/criteria shown during practice
  - Timer starts when user clicks "Begin"
  - Timer shown in header area
  - "Finish & Grade" button appears
  - On finish: full assessment checklist presented for self-grading

**Changes to `app.js`:**
- Add `practiceMode` state variable
- Add `toggleMode()`, `startTimer()`, `stopTimer()`, `finishPractice()` functions
- In free practice: SVG still renders based on selected step/view, but overlays are hidden
- Timer: simple `setInterval` with mm:ss display

**Changes to `styles.css`:**
- Mode toggle button styles
- Timer display styles
- Transition animations for mode switching

---

### 7. Real-Time Warning System

**New feature:** Visual warnings shown in the step details panel and SVG.

**Warning levels:**
- 🔴 **Critical:** Adjacent tooth contact imminent, depth exceeding safe limit
- 🟡 **Warning:** Approaching over-extension, enamel lip too thin/thick, bur not parallel, isthmus over-reduction risk

**Implementation:**
- Each step's `validations` array defines what to warn about
- Warnings are shown as colored alert boxes below the step description
- In SVG: danger zones shown as red-tinted areas when relevant step is active
- e.g., Step 5 (Proximal Extension): red zone near adjacent tooth in proximal view
- e.g., Step 15 (S-Curve): yellow warning zone in isthmus area

**Changes to `app.js`:**
- Add `WARNINGS` data per step
- Render warning boxes in `updateStepDetails()`
- Add danger zone overlays to SVG draw functions

**Changes to `styles.css`:**
- Warning alert styles (critical = red bg, warning = yellow bg)

---

### 8. Duration Estimates + Total Time Display

Same as previous plan, but now with 16 steps:

| Step | Duration |
|------|----------|
| 1. Isolation | 2-3 min |
| 2. Marking | 2-3 min |
| 3. Punch Cut | 1-2 min |
| 4. Occlusal Extension | 2-3 min |
| 5. Proximal Extension | 2-3 min |
| 6. BL Extension | 2-3 min |
| 7. Drop the Bur | 2-3 min |
| 8. Join Ditches | 2-3 min |
| 9. Protect Adjacent | 1-2 min |
| 10. Break Wall | 2-3 min |
| 11. Check Clearance | 1-2 min |
| 12. Bird Beaks | 2-3 min |
| 13. Gingival Seat | 2-3 min |
| 14. Occlusal Floor | 2-3 min |
| 15. S-Curve | 1-2 min |
| 16. Final Verification | 2-3 min |
| **Total** | **~28-42 min** |

Displayed as badge per step in nav + total in progress area.

---

### 9. Fix Clinical Accuracy Issues

**Axial wall depth inconsistency:**
- `index.html` measurements panel: Change `1.5mm` → `~0.5mm past DEJ`
- `app.js` SVG proximal view label: Change `~1.5mm` → `~0.5mm`

**Pulpal floor depth precision:**
- Update descriptions to say "0.5mm into dentin (~1.5-2mm from occlusal surface)" instead of just "1.5-2mm"

**Proximal bevel — KEEP CURRENT (correct):**
- Butt joint, no bevel on proximal box — this is evidence-based and exam-correct

**New measurements from spec:**
- Enamel lip: 0.5mm before wall break
- Proximal box bur depth: 3mm (245 bur full length)
- Clearance from adjacent: 0.5mm (buccal, lingual, gingival)
- Tooth structure above gingiva: minimum 1mm
- Final occlusal depth: ~2mm
- Add these to the measurements panel in `index.html`

---

### 10. Update SVG Visualizations for 16 Steps

The existing 3 SVG views need overlay updates for all 16 steps, plus 2 new views.

**Occlusal view overlays by step:**
| Step | Overlay |
|------|---------|
| 1 | Rubber dam border, fender wedge marker |
| 2 | Pencil marking outline (dashed orange) |
| 3 | Punch cut dot in proximal pit |
| 4 | Occlusal extension along fissures (highlight) |
| 5 | Proximal extension arrow (distal direction) |
| 6 | BL extension creating T-shape (highlight both arms) |
| 7-8 | Proximal box depth indicators |
| 9 | Matrix band overlay on distal |
| 10 | Wall break zone (red dashed, then removed) |
| 11 | Clearance measurement arrows |
| 12 | Bird beak zones highlighted |
| 13-14 | Smooth floor/wall indicators |
| 15 | S-curve/funnel zone in isthmus |
| 16 | Full margin check (green outline) |

**Proximal view overlays by step:**
| Step | Overlay |
|------|---------|
| 1 | Fender wedge between teeth |
| 5 | Proximal extension with enamel lip dimension |
| 7 | Two depth ditches (buccal + lingual end) |
| 8 | Joined ditches with 0.5mm enamel lip |
| 9 | Matrix band against adjacent tooth |
| 10 | Wall break (enamel fragment removal) |
| 11 | Clearance dimensions (0.5mm arrows) |
| 12 | Bird beak angle indicators (90°) |
| 13 | Gingival seat highlight with smoothness indicator |
| 15 | S-curve/funnel profile |
| 16 | Full check (all dimensions shown) |

**Cross-Section view (NEW) overlays by step:**
| Step | Overlay |
|------|---------|
| 3 | Punch cut depth (1.5mm indicator) |
| 6 | T-shape cross-section with BL width |
| 11 | Clearance check from all directions |
| 14 | Floor depth + wall angle verification |
| 15 | S-curve/funnel profile from BL perspective |

**Buccal + Lingual views:** Similar to current buccal, showing progressive preparation outline.

---

## Files Modified

| File | Changes |
|------|---------|
| `app.js` | 16-step STEPS array, 2 new SVG draw functions, all SVG overlays for 16 steps, bur selection system, quiz system (15 questions), assessment scoring with auto-fail, free practice mode + timer, warning system, duration fields, clinical accuracy fixes |
| `index.html` | 2 new view tabs, bur selector area in step details, quiz section, rebuilt checklist with weights/auto-fail/4-point grading, mode toggle, timer display, expanded measurements panel |
| `styles.css` | 5-view tab layout, bur card styles, quiz styles, assessment/grading styles, auto-fail alert, mode toggle, timer, warning alerts, new SVG overlay styles |

---

## What We Are NOT Doing (deferred / not feasible)

- **Haptic feedback** — requires native hardware APIs
- **Video tutorials** — requires external video hosting/content creation
- **Physics-based material removal** — requires WebGL/3D engine
- **Session recording/replay** — requires complex state serialization
- **Progress tracking with localStorage** — deferred to future iteration (keeps this PR focused)
- **Gamification (badges, leaderboard)** — deferred to future iteration
- **Multiple tooth anatomies** — deferred (current uses upper premolar only)

---

## Implementation Order

1. Rewrite STEPS array (16 steps with full content) + duration fields
2. Fix clinical accuracy (axial wall, pulpal floor, measurements panel)
3. Update existing 3 SVG views for 16-step overlays
4. Add Cross-Section + Lingual SVG views
5. Add bur selection interface
6. Add warning system
7. Add quiz system
8. Rebuild checklist → assessment system with auto-fail + 4-point grading
9. Add free practice mode + timer
10. CSS for all new features
