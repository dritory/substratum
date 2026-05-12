/* substratum site — single-page app
 *
 * Loads docs/data.json (built from data/ and benchmarks/), renders four views:
 *   1. tensions over time (combined chart + per-tension small multiples)
 *   2. length–energy landscape scatter
 *   3. benchmark coverage donuts
 *   4. browseable filterable table
 *
 * Plotly is loaded via CDN in index.html; everything else is vanilla DOM.
 */

const REPO_BLOB = "https://github.com/dritory/substratum/blob/main";

const DOMAIN_COLOR = {
  particle:         "#7fb1e1",
  cosmology:        "#e0a04a",
  gravitation:      "#b69adf",
  atomic:           "#6dc197",
  nuclear:          "#d4b974",
  astrophysics:     "#82b9d4",
  condensed_matter: "#d77ea1",
  theoretical:      "#9ea3b3",
};

const KIND_COLOR = {
  reduction:               "#6dc197",
  precision_test:          "#7fb1e1",
  principle_invariance:    "#b69adf",
  forbidden_phenomenon:    "#e0a04a",
  cosmological_observable: "#82b9d4",
  tension_to_address:      "#d77ea1",
};

const EVAL_COLOR = {
  trivial:             "#6dc197",
  tractable:           "#7fb1e1",
  requires_code:       "#d4b974",
  requires_simulation: "#e0a04a",
  requires_lattice:    "#d77ea1",
  research_problem:    "#9ea3b3",
};

const STATUS_COLOR = {
  open:        "#e0a04a",
  contested:   "#d4b974",
  resolved:    "#6dc197",
  theoretical: "#9ea3b3",
  watching:    "#7fb1e1",
};

const VERDICT_COLOR = {
  pass:         "#6dc197",
  fail:         "#d96a6a",
  contested:    "#d4b974",
  inapplicable: "#82b9d4",
  open:         "#3a4257",
  no_evaluator: "#2a3142",
};

const VERDICT_ORDER = ["pass", "fail", "contested", "inapplicable", "open", "no_evaluator"];

const PUZZLE_VERDICT_COLOR = {
  closed:             "#6dc197",
  partial:            "#d4b974",
  requires_external:  "#9683bd",
  untouched:          "#2a3142",
};

const PUZZLE_VERDICT_ORDER = ["closed", "partial", "requires_external", "untouched"];

const PUZZLE_VERDICT_LABEL = {
  closed:             "closed",
  partial:            "partial",
  requires_external:  "requires external",
  untouched:          "untouched",
};

const VERDICT_LABEL = {
  pass:         "pass",
  fail:         "fail",
  contested:    "contested",
  inapplicable: "n/a",
  open:         "open (no prediction)",
  no_evaluator: "no evaluator",
};

const PLOTLY_BASE = {
  displaylogo: false,
  responsive: true,
  modeBarButtonsToRemove: ["lasso2d", "select2d", "autoScale2d"],
};

const FONT_BODY = '"Iowan Old Style","Charter","Source Serif Pro",Georgia,serif';
const FONT_MONO = '"JetBrains Mono","Iosevka","SF Mono",Menlo,monospace';

// Plotly theme — kept in sync with CSS custom properties in styles.css
const THEME = {
  paper:   "#161a23",   // --bg-elev
  plot:    "#161a23",
  ink:     "#e6e3d6",   // --ink
  ink_soft:"#aeb1bd",   // --ink-soft
  ink_faint:"#6b7180",  // --ink-faint
  grid:    "#22293a",
  grid_soft:"#1d2330",
  spike:   "#3a4257",
  marker_edge:"#0f1218", // --bg
  annot_bg:"rgba(15,18,24,0.85)",
};

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === "class") node.className = v;
    else if (k === "html") node.innerHTML = v;
    else if (k === "on") {
      for (const [evt, fn] of Object.entries(v)) node.addEventListener(evt, fn);
    } else if (k === "data") {
      for (const [dk, dv] of Object.entries(v)) node.dataset[dk] = dv;
    } else node.setAttribute(k, v);
  }
  for (const c of children.flat()) {
    if (c == null || c === false) continue;
    node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  }
  return node;
}

function fmtScale(x) {
  if (x == null || isNaN(x)) return "—";
  if (x === 0) return "0";
  const e = Math.log10(Math.abs(x));
  const exp = Math.round(e);
  const mant = x / Math.pow(10, exp);
  if (Math.abs(mant - 1) < 1e-3) return `10^${exp}`;
  return `${mant.toFixed(1)}×10^${exp}`;
}

/* ---------- main ---------- */

async function main() {
  let bundle;
  try {
    const res = await fetch("data.json", { cache: "no-cache" });
    bundle = await res.json();
  } catch (e) {
    document.body.innerHTML =
      '<div style="padding:3rem;font:18px/1.5 serif">' +
      "Could not load <code>data.json</code>. " +
      "Run <code>python3 scripts/build_site.py</code> from the repo root." +
      "</div>";
    return;
  }

  // header counts
  document.getElementById("count-tensions").textContent = bundle.counts.tensions;
  document.getElementById("count-benchmarks").textContent = bundle.counts.benchmarks;
  document.getElementById("count-frameworks").textContent =
    bundle.counts.frameworks ?? 0;
  document.getElementById("generated-at").textContent =
    new Date(bundle.generated_at).toLocaleString();

  // Optional header counts — only populate if the placeholder exists in
  // the current build of index.html.
  const pz = document.getElementById("count-puzzles");
  if (pz) pz.textContent = bundle.counts.puzzles ?? 0;
  const mz = document.getElementById("count-mechanisms");
  if (mz) mz.textContent = bundle.counts.mechanisms ?? 0;

  setupTabs();
  renderTensionsView(bundle);
  renderLandscape(bundle);
  renderBenchmarkCharts(bundle);
  renderEvaluation(bundle);
  renderAlignment(bundle);
  renderBrowse(bundle);
  hookupKeyboard();

  // After everything is in the DOM, force one resize pass so charts that were
  // initially hidden pick up their final container width.
  requestAnimationFrame(() => resizeChartsIn(document));
  window.addEventListener("resize", () => resizeChartsIn(document));
}

function setupTabs() {
  const tabs = document.querySelectorAll(".tab");
  const views = document.querySelectorAll(".view");
  tabs.forEach((t) =>
    t.addEventListener("click", () => {
      tabs.forEach((x) => x.classList.remove("active"));
      t.classList.add("active");
      let activated;
      views.forEach((v) => {
        const match = v.id === "view-" + t.dataset.view;
        v.classList.toggle("active", match);
        v.hidden = !match;
        if (match) activated = v;
      });
      // Plotly charts drawn into hidden containers latch onto the fallback
      // size; resize them now that their container has its real width.
      if (activated) resizeChartsIn(activated);
    })
  );
}

function resizeChartsIn(root) {
  if (!root || !window.Plotly) return;
  root.querySelectorAll(".chart, .chart-mini").forEach((div) => {
    // Plotly tags drawn divs with internal state; `_fullLayout` is present
    // once newPlot has run. Skip undrawn divs.
    if (div._fullLayout) {
      try { Plotly.Plots.resize(div); } catch (_) { /* ignore */ }
    }
  });
}

/* ---------- tensions view ---------- */

