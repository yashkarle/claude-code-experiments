# Dental Cavity Prep Simulator — Updated Integration Plan

## Context

We have three sources to reconcile:
1. **Current implementation** — Vanilla JS, 7 steps, 3-view SVG, simple checklist
2. **React alternative** — 8 steps, quiz, weighted assessment, duration estimates
3. **Full project spec** — 16-step guided mode, free practice mode, auto-fail system, 5 camera views, bur selection, progress tracking, gamification

Additionally, we have two **official IDC 2025 exam documents** that are the ground truth:
- **Bench Test Criteria 2025 PDF** — The actual marking sheets examiners use (G/P/B/F grading)
- **IDC Bench Test Tooth Class II Preparations PDF** — Course slides with key guidelines

**The sole aim of this simulator is to help candidates pass the IDC Bench Test.** All features must align with the actual exam criteria, terminology, and grading system.

---

## Key Exam Facts (from IDC 2025 Documents)

### Exam Grading System: G / P / B / F

The IDC uses a **4-grade scale** across two bands:

| Grade | Band | Meaning |
|-------|------|---------|
| **G** | Satisfactory | Good — meets the standard |
| **P** | Satisfactory | Pass — minor deviations only |
| **B** | Unsatisfactory | Bad — significant issues |
| **F** | Unsatisfactory | Fail — gross errors, dangerous |

### Marking Sheets (4 separate sheets)

1. **Rubber Dam Criteria Sheet** — standalone G/P/B/F assessment
2. **Quality Evaluation: Composite Resin Cavity** — 3 columns, each graded G/P/B/F
3. **Quality Evaluation: Crown Preparation** — (not relevant to this simulator)
4. **Temporary Restoration** — (not relevant to this simulator)

### Composite Cavity Marking — 3 Assessment Columns

| Column | G (Good) | P (Pass) | B (Bad) | F (Fail) |
|--------|----------|----------|---------|----------|
| **Finish of Walls & Margins / Cavity Definition** | Walls and margins smooth, cavity well defined | Slight roughness of walls or margins; slight lack of cavity definition | Walls or margins rough | Enamel margins grossly undermined |
| **External Outline** | Minimum extension to remove caries only; no beveling; convenience form for access to ADJ and material placement; proximal contact included in preparation | Slightly underextended; slightly overextended | Extended beyond lesion margins or underextended impeding restoration; unsupported enamel removed; supporting or adjacent tooth damaged | Grossly underextended; grossly overextended; supporting or adjacent tooth mutilated |
| **Internal Outline** | Extended into dentine; no excessive tissue loss | Pulpal or axial walls shallow; pulpal or axial walls deeper than required | Pulpal or axial walls require liner/base unnecessarily — would compromise pulpal health | Pulpal floor/axial wall entirely in enamel; would likely cause pulp exposure; tooth prepared without water (heat damage risk) |

### Rubber Dam Criteria — Standalone G/P/B/F

| Grade | Criteria |
|-------|----------|
| **G** | Dam everted around tooth; appropriate clamp(s) selected and stable; appropriate number of teeth isolated; dam intact |
| **P** | Dam is not everted around the tooth |
| **B** | Clamp not stable; minimal tears; inappropriate number of teeth; frame positioning incorrect; inappropriate tooth clamped |
| **F** | Extensive tears; clamp very unstable; frame positioning hinders procedure; interference with another candidate |

### Standard Class II Guidelines (from IDC slides)

- This should be a **"step" cavity preparation**
- Proximal box should extend **just beyond the contact point**
- Occlusal portion should be **2mm in depth**
- Occlusal portion should be **no more than 1/3 of the intercuspal width, preferably just a bur width**
- Occlusal portion should **extend as far as the transverse ridge but not break it**
- **No beveling** for composite (butt joint)

### Golden Reference: IDC Cavity Outline Images (Page 2 of IDC slides)

The IDC slides include 4 reference photographs of a maxillary first molar Class II prep (silhouette overlays + typodont photos) showing both the **proximal box view** and **occlusal view**. These are the gold standard for what the examiner expects to see. Our SVG visualizations must match these outlines.

