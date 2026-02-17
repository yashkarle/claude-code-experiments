// ============================================================
// DO Class 2 Cavity Prep Simulator
// Interactive step-by-step dental preparation guide
// Irish Dental Council Bench Test — "Step" Cavity Preparation
// ============================================================

(function () {
  'use strict';

  // ----------------------------------------------------------
  // STEP DATA — 16-step guided sequence
  // ----------------------------------------------------------
  const STEPS = [
    {
      id: 1,
      title: 'Rubber Dam Isolation & Protection',
      phase: 'Pre-Procedure',
      duration: '2-3 min',
      description: `<p>Begin by selecting an appropriate clamp for the upper molar. For most upper molars, a Wingless W8A (Ivory) or 14A (Ash) clamp works well. Test the clamp on the tooth before placing the dam to ensure it seats firmly below the height of contour on all four line angles without rocking. The clamp must be stable &mdash; any rocking or displacement during the procedure will cost marks on the IDC Rubber Dam Criteria Sheet.</p>
<p>Punch holes for the teeth you plan to isolate. For a DO preparation on an upper molar, isolate at minimum the tooth being prepared and one tooth either side (typically the molar and at least one tooth either side). The IDC marking sheet specifically assesses whether an &ldquo;appropriate number of teeth&rdquo; have been isolated. Punch the holes using the correct punch size &mdash; use the molar setting. Space the holes according to the arch form.</p>
<p>Place the dam using your preferred technique (wing or wingless). Once seated, evert the dam around the necks of all isolated teeth using a flat plastic instrument and floss. Eversion is a specific criterion on the IDC Rubber Dam Criteria Sheet &mdash; the dam must be tucked into the gingival sulcus to create a seal. If the dam is not everted, it will pool saliva and obscure the operating field, and you will lose marks.</p>
<p>Verify that the dam is intact with no tears. A torn dam is marked as a deficiency. Ensure the dam provides clear visibility and access to the distal surface of the molar. Place a protective matrix band (e.g., a Tofflemire band or sectional matrix) on the adjacent tooth distally to prevent inadvertent damage during preparation. The IDC grades adjacent tooth damage harshly: &ldquo;damaged&rdquo; = B grade; &ldquo;mutilated&rdquo; = automatic F.</p>
<p>Confirm that your high-speed handpiece water spray is functioning. The IDC mandates that all cutting with the high-speed handpiece must be done with water coolant. Preparing without water is an automatic F grade due to &ldquo;risk of heat damage to pulp.&rdquo; Test the spray before you begin cutting.</p>`,
      instruments: [
        'Rubber dam sheet',
        'Rubber dam frame (Young\'s or Nygaard-Ostby)',
        'Rubber dam clamp (W8A / 14A)',
        'Rubber dam punch',
        'Rubber dam forceps',
        'Floss / tape for ligatures',
        'Flat plastic instrument (for eversion)',
        'Protective matrix band',
        'Clamp stabilising compound (if needed)',
      ],
      recommendedBur: null,
      tips: [
        'Practise your rubber dam placement to get it under 3 minutes &mdash; time spent here eats into preparation time',
        'Always test the clamp on the tooth before committing to the dam placement',
        'Bring multiple clamp sizes to the exam in case your first choice does not fit',
        'Use floss tied to the clamp bow as a safety retrieval line &mdash; some examiners look for this',
        'Eversion is easy to forget under pressure but is explicitly marked on the separate Rubber Dam Criteria Sheet',
      ],
      criteria: [
        { text: 'Clamp is stable and does not rock on the tooth', critical: true },
        { text: 'Appropriate number of teeth isolated (minimum: tooth + 1 either side)', critical: false },
        { text: 'Dam is everted around all isolated teeth', critical: false },
        { text: 'Dam is intact with no tears', critical: true },
        { text: 'Adjacent tooth has protective band or matrix in place', critical: true },
        { text: 'Water coolant confirmed functional before cutting', critical: true },
      ],
      commonMistakes: [
        'Choosing a clamp that rocks or pops off mid-procedure, wasting valuable time',
        'Failing to evert the dam &mdash; lost marks on the Rubber Dam Criteria Sheet',
        'Not placing a protective band on the adjacent tooth before starting the prep',
        'Tearing the dam during placement and not replacing it',
        'Isolating too few teeth, making access difficult and losing marks for inappropriate isolation',
        'Forgetting to check the water spray before beginning to cut',
      ],
      view: 'occlusal',
    },
    {
      id: 2,
      title: 'Marking with Pencil',
      phase: 'Pre-Procedure',
      duration: '2-3 min',
      description: `<p>Using a sharp pencil (a standard graphite pencil works well on the Frasaco tooth surface), mark out the entire cavity outline on the occlusal and proximal surfaces before making any cuts. This step is not assessed directly, but it serves as your roadmap and dramatically reduces errors during cutting. Take your time here &mdash; a well-planned outline prevents the most common IDC failures.</p>
<p>On the occlusal surface, mark the central fossa and the distal pit. Draw a line connecting them that follows the central groove. The occlusal outline should be conservative &mdash; no wider than one-third of the intercuspal width, and preferably just slightly wider than the bur head (approximately 1.5&ndash;2mm wide). Mark the mesial extent: the preparation should reach the transverse (oblique) ridge but must NOT cross it. Breaking the transverse ridge is a common error that weakens the remaining tooth structure unnecessarily.</p>
<p>On the distal surface, mark the proximal box outline. The box should extend just beyond the contact point to ensure the &ldquo;proximal contact is included in preparation&rdquo; &mdash; this is a specific G criterion on the IDC marking sheet. Mark the buccal and lingual walls of the box so that they clear the contact area. The gingival margin of the box should be approximately 1mm below the contact point, placing it just into the gingival embrasure.</p>
<p>Mark the depth references: the occlusal floor will sit at approximately 2mm depth (into dentine), and the axial wall of the proximal box at approximately 1.5mm from the external tooth surface. Remember the critical IDC criterion: &ldquo;Extended into dentine; no excessive tissue loss.&rdquo; The pulpal floor and axial wall must be in dentine &mdash; if entirely in enamel, this is an automatic F grade. Conversely, preparing excessively deep risks pulpal exposure.</p>
<p>Step back and review your markings from the occlusal, buccal, and proximal views. Verify symmetry and that the outline does not extend onto cuspal inclines. Confirm that your planned preparation will result in a &ldquo;step&rdquo; cavity shape &mdash; the IDC&rsquo;s own term for this preparation design &mdash; with a clear occlusal step and a proximal box connected at the isthmus.</p>`,
      instruments: [
        'Sharp graphite pencil',
        'Mouth mirror',
        'Probe / explorer',
        'Periodontal probe (for measurements)',
      ],
      recommendedBur: null,
      tips: [
        'Spend adequate time on planning &mdash; 2 minutes of marking can save 5 minutes of corrective cutting',
        'Use the periodontal probe to measure 2mm on the occlusal and mark depth reference points',
        'If your pencil marks are hard to see on the Frasaco tooth, try a softer lead pencil',
        'Mark the transverse ridge clearly so you know exactly where to stop your mesial extension',
        'Photograph your markings mentally &mdash; you will lose the pencil lines once you start cutting',
      ],
      criteria: [
        { text: 'Occlusal outline is no wider than 1/3 of intercuspal width', critical: false },
        { text: 'Proximal box outline clears the contact area', critical: false },
        { text: 'Mesial extent reaches but does not cross the transverse ridge', critical: false },
        { text: 'Outline follows a conservative "step" cavity design', critical: false },
        { text: 'Depth references marked at 2mm occlusal and 1.5mm axial', critical: false },
      ],
      commonMistakes: [
        'Skipping this step entirely due to time pressure &mdash; leads to freehand errors',
        'Making the occlusal outline too wide (exceeding 1/3 intercuspal width)',
        'Planning the proximal box too narrow, failing to clear the contact',
        'Forgetting to mark depth reference points, leading to inconsistent depth during cutting',
        'Not accounting for the transverse ridge and subsequently breaking it during preparation',
      ],
      view: 'occlusal',
    },
    {
      id: 3,
      title: 'Punch Cut in Proximal Pit',
      phase: 'Initial Access',
      duration: '1-2 min',
      description: `<p>With your round (001) carbide bur (Blue band) in the high-speed handpiece and water coolant running, make the initial entry point (the &ldquo;punch cut&rdquo;) in the distal pit / distal fossa of the occlusal surface. Hold the bur perpendicular to the occlusal surface (parallel to the long axis of the tooth). Apply the bur with a light, controlled touch &mdash; let the bur do the work. Do not force it.</p>
<p>Sink the bur to a depth of approximately 2mm. Use the bur shank as a visual depth reference. At 2mm depth in an upper molar, you should be cutting into dentine. If you are still entirely in enamel at 2mm, your angulation may be off or the tooth anatomy may require slight adjustment &mdash; but remember, the pulpal floor being entirely in enamel is an automatic F grade.</p>
<p>This initial punch cut serves two purposes: it establishes the correct depth for the occlusal portion of the cavity and it provides a reference point from which you will extend in subsequent steps. The cut should produce a small, clean, round-bottomed depression in the distal fossa area, approximately one bur-width in diameter.</p>
<p>Keep the bur steady &mdash; avoid any lateral rocking or tilting that could widen the preparation beyond what is needed. The IDC emphasises &ldquo;convenience form to allow access to ADJ and allow material to be placed in cavity&rdquo; &mdash; the preparation must be functional but conservative. Excessive tissue removal at this stage will compound as you extend the outline.</p>
<p>After making the punch cut, briefly pause and use the probe to verify the depth. Insert the probe into the cut and confirm approximately 2mm. This takes only a few seconds and ensures you are working to the correct depth from the outset.</p>`,
      instruments: [
        'High-speed handpiece with water coolant',
        'Round (001) carbide bur (Blue band)',
        'Mouth mirror',
        'Probe / explorer',
      ],
      recommendedBur: 'round-001',
      tips: [
        'Use the bur head length (approximately 1.5mm) as a built-in depth gauge &mdash; when the head is just past fully submerged, you are at approximately 2mm',
        'Ensure water spray is hitting the bur tip &mdash; adjust the nozzle if needed before starting',
        'A light touch and letting the bur speed do the work gives you more control than pressing hard',
        'Keep your finger rest (fulcrum) on a stable tooth nearby for maximum control',
        'If the Frasaco tooth feels different to a natural tooth, practise beforehand to calibrate your pressure',
      ],
      criteria: [
        { text: 'Initial cut placed accurately in the distal fossa', critical: false },
        { text: 'Depth of approximately 2mm achieved (into dentine)', critical: true },
        { text: 'Cut is approximately one bur-width in diameter (conservative)', critical: false },
        { text: 'Water coolant used throughout cutting', critical: true },
        { text: 'No lateral rocking or uncontrolled widening', critical: false },
      ],
      commonMistakes: [
        'Cutting without water coolant &mdash; automatic F for risk of heat damage to pulp',
        'Making the punch cut too shallow (staying in enamel) or too deep (risking pulpal exposure)',
        'Placing the initial cut too far mesially or distally relative to the planned outline',
        'Rocking the bur laterally, creating an unnecessarily wide initial opening',
        'Pressing too hard on the bur, reducing control and risking over-preparation',
      ],
      view: 'occlusal',
    },
    {
      id: 4,
      title: 'Occlusal Extension',
      phase: 'Outline Form',
      duration: '2-3 min',
      description: `<p>From the initial punch cut, extend the preparation mesially along the central groove toward the transverse ridge. Continue using the pear-shaped (330) carbide bur (Blue band) at the same 2mm depth. Move the bur in a controlled, sweeping motion along the groove pattern, maintaining a consistent depth and width. The preparation should follow the natural groove anatomy of the tooth.</p>
<p>The critical boundary is the transverse (oblique) ridge. Extend TO the ridge but do NOT break through it. The transverse ridge is a structural keystone of the molar &mdash; preserving it maintains the tooth&rsquo;s resistance to fracture. Visually, your mesial extent should stop at the point where the ridge begins to rise from the central fossa. If you are uncertain, err on the side of stopping slightly short rather than going too far. You can always refine later; you cannot add tooth structure back.</p>
<p>Maintain the width of the occlusal preparation at no more than one-third of the intercuspal (buccolingual) width. Ideally, keep it to just wider than the bur head &mdash; approximately 1.5&ndash;2mm. The IDC marking sheet criterion states the preparation should be no wider than &ldquo;1/3 intercuspal width.&rdquo; Going wider weakens the remaining cusps and is marked as a deficiency. Use the cuspal tips as visual references and try to stay well within the inner inclines.</p>
<p>As you extend mesially, ensure the occlusal floor (pulpal floor) remains flat and at a uniform 2mm depth. Avoid creating a scalloped or uneven floor &mdash; this will be assessed during the Quality Check phase. The floor should be smooth and perpendicular to the long axis of the tooth. The internal walls should have a slight divergence toward the occlusal surface (approximately 5&ndash;10 degrees) to provide a butt-joint margin suitable for composite restoration. Remember: no beveling for composite &mdash; this is an explicit G criterion on the IDC marking sheet.</p>
<p>After completing the mesial extension, verify the outline from the occlusal view. The preparation at this stage should appear as a narrow trough running from the distal fossa to just short of the transverse ridge, approximately 2mm deep and 1.5&ndash;2mm wide. The walls should be well-defined and the margins crisp.</p>`,
      instruments: [
        'High-speed handpiece with water coolant',
        'Pear-shaped (330) carbide bur (Blue band)',
        'Mouth mirror',
        'Probe / explorer',
        'Periodontal probe (for width measurement)',
      ],
      recommendedBur: 'pear-330',
      tips: [
        'Use the cusp tips as landmarks &mdash; staying within the inner third of the intercuspal distance keeps you safe',
        'If you cannot clearly see the transverse ridge, dry the tooth briefly with air and identify it before cutting further',
        'Move the bur in one direction (mesially) with controlled strokes rather than back-and-forth sawing',
        'Check your depth frequently by placing the probe alongside the bur head for reference',
        'A flat pulpal floor is easier to achieve if you keep your handpiece at a consistent angulation throughout',
      ],
      criteria: [
        { text: 'Occlusal extension reaches transverse ridge without breaking it', critical: true },
        { text: 'Width does not exceed 1/3 of intercuspal width', critical: true },
        { text: 'Uniform depth of 2mm maintained throughout', critical: false },
        { text: 'Pulpal floor is flat and smooth', critical: false },
        { text: 'No beveling of enamel margins (butt joint for composite)', critical: true },
        { text: 'Walls diverge slightly toward occlusal surface', critical: false },
      ],
      commonMistakes: [
        'Breaking through the transverse ridge &mdash; one of the most common errors in the IDC bench test',
        'Making the occlusal portion too wide, exceeding 1/3 intercuspal width and weakening cusps',
        'Inconsistent depth &mdash; deeper in some areas, shallower in others, creating an uneven pulpal floor',
        'Beveling the margins &mdash; composite restorations require butt-joint margins, not bevels',
        'Extending too far mesially past the transverse ridge out of habit from Class I preparations',
      ],
      view: 'occlusal',
    },
    {
      id: 5,
      title: 'Proximal Extension',
      phase: 'Outline Form',
      duration: '2-3 min',
      description: `<p>Now extend the preparation distally from the punch cut toward the proximal surface. Switch to the long needle / interproximal bur (Blue band), which is specifically designed for breaking through contact points without damaging the adjacent tooth. The goal is to begin establishing the proximal box by cutting through the marginal ridge and extending just past the contact area on the distal surface.</p>
<p>Angle the bur so that you are cutting distally, maintaining the same 2mm depth established in the occlusal portion. As you approach the marginal ridge, you will feel the bur begin to cut through the ridge. Continue until the bur has passed through the marginal ridge and the preparation opens onto the proximal surface. At this stage, you are creating the initial ditch or channel that will become the proximal box.</p>
<p>The proximal extension must include the contact area. The IDC marking sheet has a specific G criterion: &ldquo;Proximal contact included in preparation.&rdquo; If your preparation does not extend far enough distally to clear the contact point, the restoration will not be able to establish a proper contact with the adjacent tooth. Use the probe to verify that the preparation extends just past where the contact area would be.</p>
<p>Be extremely cautious of the adjacent tooth. Even with a protective matrix band in place, aggressive bur angulation or loss of control can damage the adjacent surface. The IDC grades this severely: &ldquo;damaged&rdquo; adjacent tooth = B grade; &ldquo;mutilated&rdquo; adjacent tooth = automatic F. Keep your bur angled slightly toward the tooth being prepared (away from the adjacent tooth) and maintain a steady fulcrum.</p>
<p>At this stage, do not attempt to create the full depth of the proximal box or the gingival seat. You are simply establishing the distal extension and opening the proximal surface. The box will be deepened and refined in subsequent steps. The result should be a channel or ditch that connects the occlusal trough to the proximal surface, approximately one bur-width wide at this point.</p>`,
      instruments: [
        'High-speed handpiece with water coolant',
        'Long needle / interproximal bur (Blue band)',
        'Mouth mirror',
        'Probe / explorer',
        'Protective matrix band on adjacent tooth',
      ],
      recommendedBur: 'long-needle',
      tips: [
        'Ensure the protective matrix band on the adjacent tooth is still in position before you begin this step',
        'Angle the bur slightly away from the adjacent tooth (toward the tooth being prepared) to minimise risk of damage',
        'You will feel a change in resistance as you cut through the marginal ridge &mdash; this is normal, maintain control',
        'Do not try to establish the full proximal box in one pass &mdash; this step is about extension only, not depth or form',
        'If you are unsure whether you have cleared the contact, slide a probe along the distal surface to check',
      ],
      criteria: [
        { text: 'Proximal contact area is included in the preparation', critical: true },
        { text: 'Marginal ridge has been cut through to open the proximal surface', critical: false },
        { text: 'Adjacent tooth is undamaged', critical: true },
        { text: 'Extension is conservative &mdash; just past the contact, not excessively wide', critical: false },
        { text: 'Water coolant used throughout', critical: true },
      ],
      commonMistakes: [
        'Not extending far enough distally, leaving the contact area intact (fails G criterion)',
        'Damaging the adjacent tooth with the bur &mdash; a B or F grade consequence',
        'Removing too much marginal ridge structure, making the isthmus area too wide',
        'Attempting to create the full proximal box depth in this step, losing control',
        'Losing the protective matrix band without noticing and subsequently damaging the adjacent tooth',
      ],
      view: 'proximal',
    },
    {
      id: 6,
      title: 'Buccolingual Extension (T-Shape)',
      phase: 'Outline Form',
      duration: '2-3 min',
      description: `<p>At the isthmus area where the occlusal portion meets the proximal box, extend the preparation buccolingually to create the characteristic T-shape (or &ldquo;step&rdquo; shape in IDC terminology) when viewed from the occlusal. This extension provides the convenience form necessary for proper access to the axio-pulpal line angle and for placement of the composite material.</p>
<p>Using the pear-shaped (330) bur, widen the distal portion of the occlusal preparation at the junction with the proximal box. The buccolingual width at the isthmus should be approximately 2&ndash;2.5mm &mdash; wide enough to allow a condenser or placement instrument to access the proximal box, but not so wide that you are unnecessarily removing tooth structure. The IDC G criterion specifies &ldquo;convenience form to allow access to ADJ and allow material to be placed in cavity.&rdquo;</p>
<p>The resulting shape, when viewed from the occlusal surface, should resemble a T: the stem of the T is the narrow occlusal trough extending mesially, and the crossbar of the T is the slightly wider isthmus/proximal box area extending buccolingually. This design is fundamental to the Class II &ldquo;step&rdquo; cavity preparation.</p>
<p>Ensure that the buccal and lingual walls of the proximal box extension diverge slightly toward the occlusal surface. This divergence (approximately 5&ndash;10 degrees from the vertical) ensures there are no undercuts that would trap air or prevent material placement. For composite, the walls should provide a clear path of insertion from the occlusal. Remember: no bevels &mdash; the margins must be butt joints.</p>
<p>Check the preparation from both the buccal and lingual aspects to confirm the T-shape is symmetrical and that neither the buccal nor lingual extension is excessive. The buccal and lingual walls of the proximal portion should just clear the contact area &mdash; extending significantly beyond this removes healthy tooth structure unnecessarily and may weaken the cusps. Verify that the enamel margins are not undermined; the IDC states that &ldquo;enamel margins grossly undermined&rdquo; is an F grade criterion.</p>`,
      instruments: [
        'High-speed handpiece with water coolant',
        'Pear-shaped (330) carbide bur (Blue band)',
        'Mouth mirror',
        'Probe / explorer',
      ],
      recommendedBur: 'pear-330',
      tips: [
        'Think of the T-shape as functional &mdash; the crossbar needs to be just wide enough for your condenser to reach the box floor',
        'Check the width with a condenser or flat plastic to make sure an instrument can physically access the proximal box through the isthmus',
        'The T-shape is more forgiving than you think &mdash; a slightly wider isthmus is better than one too narrow to instrument',
        'View from both buccal and lingual sides to confirm symmetry',
        'If in doubt about enamel undermining, check with a probe along the cavosurface margin',
      ],
      criteria: [
        { text: 'T-shape (step cavity form) clearly established when viewed occlusally', critical: false },
        { text: 'Isthmus width allows instrument access to proximal box', critical: true },
        { text: 'Enamel margins are not undermined', critical: true },
        { text: 'Buccal and lingual walls diverge slightly (no undercuts)', critical: false },
        { text: 'No beveling &mdash; butt-joint margins maintained', critical: true },
        { text: 'Extension is symmetrical and conservative', critical: false },
      ],
      commonMistakes: [
        'Making the isthmus too narrow, preventing proper instrument access to the proximal box',
        'Over-extending buccolingually, unnecessarily weakening the buccal or lingual cusps',
        'Creating undercuts in the walls that will trap air bubbles during composite placement',
        'Undermining enamel at the cavosurface margin &mdash; an F grade if grossly undermined',
        'Forgetting to check convenience form by physically testing instrument access',
      ],
      view: 'occlusal',
    },
    {
      id: 7,
      title: 'Drop the Bur (Proximal Depth)',
      phase: 'Proximal Box',
      duration: '2-3 min',
      description: `<p>This step establishes the depth of the proximal box. Using the pear-shaped (330) bur (Blue band), create two depth-cut ditches in the proximal box &mdash; one on the buccal wall and one on the lingual wall. These cuts serve primarily as depth guides to ensure a consistent and correct proximal box depth.</p>
<p>Position the bur against the buccal wall of the proximal box, near the bucco-axial line angle. Plunge the bur gingivally to create a vertical ditch or groove. The depth of this ditch should be approximately 1.5mm from the external proximal surface &mdash; enough to be clearly in dentine. Use a periodontal probe to verify the depth. Repeat the same cut on the lingual wall.</p>
<p>These two ditches serve as reference points: they define where the axial wall of the proximal box will sit, and they establish the gingival extent of the box. The gingival margin of the box should sit approximately 1&ndash;1.5mm below the original contact point level, placing it in the gingival embrasure but not extending excessively toward the CEJ.</p>
<p>The axial wall depth is critical for the IDC marking sheet. The criterion &ldquo;Extended into dentine; no excessive tissue loss&rdquo; means your preparation must reach dentine at the axial wall, but you must not cut so deep that you risk the pulp. In an upper molar, the pulp chamber is positioned centrally &mdash; the axial wall at 1.5mm from the proximal surface should provide adequate clearance while ensuring the preparation is in dentine.</p>
<p>Keep the bur parallel to the long axis of the tooth as you create these depth cuts. Any tilting or angulation will result in an uneven axial wall that will need correction later. Ensure water coolant is running throughout. After creating both ditches, use the probe to verify the depth and symmetry of the two cuts.</p>`,
      instruments: [
        'High-speed handpiece with water coolant',
        'Pear-shaped (330) carbide bur (Blue band)',
        'Mouth mirror',
        'Probe / explorer',
        'Periodontal probe (for depth measurement)',
      ],
      recommendedBur: 'pear-330',
      tips: [
        'Use a periodontal probe to verify 1.5mm depth at the proximal wall after each ditch cut',
        'Create the buccal ditch first, then the lingual &mdash; having one reference makes the second easier to match',
        'Keep the bur parallel to the long axis of the tooth to ensure a flat gingival seat later',
        'Do not extend the gingival margin excessively deep &mdash; 1&ndash;1.5mm below contact level is sufficient',
        'These depth cuts are guides for the next step, so accuracy here saves time later',
      ],
      criteria: [
        { text: 'Buccal and lingual depth ditches are at consistent depth (approximately 1.5mm)', critical: false },
        { text: 'Preparation extends into dentine at the axial wall', critical: true },
        { text: 'No excessive tissue removal risking pulpal exposure', critical: true },
        { text: 'Gingival extent is appropriate (1&ndash;1.5mm below contact level)', critical: false },
        { text: 'Ditches are parallel to the long axis of the tooth', critical: false },
        { text: 'Water coolant used throughout', critical: true },
      ],
      commonMistakes: [
        'Creating depth cuts that are too shallow, leaving the axial wall in enamel (F grade criterion)',
        'Creating depth cuts that are too deep, risking pulpal exposure',
        'Making the buccal and lingual ditches at different depths, leading to an asymmetric box',
        'Tilting the bur so the ditches are not parallel to the long axis, creating an angled gingival seat',
        'Extending the gingival margin too far apically, removing excessive tissue',
      ],
      view: 'proximal',
    },
    {
      id: 8,
      title: 'Join the Two Ditches',
      phase: 'Proximal Box',
      duration: '2-3 min',
      description: `<p>With the two depth-cut ditches established on the buccal and lingual walls (from Step 7), now connect them by removing the tooth structure between them. This creates the full proximal box with a defined axial wall, gingival seat, and buccal and lingual walls. Continue using the pear-shaped (330) bur (Blue band).</p>
<p>Starting from one ditch (e.g., the buccal), sweep the bur across the proximal surface at the depth established by your ditches, moving toward the lingual ditch. The bur should remove the intervening tooth structure in controlled, overlapping passes. Work from the occlusal aspect gingivally, removing tooth structure layer by layer rather than attempting to cut the entire depth in one pass.</p>
<p>As you join the ditches, you are forming the axial wall of the proximal box. This wall should be flat, smooth, and at a consistent depth of approximately 1.5mm from the proximal surface. The axial wall should be roughly perpendicular to the buccal and lingual walls (when viewed in cross-section) and should meet the pulpal floor of the occlusal portion at a rounded axio-pulpal line angle.</p>
<p>The gingival seat (floor of the proximal box) should be flat and perpendicular to the long axis of the tooth. At this stage, it may be slightly rough &mdash; it will be refined in Step 13. The important thing now is that the gingival seat is at a consistent level across the full buccolingual width of the box, and that it creates a clear, defined margin.</p>
<p>After joining the ditches, inspect the proximal box from the proximal view. You should see a well-defined box shape: flat axial wall at the back, relatively flat gingival seat at the bottom, and buccal and lingual walls that diverge slightly toward the proximal surface (5&ndash;10 degrees). The box should transition smoothly into the occlusal portion at the isthmus. Check that all margins are in tooth structure and none are unsupported or undermined.</p>`,
      instruments: [
        'High-speed handpiece with water coolant',
        'Pear-shaped (330) carbide bur (Blue band)',
        'Mouth mirror',
        'Probe / explorer',
      ],
      recommendedBur: 'pear-330',
      tips: [
        'Work in overlapping passes from occlusal to gingival &mdash; this gives better control than trying to cut the full depth at once',
        'The axial wall depth should match the depth of your ditches &mdash; use the ditches as your guide and do not go deeper',
        'Pause periodically to clear debris with air/water and visually confirm your progress',
        'If you feel the bur &ldquo;chattering&rdquo; or vibrating, reduce pressure and let the bur speed do the cutting',
        'The transition between the occlusal floor and the axial wall (axio-pulpal line angle) should be gently rounded, not sharp',
      ],
      criteria: [
        { text: 'Buccal and lingual ditches are fully connected with a flat axial wall', critical: false },
        { text: 'Axial wall is at consistent depth (approximately 1.5mm from proximal surface)', critical: false },
        { text: 'Gingival seat is at a consistent level across the box width', critical: false },
        { text: 'Buccal and lingual walls diverge slightly toward the proximal surface', critical: false },
        { text: 'Smooth transition from occlusal portion to proximal box at isthmus', critical: false },
        { text: 'No unsupported or undermined enamel margins', critical: true },
      ],
      commonMistakes: [
        'Leaving a ridge of tooth structure between the two ditches (incomplete joining)',
        'Creating an axial wall that is deeper in the middle than at the sides (scalloped wall)',
        'Making the gingival seat uneven &mdash; higher on one side than the other',
        'Sharp axio-pulpal line angle instead of rounded &mdash; creates stress concentration',
        'Cutting too aggressively and going deeper than the planned axial wall depth',
      ],
      view: 'proximal',
    },
    {
      id: 9,
      title: 'Protect Adjacent Tooth',
      phase: 'Proximal Box',
      duration: '1-2 min',
      description: `<p>Before proceeding further with the proximal box, pause to verify and reinforce the protection of the adjacent tooth. This step is a deliberate checkpoint &mdash; adjacent tooth damage is one of the most heavily penalised errors on the IDC marking sheet (&ldquo;damaged&rdquo; = B grade; &ldquo;mutilated&rdquo; = automatic F grade). Taking a moment to verify protection now can save your entire exam result.</p>
<p>Check the protective matrix band that was placed in Step 1. Is it still in position? Has it shifted during the proximal cutting? If the band has moved, reposition it carefully. If it has been damaged by the bur, replace it with a fresh band. The band should sit snugly against the adjacent tooth&rsquo;s mesial surface, covering the area directly opposite your proximal box.</p>
<p>Visually inspect the adjacent tooth&rsquo;s surface that faces your preparation. Look for any scratches, nicks, or gouges that may have been caused by the bur during Steps 5, 7, or 8. On a Frasaco tooth, bur marks will be visible as scratches or divots in the plastic surface. If you notice any damage, note it &mdash; it cannot be undone, but you can take extra care for the remaining steps to prevent further injury.</p>
<p>Consider the angulation of your bur for the remaining proximal box steps. The most dangerous moment for adjacent tooth damage is when the bur exits the proximal surface of the tooth being prepared. At this point, if the bur is angled even slightly toward the adjacent tooth, it can contact and damage it. For all subsequent proximal cutting, angle the bur slightly away from the adjacent tooth (toward the tooth being prepared) and use a light touch as you approach the proximal surface.</p>
<p>If you have not already done so, consider placing a thin metal strip (e.g., a dead-soft matrix band or a Tofflemire band) between the teeth to act as a physical barrier. This provides an additional layer of protection beyond the band already in place. Some candidates use two layers of protection in the IDC exam &mdash; the slight time investment is worth the security.</p>`,
      instruments: [
        'Protective matrix band (replacement if needed)',
        'Mouth mirror',
        'Probe / explorer',
        'Thin metal strip / dead-soft matrix band (additional protection)',
        'College tweezers',
      ],
      recommendedBur: null,
      tips: [
        'This checkpoint takes only 1&ndash;2 minutes but can be the difference between passing and failing the entire exam',
        'If you notice the matrix band has shifted, do NOT continue cutting until it is repositioned',
        'Some candidates bring extra matrix bands pre-cut to size &mdash; this saves time if a replacement is needed',
        'From this point forward, always visualise the adjacent tooth position before engaging the bur in the proximal box',
        'If you have already inadvertently scratched the adjacent tooth, do not panic &mdash; a minor scratch is a B grade, not an F. Focus on preventing further damage',
      ],
      criteria: [
        { text: 'Protective matrix band is in correct position on adjacent tooth', critical: true },
        { text: 'Adjacent tooth shows no signs of damage', critical: true },
        { text: 'Additional protection placed if needed', critical: false },
        { text: 'Bur angulation strategy confirmed for remaining proximal steps', critical: false },
      ],
      commonMistakes: [
        'Not checking the matrix band position &mdash; assuming it is still where you placed it in Step 1',
        'Continuing to cut the proximal box with a displaced or absent matrix band',
        'Ignoring minor damage to the adjacent tooth and continuing with the same bur angulation',
        'Using excessive force near the proximal surface, causing the bur to jump toward the adjacent tooth',
        'Not having replacement matrix bands prepared, losing time if the original band is damaged',
      ],
      view: 'proximal',
    },
    {
      id: 10,
      title: 'Break the Wall',
      phase: 'Proximal Box',
      duration: '2-3 min',
      description: `<p>If any remaining thin shell of enamel exists on the proximal surface (the &ldquo;wall&rdquo;), it must now be intentionally removed to complete the proximal box opening. In some preparations, Steps 5&ndash;8 will have already removed all proximal enamel, but frequently a thin, unsupported shell remains, particularly at the buccal and lingual corners of the box. This step ensures complete removal of this wall.</p>
<p>Using the pear-shaped (330) bur at low speed or a hand instrument (such as an enamel hatchet or a spoon excavator), carefully remove any remaining thin enamel shell. If using the bur, use a very light touch &mdash; the shell is thin and the bur can easily pass through it and contact the adjacent tooth. A hand instrument may be safer for this step: place the blade against the inner surface of the enamel shell and apply gentle outward pressure to fracture it away.</p>
<p>After removing the wall, examine the proximal box from the proximal view. The box should now be fully open to the proximal surface. The axial wall should be visible and the gingival seat clearly defined. The buccal and lingual walls of the box should form clean, defined margins that are continuous with the enamel of the tooth surface.</p>
<p>Check critically for any unsupported enamel remaining at the margins of the proximal box. The IDC marking sheet states that &ldquo;enamel margins grossly undermined&rdquo; is an automatic F grade. Run your probe along all the margins of the proximal box &mdash; buccal wall, lingual wall, and gingival seat. If the probe catches on any thin, unsupported enamel flakes, remove them with the probe or a hand instrument. Every margin must be supported by sound dentine beneath.</p>
<p>At the completion of this step, the basic cavity form should be fully established: occlusal trough connected to a proximal box, forming the characteristic &ldquo;step&rdquo; cavity design. The remaining steps focus on verification and refinement of this form. Take a moment to assess the overall preparation from multiple angles &mdash; occlusal, buccal, lingual, and proximal &mdash; before proceeding.</p>`,
      instruments: [
        'High-speed handpiece with water coolant (light touch)',
        'Pear-shaped (330) carbide bur (Blue band)',
        'Enamel hatchet',
        'Spoon excavator',
        'Probe / explorer',
        'Mouth mirror',
      ],
      recommendedBur: 'pear-330',
      tips: [
        'A hand instrument is often safer than a bur for removing the final thin enamel shell &mdash; less risk of adjacent tooth damage',
        'If the enamel shell does not fracture cleanly, use the bur at very low pressure to thin it further before fracturing',
        'Run the probe along every margin after removing the wall &mdash; feel for any remaining thin, unsupported enamel',
        'This is a good moment to step back and assess the overall preparation from multiple angles',
        'Do not rush this step &mdash; unsupported enamel left behind is an F-grade criterion',
      ],
      criteria: [
        { text: 'All remaining thin enamel shell removed from proximal surface', critical: false },
        { text: 'No grossly undermined enamel at any margin', critical: true },
        { text: 'Proximal box is fully open with visible axial wall and gingival seat', critical: false },
        { text: 'All margins are supported by sound tooth structure', critical: true },
        { text: 'Adjacent tooth undamaged during wall removal', critical: true },
        { text: 'Overall "step" cavity form is established', critical: false },
      ],
      commonMistakes: [
        'Leaving unsupported enamel shell in place &mdash; appears as undermined margins (F grade)',
        'Using excessive bur force to remove the wall and contacting the adjacent tooth',
        'Breaking the wall unevenly, leaving irregular margins that are difficult to refine',
        'Not checking all margins with a probe &mdash; undermined enamel can be hard to see visually',
        'Removing too much tooth structure while breaking the wall, over-extending the box',
      ],
      view: 'proximal',
    },
    {
      id: 11,
      title: 'Check Clearance',
      phase: 'Verification',
      duration: '1-2 min',
      description: `<p>This is a critical verification step. Before moving to refinement, confirm that the proximal box has adequate clearance from the adjacent tooth. Pass a probe or explorer through the proximal embrasure between the prepared tooth and the adjacent tooth. The instrument should pass freely through the space without catching on the preparation margins or the adjacent tooth.</p>
<p>Check the clearance at three levels: (1) at the gingival seat level &mdash; the probe should pass gingivally past the gingival margin without obstruction; (2) at the mid-box level &mdash; the probe should confirm that the buccal and lingual walls have cleared the contact area; (3) at the marginal ridge level &mdash; confirm the marginal ridge has been fully removed and there is clear access from the occlusal.</p>
<p>Verify the critical dimensions in cross-section. The axial wall should be approximately 1.5mm deep from the proximal surface. The pulpal floor of the occlusal portion should be approximately 2mm deep from the occlusal surface. These two planes should meet at the axio-pulpal line angle, which should be gently rounded (not a sharp 90-degree angle). Use the periodontal probe to measure these depths &mdash; the probe markings provide reliable measurements.</p>
<p>Confirm that the preparation has achieved the IDC criterion: &ldquo;Extended into dentine; no excessive tissue loss.&rdquo; The pulpal floor and axial wall must both be in dentine. On a Frasaco tooth, the dentine layer is typically represented by a different colour or texture than the enamel &mdash; use this visual cue. If either surface appears to still be in enamel, the preparation is too shallow and will receive an F grade. If the preparation appears excessively deep (approaching the pulp chamber representation), it is too deep.</p>
<p>Finally, verify that the overall cavity form has &ldquo;convenience form&rdquo; &mdash; can you physically access all surfaces of the preparation with a condenser or placement instrument? Insert a flat plastic or condenser through the occlusal opening and verify it can reach the gingival seat of the proximal box, the axial wall, and the buccal and lingual walls. If any surface is inaccessible, the isthmus or box may need slight widening.</p>`,
      instruments: [
        'Probe / explorer',
        'Periodontal probe (for measurements)',
        'Mouth mirror',
        'Flat plastic / condenser (for access testing)',
        'Three-in-one syringe (air/water for visibility)',
      ],
      recommendedBur: null,
      tips: [
        'Use the periodontal probe systematically &mdash; check depths at multiple points, not just the centre',
        'The Frasaco tooth enamel-dentine junction may be visible as a colour change &mdash; use this to confirm you are in dentine',
        'If the probe catches anywhere in the proximal embrasure, note exactly where and address it in the refinement steps',
        'Testing instrument access now is much better than discovering access problems during a timed exam restoration',
        'This verification should take only 1&ndash;2 minutes &mdash; it is a check, not a rework. If you find major issues, address them before proceeding to refinement',
      ],
      criteria: [
        { text: 'Proximal clearance confirmed &mdash; probe passes freely through embrasure', critical: false },
        { text: 'Axial wall depth approximately 1.5mm (in dentine)', critical: true },
        { text: 'Pulpal floor depth approximately 2mm (in dentine)', critical: true },
        { text: 'Axio-pulpal line angle is rounded', critical: false },
        { text: 'Convenience form confirmed &mdash; instruments can access all surfaces', critical: true },
        { text: 'No excessive tissue removal', critical: true },
      ],
      commonMistakes: [
        'Skipping this verification step to save time &mdash; errors found later take more time to fix',
        'Measuring depth at only one point and assuming the rest is consistent',
        'Not testing actual instrument access &mdash; assuming the opening looks wide enough without physical verification',
        'Failing to notice that the preparation is still in enamel (particularly at the axial wall)',
        'Not identifying a remaining enamel overhang or catch point in the proximal embrasure',
      ],
      view: 'cross-section',
    },
    {
      id: 12,
      title: 'Prep the Bird Beaks',
      phase: 'Refinement',
      duration: '2-3 min',
      description: `<p>The &ldquo;bird beaks&rdquo; are the buccal and lingual cavosurface margins of the proximal box where they meet the external tooth surface. These margins are critical for the seal and aesthetics of the final restoration. They must be smooth, well-defined, and slightly flared to ensure no undermined enamel remains and to create clean, accessible margins for composite placement.</p>
<p>Switch to the football/egg (379) bur (Green band). This bur&rsquo;s rounded profile allows precise contouring of the buccal and lingual walls of the proximal box without removing excessive tooth structure. Position the bur against the buccal wall of the proximal box and run it gingivally along the wall from the isthmus to the gingival seat. The goal is to create a smooth, slightly flared wall that eliminates any enamel undermining and creates a definitive cavosurface margin.</p>
<p>The flare should be gentle &mdash; approximately 5&ndash;10 degrees of divergence from the vertical (toward the proximal surface). This ensures that the enamel rods at the margin are supported by underlying tooth structure and that the composite can be placed and finished to a smooth, flush margin. Repeat on the lingual wall.</p>
<p>When viewed from the proximal, the completed bird beaks should create a smooth, gentle curve from the buccal and lingual tooth surfaces into the proximal box. There should be no sharp angles, ledges, or steps in the margin. The transition should be continuous and flowing. The margin should be clearly visible and palpable with a probe &mdash; run the probe along the entire buccal and lingual margins to verify smoothness.</p>
<p>Be conservative with the football/egg bur &mdash; the Green band indicates it is coarse and it is easy to remove more tooth structure than intended. Use light, controlled strokes and check your progress frequently. The bird beaks do not need to be perfectly symmetrical, but both should be equally smooth and well-defined. Remember: the IDC marking sheet assesses &ldquo;walls and margins smooth and cavity well defined&rdquo; for a G grade.</p>`,
      instruments: [
        'High-speed handpiece with water coolant',
        'Football/egg (379) bur (Green band)',
        'Mouth mirror',
        'Probe / explorer',
      ],
      recommendedBur: 'football-379',
      tips: [
        'The football/egg bur (Green band) is coarse &mdash; use a light touch and let the bur speed do the work',
        'Run the probe along the margin after each pass to feel for any remaining ledges or irregularities',
        'The flare should be subtle &mdash; think of it as &ldquo;opening up&rdquo; the margin, not creating a wide chamfer',
        'View the margins from the proximal aspect to verify the bird beak contour &mdash; it should be a smooth, gentle curve',
        'If you are unsure about the degree of flare, err on the side of less &mdash; you can always refine further',
      ],
      criteria: [
        { text: 'Buccal and lingual bird beaks are smooth and well-defined', critical: false },
        { text: 'Gentle flare of 5&ndash;10 degrees provides supported enamel margins', critical: false },
        { text: 'No enamel undermining at the proximal margins', critical: true },
        { text: 'Continuous, flowing transition from tooth surface into proximal box', critical: false },
        { text: 'Margins are clearly visible and palpable with a probe', critical: false },
        { text: 'No excessive tooth structure removal during refinement', critical: true },
      ],
      commonMistakes: [
        'Over-flaring the bird beaks, creating excessively wide proximal margins',
        'Leaving a ledge or step in the buccal-lingual margin transition',
        'Not checking with a probe &mdash; visual inspection alone can miss subtle irregularities',
        'Using a bur that is too large for this delicate refinement work',
        'Creating asymmetric bird beaks (one well-refined, one neglected)',
      ],
      view: 'proximal',
    },
    {
      id: 13,
      title: 'Smoothen Gingival Seat',
      phase: 'Refinement',
      duration: '2-3 min',
      description: `<p>The gingival seat (floor of the proximal box) must be refined to be flat, smooth, and at a consistent level across the full buccolingual width of the box. Switch to the finishing bur (Red or Yellow band), which is ideal for smoothing without removing significant additional tooth structure. The finishing bur provides a finishing action rather than a cutting action.</p>
<p>Run the finishing bur across the gingival seat in gentle, sweeping passes from buccal to lingual. The bur should lightly abrade the surface, removing any roughness, ridges, or irregularities left by the pear-shaped (330) bur during the initial box preparation. The goal is a glass-smooth seat that will provide a perfect seal with the composite at the gingival margin.</p>
<p>The gingival seat should be perpendicular to the long axis of the tooth. Check this by viewing the preparation from the buccal or lingual aspect &mdash; the gingival seat should appear as a horizontal line (relative to the tooth axis). If the seat is angled, it will compromise the margin seal and may be marked as a deficiency. Use the periodontal probe laid flat on the gingival seat to visually confirm it is flat and level.</p>
<p>Pay particular attention to the junction of the gingival seat with the axial wall (the gingivoaxial line angle). This junction should be a clearly defined, slightly rounded angle &mdash; not a sharp 90-degree corner (which would create a stress concentration) and not a vague, rounded-over transition (which would make the gingival margin indistinct). The IDC assesses whether the &ldquo;cavity is well defined&rdquo; for a G grade, and a clean gingivoaxial line angle is part of this criterion.</p>
<p>After smoothing, run the probe along the gingival seat and across the gingivoaxial line angle. The probe should glide smoothly across the entire seat without catching on any roughness, ridges, or debris. The gingival margin should be clearly palpable as a distinct edge where the seat meets the external tooth surface. A well-defined gingival margin is essential for a successful composite restoration and for a G grade on the IDC marking sheet.</p>`,
      instruments: [
        'High-speed or slow-speed handpiece with water coolant',
        'Finishing bur (Red or Yellow band)',
        'Periodontal probe (for flatness check)',
        'Probe / explorer',
        'Mouth mirror',
      ],
      recommendedBur: 'finishing',
      tips: [
        'The finishing bur should be used with minimal pressure &mdash; it is a finishing instrument, not a cutting one',
        'Lay the periodontal probe flat on the gingival seat and look for any rocking &mdash; a flat seat will not rock the probe',
        'The gingival seat is one of the most scrutinised areas by IDC examiners &mdash; invest the time to get it right',
        'If you find the seat is angled, use the pear-shaped (330) bur briefly to correct the angle before finishing',
        'Good lighting and a dry field (air syringe) are essential for evaluating the smoothness of the gingival seat',
      ],
      criteria: [
        { text: 'Gingival seat is flat and smooth', critical: false },
        { text: 'Seat is perpendicular to the long axis of the tooth', critical: false },
        { text: 'Gingivoaxial line angle is clearly defined and slightly rounded', critical: false },
        { text: 'Gingival margin is distinct and well-defined', critical: true },
        { text: 'No roughness, ridges, or debris on the seat', critical: false },
        { text: 'Walls and margins smooth and cavity well defined (IDC G criterion)', critical: true },
      ],
      commonMistakes: [
        'Leaving the gingival seat rough from the initial bur cuts &mdash; examiners will feel this with a probe',
        'Creating a gingival seat that is angled rather than perpendicular to the tooth axis',
        'Over-smoothing and inadvertently deepening the gingival seat, creating excessive tissue loss',
        'Neglecting the gingivoaxial line angle &mdash; leaving it either too sharp or too vague',
        'Not verifying flatness with a probe laid on the seat &mdash; visual inspection alone is insufficient',
      ],
      view: 'proximal',
    },
    {
      id: 14,
      title: 'Smoothen Occlusal Floor & Walls',
      phase: 'Refinement',
      duration: '2-3 min',
      description: `<p>Refine the occlusal portion of the preparation. The pulpal floor and all internal walls must be smooth and well-defined. Use the finishing bur (Red or Yellow band) for the floor and the round (001) bur (Blue band) for rounding internal line angles. This step addresses the IDC G criterion: &ldquo;walls and margins smooth and cavity well defined.&rdquo;</p>
<p>Start with the pulpal floor (occlusal floor). Run the finishing bur gently across the floor in mesio-distal passes. The floor should be flat, smooth, and at a consistent 2mm depth from the occlusal surface. Any ridges, grooves, or unevenness from the initial cutting should be smoothed away. The floor should be perpendicular to the long axis of the tooth when viewed in cross-section.</p>
<p>Next, refine the buccal and lingual walls of the occlusal portion. These walls should be smooth and should diverge slightly toward the occlusal surface (approximately 5&ndash;10 degrees). Run the finishing bur lightly along each wall. Check that the cavosurface margins at the occlusal surface are sharp, clean butt joints &mdash; no beveling, no rounding, no feathered edges. The IDC explicitly marks the absence of beveling as a G criterion for composite preparations.</p>
<p>Using the round (001) bur (Blue band, slow-speed), gently round all internal line angles. The pulpo-buccal, pulpo-lingual, and pulpo-axial line angles should be gently rounded, not sharp. Sharp internal line angles concentrate stress and can lead to fracture of the restoration or the remaining tooth structure. The rounding should be subtle &mdash; just enough to eliminate the sharp corner, not enough to create a coved or concave junction.</p>
<p>After completing the wall and floor refinement, examine the preparation in cross-section view (mentally or by viewing from the proximal). You should see: a flat pulpal floor at 2mm depth, smooth buccal and lingual walls diverging toward the occlusal, rounded internal line angles, and crisp butt-joint margins at the cavosurface. The transition from the occlusal portion to the proximal box at the isthmus should be smooth and continuous. All surfaces should be free of bur marks, ridges, or debris.</p>`,
      instruments: [
        'High-speed or slow-speed handpiece',
        'Finishing bur \u2014 Red or Yellow band (floor and walls)',
        'Round (001) bur \u2014 Blue band (line angles)',
        'Probe / explorer',
        'Mouth mirror',
        'Three-in-one syringe',
      ],
      recommendedBur: 'finishing',
      tips: [
        'Use the finishing bur at light pressure &mdash; you are finishing, not cutting',
        'Switch to the round (001) bur in the slow-speed handpiece for rounding line angles &mdash; better control at low speed',
        'After smoothing, dry the preparation with air and examine under good lighting to see any remaining irregularities',
        'The cavosurface margin must be a butt joint &mdash; if you see any hint of a bevel or feathered edge, it needs correction',
        'Run the probe along the floor from mesial to distal &mdash; it should glide without catching',
      ],
      criteria: [
        { text: 'Pulpal floor is flat, smooth, and at consistent 2mm depth', critical: false },
        { text: 'Buccal and lingual walls are smooth with slight occlusal divergence', critical: false },
        { text: 'Cavosurface margins are butt joints with no beveling', critical: true },
        { text: 'All internal line angles are gently rounded', critical: false },
        { text: 'Walls and margins smooth and cavity well defined (IDC G criterion)', critical: true },
        { text: 'No bur marks, ridges, or debris on any surface', critical: false },
        { text: 'Transition from occlusal to proximal is smooth and continuous', critical: false },
      ],
      commonMistakes: [
        'Inadvertently beveling the cavosurface margins while smoothing the walls',
        'Leaving sharp internal line angles &mdash; stress concentrators that reduce restoration longevity',
        'Over-smoothing and creating a concave floor (deeper in the centre than at the edges)',
        'Neglecting the mesial wall (near the transverse ridge) &mdash; it needs smoothing too',
        'Using the finishing bur too aggressively and deepening the preparation beyond 2mm',
      ],
      view: 'cross-section',
    },
    {
      id: 15,
      title: 'Make the S-Curve / Funnel',
      phase: 'Refinement',
      duration: '1-2 min',
      description: `<p>This step creates the final proximal box contour &mdash; the characteristic S-curve (also described as a &ldquo;funnel&rdquo; shape) of the proximal box walls when viewed from the proximal aspect. The S-curve refers to the gentle, flowing transition from the narrower axial wall depth to the wider proximal opening. This contour ensures no undercuts exist that would trap air, and it provides a smooth path of withdrawal for placement instruments.</p>
<p>Using the football/egg (379) bur (Green band), refine the buccal and lingual walls of the proximal box so that they diverge gradually and smoothly from the axial wall toward the proximal surface. The walls should not be dead straight &mdash; they should have a subtle, continuous curve that flares outward. When traced from the axial wall to the cavosurface margin, the wall profile should describe a gentle S-shape: slightly concave near the axial wall, transitioning to slightly convex near the external surface.</p>
<p>This S-curve or funnel shape serves several clinical purposes: it eliminates undercuts that would trap air during composite placement; it ensures all enamel rods at the cavosurface margin are supported by underlying structure; it provides a smooth, flowing path for condensing instruments; and it creates aesthetically pleasing proximal contours for the final restoration.</p>
<p>Use very light, controlled strokes with the football/egg bur. You are making subtle adjustments to the wall contour, not removing significant tooth structure. Check your progress frequently by viewing the proximal box from the proximal aspect. The buccal and lingual walls should appear as smooth, gently curving surfaces that open outward like a funnel. There should be no flat spots, ledges, or abrupt changes in angulation.</p>
<p>After establishing the S-curve on both walls, run the probe from the axial wall along the buccal wall to the cavosurface margin, then repeat on the lingual wall. The probe should follow a smooth, continuous curve without catching on any irregularity. The final proximal box, when viewed from the proximal aspect, should appear as a well-proportioned, symmetrical funnel shape that invites easy access for composite placement.</p>`,
      instruments: [
        'High-speed handpiece with water coolant',
        'Football/egg (379) bur (Green band)',
        'Probe / explorer',
        'Mouth mirror',
      ],
      recommendedBur: 'football-379',
      tips: [
        'The S-curve is subtle &mdash; you are refining the wall contour, not reshaping the entire box',
        'Think of the S-curve as removing any undercuts while creating a smooth, flowing wall profile',
        'Check from the proximal view after each pass &mdash; the improvement should be visible',
        'The funnel shape should be symmetrical &mdash; spend equal time on both the buccal and lingual walls',
        'If you are uncertain about undercuts, try inserting a flat plastic instrument along each wall &mdash; it should slide in and out without catching',
      ],
      criteria: [
        { text: 'Proximal box walls exhibit a smooth S-curve / funnel shape', critical: false },
        { text: 'No undercuts present in the proximal box', critical: true },
        { text: 'Buccal and lingual walls diverge smoothly toward the proximal surface', critical: false },
        { text: 'Wall profiles are continuous with no flat spots or ledges', critical: false },
        { text: 'Symmetrical funnel shape when viewed from proximal', critical: false },
        { text: 'All enamel margins supported at the cavosurface', critical: true },
      ],
      commonMistakes: [
        'Over-refining the walls and creating an excessively wide proximal box',
        'Leaving an undercut on one wall while successfully eliminating it on the other',
        'Creating a sharp transition point in the wall instead of a smooth, continuous curve',
        'Not checking for undercuts with an instrument &mdash; assuming visual inspection is sufficient',
        'Spending too long on this refinement step at the expense of the final verification',
      ],
      view: 'proximal',
    },
    {
      id: 16,
      title: 'Final Verification & Inspection',
      phase: 'Quality Check',
      duration: '2-3 min',
      description: `<p>This is your final quality assurance check before presenting the preparation for examination. Systematically inspect every aspect of the preparation against the IDC marking sheet criteria. This step should be methodical and thorough &mdash; go through each criterion in order and verify compliance. Do not rush this step; it is your last opportunity to identify and correct any deficiencies.</p>
<p><strong>External Outline (from occlusal view):</strong> Verify the &ldquo;step&rdquo; cavity form. The occlusal portion should extend from the distal fossa to the transverse ridge (but not breaking it), with a width no greater than 1/3 of the intercuspal distance. The proximal box should open onto the distal surface, clearing the contact area. The T-shape should be clearly visible. Confirm there is no beveling at any margin &mdash; all cavosurface margins should be butt joints.</p>
<p><strong>Internal Outline (cross-section view):</strong> Verify depth: occlusal floor at 2mm, axial wall at approximately 1.5mm. Both surfaces must be in dentine &mdash; not in enamel (F grade) and not excessively deep (excessive tissue loss). The axio-pulpal line angle should be rounded. All internal line angles should be rounded. Walls should diverge slightly toward the occlusal / proximal surfaces. Verify &ldquo;convenience form&rdquo; &mdash; instruments can access all surfaces. Check that the preparation has been &ldquo;extended into dentine; no excessive tissue loss.&rdquo;</p>
<p><strong>Proximal Box (proximal view):</strong> Gingival seat is flat, smooth, and perpendicular to the long axis. Bird beaks are smooth and well-defined. S-curve / funnel shape established on buccal and lingual walls. No undercuts. No undermined enamel. The gingival margin is clearly defined.</p>
<p><strong>Overall Quality:</strong> All walls and margins must be &ldquo;smooth and cavity well defined&rdquo; (G criterion). Run the probe along every margin &mdash; occlusal cavosurface, proximal cavosurface (buccal and lingual), and gingival margin. The probe should glide smoothly without catching. Check for any debris, loose enamel fragments, or residual pencil markings in the preparation. Clean the preparation with air/water.</p>
<p><strong>Adjacent Tooth:</strong> Perform a final inspection of the adjacent tooth. Check the mesial surface for any damage &mdash; scratches, nicks, or gouges. The IDC grades this severely: &ldquo;damaged&rdquo; = B grade; &ldquo;mutilated&rdquo; = F grade. If the rubber dam is still in place, verify it is intact. Remove the protective matrix band and inspect the adjacent tooth surface carefully before presenting the preparation for marking.</p>`,
      instruments: [
        'Probe / explorer',
        'Periodontal probe (for final measurements)',
        'Mouth mirror',
        'Three-in-one syringe (air/water)',
        'College tweezers (for debris removal)',
      ],
      recommendedBur: null,
      tips: [
        'Use the IDC marking sheet criteria as a literal checklist &mdash; go through each criterion and verify it one by one',
        'The most commonly failed criteria are: preparation not in dentine, undermined enamel, adjacent tooth damage, and absent convenience form',
        'Dry the preparation with air for visual inspection, then use the probe for tactile verification &mdash; both are needed',
        'If you find a deficiency during this check, fix it now &mdash; it is better to spend 30 seconds correcting an issue than to lose marks',
        'Before presenting, take one final look from each view: occlusal, buccal, lingual, proximal, and cross-section',
        'Clean out any debris or pencil residue &mdash; a clean, well-defined preparation makes a better impression on the examiner',
      ],
      criteria: [
        { text: 'Transverse ridge intact (not broken)', critical: true },
        { text: 'Occlusal width not exceeding 1/3 intercuspal distance', critical: true },
        { text: 'Proximal contact included in preparation', critical: true },
        { text: 'Extended into dentine; no excessive tissue loss', critical: true },
        { text: 'No beveling &mdash; butt-joint margins for composite', critical: true },
        { text: 'Convenience form allows access and material placement', critical: true },
        { text: 'Enamel margins not grossly undermined', critical: true },
        { text: 'Walls and margins smooth and cavity well defined', critical: true },
        { text: 'Adjacent tooth undamaged', critical: true },
        { text: 'Rubber dam intact and properly placed', critical: false },
        { text: 'All internal line angles rounded', critical: false },
        { text: 'Gingival seat flat and well-defined', critical: false },
      ],
      commonMistakes: [
        'Rushing through the final check due to time pressure &mdash; missing a correctable deficiency',
        'Not using the probe for tactile inspection &mdash; relying only on visual assessment',
        'Forgetting to check the adjacent tooth after removing the protective matrix band',
        'Leaving debris or loose enamel fragments in the preparation',
        'Not verifying that the preparation is in dentine at both the pulpal floor and axial wall',
        'Overlooking a small area of undermined enamel at a margin corner',
        'Presenting the preparation without cleaning it with air/water first',
      ],
      view: 'occlusal',
    },
  ];

  // ----------------------------------------------------------
  // SVG DRAWING FUNCTIONS
  // ----------------------------------------------------------

  function svgEl(tag, attrs, children) {
    const ns = 'http://www.w3.org/2000/svg';
    const el = document.createElementNS(ns, tag);
    if (attrs) Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
    if (children) {
      if (typeof children === 'string') {
        el.textContent = children;
      } else if (Array.isArray(children)) {
        children.forEach((c) => { if (c) el.appendChild(c); });
      }
    }
    return el;
  }

  // Arrow markers for dimension lines
  function createDefs() {
    const defs = svgEl('defs');

    const markerStart = svgEl('marker', {
      id: 'arrow-start', markerWidth: '8', markerHeight: '8',
      refX: '2', refY: '4', orient: 'auto',
    });
    markerStart.appendChild(svgEl('path', { d: 'M8,0 L0,4 L8,8', fill: '#e74c3c', 'stroke-width': '0' }));

    const markerEnd = svgEl('marker', {
      id: 'arrow-end', markerWidth: '8', markerHeight: '8',
      refX: '6', refY: '4', orient: 'auto',
    });
    markerEnd.appendChild(svgEl('path', { d: 'M0,0 L8,4 L0,8', fill: '#e74c3c', 'stroke-width': '0' }));

    defs.appendChild(markerStart);
    defs.appendChild(markerEnd);
    return defs;
  }

  // Map new 16-step IDs to SVG overlay phases for existing views
  // (Full per-step overlays will be added in Phase 2)
  function getOcclusalPhase(stepId) {
    if (stepId <= 2) return 'pre';       // pre-procedure
    if (stepId === 3) return 'punch';     // initial access
    if (stepId <= 6) return 'outline';    // outline form
    if (stepId <= 10) return 'box';       // proximal box
    if (stepId <= 15) return 'refine';    // refinement
    return 'final';                       // final check
  }

  // ---- OCCLUSAL VIEW ----
  function drawOcclusalView(stepId) {
    const g = svgEl('g', { transform: 'translate(250,250)' });
    const phase = getOcclusalPhase(stepId);

    // Tooth outline (molar occlusal - rounded rectangular)
    g.appendChild(svgEl('ellipse', {
      cx: '0', cy: '0', rx: '120', ry: '100',
      class: 'tooth-outline',
    }));

    // Cusps suggestions
    g.appendChild(svgEl('ellipse', { cx: '-45', cy: '50', rx: '40', ry: '30', fill: 'none', stroke: '#c9b99a', 'stroke-width': '1', opacity: '0.5' }));
    g.appendChild(svgEl('ellipse', { cx: '45', cy: '50', rx: '40', ry: '30', fill: 'none', stroke: '#c9b99a', 'stroke-width': '1', opacity: '0.5' }));
    g.appendChild(svgEl('ellipse', { cx: '0', cy: '-45', rx: '55', ry: '35', fill: 'none', stroke: '#c9b99a', 'stroke-width': '1', opacity: '0.5' }));

    // Fissure pattern
    g.appendChild(svgEl('path', { d: 'M-70,5 Q-30,-5 0,0 Q30,5 70,0', class: 'fissure-line' }));
    g.appendChild(svgEl('path', { d: 'M50,0 Q60,-15 70,-30', class: 'fissure-line' }));
    g.appendChild(svgEl('path', { d: 'M-50,0 Q-60,-10 -70,-25', class: 'fissure-line' }));

    // Orientation labels
    g.appendChild(svgEl('text', { x: '0', y: '-130', 'text-anchor': 'middle', class: 'annotation-text', 'font-weight': 'bold' }, 'PALATAL'));
    g.appendChild(svgEl('text', { x: '0', y: '135', 'text-anchor': 'middle', class: 'annotation-text', 'font-weight': 'bold' }, 'BUCCAL'));
    g.appendChild(svgEl('text', { x: '-155', y: '5', 'text-anchor': 'middle', class: 'annotation-text', 'font-weight': 'bold' }, 'MESIAL'));
    g.appendChild(svgEl('text', { x: '155', y: '5', 'text-anchor': 'middle', class: 'annotation-text', 'font-weight': 'bold' }, 'DISTAL'));

    // Marginal ridges
    g.appendChild(svgEl('path', {
      d: 'M-85,-65 Q-110,0 -85,65',
      fill: 'none', stroke: '#b0a080', 'stroke-width': '3', opacity: '0.6',
    }));
    g.appendChild(svgEl('text', { x: '-130', y: '50', class: 'annotation-text', 'font-size': '9', opacity: '0.6' }, 'Mesial ridge'));

    g.appendChild(svgEl('path', {
      d: 'M85,-65 Q110,0 85,65',
      fill: 'none', stroke: '#b0a080', 'stroke-width': '3', opacity: '0.6',
    }));
    g.appendChild(svgEl('text', { x: '95', y: '50', class: 'annotation-text', 'font-size': '9', opacity: '0.6' }, 'Distal ridge'));

    // --- Step-specific overlays ---
    if (phase === 'pre' && stepId === 2) {
      // Pencil marking outline (dashed)
      g.appendChild(svgEl('path', {
        d: 'M-30,15 Q-15,-10 0,-5 Q15,-10 30,15 Q50,15 70,20 Q85,10 105,0 Q85,-10 70,-25 Q50,-15 25,-20 L-25,-20 Q-35,-15 -40,0 Q-35,10 -30,15 Z',
        fill: 'none', stroke: '#e67e22', 'stroke-width': '2', 'stroke-dasharray': '6 3', opacity: '0.8',
      }));
      g.appendChild(svgEl('text', { x: '-60', y: '-45', class: 'annotation-text', fill: '#e67e22', 'font-size': '10' }, 'Pencil outline'));
    }

    if (phase === 'punch') {
      // Punch cut dot
      g.appendChild(svgEl('circle', {
        cx: '30', cy: '0', r: '8',
        class: 'highlight-area',
      }));
      g.appendChild(svgEl('text', { x: '30', y: '-20', 'text-anchor': 'middle', class: 'dimension-text', 'font-size': '9' }, '2mm deep'));
    }

    if (phase === 'outline' || phase === 'box' || phase === 'refine' || phase === 'final') {
      // Occlusal preparation outline
      g.appendChild(svgEl('path', {
        d: 'M-30,15 Q-15,-10 0,-5 Q15,-10 30,15 Q35,10 40,0 Q35,-15 25,-20 L-25,-20 Q-35,-15 -40,0 Q-35,10 -30,15 Z',
        class: phase === 'outline' && stepId === 4 ? 'highlight-area' : 'prep-filled',
      }));

      // Isthmus width dimension (step 4)
      if (stepId === 4) {
        g.appendChild(svgEl('line', { x1: '-25', y1: '-35', x2: '25', y2: '-35', class: 'dimension-line' }));
        g.appendChild(svgEl('text', { x: '0', y: '-40', 'text-anchor': 'middle', class: 'dimension-text' }, 'Max 1/3 intercuspal (prefer bur width)'));
        g.appendChild(svgEl('rect', { x: '-5', y: '-5', width: '10', height: '3', fill: '#e74c3c', opacity: '0.6', rx: '1' }));
        g.appendChild(svgEl('text', { x: '20', y: '-1', class: 'dimension-text', 'font-size': '9' }, '2mm deep'));
      }
    }

    if (phase === 'outline' && stepId >= 5) {
      // Extension towards distal marginal ridge
      g.appendChild(svgEl('path', {
        d: 'M30,15 Q50,15 70,20 Q85,10 85,-10 Q70,-20 50,-15 Q35,-15 25,-20',
        class: stepId === 5 ? 'highlight-area' : 'prep-filled',
      }));

      if (stepId === 5) {
        g.appendChild(svgEl('line', { x1: '40', y1: '0', x2: '75', y2: '0', stroke: '#e74c3c', 'stroke-width': '2', 'marker-end': 'url(#arrow-end)' }));
        g.appendChild(svgEl('text', { x: '55', y: '-10', class: 'dimension-text', 'font-size': '9', 'text-anchor': 'middle' }, 'Just beyond contact'));
      }
    }

    if (phase === 'box' || phase === 'refine' || phase === 'final') {
      // Full proximal extension + box visible from occlusal
      g.appendChild(svgEl('path', {
        d: 'M30,15 Q50,15 70,20 Q85,10 85,-10 Q70,-20 50,-15 Q35,-15 25,-20',
        class: 'prep-filled',
      }));

      // Proximal box opening
      g.appendChild(svgEl('path', {
        d: 'M70,25 Q100,30 105,0 Q100,-30 70,-25',
        class: phase === 'box' && stepId === 10 ? 'highlight-area' : 'prep-filled',
      }));
    }

    // T-shape highlight (step 6)
    if (stepId === 6) {
      g.appendChild(svgEl('path', {
        d: 'M30,15 Q50,15 70,20 Q85,10 85,-10 Q70,-20 50,-15 Q35,-15 25,-20',
        class: 'highlight-area',
      }));
      g.appendChild(svgEl('path', {
        d: 'M70,25 Q100,30 105,0 Q100,-30 70,-25',
        class: 'highlight-area',
      }));
      g.appendChild(svgEl('text', { x: '-60', y: '-40', class: 'annotation-text', fill: '#e67e22', 'font-size': '10', 'font-weight': 'bold' }, 'T-shape / "step" form'));
    }

    if (phase === 'final') {
      // Green outline for final check
      g.appendChild(svgEl('path', {
        d: 'M-30,15 Q-15,-10 0,-5 Q15,-10 30,15 Q50,15 70,20 Q85,10 105,0 Q85,-10 70,-25 Q50,-15 25,-20 L-25,-20 Q-35,-15 -40,0 Q-35,10 -30,15 Z',
        fill: 'none', stroke: '#27ae60', 'stroke-width': '3',
      }));
      g.appendChild(svgEl('text', { x: '-60', y: '-40', class: 'annotation-text', fill: '#27ae60', 'font-size': '10', 'font-weight': 'bold' }, 'Smooth margins \u2713'));
    }

    return g;
  }

  // ---- PROXIMAL VIEW ----
  function drawProximalView(stepId) {
    const g = svgEl('g', { transform: 'translate(250,250)' });

    // Background gingiva
    g.appendChild(svgEl('path', {
      d: 'M-200,120 Q-100,95 0,100 Q100,95 200,120 L200,200 L-200,200 Z',
      class: 'gingiva-area',
    }));

    // Alveolar bone
    g.appendChild(svgEl('path', {
      d: 'M-200,150 Q-100,130 0,135 Q100,130 200,150 L200,200 L-200,200 Z',
      class: 'bone-area',
    }));

    // Adjacent tooth
    g.appendChild(svgEl('path', {
      d: 'M130,-120 Q150,-120 160,-100 L165,90 Q155,100 140,105 L130,105 L130,-120 Z',
      class: 'adjacent-tooth',
    }));
    g.appendChild(svgEl('text', { x: '148', y: '-5', class: 'annotation-text', 'font-size': '9', 'text-anchor': 'middle', opacity: '0.6' }, 'Adjacent'));
    g.appendChild(svgEl('text', { x: '148', y: '7', class: 'annotation-text', 'font-size': '9', 'text-anchor': 'middle', opacity: '0.6' }, 'tooth'));

    // Main tooth outer profile (enamel)
    g.appendChild(svgEl('path', {
      d: 'M-100,-120 Q-110,-120 -115,-100 L-120,80 Q-110,100 -80,105 Q-20,110 20,110 Q60,108 90,100 Q110,90 115,80 L110,-100 Q105,-120 95,-120 Q50,-135 -10,-140 Q-60,-135 -100,-120 Z',
      class: 'tooth-outline',
    }));

    // DEJ
    g.appendChild(svgEl('path', {
      d: 'M-80,-100 Q-85,-90 -88,60 Q-75,80 -50,85 Q0,90 40,88 Q65,82 80,70 L82,-90 Q78,-100 70,-105 Q30,-115 -10,-118 Q-50,-112 -80,-100 Z',
      fill: 'none', stroke: '#d4b85c', 'stroke-width': '1', 'stroke-dasharray': '4 2', opacity: '0.6',
    }));

    // Dentine region
    g.appendChild(svgEl('path', {
      d: 'M-80,-100 Q-85,-90 -88,60 Q-75,80 -50,85 Q0,90 40,88 Q65,82 80,70 L82,-90 Q78,-100 70,-105 Q30,-115 -10,-118 Q-50,-112 -80,-100 Z',
      fill: '#f0d890', stroke: 'none', opacity: '0.4',
    }));

    // Pulp chamber
    g.appendChild(svgEl('path', {
      d: 'M-30,-50 Q-35,-30 -35,10 Q-25,30 0,35 Q25,30 35,10 Q35,-30 30,-50 Q15,-60 0,-65 Q-15,-60 -30,-50 Z',
      class: 'pulp-area',
    }));
    g.appendChild(svgEl('text', { x: '0', y: '-10', class: 'annotation-text', 'text-anchor': 'middle', 'font-size': '10', fill: '#c0392b' }, 'Pulp'));

    // Orientation labels
    g.appendChild(svgEl('text', { x: '-140', y: '-50', class: 'annotation-text', 'font-weight': 'bold' }, 'BUCCAL'));
    g.appendChild(svgEl('text', { x: '115', y: '-50', class: 'annotation-text', 'font-weight': 'bold' }, 'DISTAL'));

    // --- Step-specific overlays ---
    if (stepId >= 7) {
      // Proximal box preparation
      const boxPath = 'M40,-120 L40,-40 Q42,-30 50,-25 L90,-25 Q100,-28 105,-35 L108,-120 Z';
      g.appendChild(svgEl('path', {
        d: boxPath,
        class: (stepId >= 7 && stepId <= 10) ? 'highlight-area' : 'prep-filled',
      }));

      // Axial wall
      g.appendChild(svgEl('line', {
        x1: '50', y1: '-25', x2: '50', y2: '55',
        stroke: (stepId >= 7 && stepId <= 10) ? '#e74c3c' : '#3498db',
        'stroke-width': (stepId >= 7 && stepId <= 10) ? '2.5' : '1.5',
      }));

      if (stepId === 7 || stepId === 8) {
        // Label axial wall
        g.appendChild(svgEl('rect', { x: '12', y: '10', width: '55', height: '16', class: 'label-bg' }));
        g.appendChild(svgEl('text', { x: '40', y: '22', class: 'annotation-text', 'text-anchor': 'middle', 'font-size': '10', fill: '#e74c3c' }, 'Axial wall'));

        // Gingival seat
        g.appendChild(svgEl('line', { x1: '50', y1: '55', x2: '100', y2: '55', stroke: '#e74c3c', 'stroke-width': '2.5' }));
        g.appendChild(svgEl('rect', { x: '55', y: '58', width: '75', height: '16', class: 'label-bg' }));
        g.appendChild(svgEl('text', { x: '92', y: '70', class: 'annotation-text', 'text-anchor': 'middle', 'font-size': '10', fill: '#e74c3c' }, 'Gingival seat'));

        // Depth dimension
        g.appendChild(svgEl('line', { x1: '50', y1: '75', x2: '80', y2: '75', class: 'dimension-line' }));
        g.appendChild(svgEl('text', { x: '65', y: '88', class: 'dimension-text', 'text-anchor': 'middle', 'font-size': '9' }, '~1.5mm'));
      }

      // Step 9: matrix band highlight
      if (stepId === 9) {
        g.appendChild(svgEl('rect', {
          x: '120', y: '-100', width: '5', height: '190',
          fill: 'rgba(52, 152, 219, 0.3)', stroke: '#3498db', 'stroke-width': '1',
        }));
        g.appendChild(svgEl('text', { x: '140', y: '30', class: 'annotation-text', 'font-size': '9', fill: '#3498db' }, 'Matrix'));
        g.appendChild(svgEl('text', { x: '140', y: '42', class: 'annotation-text', 'font-size': '9', fill: '#3498db' }, 'band'));
      }
    }

    // Step 5/6: proximal extension (before full box)
    if (stepId === 5 || stepId === 6) {
      g.appendChild(svgEl('path', {
        d: 'M60,-120 L60,-80 Q70,-75 90,-75 L108,-120 Z',
        class: 'highlight-area',
      }));
      if (stepId === 5) {
        g.appendChild(svgEl('text', { x: '85', y: '-85', class: 'dimension-text', 'font-size': '9' }, 'Just past'));
        g.appendChild(svgEl('text', { x: '85', y: '-75', class: 'dimension-text', 'font-size': '9' }, 'contact'));
      }
    }

    if (stepId === 13) {
      // Highlight gingival seat
      g.appendChild(svgEl('line', {
        x1: '50', y1: '55', x2: '100', y2: '55',
        stroke: '#f39c12', 'stroke-width': '4',
      }));
      g.appendChild(svgEl('path', {
        d: 'M50,40 Q50,55 60,55',
        fill: 'none', stroke: '#e74c3c', 'stroke-width': '3',
      }));
      g.appendChild(svgEl('rect', { x: '10', y: '35', width: '38', height: '16', class: 'label-bg' }));
      g.appendChild(svgEl('text', { x: '29', y: '46', class: 'dimension-text', 'text-anchor': 'middle', 'font-size': '8' }, 'Rounded'));
      g.appendChild(svgEl('rect', { x: '95', y: '48', width: '8', height: '8', fill: 'none', stroke: '#e74c3c', 'stroke-width': '1.5' }));
      g.appendChild(svgEl('text', { x: '115', y: '58', class: 'dimension-text', 'font-size': '9' }, '~90\u00B0'));
    }

    if (stepId === 12 || stepId === 15) {
      // Bird beak / S-curve indicators
      g.appendChild(svgEl('line', { x1: '50', y1: '-25', x2: '42', y2: '-100', stroke: '#3498db', 'stroke-width': '2' }));
      g.appendChild(svgEl('line', { x1: '100', y1: '-25', x2: '108', y2: '-100', stroke: '#3498db', 'stroke-width': '2' }));

      if (stepId === 12) {
        g.appendChild(svgEl('text', { x: '20', y: '-75', class: 'annotation-text', 'font-size': '9', fill: '#3498db' }, 'Bird'));
        g.appendChild(svgEl('text', { x: '20', y: '-65', class: 'annotation-text', 'font-size': '9', fill: '#3498db' }, 'beak'));
        g.appendChild(svgEl('text', { x: '112', y: '-75', class: 'annotation-text', 'font-size': '9', fill: '#3498db' }, 'Bird'));
        g.appendChild(svgEl('text', { x: '112', y: '-65', class: 'annotation-text', 'font-size': '9', fill: '#3498db' }, 'beak'));
      }
      if (stepId === 15) {
        g.appendChild(svgEl('text', { x: '20', y: '-75', class: 'annotation-text', 'font-size': '9', fill: '#e67e22' }, 'S-curve'));
        g.appendChild(svgEl('text', { x: '112', y: '-75', class: 'annotation-text', 'font-size': '9', fill: '#e67e22' }, 'Funnel'));
      }
    }

    if (stepId === 14) {
      // Internal line angles
      g.appendChild(svgEl('path', { d: 'M50,40 Q50,55 60,55', fill: 'none', stroke: '#e74c3c', 'stroke-width': '3' }));
      g.appendChild(svgEl('path', { d: 'M50,-25 Q42,-25 42,-15', fill: 'none', stroke: '#e74c3c', 'stroke-width': '3' }));
      g.appendChild(svgEl('path', { d: 'M48,-25 Q50,-20 50,-15', fill: 'none', stroke: '#e74c3c', 'stroke-width': '4' }));
      g.appendChild(svgEl('rect', { x: '5', y: '-50', width: '90', height: '16', class: 'label-bg' }));
      g.appendChild(svgEl('text', { x: '50', y: '-39', class: 'dimension-text', 'text-anchor': 'middle', 'font-size': '9' }, 'Axiopulpal (ROUND!)'));
      g.appendChild(svgEl('text', { x: '70', y: '0', class: 'annotation-text', 'font-size': '20', fill: '#27ae60', 'text-anchor': 'middle' }, '\u2713'));
      g.appendChild(svgEl('text', { x: '70', y: '15', class: 'annotation-text', 'font-size': '9', fill: '#27ae60', 'text-anchor': 'middle' }, 'No undercuts'));
    }

    return g;
  }

  // ---- BUCCAL VIEW ----
  function drawBuccalView(stepId) {
    const g = svgEl('g', { transform: 'translate(250,260)' });

    // Gingiva
    g.appendChild(svgEl('path', {
      d: 'M-200,80 Q-100,55 0,60 Q100,55 200,80 L200,200 L-200,200 Z',
      class: 'gingiva-area',
    }));

    // Adjacent tooth on left (mesial)
    g.appendChild(svgEl('path', {
      d: 'M-200,-160 Q-180,-175 -155,-170 Q-130,-160 -125,-140 L-120,55 Q-130,65 -150,68 L-200,75 Z',
      class: 'adjacent-tooth',
    }));

    // Main tooth outline from buccal
    g.appendChild(svgEl('path', {
      d: 'M-90,-140 Q-70,-165 -30,-170 Q10,-172 50,-165 Q80,-155 95,-135 L100,50 Q90,65 60,70 Q20,75 -20,75 Q-60,72 -85,65 L-95,50 Z',
      class: 'tooth-outline',
    }));

    // Cusps
    g.appendChild(svgEl('path', { d: 'M-90,-140 Q-60,-165 -30,-170 Q-30,-155 -10,-148', fill: 'none', stroke: '#c9b99a', 'stroke-width': '1' }));
    g.appendChild(svgEl('path', { d: 'M95,-135 Q70,-158 50,-165 Q50,-150 30,-145', fill: 'none', stroke: '#c9b99a', 'stroke-width': '1' }));
    g.appendChild(svgEl('circle', { cx: '-50', cy: '-155', r: '3', fill: '#c9b99a' }));
    g.appendChild(svgEl('circle', { cx: '60', cy: '-150', r: '3', fill: '#c9b99a' }));

    // Orientation
    g.appendChild(svgEl('text', { x: '-120', y: '-80', class: 'annotation-text', 'font-weight': 'bold' }, 'MESIAL'));
    g.appendChild(svgEl('text', { x: '108', y: '-80', class: 'annotation-text', 'font-weight': 'bold' }, 'DISTAL'));
    g.appendChild(svgEl('text', { x: '0', y: '-195', 'text-anchor': 'middle', class: 'annotation-text', 'font-weight': 'bold' }, 'OCCLUSAL'));

    // Contact point
    g.appendChild(svgEl('ellipse', {
      cx: '-105', cy: '-60', rx: '12', ry: '20',
      fill: 'rgba(255,200,50,0.2)', stroke: '#c0820a', 'stroke-width': '1', 'stroke-dasharray': '3 2',
    }));
    g.appendChild(svgEl('text', { x: '-105', y: '-90', class: 'annotation-text', 'font-size': '8', 'text-anchor': 'middle', fill: '#c0820a' }, 'Contact'));

    // --- Step-specific overlays ---
    if (stepId >= 3) {
      // Occlusal prep visible from buccal
      g.appendChild(svgEl('path', {
        d: 'M-20,-148 Q0,-140 20,-143 Q25,-148 20,-153 Q0,-145 -20,-148 Z',
        fill: 'rgba(100,180,255,0.4)', stroke: '#3498db', 'stroke-width': '1.5',
      }));
    }

    if (stepId >= 5) {
      // Proximal box visible from buccal
      g.appendChild(svgEl('path', {
        d: 'M20,-143 Q40,-145 60,-140 Q70,-130 75,-100 Q75,-50 72,0 Q70,20 65,35 Q55,40 45,35 Q40,20 42,-20 Q45,-80 45,-120 Q40,-138 20,-143 Z',
        class: stepId <= 10 ? 'highlight-area' : 'prep-filled',
      }));
    }

    if (stepId === 16) {
      // Final outline
      g.appendChild(svgEl('path', {
        d: 'M-20,-148 Q0,-140 20,-143 Q40,-145 60,-140 Q70,-130 75,-100 Q75,-50 72,0 Q70,20 65,35 Q55,40 45,35 Q40,20 42,-20 Q45,-80 45,-120 Q40,-138 20,-143 Q0,-145 -20,-148 Z',
        fill: 'none', stroke: '#27ae60', 'stroke-width': '3',
      }));
      g.appendChild(svgEl('text', { x: '85', y: '-70', class: 'annotation-text', 'font-size': '9', fill: '#27ae60', 'font-weight': 'bold' }, '90\u00B0 butt'));
      g.appendChild(svgEl('text', { x: '85', y: '-58', class: 'annotation-text', 'font-size': '9', fill: '#27ae60', 'font-weight': 'bold' }, 'joint'));
      g.appendChild(svgEl('line', { x1: '84', y1: '-50', x2: '76', y2: '-40', stroke: '#27ae60', 'stroke-width': '1.5', 'marker-end': 'url(#arrow-end)' }));
    }

    return g;
  }

  // ---- CROSS-SECTION VIEW (placeholder for Phase 2) ----
  function drawCrossSectionView(stepId) {
    const g = svgEl('g', { transform: 'translate(250,250)' });

    // Outer enamel shell (cross-section)
    g.appendChild(svgEl('path', {
      d: 'M-120,-100 Q-130,-80 -130,20 Q-120,80 -80,100 Q-20,115 20,115 Q80,100 120,80 Q130,20 130,-80 Q120,-100 80,-110 Q20,-120 -20,-120 Q-80,-110 -120,-100 Z',
      class: 'tooth-outline',
    }));

    // DEJ line
    g.appendChild(svgEl('path', {
      d: 'M-90,-75 Q-100,-60 -100,10 Q-90,60 -55,78 Q-10,90 20,90 Q55,78 90,60 Q100,10 100,-60 Q90,-75 55,-85 Q20,-92 -10,-92 Q-55,-85 -90,-75 Z',
      fill: '#f0d890', stroke: '#d4b85c', 'stroke-width': '1', 'stroke-dasharray': '4 2', opacity: '0.6',
    }));

    // Pulp
    g.appendChild(svgEl('path', {
      d: 'M-30,-25 Q-35,-10 -35,15 Q-25,35 0,40 Q25,35 35,15 Q35,-10 30,-25 Q15,-35 0,-38 Q-15,-35 -30,-25 Z',
      class: 'pulp-area',
    }));
    g.appendChild(svgEl('text', { x: '0', y: '5', class: 'annotation-text', 'text-anchor': 'middle', 'font-size': '10', fill: '#c0392b' }, 'Pulp'));

    // Labels
    g.appendChild(svgEl('text', { x: '-150', y: '0', class: 'annotation-text', 'font-weight': 'bold' }, 'BUCCAL'));
    g.appendChild(svgEl('text', { x: '135', y: '0', class: 'annotation-text', 'font-weight': 'bold' }, 'LINGUAL'));
    g.appendChild(svgEl('text', { x: '0', y: '-135', 'text-anchor': 'middle', class: 'annotation-text', 'font-weight': 'bold' }, 'CROSS-SECTION'));

    // Prep cavity in cross-section
    if (stepId >= 3) {
      g.appendChild(svgEl('path', {
        d: 'M-20,-110 L-20,-65 Q-15,-55 0,-55 Q15,-55 20,-65 L20,-110 Z',
        class: 'prep-filled',
      }));

      // Depth measurement
      g.appendChild(svgEl('line', { x1: '30', y1: '-110', x2: '30', y2: '-65', class: 'dimension-line' }));
      g.appendChild(svgEl('text', { x: '45', y: '-85', class: 'dimension-text', 'font-size': '9' }, '2mm'));

      // Width measurement
      if (stepId === 11 || stepId === 14) {
        g.appendChild(svgEl('line', { x1: '-20', y1: '-50', x2: '20', y2: '-50', class: 'dimension-line' }));
        g.appendChild(svgEl('text', { x: '0', y: '-38', 'text-anchor': 'middle', class: 'dimension-text', 'font-size': '9' }, 'Max 1/3 intercuspal'));

        // Floor flatness indicator
        g.appendChild(svgEl('line', { x1: '-18', y1: '-65', x2: '18', y2: '-65', stroke: '#27ae60', 'stroke-width': '2' }));
        g.appendChild(svgEl('text', { x: '0', y: '-70', 'text-anchor': 'middle', class: 'annotation-text', 'font-size': '9', fill: '#27ae60' }, 'Flat floor'));
      }
    }

    return g;
  }

  // ----------------------------------------------------------
  // STATE & RENDERING
  // ----------------------------------------------------------
  let currentStep = 0;
  let currentView = 'occlusal';

  const svg = document.getElementById('tooth-svg');
  const stepList = document.getElementById('step-list');
  const stepNumber = document.getElementById('step-number');
  const stepTitle = document.getElementById('step-title');
  const stepDescription = document.getElementById('step-description');
  const instrumentList = document.getElementById('instrument-list');
  const tipsList = document.getElementById('tips-list');
  const criteriaList = document.getElementById('criteria-list');
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const progressFill = document.getElementById('progress-fill');
  const legend = document.getElementById('legend');

  function populateStepNav() {
    stepList.innerHTML = '';
    let lastPhase = '';
    STEPS.forEach((step, i) => {
      // Phase separator
      if (step.phase !== lastPhase) {
        const phaseEl = document.createElement('li');
        phaseEl.className = 'phase-header';
        phaseEl.textContent = step.phase;
        stepList.appendChild(phaseEl);
        lastPhase = step.phase;
      }

      const li = document.createElement('li');
      li.dataset.index = i;
      li.innerHTML = `<span class="step-indicator">${step.id}</span><span class="step-nav-title">${step.title}</span><span class="step-duration">${step.duration}</span>`;
      li.addEventListener('click', () => goToStep(i));
      stepList.appendChild(li);
    });
  }

  function updateLegend() {
    legend.innerHTML = '';
    const items = [
      { color: '#f5f0e8', border: '#c9b99a', label: 'Enamel' },
      { color: '#f0d890', border: '#d4b85c', label: 'Dentine' },
      { color: '#ff8a80', border: '#e74c3c', label: 'Pulp' },
      { color: 'rgba(100,180,255,0.35)', border: '#3498db', label: 'Preparation' },
      { color: 'rgba(255,200,50,0.3)', border: '#f39c12', label: 'Current step highlight' },
      { color: '#e8a0a0', border: '#c08080', label: 'Gingiva' },
    ];
    items.forEach((item) => {
      const div = document.createElement('div');
      div.className = 'legend-item';
      div.innerHTML = `<span class="legend-swatch" style="background:${item.color};border-color:${item.border}"></span>${item.label}`;
      legend.appendChild(div);
    });
  }

  function renderSVG() {
    svg.innerHTML = '';
    svg.appendChild(createDefs());

    const stepId = STEPS[currentStep].id;

    let drawing;
    switch (currentView) {
      case 'occlusal':
        drawing = drawOcclusalView(stepId);
        break;
      case 'proximal':
        drawing = drawProximalView(stepId);
        break;
      case 'buccal':
        drawing = drawBuccalView(stepId);
        break;
      case 'cross-section':
        drawing = drawCrossSectionView(stepId);
        break;
    }

    if (drawing) {
      drawing.classList.add('fade-in');
      svg.appendChild(drawing);
    }
  }

  function updateStepDetails() {
    const step = STEPS[currentStep];

    stepNumber.textContent = step.id;
    stepTitle.textContent = step.title;
    stepDescription.innerHTML = step.description;

    // Update phase and duration display
    const phaseEl = document.getElementById('step-phase');
    if (phaseEl) phaseEl.textContent = step.phase;
    const durationEl = document.getElementById('step-duration-display');
    if (durationEl) durationEl.textContent = step.duration;

    instrumentList.innerHTML = '';
    step.instruments.forEach((inst) => {
      const li = document.createElement('li');
      li.innerHTML = inst;
      instrumentList.appendChild(li);
    });

    tipsList.innerHTML = '';
    step.tips.forEach((tip) => {
      const li = document.createElement('li');
      li.innerHTML = tip;
      tipsList.appendChild(li);
    });

    criteriaList.innerHTML = '';
    step.criteria.forEach((c) => {
      const li = document.createElement('li');
      if (c.critical) li.classList.add('criteria-critical');
      li.innerHTML = c.critical ? `<strong>${c.text}</strong> <span class="critical-badge">IDC Critical</span>` : c.text;
      criteriaList.appendChild(li);
    });

    // Common mistakes
    const mistakesList = document.getElementById('mistakes-list');
    if (mistakesList) {
      mistakesList.innerHTML = '';
      step.commonMistakes.forEach((m) => {
        const li = document.createElement('li');
        li.innerHTML = m;
        mistakesList.appendChild(li);
      });
    }
  }

  function updateNavState() {
    const items = stepList.querySelectorAll('li:not(.phase-header)');
    items.forEach((li, i) => {
      li.classList.remove('active', 'completed');
      if (i === currentStep) li.classList.add('active');
      if (i < currentStep) li.classList.add('completed');
    });

    prevBtn.disabled = currentStep === 0;
    nextBtn.disabled = currentStep === STEPS.length - 1;
    nextBtn.textContent = currentStep === STEPS.length - 1 ? 'Complete' : 'Next \u2192';

    const pct = ((currentStep + 1) / STEPS.length) * 100;
    progressFill.style.width = pct + '%';
  }

  function goToStep(index) {
    if (index < 0 || index >= STEPS.length) return;
    currentStep = index;

    // Switch to the recommended view for this step
    const recommendedView = STEPS[currentStep].view;
    if (recommendedView) {
      currentView = recommendedView;
      document.querySelectorAll('.view-tab').forEach((tab) => {
        tab.classList.toggle('active', tab.dataset.view === currentView);
      });
    }

    renderSVG();
    updateStepDetails();
    updateNavState();
  }

  // ----------------------------------------------------------
  // EVENT LISTENERS
  // ----------------------------------------------------------
  prevBtn.addEventListener('click', () => goToStep(currentStep - 1));
  nextBtn.addEventListener('click', () => goToStep(currentStep + 1));

  document.querySelectorAll('.view-tab').forEach((tab) => {
    tab.addEventListener('click', () => {
      currentView = tab.dataset.view;
      document.querySelectorAll('.view-tab').forEach((t) => t.classList.remove('active'));
      tab.classList.add('active');
      renderSVG();
    });
  });

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      e.preventDefault();
      goToStep(currentStep + 1);
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      e.preventDefault();
      goToStep(currentStep - 1);
    }
  });

  // ----------------------------------------------------------
  // INIT
  // ----------------------------------------------------------
  populateStepNav();
  updateLegend();
  goToStep(0);
})();