function renderTensionsView(bundle) {
  // overview chart with one trace per tension
  const traces = bundle.tensions
    .map((t) => buildTensionTrace(t))
    .filter(Boolean);

  Plotly.newPlot(
    "chart-overview",
    traces,
    {
      margin: { l: 50, r: 16, t: 16, b: 50 },
      paper_bgcolor: THEME.paper,
      plot_bgcolor: THEME.plot,
      font: { family: FONT_BODY, size: 13, color: THEME.ink },
      xaxis: {
        title: { text: "year", font: { size: 12 } },
        gridcolor: THEME.grid,
        zeroline: false,
        tickformat: "d",
      },
      yaxis: {
        title: { text: "significance σ", font: { size: 12 } },
        gridcolor: THEME.grid,
        rangemode: "tozero",
      },
      legend: {
        orientation: "h",
        y: -0.18,
        x: 0,
        bgcolor: "rgba(0,0,0,0)",
        font: { size: 12 },
      },
      hoverlabel: { font: { family: FONT_MONO, size: 12 } },
    },
    PLOTLY_BASE
  );

  // small multiples — one card per tension
  const grid = document.getElementById("grid-small-multiples");
  bundle.tensions.forEach((t) => {
    const trace = buildTensionTrace(t, /*forSmall*/ true);
    const card = el(
      "div",
      { class: "sm-card" },
      el(
        "h3",
        {},
        t.name,
        el("span", { class: "domain-chip", style: `background:${DOMAIN_COLOR[t.domain] || "#666"}` }, t.domain)
      ),
      latestPill(t),
      el("div", { class: "chart-mini", id: `mini-${t.id}` }),
      el(
        "a",
        {
          class: "src",
          href: `${REPO_BLOB}/data/${t.id}.json`,
          target: "_blank",
          rel: "noopener",
        },
        `data/${t.id}.json →`
      )
    );
    grid.appendChild(card);
    if (trace) {
      Plotly.newPlot(
        `mini-${t.id}`,
        [trace],
        {
          margin: { l: 36, r: 8, t: 6, b: 28 },
          paper_bgcolor: THEME.paper,
          plot_bgcolor: THEME.plot,
          font: { family: FONT_BODY, size: 10, color: THEME.ink_soft },
          xaxis: {
            tickformat: "d",
            gridcolor: THEME.grid_soft,
            zeroline: false,
            fixedrange: true,
          },
          yaxis: {
            rangemode: "tozero",
            gridcolor: THEME.grid_soft,
            zeroline: false,
            fixedrange: true,
          },
          showlegend: false,
          hoverlabel: { font: { family: FONT_MONO, size: 11 } },
        },
        { ...PLOTLY_BASE, displayModeBar: false, staticPlot: false }
      );
    } else {
      const div = document.getElementById(`mini-${t.id}`);
      div.innerHTML =
        '<div style="padding:1.5rem;color:#6b7180;font-style:italic;font-size:0.85rem">' +
        "no numeric σ — see source for the narrative</div>";
    }
  });
}

function buildTensionTrace(t, forSmall = false) {
  const points = t._history_parsed.filter((p) => p.sigma_numeric != null && p.year != null);
  if (points.length === 0) return null;
  // sort and de-duplicate stable
  points.sort((a, b) => a.year - b.year || a.sigma_numeric - b.sigma_numeric);
  const color = DOMAIN_COLOR[t.domain] || "#444";
  return {
    x: points.map((p) => p.year),
    y: points.map((p) => p.sigma_numeric),
    text: points.map((p) =>
      [
        `<b>${escapeHtml(t.name)}</b>`,
        `σ: ${wrapText(escapeHtml(p.sigma_text), 64)}`,
        p.comparison ? `vs: ${wrapText(escapeHtml(p.comparison), 64)}` : "",
        p.note ? `<i>${wrapText(escapeHtml(truncate(p.note, 240)), 64)}</i>` : "",
      ]
        .filter(Boolean)
        .join("<br>")
    ),
    name: t.name,
    type: "scatter",
    mode: forSmall ? "lines+markers" : "lines+markers",
    line: { color, width: forSmall ? 1.6 : 2.2, shape: "linear" },
    marker: { size: forSmall ? 6 : 9, color, line: { color: THEME.marker_edge, width: 1 } },
    hovertemplate: "%{text}<extra></extra>",
  };
}

function latestPill(t) {
  if (t._latest_sigma == null) {
    return el(
      "div",
      { class: "latest" },
      "latest σ ",
      el("b", {}, "—"),
      "  ",
      el("span", {}, t.status === "theoretical" ? "naturalness, not statistical" : t.status)
    );
  }
  return el(
    "div",
    { class: "latest" },
    "latest σ ",
    el("b", {}, t._latest_sigma.toFixed(1)),
    "  ",
    el("span", {}, `(${t._latest_year}, ${t.status}${t.trend ? ", " + t.trend : ""})`)
  );
}

/* ---------- length–energy landscape ---------- */

function renderLandscape(bundle) {
  const tensionsPts = bundle.tensions
    .filter((t) => isFinite(t._length_m) && isFinite(t._energy_ev) && t._length_m > 0 && t._energy_ev > 0)
    .map((t) => ({ ...t, _key: "tensions" }));
  const benchPts = bundle.benchmarks
    .filter((b) => isFinite(b._length_m) && isFinite(b._energy_ev) && b._length_m > 0 && b._energy_ev > 0)
    .map((b) => ({ ...b, _key: "benchmarks" }));

  const tensionTrace = {
    x: tensionsPts.map((p) => p._length_m),
    y: tensionsPts.map((p) => p._energy_ev),
    customdata: tensionsPts.map((p) => p.id),
    text: tensionsPts.map((p) => buildLandscapeHover(p)),
    name: "tensions",
    mode: "markers",
    type: "scatter",
    marker: {
      symbol: "circle",
      size: 18,
      line: { width: 1.5, color: THEME.ink },
      color: tensionsPts.map((p) => STATUS_COLOR[p.status] || "#666"),
      opacity: 0.92,
    },
    hovertemplate: "%{text}<extra></extra>",
  };

  // group benchmarks by kind for legend filtering
  const traces = [tensionTrace];
  const kinds = [...new Set(benchPts.map((p) => p.kind))];
  for (const k of kinds) {
    const subset = benchPts.filter((p) => p.kind === k);
    traces.push({
      x: subset.map((p) => p._length_m),
      y: subset.map((p) => p._energy_ev),
      customdata: subset.map((p) => p.id),
      text: subset.map((p) => buildLandscapeHover(p)),
      name: k,
      mode: "markers",
      type: "scatter",
      marker: {
        symbol: "square",
        size: 12,
        color: KIND_COLOR[k] || "#888",
        line: { width: 1, color: THEME.marker_edge },
        opacity: 0.85,
      },
      hovertemplate: "%{text}<extra></extra>",
    });
  }

  // reference annotations for physical scales
  const annotations = [
    annotation(1.6e-35, 1.22e28, "Planck"),
    annotation(1e-19, 1e12, "EW / TeV"),
    annotation(1.87e-15, 1.057e8, "muon mass"),
    annotation(2.82e-15, 5.11e5, "electron Compton"),
    annotation(1e11, null, "AU", "x"),
    annotation(1e22, null, "Mpc", "x"),
    annotation(1.3e26, null, "Hubble", "x"),
    annotation(null, 2.3e-3, "meV (CMB,Λ)", "y"),
    annotation(null, 1, "1 eV", "y"),
  ];

  Plotly.newPlot(
    "chart-landscape",
    traces,
    {
      margin: { l: 70, r: 30, t: 16, b: 60 },
      paper_bgcolor: THEME.paper,
      plot_bgcolor: THEME.plot,
      font: { family: FONT_BODY, size: 13, color: THEME.ink },
      xaxis: {
        title: { text: "characteristic length  ℓ  [m]" },
        type: "log",
        gridcolor: THEME.grid,
        zeroline: false,
        showspikes: true,
        spikecolor: THEME.spike,
        spikedash: "dot",
        spikethickness: 1,
      },
      yaxis: {
        title: { text: "characteristic energy  E  [eV]" },
        type: "log",
        gridcolor: THEME.grid,
        zeroline: false,
        showspikes: true,
        spikecolor: THEME.spike,
        spikedash: "dot",
        spikethickness: 1,
      },
      legend: {
        orientation: "h",
        y: -0.16,
        x: 0,
        bgcolor: "rgba(0,0,0,0)",
        font: { size: 11 },
      },
      hoverlabel: { font: { family: FONT_MONO, size: 12 }, align: "left" },
      annotations,
    },
    PLOTLY_BASE
  );

  document
    .getElementById("chart-landscape")
    .on("plotly_click", (ev) => {
      const id = ev.points[0]?.customdata;
      if (!id) return;
      const entry =
        bundle.tensions.find((t) => t.id === id) ||
        bundle.benchmarks.find((b) => b.id === id);
      if (entry) showDetail(entry, "landscape-detail");
    });
}

function annotation(x, y, label, kind) {
  // axis-anchored grid markers
  if (kind === "x") {
    return {
      x: Math.log10(x),
      xref: "x",
      y: 0,
      yref: "paper",
      yanchor: "bottom",
      showarrow: false,
      text: label,
      font: { size: 10, color: THEME.ink_faint, family: FONT_MONO },
      bgcolor: "THEME.annot_bg",
    };
  }
  if (kind === "y") {
    return {
      y: Math.log10(y),
      yref: "y",
      x: 0,
      xref: "paper",
      xanchor: "left",
      showarrow: false,
      text: label,
      font: { size: 10, color: THEME.ink_faint, family: FONT_MONO },
      bgcolor: "THEME.annot_bg",
    };
  }
  // free annotation in (x,y) space
  return {
    x: Math.log10(x),
    y: Math.log10(y),
    xref: "x",
    yref: "y",
    showarrow: false,
    text: label,
    font: { size: 10, color: THEME.ink_faint, family: FONT_MONO, style: "italic" },
    bgcolor: "THEME.annot_bg",
  };
}