**Occlusal outline (top-down):**
- **Keyhole / T-shape**: narrow occlusal isthmus extending mesially along the central fissure, stopping cleanly at the transverse ridge (no crossover), with a wider buccolingual flare at the distal where the proximal box opens
- **Isthmus is very narrow** — the photos show approximately one bur width, at the most conservative end of the "max 1/3 intercuspal" guideline
- **Distal flare is subtle** — the T-shape arms (buccal and lingual extensions at the proximal box opening) are conservative, not wide wings
- **Outline is smooth and continuous** — no jagged edges or irregular extensions
- **The prep does NOT cross the transverse ridge** — it terminates right at it

**Proximal box outline (side view):**
- **Distinct "step" shape** — the proximal box drops significantly deeper than the occlusal floor, forming a clear step at the axiopulpal line angle
- **Rectangular box profile** — the proximal box has relatively parallel buccal and lingual walls (with slight occlusal divergence) and a flat gingival seat at the bottom
- **The gingival seat is flat** and perpendicular to the long axis of the tooth
- **Box extends just beyond the contact area** — clearing the adjacent tooth but not over-extended
- **Smooth walls** — no ledges or irregularities visible in the typodont photos

**SVG implementation implications:**
- The occlusal view SVG must show the narrow keyhole/T-shape with conservative isthmus (one bur width), NOT a wide preparation
- The proximal view SVG must show the distinct step between occlusal floor and proximal box floor — this "step" shape is fundamental to the prep identity
- The final verification step (Step 16) overlay should show the complete outline matching these IDC reference shapes so candidates can compare their mental model against the gold standard
- Consider adding an "IDC Reference Outline" toggle that overlays the ideal outline shape on the SVG at any step, so candidates always know what they're aiming for

### Matrix Systems (from IDC slides)

- **Sectional matrix** (V Ring / Palodent) — dedicated anatomical wedge + sectional matrix + holding ring; ring provides separation compensating for matrix thickness; more predictable proximal contour
- **Tofflemire matrix** — more familiar but does not fit as well; needs pre-contouring; greater thickness
- Advice: "Use what you are comfortable with. Try both more than once."

---

## What's Feasible vs Not in Current Architecture

| Spec Feature | Feasible Now? | Notes |
|---|---|---|
| 16-step guided mode | YES | Replace current 7 steps with full 16-step sequence |
| IDC G/P/B/F grading system | YES | Replace custom 4-point scale with actual exam grading |
| IDC 3-column assessment | YES | Match the real marking sheet columns exactly |
| Rubber Dam assessment section | YES | Dedicated section matching the exam's separate criteria sheet |
| Occlusal + Proximal + Buccal views | ALREADY DONE | Current SVG system |
| Cross-sectional view | YES | Add as 4th SVG view (depth/wall visualization) |
| Lingual view | YES | Add as 5th SVG view |
| Depth indicators in SVG | PARTIALLY DONE | Extend with more measurement annotations |
| Bur selection interface | YES | Add bur picker per step with validation |
| Adjacent tooth damage warnings | YES | Highlight in criteria + SVG danger zones |
| Interactive quiz | YES | 15+ questions with scoring, using exam terminology |
| Free practice mode | YES | Toggle that hides step guidance, shows only SVG + final grading |
| Matrix system guidance | YES | Educational section on sectional vs Tofflemire |
| Progress tracking (localStorage) | YES | Store completed preps, scores, weak areas |
| Haptic feedback | NO | Requires hardware/native APIs |
| Video tutorials | NO | Would need external video hosting |
| Physics-based material removal | NO | Would need WebGL/3D engine |
| Recording/replay | NO | Would need complex state serialization |
| Gamification | PARTIAL | Badges and streak tracking via localStorage |

---

## Implementation Plan — 11 Sections

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

**Clinical content for each step** will be drawn from the full spec (detailed descriptions, validation criteria, feedback messages). Duration estimates from the spec are included per step. Total: ~28-42 min.

**Important terminology:** This is a **"step" cavity preparation** (per IDC slides). Use this language throughout.

