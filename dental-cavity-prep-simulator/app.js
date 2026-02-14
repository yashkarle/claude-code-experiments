// ============================================================
// DO Class 2 Cavity Prep Simulator
// Interactive step-by-step dental preparation guide
// ============================================================

(function () {
  'use strict';

  // ----------------------------------------------------------
  // STEP DATA
  // ----------------------------------------------------------
  const STEPS = [
    {
      id: 1,
      title: 'Assessment & Caries Identification',
      description: `
        <p>Begin by examining the tooth clinically and radiographically. Identify the extent of the carious lesion on the distal surface extending onto the occlusal surface.</p>
        <p>For the bench test, the examiner will indicate which tooth to prepare and the surfaces involved (Distal-Occlusal). Ensure you understand the extent of preparation required before starting.</p>
        <p><strong>Key assessment points:</strong> Check the adjacent tooth contact, identify the marginal ridge, note the position of the pulp chamber on the radiograph, and plan your access.</p>
      `,
      instruments: [
        'Mouth mirror & explorer',
        'Periapical radiograph',
        'Periodontal probe (for measuring)',
      ],
      tips: [
        'In the bench test, you are working on a typodont/phantom head &mdash; familiarise yourself with the specific setup beforehand',
        'Plan your preparation mentally before picking up the handpiece',
        'Note the position of adjacent teeth to avoid damage',
        'Identify the deepest part of the fissure system for your initial access point',
      ],
      criteria: [
        'Demonstrates systematic assessment approach',
        'Identifies correct tooth and surfaces',
      ],
      view: 'occlusal',
    },
    {
      id: 2,
      title: 'Occlusal Access & Outline Form',
      description: `
        <p>Create the initial occlusal outline form by entering the tooth through the central fossa or the distal pit using a pear-shaped bur (330/329) at high speed with water spray.</p>
        <p>The outline should follow the fissure pattern, extending only as far as the caries or defective tooth structure requires. For composite, the outline is <strong>more conservative</strong> than for amalgam &mdash; only extend to include the carious/defective areas.</p>
        <p><strong>Isthmus width:</strong> The narrowest part of the occlusal preparation (where it joins the proximal box) should be approximately 1/4 to 1/3 of the intercuspal distance. Too narrow restricts access; too wide weakens the remaining cusps.</p>
        <p><strong>Depth:</strong> The pulpal floor should be approximately 1.5&ndash;2mm from the cavosurface margin, ideally just into dentine (past the DEJ).</p>
      `,
      instruments: [
        'High-speed handpiece with water spray',
        'Pear-shaped bur (330 or 329)',
        'Round bur (size 2 or 4) for initial penetration if preferred',
      ],
      tips: [
        'Enter through the central fossa at a slight angle towards the distal',
        'Keep the bur perpendicular to the occlusal surface for correct depth',
        'Use the periodontal probe to check depth frequently (1.5&ndash;2mm)',
        'Do NOT extend to the distal marginal ridge yet &mdash; establish occlusal form first',
        'The pulpal floor should be flat and uniform in depth',
      ],
      criteria: [
        'Correct outline following fissure anatomy',
        'Appropriate isthmus width (1/4&ndash;1/3 intercuspal)',
        'Pulpal floor at correct depth (1.5&ndash;2mm)',
        'Pulpal floor is flat and smooth',
        'No over-extension beyond carious involvement',
      ],
      view: 'occlusal',
    },
    {
      id: 3,
      title: 'Breaking the Marginal Ridge',
      description: `
        <p>This is one of the most critical steps. Extend the preparation distally to break through the marginal ridge, connecting the occlusal preparation to what will become the proximal box.</p>
        <p>Use the pear-shaped bur and extend towards the distal, but <strong>do not break through the marginal ridge from the occlusal</strong> in one aggressive cut. Instead:</p>
        <p>1. Extend the occlusal prep towards the marginal ridge<br>
        2. Thin the marginal ridge gradually from the occlusal side<br>
        3. The ridge will eventually fracture away cleanly, or you can carefully cut through it</p>
        <p><strong>Critical:</strong> The isthmus (junction between occlusal and proximal portions) should be at the height of the marginal ridge. The buccal and lingual walls should create a smooth, flowing transition from the occlusal prep into the proximal box.</p>
      `,
      instruments: [
        'Pear-shaped bur (330/329)',
        'Tapered fissure bur (169L) for refinement',
      ],
      tips: [
        'This step determines the shape of your entire proximal box &mdash; take care',
        'The marginal ridge should be thinned from the INSIDE, not attacked from the side',
        'Protect the adjacent tooth with a matrix band if needed',
        'The transition from occlusal to proximal should be smooth with no ledges',
        'In the bench test, work carefully &mdash; a damaged adjacent tooth loses marks',
      ],
      criteria: [
        'Clean break-through of marginal ridge',
        'Smooth transition from occlusal to proximal',
        'No damage to adjacent tooth',
        'Isthmus at correct width and position',
      ],
      view: 'occlusal',
    },
    {
      id: 4,
      title: 'Proximal Box Preparation',
      description: `
        <p>Establish the proximal box form. This is the rectangular (box-shaped) extension of the preparation on the distal surface of the tooth. The box has four walls and a floor:</p>
        <p><strong>Buccal wall</strong> &mdash; slightly diverges towards the buccal surface<br>
        <strong>Lingual/Palatal wall</strong> &mdash; slightly diverges towards the lingual surface<br>
        <strong>Gingival wall (floor/seat)</strong> &mdash; flat horizontal floor at the base of the box<br>
        <strong>Axial wall</strong> &mdash; the internal wall facing the pulp, following the curvature of the DEJ</p>
        <p>For composite, the buccal and lingual walls should diverge slightly outward (not converge as for amalgam). This allows for bonding access and light curing.</p>
        <p><strong>Clearance:</strong> The buccal and lingual walls must clear the adjacent tooth contact by approximately 0.5&ndash;1mm to allow matrix band placement and adequate access for finishing.</p>
      `,
      instruments: [
        'Tapered fissure bur (169L / 170)',
        'Pear-shaped bur (330) for initial shaping',
        'Gingival margin trimmer',
        'Enamel hatchet',
      ],
      tips: [
        'Use light, controlled strokes &mdash; do not force the bur',
        'Check clearance from the adjacent tooth with an explorer',
        'The axial wall should be slightly curved (convex towards the pulp), following the DEJ',
        'The gingival seat should be 1&ndash;1.5mm above the free gingival margin (in a real patient) or at the specified depth for the bench test',
        'Avoid making the box too deep &mdash; the axial wall should be just into dentine (~0.5mm past DEJ)',
      ],
      criteria: [
        'Four well-defined walls and gingival seat',
        'Adequate clearance from adjacent tooth',
        'Walls diverge slightly toward the outer surface',
        'Axial wall at correct depth following DEJ curvature',
        'No unsupported enamel',
      ],
      view: 'proximal',
    },
    {
      id: 5,
      title: 'Gingival Seat Refinement',
      description: `
        <p>The gingival seat (floor of the proximal box) requires careful attention. It should be:</p>
        <p><strong>Flat</strong> &mdash; perpendicular to the long axis of the tooth<br>
        <strong>Smooth</strong> &mdash; no irregularities that could cause microleakage<br>
        <strong>At the correct depth</strong> &mdash; just at or slightly below the contact area with the adjacent tooth</p>
        <p>The gingival seat meets the axial wall at the <strong>axio-gingival line angle</strong>, which should be gently rounded (not sharp) to reduce stress concentration.</p>
        <p><strong>Width:</strong> The gingival seat should be approximately 1mm bucco-lingually &mdash; just enough to clear the adjacent tooth contact on both sides.</p>
        <p><strong>For composite:</strong> The cavosurface angle at the gingival margin should be approximately 90 degrees (butt joint). Do NOT place a bevel here &mdash; bevelling the gingival margin leads to thin composite that is vulnerable to fracture.</p>
      `,
      instruments: [
        'Gingival margin trimmer (pair: left &amp; right)',
        'Tapered fissure bur (fine)',
        'Spoon excavator (for any remaining soft dentine)',
      ],
      tips: [
        'Use gingival margin trimmers to achieve a clean, flat seat',
        'Check with an explorer that there are no ledges or overhangs',
        'The gingival seat is one of the most commonly criticised areas in the exam',
        'Ensure no enamel is left unsupported at the gingival margin',
        'A common mistake is making the gingival seat too deep &mdash; this risks damaging the periodontium',
      ],
      criteria: [
        'Flat, smooth gingival seat',
        'Correct depth and width',
        'Rounded axio-gingival line angle',
        '90-degree cavosurface at gingival margin',
        'No unsupported enamel',
      ],
      view: 'proximal',
    },
    {
      id: 6,
      title: 'Internal Form & Line Angles',
      description: `
        <p>Refine the internal anatomy of the preparation. For composite restorations, the internal form differs from amalgam preparations:</p>
        <p><strong>No retention form needed:</strong> Composite bonds to tooth structure via adhesive, so mechanical undercuts are unnecessary and actually undesirable (they remove excess tooth structure).</p>
        <p><strong>Rounded internal line angles:</strong> All internal line angles (where two walls meet) should be gently rounded using a round bur. This:</p>
        <ul style="margin-left:1.5rem; margin-bottom:0.5rem;">
          <li>Reduces stress concentration in the tooth</li>
          <li>Allows better adaptation of the composite</li>
          <li>Improves light curing penetration to all areas</li>
        </ul>
        <p><strong>Axiopulpal line angle:</strong> Where the axial wall meets the pulpal floor, this angle must be rounded. A sharp axiopulpal line angle is a stress riser that can lead to tooth fracture.</p>
        <p><strong>Flat pulpal floor:</strong> Confirm the pulpal floor is flat and at the correct depth. Use the round bur to smooth any irregularities.</p>
      `,
      instruments: [
        'Round bur (size 2 or 4) in slow handpiece',
        'Spoon excavator',
        'Periodontal probe (depth checking)',
      ],
      tips: [
        'Use a slow-speed round bur with light pressure to round angles',
        'Pay special attention to the axiopulpal line angle &mdash; examiners check this specifically',
        'Do NOT place any undercuts &mdash; this is a composite prep, not amalgam',
        'Verify all depths with a periodontal probe after rounding',
        'The preparation should feel smooth when you run an explorer along all internal surfaces',
      ],
      criteria: [
        'All internal line angles rounded',
        'Axiopulpal line angle specifically rounded',
        'No mechanical retention features',
        'Pulpal floor flat and at correct depth',
        'Smooth internal surfaces',
      ],
      view: 'proximal',
    },
    {
      id: 7,
      title: 'Cavosurface Margins & Finishing',
      description: `
        <p>The final step is to ensure all cavosurface margins are clean, smooth, and at the correct angle.</p>
        <p><strong>For composite (critical difference from amalgam):</strong></p>
        <p><strong>Proximal box margins:</strong> The cavosurface angle should be approximately 90 degrees (butt joint). No bevel is placed on the proximal box walls or gingival seat. A bevel here would create thin, unsupported composite that fractures easily.</p>
        <p><strong>Occlusal margins:</strong> A short enamel bevel (0.5&ndash;1mm at 45 degrees) MAY be placed on the occlusal cavosurface margin only. This increases the bonding surface area and improves the marginal seal. However, some protocols omit this &mdash; follow your examiner's preference.</p>
        <p><strong>Margin quality:</strong> All margins should be smooth, continuous, and free of loose enamel rods. Use hand instruments (enamel hatchet, GMT) to plane any rough areas. Run an explorer along every margin to check for defects.</p>
        <p><strong>Final check:</strong> Remove all debris with air/water spray. Inspect the entire preparation under good light and magnification.</p>
      `,
      instruments: [
        'Enamel hatchet',
        'Gingival margin trimmer',
        'Fine diamond bur (for occlusal bevel if required)',
        'Explorer (for margin checking)',
        'Three-in-one syringe (air/water)',
      ],
      tips: [
        'Run your explorer along EVERY margin &mdash; it should glide smoothly without catching',
        'Do NOT bevel the proximal box &mdash; this is the most common composite mistake in exams',
        'Check for any unsupported enamel, especially at the gingival margin',
        'Remove any loose debris before final inspection',
        'If in doubt about a margin, refine it with a hand instrument rather than a bur (more control)',
        'Take one final look at the preparation from multiple angles before declaring it complete',
      ],
      criteria: [
        'Smooth, continuous cavosurface margins throughout',
        '~90&deg; cavosurface on proximal box (butt joint)',
        'No bevel on proximal margins',
        'Occlusal bevel appropriate (if required by examiner)',
        'No unsupported enamel anywhere',
        'No ledges, steps, or defects',
        'Preparation clean and free of debris',
      ],
      view: 'buccal',
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

  // ---- OCCLUSAL VIEW ----
  function drawOcclusalView(stepId) {
    const g = svgEl('g', { transform: 'translate(250,250)' });

    // Tooth outline (premolar occlusal - rounded rectangular)
    g.appendChild(svgEl('ellipse', {
      cx: '0', cy: '0', rx: '120', ry: '100',
      class: 'tooth-outline',
    }));

    // Cusps suggestions
    // Buccal cusps
    g.appendChild(svgEl('ellipse', { cx: '-45', cy: '50', rx: '40', ry: '30', fill: 'none', stroke: '#c9b99a', 'stroke-width': '1', opacity: '0.5' }));
    g.appendChild(svgEl('ellipse', { cx: '45', cy: '50', rx: '40', ry: '30', fill: 'none', stroke: '#c9b99a', 'stroke-width': '1', opacity: '0.5' }));
    // Palatal cusp
    g.appendChild(svgEl('ellipse', { cx: '0', cy: '-45', rx: '55', ry: '35', fill: 'none', stroke: '#c9b99a', 'stroke-width': '1', opacity: '0.5' }));

    // Fissure pattern (central fossa)
    g.appendChild(svgEl('path', {
      d: 'M-70,5 Q-30,-5 0,0 Q30,5 70,0',
      class: 'fissure-line',
    }));
    // Distal fissure
    g.appendChild(svgEl('path', {
      d: 'M50,0 Q60,-15 70,-30',
      class: 'fissure-line',
    }));
    // Mesial fissure
    g.appendChild(svgEl('path', {
      d: 'M-50,0 Q-60,-10 -70,-25',
      class: 'fissure-line',
    }));

    // Labels for orientation
    g.appendChild(svgEl('text', { x: '0', y: '-130', 'text-anchor': 'middle', class: 'annotation-text', 'font-weight': 'bold' }, 'PALATAL'));
    g.appendChild(svgEl('text', { x: '0', y: '135', 'text-anchor': 'middle', class: 'annotation-text', 'font-weight': 'bold' }, 'BUCCAL'));
    g.appendChild(svgEl('text', { x: '-155', y: '5', 'text-anchor': 'middle', class: 'annotation-text', 'font-weight': 'bold' }, 'MESIAL'));
    g.appendChild(svgEl('text', { x: '155', y: '5', 'text-anchor': 'middle', class: 'annotation-text', 'font-weight': 'bold' }, 'DISTAL'));

    // Marginal ridges
    g.appendChild(svgEl('path', {
      d: 'M-85,-65 Q-110,0 -85,65',
      fill: 'none', stroke: '#b0a080', 'stroke-width': '3', opacity: '0.6',
    }));
    // Label
    g.appendChild(svgEl('text', { x: '-130', y: '50', class: 'annotation-text', 'font-size': '9', opacity: '0.6' }, 'Mesial ridge'));

    g.appendChild(svgEl('path', {
      d: 'M85,-65 Q110,0 85,65',
      fill: 'none', stroke: '#b0a080', 'stroke-width': '3', opacity: '0.6',
    }));
    g.appendChild(svgEl('text', { x: '95', y: '50', class: 'annotation-text', 'font-size': '9', opacity: '0.6' }, 'Distal ridge'));

    // --- Step-specific overlays ---
    if (stepId >= 2) {
      // Occlusal preparation outline
      g.appendChild(svgEl('path', {
        d: 'M-30,15 Q-15,-10 0,-5 Q15,-10 30,15 Q35,10 40,0 Q35,-15 25,-20 L-25,-20 Q-35,-15 -40,0 Q-35,10 -30,15 Z',
        class: stepId === 2 ? 'highlight-area' : 'prep-filled',
      }));

      // Isthmus width dimension
      if (stepId === 2) {
        g.appendChild(svgEl('line', { x1: '-25', y1: '-35', x2: '25', y2: '-35', class: 'dimension-line' }));
        g.appendChild(svgEl('text', { x: '0', y: '-40', 'text-anchor': 'middle', class: 'dimension-text' }, '1/4\u20131/3 intercuspal'));

        // Depth indicator
        g.appendChild(svgEl('rect', { x: '-5', y: '-5', width: '10', height: '3', fill: '#e74c3c', opacity: '0.6', rx: '1' }));
        const depthLabel = svgEl('text', { x: '20', y: '-1', class: 'dimension-text', 'font-size': '9' }, '1.5\u20132mm deep');
        g.appendChild(depthLabel);
      }
    }

    if (stepId >= 3) {
      // Extension towards distal marginal ridge and break-through
      g.appendChild(svgEl('path', {
        d: 'M30,15 Q50,15 70,20 Q85,10 85,-10 Q70,-20 50,-15 Q35,-15 25,-20',
        class: stepId === 3 ? 'highlight-area' : 'prep-filled',
      }));

      if (stepId === 3) {
        // Arrow showing direction of approach
        g.appendChild(svgEl('line', { x1: '40', y1: '0', x2: '75', y2: '0', stroke: '#e74c3c', 'stroke-width': '2', 'marker-end': 'url(#arrow-end)' }));
        g.appendChild(svgEl('text', { x: '55', y: '-10', class: 'dimension-text', 'font-size': '9', 'text-anchor': 'middle' }, 'Extend distally'));

        // Marginal ridge being broken
        g.appendChild(svgEl('path', {
          d: 'M85,-30 Q95,0 85,30',
          fill: 'none', stroke: '#e74c3c', 'stroke-width': '2', 'stroke-dasharray': '4 4',
        }));
        g.appendChild(svgEl('text', { x: '105', y: '20', class: 'dimension-text', 'font-size': '9' }, 'Ridge\nremoved'));
      }
    }

    if (stepId >= 4) {
      // Proximal box visible from occlusal (flared opening)
      g.appendChild(svgEl('path', {
        d: 'M70,25 Q100,30 105,0 Q100,-30 70,-25',
        class: stepId === 4 ? 'highlight-area' : 'prep-filled',
      }));

      if (stepId === 4) {
        // Show divergence arrows
        g.appendChild(svgEl('line', { x1: '80', y1: '15', x2: '95', y2: '25', stroke: '#3498db', 'stroke-width': '1.5', 'marker-end': 'url(#arrow-end)' }));
        g.appendChild(svgEl('line', { x1: '80', y1: '-15', x2: '95', y2: '-25', stroke: '#3498db', 'stroke-width': '1.5', 'marker-end': 'url(#arrow-end)' }));
        g.appendChild(svgEl('text', { x: '110', y: '-15', class: 'annotation-text', 'font-size': '9', fill: '#3498db' }, 'Walls'));
        g.appendChild(svgEl('text', { x: '110', y: '-5', class: 'annotation-text', 'font-size': '9', fill: '#3498db' }, 'diverge'));
      }
    }

    if (stepId === 7) {
      // Highlight margins
      g.appendChild(svgEl('path', {
        d: 'M-30,15 Q-15,-10 0,-5 Q15,-10 30,15 Q50,15 70,20 Q85,10 105,0 Q85,-10 70,-25 Q50,-15 25,-20 L-25,-20 Q-35,-15 -40,0 Q-35,10 -30,15 Z',
        fill: 'none', stroke: '#27ae60', 'stroke-width': '3',
      }));
      g.appendChild(svgEl('text', { x: '-60', y: '-40', class: 'annotation-text', fill: '#27ae60', 'font-size': '10', 'font-weight': 'bold' }, 'Smooth margins'));
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

    // Adjacent tooth (mesial of next tooth)
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

    // DEJ (Dentino-enamel junction) - inner line
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
    if (stepId >= 4) {
      // Proximal box preparation
      const boxPath = 'M40,-120 L40,-40 Q42,-30 50,-25 L90,-25 Q100,-28 105,-35 L108,-120 Z';

      g.appendChild(svgEl('path', {
        d: boxPath,
        class: stepId === 4 ? 'highlight-area' : 'prep-filled',
      }));

      // Axial wall
      g.appendChild(svgEl('line', {
        x1: '50', y1: '-25', x2: '50', y2: '55',
        stroke: stepId === 4 ? '#e74c3c' : '#3498db',
        'stroke-width': stepId === 4 ? '2.5' : '1.5',
      }));

      if (stepId === 4) {
        // Label axial wall
        g.appendChild(svgEl('rect', { x: '12', y: '10', width: '55', height: '16', class: 'label-bg' }));
        g.appendChild(svgEl('text', { x: '40', y: '22', class: 'annotation-text', 'text-anchor': 'middle', 'font-size': '10', fill: '#e74c3c' }, 'Axial wall'));

        // Gingival seat
        g.appendChild(svgEl('line', {
          x1: '50', y1: '55', x2: '100', y2: '55',
          stroke: '#e74c3c', 'stroke-width': '2.5',
        }));
        g.appendChild(svgEl('rect', { x: '55', y: '58', width: '75', height: '16', class: 'label-bg' }));
        g.appendChild(svgEl('text', { x: '92', y: '70', class: 'annotation-text', 'text-anchor': 'middle', 'font-size': '10', fill: '#e74c3c' }, 'Gingival seat'));

        // Buccal and lingual walls
        g.appendChild(svgEl('line', { x1: '50', y1: '-25', x2: '42', y2: '-100', stroke: '#3498db', 'stroke-width': '2' }));
        g.appendChild(svgEl('line', { x1: '100', y1: '-25', x2: '108', y2: '-100', stroke: '#3498db', 'stroke-width': '2' }));

        // Divergence arrows
        g.appendChild(svgEl('text', { x: '20', y: '-75', class: 'annotation-text', 'font-size': '9', fill: '#3498db' }, 'Buccal'));
        g.appendChild(svgEl('text', { x: '20', y: '-65', class: 'annotation-text', 'font-size': '9', fill: '#3498db' }, 'wall'));
        g.appendChild(svgEl('text', { x: '112', y: '-75', class: 'annotation-text', 'font-size': '9', fill: '#3498db' }, 'Lingual'));
        g.appendChild(svgEl('text', { x: '112', y: '-65', class: 'annotation-text', 'font-size': '9', fill: '#3498db' }, 'wall'));

        // Depth dimension for axial wall
        g.appendChild(svgEl('line', { x1: '50', y1: '75', x2: '80', y2: '75', class: 'dimension-line' }));
        g.appendChild(svgEl('text', { x: '65', y: '88', class: 'dimension-text', 'text-anchor': 'middle', 'font-size': '9' }, '~1.5mm'));
      }
    }

    if (stepId === 5) {
      // Highlight gingival seat specifically
      g.appendChild(svgEl('line', {
        x1: '50', y1: '55', x2: '100', y2: '55',
        class: 'highlight-area', stroke: '#f39c12', 'stroke-width': '4',
      }));

      // Rounded axio-gingival line angle
      g.appendChild(svgEl('path', {
        d: 'M50,40 Q50,55 60,55',
        fill: 'none', stroke: '#e74c3c', 'stroke-width': '3',
      }));
      g.appendChild(svgEl('rect', { x: '10', y: '35', width: '38', height: '16', class: 'label-bg' }));
      g.appendChild(svgEl('text', { x: '29', y: '46', class: 'dimension-text', 'text-anchor': 'middle', 'font-size': '8' }, 'Rounded'));

      // 90-degree cavosurface indicator
      g.appendChild(svgEl('rect', { x: '95', y: '48', width: '8', height: '8', fill: 'none', stroke: '#e74c3c', 'stroke-width': '1.5' }));
      g.appendChild(svgEl('text', { x: '115', y: '58', class: 'dimension-text', 'font-size': '9' }, '~90\u00B0'));

      // Width dimension
      g.appendChild(svgEl('line', { x1: '48', y1: '68', x2: '102', y2: '68', class: 'dimension-line' }));
      g.appendChild(svgEl('text', { x: '75', y: '82', class: 'dimension-text', 'text-anchor': 'middle', 'font-size': '9' }, '~1mm'));
    }

    if (stepId === 6) {
      // Show all rounded internal line angles
      const angles = [
        { d: 'M50,40 Q50,55 60,55', label: 'Axio-gingival' },
        { d: 'M50,-25 Q42,-25 42,-15', label: 'Axio-buccal' },
      ];

      angles.forEach((a) => {
        g.appendChild(svgEl('path', {
          d: a.d,
          fill: 'none', stroke: '#e74c3c', 'stroke-width': '3',
        }));
      });

      // Axiopulpal line angle highlight
      g.appendChild(svgEl('path', {
        d: 'M48,-25 Q50,-20 50,-15',
        fill: 'none', stroke: '#e74c3c', 'stroke-width': '4',
      }));

      g.appendChild(svgEl('rect', { x: '5', y: '-50', width: '90', height: '16', class: 'label-bg' }));
      g.appendChild(svgEl('text', { x: '50', y: '-39', class: 'dimension-text', 'text-anchor': 'middle', 'font-size': '9' }, 'Axiopulpal (ROUND!)'));

      // No undercuts symbol
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
    g.appendChild(svgEl('path', {
      d: 'M-90,-140 Q-60,-165 -30,-170 Q-30,-155 -10,-148',
      fill: 'none', stroke: '#c9b99a', 'stroke-width': '1',
    }));
    g.appendChild(svgEl('path', {
      d: 'M95,-135 Q70,-158 50,-165 Q50,-150 30,-145',
      fill: 'none', stroke: '#c9b99a', 'stroke-width': '1',
    }));

    // Buccal cusp tip markers
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
    if (stepId >= 2) {
      // Occlusal prep visible from buccal (depression in occlusal surface)
      g.appendChild(svgEl('path', {
        d: 'M-20,-148 Q0,-140 20,-143 Q25,-148 20,-153 Q0,-145 -20,-148 Z',
        fill: 'rgba(100,180,255,0.4)', stroke: '#3498db', 'stroke-width': '1.5',
      }));
    }

    if (stepId >= 3) {
      // Distal extension & proximal box visible from buccal
      g.appendChild(svgEl('path', {
        d: 'M20,-143 Q40,-145 60,-140 Q70,-130 75,-100 Q75,-50 72,0 Q70,20 65,35 Q55,40 45,35 Q40,20 42,-20 Q45,-80 45,-120 Q40,-138 20,-143 Z',
        class: stepId <= 4 ? 'highlight-area' : 'prep-filled',
      }));
    }

    if (stepId === 7) {
      // Final preparation outline with clean margins
      g.appendChild(svgEl('path', {
        d: 'M-20,-148 Q0,-140 20,-143 Q40,-145 60,-140 Q70,-130 75,-100 Q75,-50 72,0 Q70,20 65,35 Q55,40 45,35 Q40,20 42,-20 Q45,-80 45,-120 Q40,-138 20,-143 Q0,-145 -20,-148 Z',
        fill: 'none', stroke: '#27ae60', 'stroke-width': '3',
      }));

      // Cavosurface angle indicators
      g.appendChild(svgEl('text', { x: '85', y: '-70', class: 'annotation-text', 'font-size': '9', fill: '#27ae60', 'font-weight': 'bold' }, '90\u00B0 butt'));
      g.appendChild(svgEl('text', { x: '85', y: '-58', class: 'annotation-text', 'font-size': '9', fill: '#27ae60', 'font-weight': 'bold' }, 'joint'));

      // Arrow pointing to proximal margin
      g.appendChild(svgEl('line', { x1: '84', y1: '-50', x2: '76', y2: '-40', stroke: '#27ae60', 'stroke-width': '1.5', 'marker-end': 'url(#arrow-end)' }));

      // Occlusal margin note
      g.appendChild(svgEl('text', { x: '-60', y: '-165', class: 'annotation-text', 'font-size': '9', fill: '#e74c3c' }, 'Optional short'));
      g.appendChild(svgEl('text', { x: '-60', y: '-155', class: 'annotation-text', 'font-size': '9', fill: '#e74c3c' }, 'bevel (occlusal only)'));
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
    STEPS.forEach((step, i) => {
      const li = document.createElement('li');
      li.dataset.index = i;
      li.innerHTML = `<span class="step-indicator">${step.id}</span><span>${step.title}</span>`;
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
      li.innerHTML = c;
      criteriaList.appendChild(li);
    });
  }

  function updateNavState() {
    // Update step list
    const items = stepList.querySelectorAll('li');
    items.forEach((li, i) => {
      li.classList.remove('active', 'completed');
      if (i === currentStep) li.classList.add('active');
      if (i < currentStep) li.classList.add('completed');
    });

    // Update buttons
    prevBtn.disabled = currentStep === 0;
    nextBtn.disabled = currentStep === STEPS.length - 1;
    nextBtn.textContent = currentStep === STEPS.length - 1 ? 'Complete' : 'Next \u2192';

    // Update progress
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