function buildLandscapeHover(p) {
  const lines = [`<b>${escapeHtml(p.name)}</b>`];
  if (p._key === "tensions") {
    lines.push(`tension · ${escapeHtml(p.domain)} · ${escapeHtml(p.status || "")}`);
    if (p._latest_sigma != null)
      lines.push(`latest σ ≈ ${p._latest_sigma.toFixed(1)} (${p._latest_year})`);
  } else {
    lines.push(`benchmark · ${escapeHtml(p.kind)}`);
    if (p._evaluator_status) lines.push(`evaluator: ${escapeHtml(p._evaluator_status)}`);
  }
  lines.push(
    `<span style="font-family:${FONT_MONO}">ℓ=${fmtScale(p._length_m)} m, E=${fmtScale(p._energy_ev)} eV</span>`
  );
  if (p.summary || p.requirement) {
    const text = truncate(p.summary || p.requirement, 240);
    lines.push(`<i>${wrapText(escapeHtml(text), 64)}</i>`);
  }
  return lines.join("<br>");
}

/* ---------- benchmark charts ---------- */

function renderBenchmarkCharts(bundle) {
  const byKind = countBy(bundle.benchmarks, (b) => b.kind);
  const byEval = countBy(bundle.benchmarks, (b) => b._evaluator_status || "(none)");

  const kindLabels = Object.keys(byKind);
  const kindCounts = kindLabels.map((k) => byKind[k]);
  Plotly.newPlot(
    "chart-bench-kind",
    [
      {
        type: "bar",
        orientation: "h",
        y: kindLabels,
        x: kindCounts,
        marker: { color: kindLabels.map((k) => KIND_COLOR[k] || "#666") },
        text: kindCounts.map(String),
        textposition: "outside",
        hovertemplate: "%{y}: %{x}<extra></extra>",
      },
    ],
    {
      title: { text: "by kind", font: { size: 13, family: FONT_BODY } },
      margin: { l: 170, r: 30, t: 36, b: 36 },
      paper_bgcolor: THEME.paper,
      plot_bgcolor: THEME.plot,
      font: { family: FONT_BODY, size: 12, color: THEME.ink },
      xaxis: { gridcolor: THEME.grid, title: "" },
      yaxis: { automargin: true, tickfont: { family: FONT_MONO, size: 11 } },
    },
    PLOTLY_BASE
  );

  const evalLabels = Object.keys(byEval);
  const evalCounts = evalLabels.map((k) => byEval[k]);
  Plotly.newPlot(
    "chart-bench-evaluator",
    [
      {
        type: "bar",
        orientation: "h",
        y: evalLabels,
        x: evalCounts,
        marker: { color: evalLabels.map((k) => EVAL_COLOR[k] || "#666") },
        text: evalCounts.map(String),
        textposition: "outside",
        hovertemplate: "%{y}: %{x}<extra></extra>",
      },
    ],
    {
      title: { text: "by evaluator status", font: { size: 13, family: FONT_BODY } },
      margin: { l: 170, r: 30, t: 36, b: 36 },
      paper_bgcolor: THEME.paper,
      plot_bgcolor: THEME.plot,
      font: { family: FONT_BODY, size: 12, color: THEME.ink },
      xaxis: { gridcolor: THEME.grid, title: "" },
      yaxis: { automargin: true, tickfont: { family: FONT_MONO, size: 11 } },
    },
    PLOTLY_BASE
  );
}

/* ---------- evaluation ---------- */

function renderEvaluation(bundle) {
  const matrix = document.getElementById("verdict-matrix");
  const tallyEl = document.getElementById("chart-eval-tally");
  const legendEl = document.getElementById("verdict-legend");

  if (!bundle.evaluation || !bundle.evaluation.frameworks?.length) {
    matrix.innerHTML =
      '<div class="matrix-empty">' +
      "No evaluation data was bundled — add a framework JSON to <code>frameworks/</code> " +
      "and rerun <code>scripts/build_site.py</code>." +
      "</div>";
    tallyEl.innerHTML = "";
    return;
  }

  // legend
  legendEl.innerHTML = "";
  for (const status of VERDICT_ORDER) {
    legendEl.appendChild(
      el(
        "span",
        {
          class: "sw",
          style: `--swatch:${VERDICT_COLOR[status]}`,
        },
        VERDICT_LABEL[status]
      )
    );
  }

  const frameworks = bundle.evaluation.frameworks;
  const verdicts = bundle.evaluation.verdicts;

  // index verdicts by (framework_id, benchmark_id)
  const verdictMap = new Map();
  for (const v of verdicts) {
    verdictMap.set(`${v.framework_id}|${v.benchmark_id}`, v);
  }

  // benchmarks ordered by pass-rate ascending? actually we want easy on
  // the left, hard on the right per the copy. compute pass fraction:
  const benchOrder = bundle.benchmarks
    .map((b) => {
      let total = 0;
      let pass = 0;
      for (const fw of frameworks) {
        const v = verdictMap.get(`${fw.id}|${b.id}`);
        if (!v) continue;
        if (v.status === "open") continue; // unscored doesn't count toward difficulty
        total += 1;
        if (v.status === "pass" || v.status === "inapplicable") pass += 1;
      }
      return {
        id: b.id,
        name: b.name,
        kind: b.kind,
        passFrac: total ? pass / total : 1.0,
        scored: total,
      };
    })
    .sort((a, b) => b.passFrac - a.passFrac || a.name.localeCompare(b.name));

  // puzzle-verdict legend (parallel to the benchmark-verdict legend)
  const puzzleLegendEl = document.getElementById("puzzle-verdict-legend");
  if (puzzleLegendEl) {
    puzzleLegendEl.innerHTML = "";
    for (const v of PUZZLE_VERDICT_ORDER) {
      puzzleLegendEl.appendChild(
        el(
          "span",
          { class: "sw", style: `--swatch:${PUZZLE_VERDICT_COLOR[v]}` },
          PUZZLE_VERDICT_LABEL[v]
        )
      );
    }
  }

  renderTallyChart(frameworks, tallyEl);
  renderPuzzleTallyChart(frameworks);
  renderCoverage(frameworks, bundle, verdictMap);
  renderMatrix(frameworks, benchOrder, verdictMap, bundle, matrix);

  document
    .getElementById("eval-hide-open")
    .addEventListener("change", () => {
      renderMatrix(frameworks, benchOrder, verdictMap, bundle, matrix);
    });
}

function renderTallyChart(frameworks, el) {
  const traces = VERDICT_ORDER.map((status) => ({
    name: VERDICT_LABEL[status],
    x: frameworks.map((fw) => fw.tally?.[status] || 0),
    y: frameworks.map((fw) => fw.name),
    type: "bar",
    orientation: "h",
    marker: { color: VERDICT_COLOR[status] },
    hovertemplate: `${VERDICT_LABEL[status]}: %{x}<extra>%{y}</extra>`,
  }));

  Plotly.newPlot(
    el,
    traces,
    {
      barmode: "stack",
      margin: { l: 200, r: 30, t: 12, b: 36 },
      paper_bgcolor: THEME.paper,
      plot_bgcolor: THEME.plot,
      font: { family: FONT_BODY, size: 12, color: THEME.ink },
      xaxis: {
        gridcolor: THEME.grid,
        title: { text: "benchmarks", font: { size: 11 } },
      },
      yaxis: {
        automargin: true,
        tickfont: { family: FONT_BODY, size: 12 },
      },
      legend: {
        orientation: "h",
        y: -0.22,
        x: 0,
        bgcolor: "rgba(0,0,0,0)",
        font: { size: 11 },
      },
      hoverlabel: { font: { family: FONT_MONO, size: 12 } },
    },
    PLOTLY_BASE
  );
}