**Note:** The React version's "Matrix & Restoration" step (Step 8 in React) is NOT included in the 16-step spec — the spec focuses on the preparation only, which matches the bench test scope. Matrix system guidance is covered in a separate educational section (Section 11).

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

### 4. Interactive Quiz System (15+ Questions)

Expanded to cover the 16-step sequence **and the actual exam criteria**:

**Questions (15):**
1. First step before cutting → Isolation & protection (rubber dam)
2. Purpose of pencil marking → Conservative outline, cannot correct over-extension
3. Initial punch cut depth → 1.5mm (accounting for 0.5mm finishing loss)
4. Why avoid transverse ridge → Structural integrity (IDC: "extend as far as transverse ridge but not break it")
5. Maximum isthmus width → No more than 1/3 intercuspal width, preferably just a bur width
6. What shape before wall break → T-shape
7. Why drop bur to full length → Consistent proximal box depth
8. Why protect adjacent tooth before wall break → Prevent iatrogenic damage (B grade if damaged, F if mutilated)
9. Wall break technique → Enamel hatchet sloped toward axial wall
10. Should you bevel the proximal box for composite? → No — butt joint, no bevel (explicit IDC G criterion)
11. Bird beak cavosurface angle → 90°
12. What makes a "G" grade for Finish of Walls & Margins? → Walls and margins smooth, cavity well defined
13. What is an automatic F on the marking sheet? → Pulp exposure risk / tooth mutilated / prepared without water / axial wall entirely in enamel
14. What does "convenience form" mean in IDC criteria? → Allow access to ADJ and allow material placement
15. Final occlusal depth → ~2mm

**UI:** Quiz section in HTML, question cards, scoring with explanations referencing the actual marking sheet criteria.

---

### 5. Assessment System — IDC G/P/B/F Marking Sheet

**Replaces** the old simple checklist. **Must exactly mirror the real exam marking sheets.**

#### 5a. Rubber Dam Assessment (Separate Section)

Standalone G/P/B/F grading matching the exam's dedicated Rubber Dam Criteria Sheet:

| Criterion | G | P | B | F |
|-----------|---|---|---|---|
| **Eversion** | Dam everted around tooth | Dam not everted | — | — |
| **Clamp** | Appropriate clamp, stable | — | Clamp not stable | Clamp very unstable |
| **Isolation** | Appropriate number of teeth | — | Inappropriate number; inappropriate tooth | — |
| **Dam integrity** | Dam intact | — | Minimal tears | Extensive tears |
| **Frame** | — | — | Frame positioning incorrect | Frame hinders procedure |

User selects G/P/B/F for the overall rubber dam. Descriptors shown inline so candidates learn what each grade means.

#### 5b. Composite Cavity Assessment (3-Column G/P/B/F)

Matches the exam's **Quality Evaluation Criteria for Prepared Composite Resin Cavity** sheet exactly.

**Column 1: Finish of Walls & Margins / Cavity Definition**

| Grade | Descriptors |
|-------|-------------|
| **G** | Walls and margins smooth, cavity well defined |
| **P** | Slight roughness of cavity walls or margins; slight lack of cavity definition |
| **B** | Walls or margins rough |
| **F** | Enamel margins grossly undermined |

**Column 2: External Outline**

| Grade | Descriptors |
|-------|-------------|
| **G** | Minimum extension to remove caries lesion only; no beveling; convenience form to allow access to ADJ and allow material to be placed in cavity; proximal contact included in preparation |
| **P** | External outline slightly underextended; external outline slightly overextended |
| **B** | Cavity margins extended beyond lesion or underextended impeding complete restoration; unsupported enamel removed; supporting or adjacent tooth damaged |
| **F** | External outline grossly underextended; external outline grossly overextended; supporting or adjacent tooth mutilated |

**Column 3: Internal Outline**

| Grade | Descriptors |
|-------|-------------|
| **G** | Extended into dentine; no excessive tissue loss |
| **P** | Pulpal or axial walls shallow; pulpal or axial walls deeper than required |
| **B** | Pulpal or axial walls require liner or base unnecessarily — would likely compromise pulpal health |
| **F** | Pulpal floor, axial wall entirely in enamel; would likely cause pulp exposure; tooth prepared without water — risk of heat damage to pulp |