function renderPuzzleTallyChart(frameworks) {
  const el = document.getElementById("chart-eval-puzzle-tally");
  if (!el) return;

  const traces = PUZZLE_VERDICT_ORDER.map((v) => ({
    name: PUZZLE_VERDICT_LABEL[v],
    x: frameworks.map((fw) => fw.puzzle_tally?.[v] || 0),
    y: frameworks.map((fw) => fw.name),
    type: "bar",
    orientation: "h",
    marker: { color: PUZZLE_VERDICT_COLOR[v] },
    hovertemplate: `${PUZZLE_VERDICT_LABEL[v]}: %{x}<extra>%{y}</extra>`,
  }));

  Plotly.newPlot(
    el,
    traces,
    {
      barmode: "stack",
      margin: { l: 200, r: 30, t: 12, b: 36 },
      paper_bgcolor: THEME.paper,
      plot_bgcolor: THEME.plot,
      font: { family: FONT_BODY, size: 12, color: THEME.ink },
      xaxis: {
        gridcolor: THEME.grid,
        title: { text: "puzzles", font: { size: 11 } },
      },
      yaxis: {
        automargin: true,
        tickfont: { family: FONT_BODY, size: 12 },
      },
      legend: {
        orientation: "h",
        y: -0.22,
        x: 0,
        bgcolor: "rgba(0,0,0,0)",
        font: { size: 11 },
      },
      hoverlabel: { font: { family: FONT_MONO, size: 12 } },
    },
    PLOTLY_BASE
  );
}

function renderCoverage(frameworks, bundle, verdictMap) {
  const grid = document.getElementById("grid-eval-coverage");
  if (!grid) return;
  grid.innerHTML = "";

  // group benchmarks by category, in the bundle's facet order
  const categories = bundle.facets.benchmark_categories || [];
  const labels = bundle.facets.category_labels || {};
  const byCategory = {};
  for (const cat of categories) byCategory[cat] = [];
  for (const b of bundle.benchmarks) {
    const cat = b._category || "uncategorized";
    if (!byCategory[cat]) byCategory[cat] = [];
    byCategory[cat].push(b);
  }

  // Categories are rendered in the same order on every card so visual
  // comparison framework-vs-framework lines up by row. Order is fixed by
  // total benchmarks descending — the broadest physics areas at the top.
  const categoryOrder = [...categories].sort(
    (a, b) => (byCategory[b]?.length || 0) - (byCategory[a]?.length || 0)
  );
  // Pad labels to the same character count so the mono-font y-axis ticks
  // visually left-align across rows (and across cards).
  const labelWidth = Math.max(
    ...categoryOrder.map((c) => (labels[c] || c).length)
  );
  const NBSP = " ";
  const padLabel = (s) => s + NBSP.repeat(Math.max(0, labelWidth - s.length));

  for (const fw of frameworks) {
    // tally per category
    const rows = categoryOrder.map((cat) => {
      const counts = { pass: 0, fail: 0, contested: 0, inapplicable: 0, open: 0, no_evaluator: 0 };
      let total = 0;
      for (const b of byCategory[cat] || []) {
        const v = verdictMap.get(`${fw.id}|${b.id}`);
        const status = v ? v.status : "open";
        counts[status] = (counts[status] || 0) + 1;
        total += 1;
      }
      const open = counts.open + counts.no_evaluator;
      return { cat, label: padLabel(labels[cat] || cat), counts, total, open };
    });

    const cardId = `coverage-${fw.id}`;
    const card = el(
      "div",
      { class: "coverage-card" },
      el("h4", {}, fw.name),
      el("div", { class: "chart", id: cardId })
    );
    grid.appendChild(card);

    const yLabels = rows.map((r) => r.label);
    const traces = VERDICT_ORDER.map((status) => ({
      name: VERDICT_LABEL[status],
      x: rows.map((r) => r.counts[status] || 0),
      y: yLabels,
      type: "bar",
      orientation: "h",
      marker: { color: VERDICT_COLOR[status] },
      hovertemplate:
        `<b>%{y}</b><br>${VERDICT_LABEL[status]}: %{x}<extra></extra>`,
    }));

    Plotly.newPlot(
      cardId,
      traces,
      {
        barmode: "stack",
        margin: { l: 130, r: 24, t: 8, b: 36 },
        paper_bgcolor: THEME.paper,
        plot_bgcolor: THEME.plot,
        font: { family: FONT_BODY, size: 11, color: THEME.ink },
        xaxis: {
          gridcolor: THEME.grid,
          title: { text: "benchmarks", font: { size: 10 } },
          dtick: 1,
        },
        yaxis: {
          automargin: true,
          tickfont: { family: FONT_MONO, size: 11, color: THEME.ink_soft },
          autorange: "reversed",
          // Identical category order across cards (set explicitly so Plotly
          // doesn't reorder when traces happen to be empty in some columns).
          categoryorder: "array",
          categoryarray: rows.map((r) => r.label),
        },
        showlegend: false,
        hoverlabel: { font: { family: FONT_MONO, size: 11 } },
      },
      PLOTLY_BASE
    );
  }
}

function renderMatrix(frameworks, benchOrder, verdictMap, bundle, root) {
  const hideOpen = document.getElementById("eval-hide-open")?.checked;
  const cols = hideOpen
    ? benchOrder.filter((b) => {
        // keep if any framework has a non-open verdict for this benchmark
        return frameworks.some((fw) => {
          const v = verdictMap.get(`${fw.id}|${b.id}`);
          return v && v.status !== "open";
        });
      })
    : benchOrder;

  root.innerHTML = "";
  if (!cols.length) {
    root.appendChild(
      el(
        "div",
        { class: "matrix-empty" },
        "No benchmarks to show with current filters."
      )
    );
    return;
  }

  const grid = el("div", {
    class: "matrix-grid",
    style: `grid-template-columns: minmax(220px, 320px) repeat(${cols.length}, 18px); grid-template-rows: 9rem repeat(${frameworks.length}, 22px);`,
  });

  // header row: top-left empty (sticky corner), then column labels
  grid.appendChild(el("div", { class: "matrix-corner" }, ""));
  for (const b of cols) {
    grid.appendChild(
      el(
        "div",
        {
          class: "matrix-col-label",
          title: `${b.name} — ${(b.passFrac * 100).toFixed(0)}% pass-rate`,
          on: {
            click: () => {
              const bench = bundle.benchmarks.find((x) => x.id === b.id);
              if (bench) showDetail(bench, "evaluation-detail");
            },
          },
        },
        b.name
      )
    );
  }

  // data rows
  for (const fw of frameworks) {
    grid.appendChild(
      el(
        "div",
        {
          class: "matrix-row-label",
          on: {
            click: () => showFrameworkDetail(fw, bundle),
          },
        },
        fw.name
      )
    );
    for (const b of cols) {
      const v = verdictMap.get(`${fw.id}|${b.id}`);
      const status = v ? v.status : "open";
      const cell = el("div", {
        class: "matrix-cell",
        "data-status": status,
        title: `${fw.name} × ${b.name}\n${VERDICT_LABEL[status]}${
          v && v.score != null ? ` (score ${v.score.toFixed(2)})` : ""
        }${v && v.note ? `\n${v.note}` : ""}`,
        on: {
          click: () => showVerdictDetail(v, fw, b, bundle),
        },
      });
      grid.appendChild(cell);
    }
  }

  root.appendChild(grid);
}