**Additional F criteria (apply across all columns):**
- Interference with another candidate's work/equipment

**UI Implementation:**
- 3 columns displayed as cards, each with G/P/B/F radio buttons
- Each grade option shows its descriptor text so candidates learn the criteria
- Rubber dam section displayed above as a separate card
- Overall result: **Satisfactory** (all columns G or P) vs **Unsatisfactory** (any column B or F)
- If ANY column is F → prominent red "FAIL" banner with the specific F reason highlighted
- Visual summary showing which columns passed/failed

**Changes across files:**
- `app.js`: `RUBBER_DAM_CRITERIA`, `CAVITY_ASSESSMENT_COLUMNS` data, `calculateResult()`, overall pass/fail logic
- `index.html`: Rebuilt assessment section with rubber dam card + 3-column cavity assessment cards, G/P/B/F selectors with descriptors
- `styles.css`: G/P/B/F button styles (G=green, P=amber, B=orange, F=red), satisfactory/unsatisfactory banner styles, column card layout

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
  - On finish: full IDC assessment (rubber dam + 3-column cavity) presented for self-grading

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

**New feature:** Visual warnings shown in the step details panel and SVG. Warnings map directly to B and F criteria from the marking sheet.

**Warning levels:**
- **F-risk (red):** Actions that would result in an F grade — adjacent tooth mutilation, pulp exposure, grossly over/underextended outline, preparing without water, axial wall entirely in enamel
- **B-risk (orange):** Actions that would result in a B grade — adjacent tooth damage, rough walls/margins, unsupported enamel, unnecessary liner/base depth, extension beyond lesion margins
- **P-risk (yellow):** Actions that would drop from G to P — slight roughness, slight under/overextension, shallow/deep pulpal or axial walls

**Implementation:**
- Each step's `validations` array defines what to warn about, mapped to the specific marking sheet criterion
- Warnings shown as colored alert boxes below the step description, with the actual examiner descriptor text
- In SVG: danger zones shown as red-tinted areas when relevant step is active
- e.g., Step 5 (Proximal Extension): red zone near adjacent tooth in proximal view
- e.g., Step 15 (S-Curve): yellow warning zone in isthmus area

**Changes to `app.js`:**
- Add `WARNINGS` data per step, each referencing the marking sheet column and grade impact
- Render warning boxes in `updateStepDetails()`
- Add danger zone overlays to SVG draw functions

**Changes to `styles.css`:**
- Warning alert styles (F-risk = red bg, B-risk = orange bg, P-risk = yellow bg)

---

### 8. Duration Estimates + Total Time Display

Same as previous plan, with 16 steps:

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
- Butt joint, no bevel on proximal box — this is explicitly a **G criterion** on the marking sheet ("No beveling")

**Isthmus width — correct per IDC slides:**
- Change current "minimum 1/4 intercuspal distance" to: **"No more than 1/3 of intercuspal width, preferably just a bur width"**
- The IDC emphasis is on keeping it **narrow and conservative**, not on a minimum width

**"Step" cavity terminology:**
- Add this term throughout descriptions: "This is a step cavity preparation" per IDC course language

**Convenience form:**
- Add explicit mention in relevant steps that the prep must provide **"convenience form to allow access to ADJ and allow material to be placed in cavity"** — this is a specific G criterion

**Proximal contact:**
- Ensure the proximal extension step explicitly states that the **"proximal contact must be included in preparation"** — another specific G criterion

**Water cooling:**
- Add reminder in cutting steps that preparing **without water is an automatic F** ("risk of heat damage to pulp")

**New measurements from spec + IDC docs:**
- Enamel lip: 0.5mm before wall break
- Proximal box bur depth: 3mm (245 bur full length)
- Clearance from adjacent: 0.5mm (buccal, lingual, gingival)
- Tooth structure above gingiva: minimum 1mm
- Final occlusal depth: ~2mm
- Isthmus width: max 1/3 intercuspal, prefer just a bur width
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
| 4 | Occlusal extension along fissures (highlight); isthmus width indicator (max 1/3 intercuspal) |
| 5 | Proximal extension arrow (distal direction); "just beyond contact point" indicator |
| 6 | BL extension creating T-shape (highlight both arms) |
| 7-8 | Proximal box depth indicators |
| 9 | Matrix band overlay on distal |
| 10 | Wall break zone (red dashed, then removed) |
| 11 | Clearance measurement arrows |
| 12 | Bird beak zones highlighted |
| 13-14 | Smooth floor/wall indicators |
| 15 | S-curve/funnel zone in isthmus |
| 16 | Full margin check (green outline); "step" shape verification |