function showVerdictDetail(verdict, fwSummary, benchSummary, bundle) {
  // Build a synthetic detail entry combining verdict + framework + benchmark.
  const benchFull = bundle.benchmarks.find((b) => b.id === benchSummary.id);
  const status = verdict?.status || "open";
  const panel = document.getElementById("evaluation-detail");
  panel.innerHTML = "";

  panel.appendChild(
    el(
      "header",
      {},
      el("h3", {}, `${fwSummary.name}  ×  ${benchSummary.name}`),
      el(
        "button",
        {
          class: "close",
          "aria-label": "close",
          on: { click: () => panel.setAttribute("hidden", "") },
        },
        "×"
      )
    )
  );

  const statusBadge = el(
    "span",
    {
      class: "pill",
      style: `background:${VERDICT_COLOR[status]};color:#0a0d12;font-weight:600`,
    },
    VERDICT_LABEL[status]
  );
  const pills = el("div", { style: "margin-bottom:0.6rem" });
  pills.appendChild(statusBadge);
  if (verdict?.score != null) {
    pills.appendChild(
      el("span", { class: "pill" }, `score ${verdict.score.toFixed(3)}`)
    );
  }
  if (verdict?.kind) pills.appendChild(el("span", { class: "pill" }, "kind: " + verdict.kind));
  panel.appendChild(pills);

  if (verdict?.note) {
    panel.appendChild(
      el(
        "section",
        {},
        el("h4", {}, "Verdict note"),
        el("p", {}, verdict.note)
      )
    );
  }

  if (verdict?.value !== undefined && verdict?.value !== null) {
    const v = verdict;
    const valueLine = `${v.value}${v.uncertainty != null ? " ± " + v.uncertainty : ""}${v.units ? " " + v.units : ""}`;
    panel.appendChild(
      el(
        "section",
        {},
        el("h4", {}, "Framework prediction"),
        el("p", { class: "mono" }, valueLine),
        v.reference ? el("p", { style: "color:var(--ink-faint);font-size:0.85rem" }, v.reference) : null
      )
    );
  }

  if (benchFull?.requirement) {
    panel.appendChild(
      el(
        "section",
        {},
        el("h4", {}, "Benchmark requirement"),
        el("p", {}, benchFull.requirement)
      )
    );
  }
  if (benchFull?.procedural?.bound_in_parameterization) {
    panel.appendChild(
      el(
        "section",
        {},
        el("h4", {}, "Bound"),
        el("p", { class: "mono" }, benchFull.procedural.bound_in_parameterization)
      )
    );
  }

  panel.appendChild(
    el(
      "section",
      {},
      el(
        "a",
        {
          href: `${REPO_BLOB}/frameworks/${fwSummary.id}.json`,
          target: "_blank",
          rel: "noopener",
        },
        `frameworks/${fwSummary.id}.json →`
      ),
      el("br", {}),
      el(
        "a",
        {
          href: `${REPO_BLOB}/benchmarks/${benchSummary.id}.json`,
          target: "_blank",
          rel: "noopener",
        },
        `benchmarks/${benchSummary.id}.json →`
      )
    )
  );

  panel.removeAttribute("hidden");
}

function showFrameworkDetail(fwSummary, bundle) {
  const panel = document.getElementById("evaluation-detail");
  panel.innerHTML = "";

  panel.appendChild(
    el(
      "header",
      {},
      el("h3", {}, fwSummary.name),
      el(
        "button",
        {
          class: "close",
          "aria-label": "close",
          on: { click: () => panel.setAttribute("hidden", "") },
        },
        "×"
      )
    )
  );

  // tally pills
  const pills = el("div", { style: "margin-bottom:0.6rem" });
  for (const status of VERDICT_ORDER) {
    const n = fwSummary.tally?.[status] || 0;
    if (!n) continue;
    pills.appendChild(
      el(
        "span",
        {
          class: "pill",
          style: `background:${VERDICT_COLOR[status]};color:#0a0d12;font-weight:600`,
        },
        `${n} ${VERDICT_LABEL[status]}`
      )
    );
  }
  panel.appendChild(pills);

  if (fwSummary.summary) {
    panel.appendChild(
      el(
        "section",
        {},
        el("h4", {}, "Summary"),
        el("p", {}, fwSummary.summary)
      )
    );
  }

  if (fwSummary.lineage?.length) {
    const ul = el("ul", {});
    for (const r of fwSummary.lineage) {
      const arxiv = r.arxiv ? ` arXiv:${r.arxiv}` : "";
      const doi = r.doi ? ` doi:${r.doi}` : "";
      ul.appendChild(el("li", {}, (r.citation || "") + arxiv + doi));
    }
    panel.appendChild(
      el("section", {}, el("h4", {}, "Lineage"), ul)
    );
  }

  if (fwSummary.tags?.length) {
    panel.appendChild(
      el(
        "section",
        {},
        el("h4", {}, "Tags"),
        el(
          "div",
          {},
          ...fwSummary.tags.map((t) => el("span", { class: "pill" }, t))
        )
      )
    );
  }

  panel.appendChild(
    el(
      "section",
      {},
      el(
        "a",
        {
          href: `${REPO_BLOB}/frameworks/${fwSummary.id}.json`,
          target: "_blank",
          rel: "noopener",
        },
        `frameworks/${fwSummary.id}.json →`
      )
    )
  );

  panel.removeAttribute("hidden");
}

/* ---------- alignment (puzzles x mechanisms) ---------- */

const ROLE_COLOR = {
  solves:           "#1f6feb",
  explains_pattern: "#7c3aed",
  ameliorates:      "#0a8754",
  requires:         "#a06900",
};
const ROLE_LABEL = {
  solves:           "solves",
  explains_pattern: "explains pattern",
  ameliorates:      "ameliorates",
  requires:         "requires",
};
const STATUS_COLOR_ALIGN = {
  mainstream: "#1f6feb",
  niche:      "#7c3aed",
  historical: "#6b7180",
  disfavored: "#b54848",
};

// Stable palette for mechanism types and puzzle kinds, used by both the
// network view and the attention-vs-progress scatter.
const MECH_TYPE_COLOR = {
  symmetry:      "#1f6feb",
  dynamical:     "#0a8754",
  uv_completion: "#7c3aed",
  geometric:     "#b78628",
  topological:   "#b54848",
  composite:     "#0891a8",
  anthropic:     "#6b7180",
};
const PUZZLE_KIND_COLOR = {
  naturalness: "#e8a838",
  pattern:     "#7c3aed",
  coincidence: "#1f6feb",
  consistency: "#0a8754",
};

function renderAlignment(bundle) {
  const puzzles = bundle.puzzles || [];
  const mechs = bundle.mechanisms || [];
  const alignment = bundle.alignment || {};
  const edges = alignment.edges || [];
  const positions = alignment.positions || {};
  if (!puzzles.length || !mechs.length) return;

  const netEl  = document.getElementById("chart-alignment-network");
  const compEl = document.getElementById("chart-alignment-compression");
  const progEl = document.getElementById("chart-alignment-progress");
  if (!netEl || !compEl || !progEl) return;

  renderAlignmentNetwork(netEl, puzzles, mechs, edges, positions);
  renderAlignmentCompression(compEl, mechs);
  renderAlignmentProgress(progEl, puzzles);
}

function renderAlignmentNetwork(node, puzzles, mechs, edges, positions) {
  const puzzleById = new Map(puzzles.map((p) => [p.id, p]));
  const mechById = new Map(mechs.map((m) => [m.id, m]));

  const px = (id) => (positions[`puzzle:${id}`] || [0, 0])[0];
  const py = (id) => (positions[`puzzle:${id}`] || [0, 0])[1];
  const mx = (id) => (positions[`mechanism:${id}`] || [0, 0])[0];
  const my = (id) => (positions[`mechanism:${id}`] || [0, 0])[1];

  // --- edge traces grouped by role ----------------------------------------
  const roleOrder = ["solves", "explains_pattern", "ameliorates", "requires"];
  const edgeTraces = [];
  for (const role of roleOrder) {
    const xs = [];
    const ys = [];
    let count = 0;
    for (const e of edges) {
      if (e.role !== role) continue;
      if (!mechById.has(e.mechanism_id) || !puzzleById.has(e.puzzle_id)) continue;
      xs.push(mx(e.mechanism_id), px(e.puzzle_id), null);
      ys.push(my(e.mechanism_id), py(e.puzzle_id), null);
      count += 1;
    }
    if (!count) continue;
    edgeTraces.push({
      type: "scattergl",
      mode: "lines",
      x: xs,
      y: ys,
      name: `${ROLE_LABEL[role]} (${count})`,
      line: { color: ROLE_COLOR[role], width: 0.9 },
      opacity: 0.45,
      hoverinfo: "skip",
      legendgroup: `role-${role}`,
      legendgrouptitle: { text: "edge role" },
    });
  }

  // --- puzzle node traces grouped by kind ---------------------------------
  const kinds = Object.keys(PUZZLE_KIND_COLOR);
  const puzzleTraces = [];
  for (const kind of kinds) {
    const ps = puzzles.filter((p) => (p.kind || "naturalness") === kind);
    if (!ps.length) continue;
    puzzleTraces.push({
      type: "scattergl",
      mode: "markers+text",
      x: ps.map((p) => px(p.id)),
      y: ps.map((p) => py(p.id)),
      text: ps.map((p) => p.name),
      textposition: "top center",
      textfont: { family: FONT_BODY, size: 10, color: THEME.ink },
      name: `puzzle: ${kind} (${ps.length})`,
      marker: {
        symbol: "square",
        size: ps.map((p) => 9 + Math.min(2.0 * (p._mechanisms_addressing || 1), 22)),
        color: PUZZLE_KIND_COLOR[kind],
        line: { color: THEME.marker_edge, width: 1.2 },
      },
      hovertemplate: ps.map((p) =>
        `<b>${p.name}</b><br>kind: ${kind}<br>` +
        `<b>${p._mechanisms_addressing || 0}</b> mechanisms address; ` +
        `<b>${p._mechanisms_closing || 0}</b> claim solves / explains_pattern<br>` +
        `<i>${(p.summary || "").replace(/\s+/g, " ").slice(0, 200)}${(p.summary || "").length > 200 ? "&hellip;" : ""}</i>` +
        `<extra></extra>`),
      legendgroup: `puzzle-${kind}`,
      legendgrouptitle: { text: "puzzle kind" },
    });
  }

  // --- mechanism node traces grouped by type ------------------------------
  const types = Object.keys(MECH_TYPE_COLOR);
  const mechTraces = [];
  for (const type of types) {
    const ms = mechs.filter((m) => (m.type || "dynamical") === type);
    if (!ms.length) continue;
    // only label degree >= 3 mechanisms to avoid clutter
    const labels = ms.map((m) => ((m._puzzles_addressed || 0) >= 3 ? m.id : ""));
    mechTraces.push({
      type: "scattergl",
      mode: "markers+text",
      x: ms.map((m) => mx(m.id)),
      y: ms.map((m) => my(m.id)),
      text: labels,
      textposition: "bottom center",
      textfont: { family: FONT_MONO, size: 9, color: THEME.ink_soft },
      name: `mechanism: ${type} (${ms.length})`,
      marker: {
        symbol: "circle",
        size: ms.map((m) => 7 + 2.2 * (m._puzzles_addressed || 1)),
        color: MECH_TYPE_COLOR[type],
        line: { color: THEME.marker_edge, width: 0.8 },
        opacity: 0.92,
      },
      hovertemplate: ms.map((m) =>
        `<b>${m.id}</b><br>type: ${type}<br>status: ${m.status || "?"}<br>` +
        `<b>${m._puzzles_addressed || 0}</b> edges &middot; ` +
        `<b>${m._puzzles_closed || 0}</b> closing<br>` +
        `<i>${(m.summary || "").replace(/\s+/g, " ").slice(0, 200)}${(m.summary || "").length > 200 ? "&hellip;" : ""}</i>` +
        `<extra></extra>`),
      legendgroup: `mech-${type}`,
      legendgrouptitle: { text: "mechanism type" },
    });
  }

  const layout = {
    ...PLOTLY_BASE,
    paper_bgcolor: THEME.paper,
    plot_bgcolor:  THEME.plot,
    font: { family: FONT_BODY, color: THEME.ink, size: 12 },
    margin: { l: 20, r: 20, t: 30, b: 20 },
    height: 720,
    showlegend: true,
    legend: {
      bgcolor: "rgba(0,0,0,0)",
      font: { color: THEME.ink_soft, size: 11 },
      itemsizing: "constant",
    },
    xaxis: {
      visible: false, range: [-1.15, 1.15],
      scaleanchor: "y", scaleratio: 1,
    },
    yaxis: { visible: false, range: [-1.15, 1.15] },
    hovermode: "closest",
  };

  Plotly.newPlot(node, [...edgeTraces, ...puzzleTraces, ...mechTraces],
                 layout, { displaylogo: false, responsive: true });
}

function renderAlignmentProgress(node, puzzles) {
  const rows = puzzles
    .filter((p) => (p._mechanisms_addressing || 0) > 0)
    .map((p) => ({
      id: p.id,
      name: p.name,
      kind: p.kind || "naturalness",
      total: p._mechanisms_addressing || 0,
      closing: p._mechanisms_closing || 0,
      frac: p._closure_fraction || 0,
      summary: p.summary || "",
    }));

  // group by kind for legend toggling + colour
  const byKind = new Map();
  for (const r of rows) {
    if (!byKind.has(r.kind)) byKind.set(r.kind, []);
    byKind.get(r.kind).push(r);
  }

  // decide which points get text labels: top-12 by attention, plus any
  // outlier (closure >= 0.55 or attention >= 12) to surface the quadrant
  // story without cluttering the centre.
  const byAttention = [...rows].sort((a, b) => b.total - a.total);
  const labelSet = new Set(byAttention.slice(0, 12).map((r) => r.id));
  for (const r of rows) {
    if (r.frac >= 0.55 || r.total >= 12) labelSet.add(r.id);
  }

  const traces = [];
  for (const [kind, list] of byKind) {
    traces.push({
      type: "scatter",
      mode: "markers+text",
      name: kind,
      x: list.map((r) => r.total),
      y: list.map((r) => r.frac),
      text: list.map((r) => (labelSet.has(r.id) ? r.name : "")),
      textposition: "top center",
      textfont: { family: FONT_BODY, size: 10, color: THEME.ink },
      marker: {
        color: PUZZLE_KIND_COLOR[kind] || THEME.ink_soft,
        size: 13,
        line: { color: THEME.marker_edge, width: 1.2 },
        opacity: 0.9,
      },
      hovertemplate: list.map((r) =>
        `<b>${r.name}</b><br>kind: ${kind}<br>` +
        `<b>${r.total}</b> mechanisms address; <b>${r.closing}</b> closing ` +
        `(${(r.frac * 100).toFixed(0)}%)<br>` +
        `<i>${r.summary.replace(/\s+/g, " ").slice(0, 200)}${r.summary.length > 200 ? "&hellip;" : ""}</i>` +
        `<extra></extra>`),
    });
  }

  const xmax = Math.max(5, ...rows.map((r) => r.total));

  const layout = {
    ...PLOTLY_BASE,
    paper_bgcolor: THEME.paper,
    plot_bgcolor:  THEME.plot,
    font: { family: FONT_BODY, color: THEME.ink, size: 12 },
    margin: { l: 60, r: 30, t: 30, b: 50 },
    height: 540,
    xaxis: {
      title: { text: "mechanisms addressing the puzzle", font: { size: 12, color: THEME.ink_soft } },
      gridcolor: THEME.grid_soft,
      zeroline: false,
      tickfont: { color: THEME.ink_soft },
      range: [0, xmax * 1.08],
    },
    yaxis: {
      title: { text: "closure fraction (solves + explains_pattern)", font: { size: 12, color: THEME.ink_soft } },
      gridcolor: THEME.grid_soft,
      zeroline: false,
      tickfont: { color: THEME.ink_soft },
      range: [-0.05, 1.05],
      tickformat: ".0%",
    },
    legend: { font: { color: THEME.ink_soft, size: 11 }, bgcolor: "rgba(0,0,0,0)" },
    annotations: [
      { x: 0.02, y: 0.97, xref: "paper", yref: "paper", text: "<i>quiet victories</i>",        showarrow: false, font: { color: THEME.ink_faint, size: 11 }, xanchor: "left",  yanchor: "top" },
      { x: 0.98, y: 0.97, xref: "paper", yref: "paper", text: "<i>active battleground</i>",    showarrow: false, font: { color: THEME.ink_faint, size: 11 }, xanchor: "right", yanchor: "top" },
      { x: 0.98, y: 0.03, xref: "paper", yref: "paper", text: "<i>attention without progress</i>", showarrow: false, font: { color: THEME.ink_faint, size: 11 }, xanchor: "right", yanchor: "bottom" },
      { x: 0.02, y: 0.03, xref: "paper", yref: "paper", text: "<i>under-targeted</i>",         showarrow: false, font: { color: THEME.ink_faint, size: 11 }, xanchor: "left",  yanchor: "bottom" },
    ],
  };

  Plotly.newPlot(node, traces, layout, { displaylogo: false, responsive: true });
}