**Proximal view overlays by step:**
| Step | Overlay |
|------|---------|
| 1 | Fender wedge between teeth |
| 5 | Proximal extension with enamel lip dimension; "just beyond contact" |
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
| 6 | T-shape cross-section with BL width; isthmus width check |
| 11 | Clearance check from all directions |
| 14 | Floor depth + wall angle verification; "extended into dentine" check |
| 15 | S-curve/funnel profile from BL perspective |

**Buccal + Lingual views:** Similar to current buccal, showing progressive preparation outline.

---

### 11. Matrix System Guidance Section

**New section** based on IDC course slides. Educational content covering both matrix options:

**Changes to `index.html`:**
- Add new `<section id="matrix-panel">` after the instruments panel
- Content:
  - **Sectional Matrix Systems** (V Ring / Palodent): anatomical wedge + sectional matrix + holding ring; ring provides separation compensating for matrix thickness; more predictable proximal contour
  - **Tofflemire Matrices**: more familiar; does not fit as well; needs pre-contouring; greater thickness
  - **Key advice**: "Use what you are comfortable with. Try both more than once." (direct IDC quote)
  - Visual comparison card layout

**Changes to `styles.css`:**
- Matrix panel card styles (reuse instrument-card pattern)

---

## Files Modified

| File | Changes |
|------|---------|
| `app.js` | 16-step STEPS array, 2 new SVG draw functions, all SVG overlays for 16 steps, bur selection system, quiz system (15 questions using exam terminology), IDC G/P/B/F assessment system (rubber dam + 3-column cavity), free practice mode + timer, warning system mapped to marking sheet criteria, duration fields, clinical accuracy fixes |
| `index.html` | 2 new view tabs, bur selector area in step details, quiz section, rebuilt assessment section (rubber dam G/P/B/F + 3-column cavity G/P/B/F with full descriptors), mode toggle, timer display, expanded measurements panel, matrix system guidance section |
| `styles.css` | 5-view tab layout, bur card styles, quiz styles, G/P/B/F grading styles, satisfactory/unsatisfactory banners, rubber dam assessment card, 3-column assessment layout, mode toggle, timer, warning alerts (F-risk/B-risk/P-risk), matrix panel styles, new SVG overlay styles |

---

## What We Are NOT Doing (deferred / not feasible)

- **Haptic feedback** — requires native hardware APIs
- **Video tutorials** — requires external video hosting/content creation
- **Physics-based material removal** — requires WebGL/3D engine
- **Session recording/replay** — requires complex state serialization
- **Progress tracking with localStorage** — deferred to future iteration (keeps this PR focused)
- **Gamification (badges, leaderboard)** — deferred to future iteration
- **Multiple tooth anatomies** — deferred (current uses upper molar UL6/26 only)
- **Crown preparation criteria** — separate exam component, out of scope for this simulator
- **Temporary restoration criteria** — separate exam component, out of scope for this simulator

---

## Implementation Order

1. Rewrite STEPS array (16 steps with full content) + duration fields + "step cavity" terminology
2. Fix clinical accuracy (isthmus width, axial wall, pulpal floor, convenience form, proximal contact, water cooling, measurements panel)
3. Update existing 3 SVG views for 16-step overlays
4. Add Cross-Section + Lingual SVG views
5. Add bur selection interface
6. Add warning system (mapped to F/B/P grade risks from marking sheet)
7. Add quiz system (15 questions referencing actual exam criteria)
8. Rebuild assessment → IDC G/P/B/F system (rubber dam section + 3-column cavity assessment with full descriptors)
9. Add matrix system guidance section
10. Add free practice mode + timer
11. CSS for all new features