function renderAlignmentCompression(node, mechs) {
  // x: params, y: puzzles closed, marker: status, size: degree
  const withClose = mechs.filter((m) => (m._puzzles_closed || 0) > 0);

  // group by status for colored traces
  const byStatus = new Map();
  for (const m of withClose) {
    const s = m.status || "unknown";
    if (!byStatus.has(s)) byStatus.set(s, []);
    byStatus.get(s).push(m);
  }

  const traces = [];
  for (const [status, list] of byStatus) {
    traces.push({
      type: "scatter",
      mode: "markers",
      name: status,
      x: list.map((m) => m._params || 0),
      y: list.map((m) => m._puzzles_closed || 0),
      text: list.map((m) =>
        `<b>${m.id}</b><br>` +
        `status: ${m.status}<br>` +
        `closed: ${m._puzzles_closed}/${m._puzzles_addressed} edges<br>` +
        `params: ${m._params}<br>` +
        `compression: ${(m._compression || 0).toFixed(2)}`
      ),
      hovertemplate: "%{text}<extra></extra>",
      marker: {
        size: list.map((m) => 8 + 3 * (m._puzzles_addressed || 1)),
        color: STATUS_COLOR_ALIGN[status] || THEME.ink_soft,
        line: { color: THEME.marker_edge, width: 1 },
        opacity: 0.85,
      },
    });
  }

  // constant-compression reference lines (y = c * x for c = 0.5, 1, 2)
  const xs = [0.5, 8];
  for (const c of [0.5, 1.0, 2.0]) {
    traces.push({
      type: "scatter",
      mode: "lines",
      x: xs,
      y: xs.map((x) => c * x),
      hoverinfo: "skip",
      showlegend: false,
      line: { color: THEME.grid, width: 1, dash: "dot" },
    });
  }

  const layout = {
    ...PLOTLY_BASE,
    paper_bgcolor: THEME.paper,
    plot_bgcolor:  THEME.plot,
    font: { family: FONT_BODY, color: THEME.ink, size: 12 },
    margin: { l: 60, r: 30, t: 30, b: 50 },
    height: 460,
    xaxis: {
      title: { text: "new parameters introduced", font: { size: 12, color: THEME.ink_soft } },
      gridcolor: THEME.grid_soft,
      zeroline: false,
      tickfont: { color: THEME.ink_soft },
    },
    yaxis: {
      title: { text: "puzzles closed (solves + explains_pattern)", font: { size: 12, color: THEME.ink_soft } },
      gridcolor: THEME.grid_soft,
      zeroline: false,
      tickfont: { color: THEME.ink_soft },
      dtick: 1,
    },
    legend: { font: { color: THEME.ink_soft, size: 11 }, bgcolor: "rgba(0,0,0,0)" },
    annotations: [
      { x: 8, y: 0.5 * 8, text: "c=0.5", showarrow: false, font: { color: THEME.ink_faint, size: 10 }, xanchor: "right", yshift: -8 },
      { x: 6,   y: 1.0 * 6,   text: "c=1.0", showarrow: false, font: { color: THEME.ink_faint, size: 10 }, xanchor: "right", yshift: -8 },
      { x: 3,   y: 2.0 * 3,   text: "c=2.0", showarrow: false, font: { color: THEME.ink_faint, size: 10 }, xanchor: "right", yshift: -8 },
    ],
  };

  Plotly.newPlot(node, traces, layout, { displaylogo: false, responsive: true });
}

/* ---------- browse ---------- */

const FILTER_STATE = {
  q: "",
  layer: new Set(["tension", "benchmark"]),
  facet: new Set(),         // kinds + domains, mixed
  evaluator: new Set(),
  status: new Set(),
};

function renderBrowse(bundle) {
  // build filters
  const filters = document.getElementById("filters");

  filters.appendChild(
    el("input", {
      type: "search",
      class: "search",
      placeholder: "search name, id, tags, requirement, summary…",
      on: {
        input: (e) => {
          FILTER_STATE.q = e.target.value.trim().toLowerCase();
          renderRows(bundle);
        },
      },
    })
  );

  filters.appendChild(
    chipGroup(
      "layer",
      ["tension", "benchmark"],
      FILTER_STATE.layer,
      () => renderRows(bundle)
    )
  );

  const allFacets = [
    ...bundle.facets.tension_domains.map((d) => ({ label: d, group: "tension" })),
    ...bundle.facets.benchmark_kinds.map((d) => ({ label: d, group: "benchmark" })),
  ];
  filters.appendChild(
    chipGroup(
      "domain / kind",
      allFacets.map((f) => f.label),
      FILTER_STATE.facet,
      () => renderRows(bundle)
    )
  );

  filters.appendChild(
    chipGroup(
      "evaluator",
      bundle.facets.benchmark_evaluator_statuses,
      FILTER_STATE.evaluator,
      () => renderRows(bundle)
    )
  );

  filters.appendChild(
    chipGroup(
      "status",
      bundle.facets.tension_statuses,
      FILTER_STATE.status,
      () => renderRows(bundle)
    )
  );

  renderRows(bundle);
}

function chipGroup(label, items, set, onChange) {
  const group = el(
    "div",
    { class: "filter-group" },
    el("label", {}, label)
  );
  for (const it of items) {
    const btn = el(
      "button",
      {
        class: "chip",
        type: "button",
        on: {
          click: () => {
            if (set.has(it)) set.delete(it);
            else set.add(it);
            btn.classList.toggle("on");
            onChange();
          },
        },
      },
      it
    );
    group.appendChild(btn);
  }
  return group;
}

function renderRows(bundle) {
  const rows = [...bundle.tensions, ...bundle.benchmarks].filter((e) => entryMatches(e));
  rows.sort((a, b) => {
    if (a._layer !== b._layer) return a._layer === "tension" ? -1 : 1;
    return (a.name || "").localeCompare(b.name || "");
  });

  const container = document.getElementById("browse-table");
  container.innerHTML = "";

  container.appendChild(
    el(
      "div",
      { class: "row row-head" },
      el("div", {}, "layer"),
      el("div", {}, "name"),
      el("div", {}, "domain / kind"),
      el("div", {}, "status / evaluator"),
      el("div", { style: "text-align:right" }, "σ / scale")
    )
  );

  if (rows.length === 0) {
    container.appendChild(
      el(
        "div",
        { class: "empty-row" },
        "no entries match the current filters."
      )
    );
    return;
  }

  for (const e of rows) {
    container.appendChild(buildRow(e));
  }
}

function entryMatches(e) {
  if (!FILTER_STATE.layer.has(e._layer)) return false;
  if (FILTER_STATE.facet.size > 0) {
    const facet = e._layer === "tension" ? e.domain : e.kind;
    if (!FILTER_STATE.facet.has(facet)) return false;
  }
  if (FILTER_STATE.evaluator.size > 0) {
    if (e._layer !== "benchmark") return false;
    if (!FILTER_STATE.evaluator.has(e._evaluator_status)) return false;
  }
  if (FILTER_STATE.status.size > 0) {
    if (e._layer !== "tension") return false;
    if (!FILTER_STATE.status.has(e.status)) return false;
  }
  if (FILTER_STATE.q) {
    const hay = [
      e.id,
      e.name,
      (e.tags || []).join(" "),
      e._category,
      e._category_label,
      e.summary || "",
      e.requirement || "",
      e.observable && e.observable.symbol,
      e.observable && e.observable.description,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    if (!hay.includes(FILTER_STATE.q)) return false;
  }
  return true;
}

function buildRow(e) {
  const sigmaCell =
    e._layer === "tension" && e._latest_sigma != null
      ? `σ≈${e._latest_sigma.toFixed(1)} (${e._latest_year})`
      : e._layer === "benchmark" && e._length_m
      ? `ℓ=${fmtScale(e._length_m)} m`
      : e._energy_ev != null
      ? `E=${fmtScale(e._energy_ev)} eV`
      : "—";

  return el(
    "div",
    {
      class: "row",
      on: {
        click: () => showDetail(e, "browse-detail"),
      },
    },
    el("div", { class: "layer " + e._layer }, e._layer),
    el(
      "div",
      { class: "name" },
      e.name,
      el("small", {}, e.id)
    ),
    el(
      "div",
      { class: "meta" },
      e._layer === "tension" ? e.domain : e.kind
    ),
    el(
      "div",
      { class: "meta" },
      e._layer === "tension"
        ? [e.status, e.trend && `(${e.trend})`].filter(Boolean).join(" ")
        : e._evaluator_status || ""
    ),
    el("div", { class: "num" }, sigmaCell)
  );
}

/* ---------- detail panel ---------- */

function showDetail(entry, panelId) {
  const panel = document.getElementById(panelId);
  panel.innerHTML = "";

  const sourceFolder = entry._layer === "tension" ? "data" : "benchmarks";
  const sourceUrl = `${REPO_BLOB}/${sourceFolder}/${entry.id}.json`;

  panel.appendChild(
    el(
      "header",
      {},
      el("h3", {}, entry.name),
      el(
        "button",
        {
          class: "close",
          "aria-label": "close",
          on: { click: () => panel.setAttribute("hidden", "") },
        },
        "×"
      )
    )
  );

  // pills row
  const pills = el("div", { style: "margin-bottom:0.6rem" });
  pills.appendChild(el("span", { class: "pill" }, entry._layer));
  if (entry.domain) pills.appendChild(el("span", { class: "pill" }, entry.domain));
  if (entry.kind)   pills.appendChild(el("span", { class: "pill" }, entry.kind));
  if (entry.status) pills.appendChild(el("span", { class: "pill" }, entry.status));
  if (entry.trend)  pills.appendChild(el("span", { class: "pill" }, "trend: " + entry.trend));
  if (entry._evaluator_status)
    pills.appendChild(el("span", { class: "pill" }, "evaluator: " + entry._evaluator_status));
  panel.appendChild(pills);

  if (entry.summary) {
    panel.appendChild(
      el(
        "section",
        {},
        el("h4", {}, "Summary"),
        el("p", {}, entry.summary)
      )
    );
  }

  if (entry.observable) {
    panel.appendChild(
      el(
        "section",
        {},
        el("h4", {}, "Observable"),
        el(
          "dl",
          { class: "kv" },
          el("dt", {}, "symbol"),
          el("dd", {}, entry.observable.symbol || "—"),
          entry.observable.units && el("dt", {}, "units"),
          entry.observable.units && el("dd", {}, entry.observable.units)
        ),
        el("p", { style: "margin-top:0.4rem" }, entry.observable.description || "")
      )
    );
  }

  if (entry.requirement) {
    panel.appendChild(
      el(
        "section",
        {},
        el("h4", {}, "Requirement"),
        el("p", {}, entry.requirement)
      )
    );
  }

  const scale = entry._length_m != null || entry._energy_ev != null;
  if (scale) {
    panel.appendChild(
      el(
        "section",
        {},
        el("h4", {}, "Characteristic scale"),
        el(
          "dl",
          { class: "kv" },
          el("dt", {}, "length"),
          el("dd", {}, entry._length_m == null ? "—" : `${fmtScale(entry._length_m)} m`),
          el("dt", {}, "energy"),
          el("dd", {}, entry._energy_ev == null ? "—" : `${fmtScale(entry._energy_ev)} eV`)
        )
      )
    );
  }

  if (entry._layer === "tension" && entry._history_parsed?.length) {
    const ul = el("ul", {});
    for (const h of entry._history_parsed) {
      ul.appendChild(
        el(
          "li",
          {},
          el(
            "span",
            { class: "mono", style: "margin-right:0.5rem" },
            h.year ?? "",
            "  σ=",
            h.sigma_text || "—"
          ),
          h.comparison ? el("i", {}, ` ${h.comparison}`) : null,
          h.note ? el("div", { style: "color:#aeb1bd;font-size:0.92em" }, h.note) : null
        )
      );
    }
    panel.appendChild(
      el(
        "section",
        {},
        el("h4", {}, "Tension history"),
        ul
      )
    );
  }

  if (entry._layer === "tension" && entry.measurements?.length) {
    const ul = el("ul", {});
    for (const m of entry.measurements) {
      ul.appendChild(
        el(
          "li",
          {},
          el(
            "span",
            { class: "mono" },
            `${m.year} `,
            `${m.experiment}: `,
            `${m.value}${m.uncertainty != null ? "±" + m.uncertainty : ""} ${m.units || ""}`
          ),
          m.note ? el("div", { style: "color:#aeb1bd;font-size:0.92em" }, m.note) : null
        )
      );
    }
    panel.appendChild(
      el(
        "section",
        {},
        el("h4", {}, "Measurements"),
        ul
      )
    );
  }

  if (entry.what_it_excludes) {
    panel.appendChild(
      el(
        "section",
        {},
        el("h4", {}, "What it excludes"),
        el("p", {}, entry.what_it_excludes)
      )
    );
  }

  if (entry.procedural) {
    const proc = entry.procedural;
    const sec = el("section", {}, el("h4", {}, "Procedural"));
    if (proc.parameterization?.name) {
      sec.appendChild(
        el("p", {}, el("b", {}, "Parameterization: "), proc.parameterization.name)
      );
      if (proc.parameterization.summary) {
        sec.appendChild(el("p", { style: "color:#aeb1bd" }, proc.parameterization.summary));
      }
    }
    if (proc.predicted_observable) {
      sec.appendChild(el("p", {}, el("b", {}, "Predicted observable: "), proc.predicted_observable));
    }
    if (proc.bound_in_parameterization) {
      sec.appendChild(el("p", {}, el("b", {}, "Bound: "), proc.bound_in_parameterization));
    }
    if (proc.framework_inputs?.length) {
      const ul = el("ul", {});
      proc.framework_inputs.forEach((s) => ul.appendChild(el("li", {}, s)));
      sec.appendChild(el("p", {}, el("b", {}, "Framework must expose:")));
      sec.appendChild(ul);
    }
    panel.appendChild(sec);
  }

  if (entry.tension_links?.length) {
    panel.appendChild(
      el(
        "section",
        {},
        el("h4", {}, "Tension links"),
        el(
          "ul",
          {},
          ...entry.tension_links.map((id) => el("li", { class: "mono" }, id))
        )
      )
    );
  }

  if (entry.cosmology_context?.extension_classes?.length) {
    const ul = el("ul", {});
    for (const c of entry.cosmology_context.extension_classes) {
      ul.appendChild(
        el(
          "li",
          {},
          el("b", {}, c.name),
          c.effect ? el("div", {}, c.effect) : null,
          c.cost_elsewhere
            ? el(
                "div",
                { style: "color:#e0a04a;margin-top:0.2rem" },
                el("i", {}, "cost elsewhere: "),
                c.cost_elsewhere
              )
            : null
        )
      );
    }
    panel.appendChild(
      el("section", {}, el("h4", {}, "Cosmology extensions"), ul)
    );
  }

  if (entry.smeft_context?.operators?.length) {
    const ul = el("ul", {});
    for (const o of entry.smeft_context.operators) {
      ul.appendChild(
        el(
          "li",
          {},
          el("span", { class: "mono" }, o.name),
          o.description ? el("div", {}, o.description) : null,
          o.current_bound
            ? el("div", { style: "color:#aeb1bd" }, el("i", {}, "bound: "), o.current_bound)
            : null
        )
      );
    }
    panel.appendChild(
      el("section", {}, el("h4", {}, "SMEFT operators"), ul)
    );
  }

  const refs = entry.references || entry.primary_references || [];
  if (refs.length) {
    const ul = el("ul", {});
    for (const r of refs) {
      const txt = r.citation || r;
      const arxiv = r.arxiv ? ` arXiv:${r.arxiv}` : "";
      const doi = r.doi ? ` doi:${r.doi}` : "";
      const li = el("li", {}, txt + arxiv + doi);
      ul.appendChild(li);
    }
    panel.appendChild(
      el("section", {}, el("h4", {}, "References"), ul)
    );
  }

  if (entry.tags?.length) {
    panel.appendChild(
      el(
        "section",
        {},
        el("h4", {}, "Tags"),
        el(
          "div",
          {},
          ...entry.tags.map((t) => el("span", { class: "pill" }, t))
        )
      )
    );
  }

  panel.appendChild(
    el(
      "section",
      {},
      el(
        "a",
        { href: sourceUrl, target: "_blank", rel: "noopener" },
        `view source on GitHub: ${sourceFolder}/${entry.id}.json →`
      )
    )
  );

  panel.removeAttribute("hidden");
}

/* ---------- helpers ---------- */

function countBy(arr, fn) {
  const out = {};
  for (const x of arr) {
    const k = fn(x);
    out[k] = (out[k] || 0) + 1;
  }
  // sort entries descending by count
  return Object.fromEntries(Object.entries(out).sort((a, b) => a[1] - b[1]));
}

function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"]/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])
  );
}

function truncate(s, n) {
  if (!s) return "";
  s = String(s);
  return s.length > n ? s.slice(0, n - 1).trimEnd() + "…" : s;
}

// Word-wrap a string into lines no longer than `width` characters, joined
// with `<br>` for use inside Plotly hoverlabels (which apply white-space:
// nowrap per line, so without explicit breaks the tooltip stretches off
// screen). Splits on whitespace; never breaks inside a word.
function wrapText(s, width = 60) {
  if (!s) return "";
  const words = String(s).split(/\s+/);
  const lines = [];
  let line = "";
  for (const w of words) {
    if (!line) {
      line = w;
    } else if (line.length + 1 + w.length <= width) {
      line += " " + w;
    } else {
      lines.push(line);
      line = w;
    }
  }
  if (line) lines.push(line);
  return lines.join("<br>");
}

function hookupKeyboard() {
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".detail-panel").forEach((p) => p.setAttribute("hidden", ""));
    }
  });
}

document.addEventListener("DOMContentLoaded", main);
