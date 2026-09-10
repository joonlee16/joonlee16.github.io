#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_notes.py — replace the Notes section of joonlee16.github.io

Run this from the root of your site repo (the folder containing _config.yml):

    python3 build_notes.py            # writes notes.html + notes/*.html
    python3 build_notes.py --flat     # writes notes.html + notes-*.html (no subfolder)
    python3 build_notes.py --dry-run  # show what would change, write nothing

The old notes.html is backed up to notes.html.bak-<timestamp> unless --no-backup.
Every generated page is a normal Jekyll page (layout: default), so your existing
nav, footer and styling wrap around it. Math is rendered with MathJax v3.
"""

import argparse
import datetime
import shutil
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Shared assets
# --------------------------------------------------------------------------

MATHJAX = r"""<script>
  window.MathJax = {
    tex: {
      inlineMath: [['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']],
      tags: 'none'
    },
    options: { skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre'] }
  };
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>"""

CSS = r"""<style>
.nb {
  --ink: #16181d;
  --muted: #5b6572;
  --accent: #0b5fc1;
  --accent-soft: #eef4fc;
  --rule: #e2e6ec;
  --panel: #f7f8fa;
  --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  --serif: Charter, "Bitstream Charter", "Iowan Old Style", "Source Serif Pro", Georgia, serif;

  max-width: 1160px;
  margin: 2rem auto 4.5rem;
  padding: 0 20px;
  color: var(--ink);
  font-family: var(--serif);
  font-size: 17px;
  line-height: 1.68;
}

/* ---------- page head ---------- */
.nb-crumb {
  font-family: var(--sans);
  font-size: .82rem;
  color: var(--muted);
  margin-bottom: 1.4rem;
}
.nb-crumb a { color: var(--muted); text-decoration: none; border-bottom: 1px solid var(--rule); }
.nb-crumb a:hover { color: var(--accent); border-color: var(--accent); }

.nb-title {
  font-family: var(--sans);
  font-size: 2.1rem;
  font-weight: 650;
  letter-spacing: -.02em;
  line-height: 1.15;
  margin: 0 0 .6rem;
}
.nb-deck {
  color: var(--muted);
  font-size: 1.05rem;
  margin: 0 0 1.6rem;
  max-width: 62ch;
}
.nb-rule { border: 0; border-top: 1px solid var(--rule); margin: 0 0 2.2rem; }

/* ---------- two-column shell ---------- */
.nb-grid { display: grid; grid-template-columns: minmax(0, 1fr) 210px; gap: 52px; align-items: start; }
.nb-body { min-width: 0; }

.nb-toc { position: sticky; top: 24px; font-family: var(--sans); font-size: .85rem; }
.nb-toc-head { font-weight: 650; margin-bottom: .6rem; font-size: .8rem; color: var(--ink); }
.nb-toc ol { list-style: none; margin: 0; padding: 0; counter-reset: toc; }
.nb-toc li { margin: 0 0 .38rem; padding-left: 1.5rem; text-indent: -1.5rem; }
.nb-toc li::before {
  counter-increment: toc; content: counter(toc) ". ";
  color: var(--muted); font-variant-numeric: tabular-nums;
}
.nb-toc a { color: var(--muted); text-decoration: none; }
.nb-toc a:hover { color: var(--accent); }

/* ---------- typography ---------- */
.nb-body { counter-reset: sec; }
.nb-body > h2 {
  font-family: var(--sans);
  font-size: 1.32rem;
  font-weight: 650;
  letter-spacing: -.01em;
  margin: 3rem 0 .9rem;
  padding-top: .2rem;
  scroll-margin-top: 20px;
}
.nb-body > h2::before {
  counter-increment: sec;
  content: counter(sec) ".";
  color: var(--accent);
  margin-right: .5rem;
  font-variant-numeric: tabular-nums;
}
.nb-body > h2:first-child { margin-top: 0; }
.nb-body h3 {
  font-family: var(--sans);
  font-size: 1.02rem;
  font-weight: 650;
  margin: 1.9rem 0 .5rem;
}
.nb-body p { margin: 0 0 1rem; max-width: 72ch; }
.nb-body ul, .nb-body ol { max-width: 70ch; padding-left: 1.35rem; margin: 0 0 1.1rem; }
.nb-body li { margin-bottom: .38rem; }
.nb-body a { color: var(--accent); text-decoration: none; border-bottom: 1px solid var(--accent-soft); }
.nb-body a:hover { border-bottom-color: var(--accent); }
.nb-body strong { font-weight: 600; }
.nb-body code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: .88em; background: var(--panel); padding: .1em .35em; border-radius: 3px;
}

/* ---------- blocks ---------- */
.nb-key {
  border-left: 3px solid var(--accent);
  background: var(--accent-soft);
  padding: .85rem 1.1rem;
  margin: 1.4rem 0;
  border-radius: 0 4px 4px 0;
}
.nb-key p { margin: 0; }
.nb-key p + p { margin-top: .6rem; }

.nb-eg {
  border: 1px solid var(--rule);
  border-radius: 5px;
  padding: .9rem 1.1rem .3rem;
  margin: 1.4rem 0;
  background: #fff;
}
.nb-eg-label {
  font-family: var(--sans); font-size: .78rem; font-weight: 650;
  color: var(--muted); margin-bottom: .5rem;
}

/* ---------- figures ---------- */
.nb-fig { margin: 1.9rem 0; }
.nb-fig svg { display: block; width: 100%; height: auto; max-width: 620px; margin: 0 auto; }
.nb-fig figcaption {
  font-family: var(--sans); font-size: .82rem; color: var(--muted);
  margin-top: .7rem; text-align: center; max-width: 60ch; margin-left: auto; margin-right: auto;
}
.nb-fig text { font-family: var(--sans); }

/* ---------- tables ---------- */
.nb-table-wrap { overflow-x: auto; margin: 1.6rem 0; }
.nb-body table { border-collapse: collapse; width: 100%; font-family: var(--sans); font-size: .87rem; }
.nb-body th, .nb-body td {
  text-align: left; padding: .55rem .7rem; border-bottom: 1px solid var(--rule); vertical-align: top;
}
.nb-body th { font-weight: 650; border-bottom: 1.5px solid var(--ink); white-space: nowrap; }
.nb-body tbody tr:last-child td { border-bottom: none; }

/* ---------- math ---------- */
mjx-container[display="true"] { margin: 1.15rem 0 !important; overflow-x: auto; overflow-y: hidden; padding: 2px 0; }

/* ---------- prev / next ---------- */
.nb-pager {
  display: flex; justify-content: space-between; gap: 1rem;
  margin-top: 3.5rem; padding-top: 1.2rem; border-top: 1px solid var(--rule);
  font-family: var(--sans); font-size: .88rem;
}
.nb-pager a { color: var(--accent); text-decoration: none; }
.nb-pager a:hover { text-decoration: underline; }
.nb-pager span { color: #b9c0c9; }

@media (max-width: 900px) {
  .nb { font-size: 16px; }
  .nb-grid { grid-template-columns: 1fr; gap: 0; }
  .nb-toc {
    position: static; order: -1; border: 1px solid var(--rule);
    border-radius: 5px; padding: .9rem 1.1rem; margin-bottom: 2rem; background: var(--panel);
  }
  .nb-title { font-size: 1.72rem; }
}
</style>"""


def make_page(title, deck, toc, body, prev_link, next_link, index_href):
    """Assemble one Jekyll notes page."""
    toc_items = "\n".join(
        '      <li><a href="#{0}">{1}</a></li>'.format(anchor, label) for anchor, label in toc
    )

    if prev_link:
        prev_html = '<a href="{0}">&larr; {1}</a>'.format(*prev_link)
    else:
        prev_html = "<span></span>"
    if next_link:
        next_html = '<a href="{0}">{1} &rarr;</a>'.format(*next_link)
    else:
        next_html = "<span></span>"

    return """---
layout: default
title: {title}
---

{mathjax}

{css}

{{% raw %}}
<div class="nb">

  <div class="nb-crumb"><a href="{index_href}">Notes</a> &middot; {title}</div>
  <h1 class="nb-title">{title}</h1>
  <p class="nb-deck">{deck}</p>
  <hr class="nb-rule">

  <div class="nb-grid">
    <div class="nb-body">
{body}

      <div class="nb-pager">
        {prev_html}
        {next_html}
      </div>
    </div>

    <nav class="nb-toc" aria-label="On this page">
      <div class="nb-toc-head">On this page</div>
      <ol>
{toc_items}
      </ol>
    </nav>
  </div>

</div>
{{% endraw %}}
""".format(
        title=title,
        deck=deck,
        mathjax=MATHJAX,
        css=CSS,
        body=body,
        toc_items=toc_items,
        prev_html=prev_html,
        next_html=next_html,
        index_href=index_href,
    )


# --------------------------------------------------------------------------
# Page 1 — System modelling
# --------------------------------------------------------------------------

TOC_SYSTEM = [
    ("state-input-dynamics", "State, input, dynamics"),
    ("dof", "Configuration and DOF"),
    ("time", "Continuous vs discrete time"),
    ("linear", "Linear vs nonlinear"),
    ("affine", "Control-affine form"),
    ("linearization", "Linearization"),
    ("actuation", "Actuation"),
    ("time-varying", "Time dependence"),
    ("uncertainty", "Uncertainty"),
    ("outputs", "Outputs and estimation"),
    ("summary", "Classifying a model"),
]

BODY_SYSTEM = r"""      <p>Almost everything in control begins with the same object: a mathematical
      description of how a system's state changes over time. Before choosing a
      controller you have to say what the system <em>is</em> — how many variables
      describe it, what you are allowed to command, whether the equations are linear,
      whether time runs continuously, and how badly the model can be wrong. Those
      choices decide which tools are available to you later.</p>

      <p>These notes give the vocabulary. They are deliberately short on proofs and
      long on the distinctions that change what you can do.</p>

      <figure class="nb-fig">
        <svg viewBox="0 0 520 262" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Five questions that classify a system model">
          <g font-size="12.5" fill="#16181d">
            <g>
              <text x="0" y="35" fill="#5b6572" font-size="11.5">How does the state enter?</text>
              <rect x="185" y="20" width="112" height="26" rx="4" fill="#eef4fc" stroke="#0b5fc1" stroke-width="1"/>
              <text x="241" y="37" text-anchor="middle" fill="#0b5fc1">linear</text>
              <line x1="303" y1="33" x2="349" y2="33" stroke="#e2e6ec" stroke-width="1.5" stroke-dasharray="3 3"/>
              <rect x="355" y="20" width="112" height="26" rx="4" fill="#f7f8fa" stroke="#e2e6ec" stroke-width="1"/>
              <text x="411" y="37" text-anchor="middle">nonlinear</text>
            </g>
            <g>
              <text x="0" y="81" fill="#5b6572" font-size="11.5">How does time advance?</text>
              <rect x="185" y="66" width="112" height="26" rx="4" fill="#eef4fc" stroke="#0b5fc1" stroke-width="1"/>
              <text x="241" y="83" text-anchor="middle" fill="#0b5fc1">continuous</text>
              <line x1="303" y1="79" x2="349" y2="79" stroke="#e2e6ec" stroke-width="1.5" stroke-dasharray="3 3"/>
              <rect x="355" y="66" width="112" height="26" rx="4" fill="#f7f8fa" stroke="#e2e6ec" stroke-width="1"/>
              <text x="411" y="83" text-anchor="middle">discrete</text>
            </g>
            <g>
              <text x="0" y="127" fill="#5b6572" font-size="11.5">Enough independent inputs?</text>
              <rect x="185" y="112" width="112" height="26" rx="4" fill="#eef4fc" stroke="#0b5fc1" stroke-width="1"/>
              <text x="241" y="129" text-anchor="middle" fill="#0b5fc1">fully actuated</text>
              <line x1="303" y1="125" x2="349" y2="125" stroke="#e2e6ec" stroke-width="1.5" stroke-dasharray="3 3"/>
              <rect x="355" y="112" width="112" height="26" rx="4" fill="#f7f8fa" stroke="#e2e6ec" stroke-width="1"/>
              <text x="411" y="129" text-anchor="middle">underactuated</text>
            </g>
            <g>
              <text x="0" y="173" fill="#5b6572" font-size="11.5">Does the law of motion drift?</text>
              <rect x="185" y="158" width="112" height="26" rx="4" fill="#eef4fc" stroke="#0b5fc1" stroke-width="1"/>
              <text x="241" y="175" text-anchor="middle" fill="#0b5fc1">time-invariant</text>
              <line x1="303" y1="171" x2="349" y2="171" stroke="#e2e6ec" stroke-width="1.5" stroke-dasharray="3 3"/>
              <rect x="355" y="158" width="112" height="26" rx="4" fill="#f7f8fa" stroke="#e2e6ec" stroke-width="1"/>
              <text x="411" y="175" text-anchor="middle">time-varying</text>
            </g>
            <g>
              <text x="0" y="219" fill="#5b6572" font-size="11.5">Is the model exact?</text>
              <rect x="185" y="204" width="112" height="26" rx="4" fill="#eef4fc" stroke="#0b5fc1" stroke-width="1"/>
              <text x="241" y="221" text-anchor="middle" fill="#0b5fc1">nominal</text>
              <line x1="303" y1="217" x2="349" y2="217" stroke="#e2e6ec" stroke-width="1.5" stroke-dasharray="3 3"/>
              <rect x="355" y="204" width="112" height="26" rx="4" fill="#f7f8fa" stroke="#e2e6ec" stroke-width="1"/>
              <text x="411" y="221" text-anchor="middle">uncertain</text>
            </g>
            <text x="0" y="252" fill="#5b6572" font-size="11">Left column: the convenient case. Every step right removes tools from the kit.</text>
          </g>
        </svg>
        <figcaption>A model is fixed by answering five independent questions, and the answers are what decide which controllers are available later.</figcaption>
      </figure>

      <h2 id="state-input-dynamics">State, input, dynamics</h2>

      <p>A model has three pieces. The <strong>state</strong> \(x \in \mathbb{R}^n\) is the
      smallest set of numbers that summarises the past well enough to predict the future.
      The <strong>input</strong> \(u \in \mathbb{R}^m\) is what you are allowed to command —
      a force, a torque, a thrust, a wheel speed. The <strong>dynamics</strong> \(f\) tie them
      together:</p>

      $$\dot{x} = f(x, u).$$

      <p>The defining property of a state is sufficiency: if you know \(x(t_0)\) and the
      whole input signal \(u(\cdot)\) on \([t_0, t]\), you can compute \(x(t)\) without
      knowing anything else about what happened before \(t_0\). Anything you need to
      remember belongs in \(x\); anything you don't, doesn't.</p>

      <div class="nb-eg">
        <div class="nb-eg-label">Example — a mass on a line</div>
        <p>Let \(p\) be position and \(v\) velocity, and let the input be acceleration.
        Position alone is not a state: knowing where the mass is tells you nothing about
        where it goes next. Position and velocity together are.</p>
        $$x = \begin{bmatrix} p \\ v \end{bmatrix}, \qquad
          \dot{x} = \begin{bmatrix} v \\ u \end{bmatrix}.$$
      </div>

      <div class="nb-key">
        <p>Choosing the state is a modelling decision, not a fact about the world. Adding
        states buys fidelity (motor lag, tire slip, an integrator on the error) and costs
        you dimension, identification effort, and often controller tractability.</p>
      </div>

      <h2 id="dof">Configuration and degrees of freedom</h2>

      <p>For mechanical systems it is usually cleaner to split the state into
      <strong>configuration</strong> \(q \in \mathbb{R}^k\) — joint angles, positions,
      orientations — and its velocity \(\dot q\):</p>

      $$x = \begin{bmatrix} q \\ \dot q \end{bmatrix} \in \mathbb{R}^{2k}.$$

      <p>The number \(k\) of independent configuration coordinates is the number of
      <strong>degrees of freedom</strong>. A pendulum has one (\(q = \theta\)). A cart-pole
      has two (cart position and pole angle). A planar mobile robot has three
      (\(p_x, p_y, \psi\)). A free rigid body in 3D has six.</p>

      <p>Written this way, Lagrangian mechanics gives the standard manipulator form</p>

      $$M(q)\,\ddot q + C(q,\dot q)\,\dot q + G(q) = B(q)\,u,$$

      <p>with \(M\) the inertia matrix, \(C\) the Coriolis and centrifugal terms, \(G\)
      gravity, and \(B\) the map from inputs to generalised forces. The shape of \(B\) is
      what decides actuation, which is the subject of section 7.</p>

      <h2 id="time">Continuous time and discrete time</h2>

      <p>Physics is written in continuous time,</p>

      $$\dot{x} = f(x,u),$$

      <p>but controllers run on computers at a fixed rate, so the model you actually
      implement is a difference equation</p>

      $$x_{k+1} = F(x_k, u_k),$$

      <p>where \(x_k \approx x(k\Delta t)\) and the input is held constant between samples.
      Both descriptions of the same robot coexist: you analyse in continuous time and
      implement in discrete time, or you discretise once and do everything discretely.</p>

      <figure class="nb-fig">
        <svg viewBox="0 0 520 206" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A continuous trajectory sampled at fixed intervals with a zero-order-hold staircase">
          <line x1="50" y1="170" x2="500" y2="170" stroke="#c8cfd8" stroke-width="1"/>
          <line x1="60" y1="30" x2="60" y2="170" stroke="#c8cfd8" stroke-width="1"/>
          <path d="M 60 150 L 90 139 L 120 129 L 150 121 L 180 113 L 210 106 L 240 99 L 270 92.5 L 300 86 L 330 80 L 360 74 L 390 68 L 420 62 L 450 56 L 480 50"
                fill="none" stroke="#16181d" stroke-width="1.8"/>
          <path d="M 60 150 H 120 V 129 H 180 V 113 H 240 V 99 H 300 V 86 H 360 V 74 H 420 V 62 H 480 V 50"
                fill="none" stroke="#0b5fc1" stroke-width="1.5" stroke-dasharray="4 3"/>
          <g fill="#0b5fc1">
            <circle cx="60" cy="150" r="3.2"/><circle cx="120" cy="129" r="3.2"/>
            <circle cx="180" cy="113" r="3.2"/><circle cx="240" cy="99" r="3.2"/>
            <circle cx="300" cy="86" r="3.2"/><circle cx="360" cy="74" r="3.2"/>
            <circle cx="420" cy="62" r="3.2"/><circle cx="480" cy="50" r="3.2"/>
          </g>
          <g stroke="#5b6572" stroke-width="1">
            <line x1="180" y1="178" x2="240" y2="178"/>
            <line x1="180" y1="174" x2="180" y2="182"/>
            <line x1="240" y1="174" x2="240" y2="182"/>
          </g>
          <text x="210" y="195" text-anchor="middle" font-size="11.5" fill="#5b6572">&#916;t</text>
          <text x="330" y="128" font-size="12" fill="#16181d">true trajectory</text>
          <text x="330" y="144" font-size="12" fill="#0b5fc1">held between samples</text>
        </svg>
        <figcaption>The controller only sees the dots. Everything between them is the discretisation's problem.</figcaption>
      </figure>

      <p>Three ways to get \(F\) from \(f\), in increasing order of cost and accuracy:</p>

      <ul>
        <li><strong>Forward Euler.</strong> \(x_{k+1} = x_k + \Delta t\, f(x_k, u_k)\).
        One evaluation, local error \(O(\Delta t^2)\). Fine for fast sample rates and gentle
        dynamics; it will quietly inject energy into oscillatory systems.</li>
        <li><strong>Runge–Kutta 4.</strong> Four evaluations per step, local error
        \(O(\Delta t^5)\). The usual default for simulation and for MPC prediction models.</li>
        <li><strong>Exact discretisation (linear systems only).</strong> For \(\dot x = Ax + Bu\)
        with \(u\) held constant over each interval,
        $$A_d = e^{A\Delta t}, \qquad B_d = \left(\int_0^{\Delta t} e^{A\tau}\,d\tau\right) B,$$
        which is exact, not an approximation.</li>
      </ul>

      <div class="nb-key">
        <p>Discretisation is not cosmetic. A controller proven stable in continuous time can
        go unstable when sampled too slowly, and constraints enforced only at sample instants
        can be violated between them. If you rely on a guarantee, check that it survives
        sampling.</p>
      </div>

      <h2 id="linear">Linear and nonlinear systems</h2>

      <p>A system is <strong>linear</strong> (LTI, if also time-invariant) when it can be
      written as</p>

      $$\dot{x} = A x + B u, \qquad y = C x + D u.$$

      <p>Equivalently, it obeys superposition: the response to \(\alpha u_1 + \beta u_2\)
      is \(\alpha\) times the response to \(u_1\) plus \(\beta\) times the response to
      \(u_2\). Anything else — \(\sin x\), \(x^2\), \(x_1 x_2\), \(xu\), \(\|x\|x\) — is
      <strong>nonlinear</strong>, and the general form is just \(\dot x = f(x,u)\).</p>

      <p>Two quick tests. Products of states with each other or with the input are
      nonlinear. A constant term (\(\dot x = Ax + Bu + c\)) is <em>affine</em>, not linear,
      though it is usually made linear by shifting coordinates to the equilibrium.</p>

      <p>The distinction matters because linearity buys an enormous amount:</p>

      <ul>
        <li>Closed-form solutions, transfer functions, frequency response.</li>
        <li>Stability decided entirely by the eigenvalues of \(A\) — global, not local.</li>
        <li>Controllability and observability reduced to rank tests on a single matrix.</li>
        <li>Optimal control that solves in closed form (LQR) and convex MPC.</li>
      </ul>

      <p>None of that survives nonlinearity intact. Most real robots are nonlinear:
      rotations, gravity, friction, contact, and aerodynamics all break superposition.</p>

      <h2 id="affine">The control-affine middle ground</h2>

      <p>Fortunately, a huge fraction of robotic systems sit in a convenient middle class,
      <strong>control-affine</strong>:</p>

      $$\dot{x} = f(x) + g(x)\,u.$$

      <p>The state may enter as badly as it likes, but the input enters linearly. Here
      \(f(x)\) is the drift (what the system does with \(u = 0\)) and \(g(x)\) is the
      control-input matrix.</p>

      <div class="nb-eg">
        <div class="nb-eg-label">Example — pendulum</div>
        <p>With \(x_1 = \theta\), \(x_2 = \dot\theta\) and torque input \(u\):</p>
        $$\dot{x} =
          \begin{bmatrix} x_2 \\[2pt] -\dfrac{g}{\ell}\sin x_1 - \dfrac{b}{m\ell^2}x_2 \end{bmatrix}
          + \begin{bmatrix} 0 \\[2pt] \dfrac{1}{m\ell^2} \end{bmatrix} u.$$
        <p>Nonlinear because of \(\sin x_1\), but control-affine because \(u\) appears linearly.</p>
      </div>

      <div class="nb-key">
        <p>Control-affine structure is why so much of modern safe control works. Because
        \(\dot V\) and \(\dot h\) are affine in \(u\), conditions like a control Lyapunov
        function decrease condition or a control barrier function condition become
        <em>linear inequalities in \(u\)</em>. That turns controller synthesis into a
        quadratic program you can solve at every timestep.</p>
      </div>

      <h2 id="linearization">Linearization</h2>

      <p>Nonlinear systems are often well approximated by a linear one near an operating
      point \((x^\star, u^\star)\). Writing \(\delta x = x - x^\star\) and
      \(\delta u = u - u^\star\), a first-order Taylor expansion gives</p>

      $$\delta\dot{x} = A\,\delta x + B\,\delta u, \qquad
        A = \left.\frac{\partial f}{\partial x}\right|_{(x^\star,u^\star)}, \qquad
        B = \left.\frac{\partial f}{\partial u}\right|_{(x^\star,u^\star)}.$$

      <p>If \((x^\star, u^\star)\) is an equilibrium — \(f(x^\star,u^\star) = 0\) — then
      Lyapunov's indirect method applies: if every eigenvalue of \(A\) has strictly negative
      real part, the nonlinear system is locally asymptotically stable there. If any has
      strictly positive real part, it is unstable. Eigenvalues exactly on the imaginary axis
      tell you nothing and you have to go back to the nonlinear model.</p>

      <figure class="nb-fig">
        <svg viewBox="0 0 520 218" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A nonlinear function with its tangent line at an operating point">
          <rect x="188" y="24" width="86" height="152" fill="#eef4fc"/>
          <line x1="50" y1="176" x2="500" y2="176" stroke="#c8cfd8" stroke-width="1"/>
          <line x1="60" y1="24" x2="60" y2="176" stroke="#c8cfd8" stroke-width="1"/>
          <path d="M 70 162 Q 170 162 231 108 T 420 42" fill="none" stroke="#16181d" stroke-width="1.9"/>
          <line x1="150" y1="164" x2="350" y2="30" stroke="#0b5fc1" stroke-width="1.6" stroke-dasharray="5 3"/>
          <circle cx="231" cy="108" r="4" fill="#0b5fc1"/>
          <line x1="231" y1="108" x2="231" y2="176" stroke="#0b5fc1" stroke-width="1" stroke-dasharray="2 3"/>
          <text x="231" y="192" text-anchor="middle" font-size="12" fill="#0b5fc1">x*</text>
          <text x="352" y="112" font-size="12.5" fill="#16181d">f(x, u)</text>
          <text x="352" y="26" font-size="12.5" fill="#0b5fc1">A&#948;x + B&#948;u</text>
          <text x="231" y="212" text-anchor="middle" font-size="11" fill="#5b6572">the approximation is only honest inside the shaded band</text>
        </svg>
        <figcaption>Linearization is local. The band where it is trustworthy is a design assumption you should state and, ideally, enforce.</figcaption>
      </figure>

      <p>Linearizing around a trajectory rather than a point gives a time-varying linear
      system \(\delta\dot x = A(t)\,\delta x + B(t)\,\delta u\), which is the basis of
      trajectory-tracking LQR and of iLQR/DDP.</p>

      <h2 id="actuation">Fully actuated and underactuated systems</h2>

      <p>Count the independent inputs against the degrees of freedom. A system is
      <strong>fully actuated</strong> in a configuration \(q\) when the input can produce
      an arbitrary instantaneous acceleration \(\ddot q\) — for the manipulator form above,
      when \(\operatorname{rank} B(q) = k\). It is <strong>underactuated</strong> when the
      rank is lower: some accelerations are simply not commandable at that instant.</p>

      <figure class="nb-fig">
        <svg viewBox="0 0 520 212" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A two-link arm with two motors compared with a cart-pole with one force input">
          <line x1="260" y1="16" x2="260" y2="196" stroke="#e2e6ec" stroke-width="1"/>
          <g>
            <line x1="40" y1="164" x2="150" y2="164" stroke="#c8cfd8" stroke-width="2"/>
            <line x1="95" y1="164" x2="130" y2="98" stroke="#16181d" stroke-width="3.5" stroke-linecap="round"/>
            <line x1="130" y1="98" x2="200" y2="76" stroke="#16181d" stroke-width="3.5" stroke-linecap="round"/>
            <circle cx="95" cy="164" r="6" fill="#fff" stroke="#0b5fc1" stroke-width="2.2"/>
            <circle cx="130" cy="98" r="6" fill="#fff" stroke="#0b5fc1" stroke-width="2.2"/>
            <text x="76" y="152" font-size="12" fill="#0b5fc1">&#964;&#8321;</text>
            <text x="112" y="86" font-size="12" fill="#0b5fc1">&#964;&#8322;</text>
            <text x="120" y="192" text-anchor="middle" font-size="12" fill="#16181d">2 DOF, 2 inputs</text>
            <text x="120" y="207" text-anchor="middle" font-size="11.5" fill="#5b6572">fully actuated</text>
          </g>
          <g>
            <line x1="300" y1="164" x2="490" y2="164" stroke="#c8cfd8" stroke-width="2"/>
            <rect x="360" y="140" width="58" height="22" rx="3" fill="#fff" stroke="#16181d" stroke-width="2"/>
            <circle cx="373" cy="164" r="4.5" fill="#fff" stroke="#16181d" stroke-width="1.6"/>
            <circle cx="405" cy="164" r="4.5" fill="#fff" stroke="#16181d" stroke-width="1.6"/>
            <line x1="389" y1="140" x2="428" y2="70" stroke="#16181d" stroke-width="3" stroke-linecap="round"/>
            <circle cx="428" cy="70" r="7" fill="#16181d"/>
            <circle cx="389" cy="140" r="4" fill="#fff" stroke="#c8cfd8" stroke-width="2"/>
            <line x1="316" y1="151" x2="352" y2="151" stroke="#0b5fc1" stroke-width="2.2"/>
            <path d="M 352 151 l -7 -4 v 8 z" fill="#0b5fc1"/>
            <text x="330" y="140" font-size="12" fill="#0b5fc1">F</text>
            <text x="400" y="192" text-anchor="middle" font-size="12" fill="#16181d">2 DOF, 1 input</text>
            <text x="400" y="207" text-anchor="middle" font-size="11.5" fill="#5b6572">underactuated</text>
          </g>
        </svg>
        <figcaption>Left: every joint has its own motor. Right: the pole angle can only be influenced by moving the cart underneath it.</figcaption>
      </figure>

      <p>The consequences are large. For fully actuated systems you can cancel the dynamics
      outright — computed torque, \(u = B^{-1}(M\,\ddot q_{\text{des}} + C\dot q + G)\) — and
      reduce tracking to a linear problem. Underactuated systems give you no such option.
      You have to exploit the dynamics rather than override them, and desirable motions may
      be reachable only through a detour.</p>

      <p>Common underactuated systems: quadrotors (6 DOF, 4 inputs — to translate sideways
      a quadrotor must first tilt), cart-poles, Acrobots, legged robots during flight phases,
      fixed-wing aircraft, and any car with nonholonomic constraints.</p>

      <div class="nb-key">
        <p>Underactuation is not the same as nonholonomy. Underactuation is a shortage of
        inputs; nonholonomy is a constraint on velocities that cannot be integrated into a
        constraint on configurations. A unicycle has as many inputs as it needs to move, but
        it cannot slide sideways — that is nonholonomy.</p>
      </div>

      <h2 id="time-varying">Time-invariant and time-varying systems</h2>

      <p>A system is <strong>time-invariant</strong> when \(f\) has no explicit dependence on
      \(t\): shifting an experiment an hour later gives an identically shifted response.
      It is <strong>time-varying</strong> when it does, \(\dot x = f(x,u,t)\) — a rocket
      burning fuel, a manipulator with changing payload, a system linearized about a
      trajectory.</p>

      <p>For linear time-varying systems, eigenvalues of \(A(t)\) are <em>not</em> a stability
      test. Fixed at every frozen instant, \(A(t)\) can be Hurwitz for all \(t\) while the
      system diverges. You need the state transition matrix or a Lyapunov argument instead.</p>

      <h2 id="uncertainty">Modelling uncertainty</h2>

      <p>Everything above is the <strong>nominal</strong> model. Real systems differ from it,
      and how you write the difference determines what kind of guarantee you can get.</p>

      <h3>Bounded (set-based) uncertainty</h3>

      $$\dot{x} = f(x,u) + d, \qquad d \in \mathcal{D},\ \ \|d\| \le \bar{d}.$$

      <p>The disturbance is unknown but confined to a known set. This supports worst-case
      guarantees — robust control, tube MPC, input-to-state stability, robust CBFs — at the
      cost of conservatism, since you design against the worst member of \(\mathcal D\)
      whether or not it ever occurs.</p>

      <h3>Stochastic uncertainty</h3>

      $$dx = f(x,u)\,dt + \sigma(x,u)\,dW_t.$$

      <p>The disturbance is a random process with known statistics. Guarantees become
      probabilistic: expected cost, chance constraints \(\Pr[x \in \mathcal{X}] \ge 1-\epsilon\),
      covariance bounds. Less conservative, but a stochastic guarantee is not a worst-case one.</p>

      <h3>Parametric and structural uncertainty</h3>

      <p>\(\dot x = f(x,u;\theta)\) with \(\theta\) unknown but constant — masses, inertias,
      friction coefficients, the tire-road friction \(\mu\). This is what adaptive control and
      system identification address. Distinguish it from <em>unmodelled dynamics</em>:
      structure you left out entirely (actuator lag, flexible modes), which no amount of
      parameter fitting will recover.</p>

      <h3>Matched vs unmatched</h3>

      <p>A disturbance is <strong>matched</strong> if it enters through the same channel as
      the input, \(\dot x = f(x) + g(x)(u + d)\). Matched disturbances can in principle be
      cancelled by the controller. <strong>Unmatched</strong> disturbances act in directions
      the input cannot reach and are strictly harder.</p>

      <figure class="nb-fig">
        <svg viewBox="0 0 520 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A nominal trajectory surrounded by a tube of possible trajectories">
          <path d="M 60 126 C 170 126 220 40 460 34 L 460 78 C 220 84 170 170 60 170 Z" fill="#eef4fc"/>
          <path d="M 60 148 C 170 148 220 62 460 56" fill="none" stroke="#0b5fc1" stroke-width="2"/>
          <path d="M 60 148 C 168 142 216 84 460 48" fill="none" stroke="#5b6572" stroke-width="1" stroke-dasharray="3 3"/>
          <path d="M 60 148 C 174 154 224 92 460 66" fill="none" stroke="#5b6572" stroke-width="1" stroke-dasharray="3 3"/>
          <circle cx="60" cy="148" r="4" fill="#0b5fc1"/>
          <text x="300" y="118" font-size="12.5" fill="#0b5fc1">nominal prediction</text>
          <text x="300" y="30" font-size="12.5" fill="#5b6572">reachable set under &#8214;d&#8214; &#8804; d&#772;</text>
          <text x="46" y="182" font-size="11.5" fill="#5b6572">x(0)</text>
        </svg>
        <figcaption>Under bounded disturbance the prediction is a set, not a curve. Robust design keeps the whole set out of trouble.</figcaption>
      </figure>

      <h2 id="outputs">Outputs and estimation</h2>

      <p>You rarely measure the full state. The measurement model is</p>

      $$y = h(x,u) + \nu, \qquad \text{or linearly} \qquad y = Cx + Du + \nu,$$

      <p>with \(\nu\) sensor noise. A GPS gives position but not velocity; an encoder gives
      joint angle but not joint rate; a camera gives pixels.</p>

      <p><strong>Observability</strong> asks whether \(x(0)\) can be reconstructed from
      \(y(\cdot)\) and \(u(\cdot)\) over a finite window. For LTI systems it is the rank
      condition</p>

      $$\operatorname{rank} \begin{bmatrix} C \\ CA \\ \vdots \\ CA^{n-1}\end{bmatrix} = n,$$

      <p>the dual of controllability. If a system is observable you can build an observer —
      a Luenberger observer, a Kalman filter, a moving-horizon estimator — and feed its
      estimate \(\hat x\) to a controller designed as if the state were measured. For LTI
      systems the <em>separation principle</em> says designing the controller and observer
      independently still yields a stable closed loop; for nonlinear systems it generally
      does not, and the coupling has to be handled explicitly.</p>

      <h2 id="summary">Classifying a model</h2>

      <p>Every model can be placed against the same checklist, and the placement is what
      tells you which controllers are candidates.</p>

      <div class="nb-table-wrap">
      <table>
        <thead>
          <tr><th>Question</th><th>If yes</th><th>If no</th></tr>
        </thead>
        <tbody>
          <tr>
            <td>Is it \(\dot x = Ax+Bu\)?</td>
            <td>Pole placement, LQR, \(H_\infty\), convex MPC, frequency-domain design</td>
            <td>Go to the next rows</td>
          </tr>
          <tr>
            <td>Is it control-affine?</td>
            <td>Feedback linearization, CLF-QP, CBF safety filters, sliding mode</td>
            <td>Nonlinear MPC, sampling-based, learned policies</td>
          </tr>
          <tr>
            <td>Is it fully actuated?</td>
            <td>Computed torque, inverse dynamics, task-space control</td>
            <td>Trajectory optimization, partial feedback linearization, differential flatness</td>
          </tr>
          <tr>
            <td>Is it time-invariant?</td>
            <td>Static feedback gains; analyse with eigenvalues</td>
            <td>Gain scheduling, time-varying LQR; eigenvalue tests are invalid</td>
          </tr>
          <tr>
            <td>Is the disturbance bounded?</td>
            <td>Robust control, tube MPC, ISS, robust CBFs</td>
            <td>Stochastic MPC, chance constraints, LQG</td>
          </tr>
          <tr>
            <td>Is the full state measured?</td>
            <td>Design the feedback law directly</td>
            <td>Add an observer; check the coupling if nonlinear</td>
          </tr>
        </tbody>
      </table>
      </div>

      <div class="nb-key">
        <p>The single most common modelling mistake is over-fidelity: writing down every
        effect you can think of, then discovering the model is too heavy to control with and
        too poorly identified to trust. Start with the coarsest model that captures the
        behaviour you care about, and add terms only when a specific failure demands them.</p>
      </div>
"""


# --------------------------------------------------------------------------
# Page 2 — Common dynamic models
# --------------------------------------------------------------------------

TOC_MODELS = [
    ("single-integrator", "Single integrator"),
    ("double-integrator", "Double integrator"),
    ("unicycle", "Unicycle"),
    ("diff-drive", "Differential drive"),
    ("bicycle", "Bicycle models"),
    ("pendulum", "Pendulum and cart-pole"),
    ("quadrotor", "Quadrotor"),
    ("discrete", "Discrete-time versions"),
    ("compare", "Side by side"),
]

BODY_MODELS = r"""      <p>A small library of models covers most of robotics. They are worth knowing by heart,
      not because any of them is exactly right, but because choosing among them is the first
      real design decision in a project: the model fixes what your controller can reason
      about and how expensive that reasoning will be.</p>

      <p>Every model below is written in the continuous-time form \(\dot x = f(x,u)\), with the
      state dimension, input dimension, and classification stated alongside.</p>

      <h2 id="single-integrator">Single integrator</h2>

      <p>The simplest useful model. You command velocity directly.</p>

      $$x = \begin{bmatrix} p_x \\ p_y \end{bmatrix} \in \mathbb{R}^2, \qquad
        u = \begin{bmatrix} u_x \\ u_y \end{bmatrix} \in \mathbb{R}^2, \qquad
        \dot{x} = u.$$

      <p>Linear, fully actuated, and about as easy as control gets: \(A = 0\), \(B = I\).
      It is the workhorse of multi-agent coordination, because consensus, formation, and
      coverage results are cleanest here and the graph structure — not the dynamics — is the
      interesting part.</p>

      <p>The catch is that no physical robot is a single integrator. Velocity commands are
      tracked by a lower-level loop with finite bandwidth, so results proven for integrators
      transfer only if that inner loop is much faster than the outer one.</p>

      <h2 id="double-integrator">Double integrator</h2>

      <p>One step up: you command acceleration, and velocity becomes a state.</p>

      $$x = \begin{bmatrix} p \\ v \end{bmatrix} \in \mathbb{R}^{2d}, \qquad
        u = a \in \mathbb{R}^{d}, \qquad
        \dot{x} = \begin{bmatrix} 0 & I \\ 0 & 0 \end{bmatrix} x
                + \begin{bmatrix} 0 \\ I \end{bmatrix} u.$$

      <p>Still linear and still fully actuated, but now the robot has momentum, which is what
      makes collision avoidance and braking distance meaningful. It is Newton's second law with
      unit mass, and it is the right minimal model whenever inertia matters and orientation
      does not.</p>

      <div class="nb-key">
        <p>The jump from single to double integrator is the jump from "where do I want to be"
        to "can I stop in time". Safety constraints that are trivially enforceable on a single
        integrator become relative-degree-two problems on a double integrator.</p>
      </div>

      <h2 id="unicycle">Unicycle</h2>

      <p>The standard model for a wheeled robot that drives forward along its heading and
      turns, but cannot slide sideways.</p>

      $$x = \begin{bmatrix} p_x \\ p_y \\ \psi \end{bmatrix} \in \mathbb{R}^3, \qquad
        u = \begin{bmatrix} v \\ \omega \end{bmatrix} \in \mathbb{R}^2, \qquad
        \dot{x} = \begin{bmatrix} v\cos\psi \\ v\sin\psi \\ \omega \end{bmatrix}.$$

      <figure class="nb-fig">
        <svg viewBox="0 0 520 208" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Unicycle robot showing position, heading angle and forward velocity">
          <line x1="55" y1="172" x2="470" y2="172" stroke="#c8cfd8" stroke-width="1"/>
          <line x1="70" y1="24" x2="70" y2="172" stroke="#c8cfd8" stroke-width="1"/>
          <text x="470" y="190" font-size="12" fill="#5b6572">x</text>
          <text x="56" y="24" font-size="12" fill="#5b6572">y</text>
          <line x1="250" y1="104" x2="250" y2="172" stroke="#c8cfd8" stroke-width="1" stroke-dasharray="3 3"/>
          <line x1="70" y1="104" x2="250" y2="104" stroke="#c8cfd8" stroke-width="1" stroke-dasharray="3 3"/>
          <text x="243" y="190" font-size="12" fill="#5b6572">p</text><text x="250" y="194" font-size="9" fill="#5b6572">x</text>
          <text x="44" y="108" font-size="12" fill="#5b6572">p</text><text x="51" y="112" font-size="9" fill="#5b6572">y</text>
          <line x1="250" y1="104" x2="330" y2="104" stroke="#c8cfd8" stroke-width="1" stroke-dasharray="3 3"/>
          <path d="M 288 104 A 38 38 0 0 0 282.9 84.3" fill="none" stroke="#5b6572" stroke-width="1.2"/>
          <text x="298" y="94" font-size="12.5" fill="#5b6572">&#968;</text>
          <line x1="250" y1="104" x2="331" y2="57" stroke="#0b5fc1" stroke-width="2.2"/>
          <path d="M 331 57 l -10.4 0.6 l 4.4 7.6 z" fill="#0b5fc1"/>
          <text x="340" y="52" font-size="12.5" fill="#0b5fc1">v</text>
          <circle cx="250" cy="104" r="9" fill="#fff" stroke="#16181d" stroke-width="2.2"/>
          <path d="M 234.4 113 A 18 18 0 0 0 234.4 95" fill="none" stroke="#0b5fc1" stroke-width="1.6"/>
          <path d="M 234.4 95 l -1.6 7.6 l 7 -3.6 z" fill="#0b5fc1"/>
          <text x="212" y="94" font-size="12.5" fill="#0b5fc1">&#969;</text>
        </svg>
        <figcaption>Three states, two inputs. The robot can go forward and turn, but the sideways direction is unreachable at any instant.</figcaption>
      </figure>

      <p>Nonlinear because of \(\cos\psi\) and \(\sin\psi\), and control-affine:</p>

      $$\dot{x} = \underbrace{\begin{bmatrix} 0 \\ 0 \\ 0 \end{bmatrix}}_{f(x)}
        + \underbrace{\begin{bmatrix} \cos\psi & 0 \\ \sin\psi & 0 \\ 0 & 1 \end{bmatrix}}_{g(x)}
          \begin{bmatrix} v \\ \omega \end{bmatrix}.$$

      <p>Two inputs for three states makes it underactuated, and the inability to move
      sideways is a nonholonomic constraint, \(\dot p_x \sin\psi - \dot p_y \cos\psi = 0\).
      Brockett's condition shows there is no smooth time-invariant feedback that stabilises
      the unicycle to a point — parallel parking is genuinely hard, and the standard fixes are
      time-varying or discontinuous laws, or the trick below.</p>

      <div class="nb-eg">
        <div class="nb-eg-label">Near-identity diffeomorphism</div>
        <p>Control a point a distance \(\ell &gt; 0\) ahead of the wheel axis instead of the
        axis itself. That point obeys single-integrator dynamics, and the required unicycle
        inputs come from</p>
        $$\begin{bmatrix} v \\ \omega \end{bmatrix} =
          \begin{bmatrix} \cos\psi & \sin\psi \\ -\tfrac{1}{\ell}\sin\psi & \tfrac{1}{\ell}\cos\psi \end{bmatrix}
          \begin{bmatrix} \dot p_x^{\text{des}} \\ \dot p_y^{\text{des}} \end{bmatrix}.$$
        <p>This is how single-integrator multi-robot results get run on real differential-drive
        hardware. The cost is that you control the offset point, not the robot, and orientation
        is left to take care of itself.</p>
      </div>

      <h2 id="diff-drive">Differential drive</h2>

      <p>The same robot, with the inputs written as what the motors actually receive. For
      wheel radius \(r\) and axle length \(L\), with wheel speeds \(\omega_R, \omega_L\),</p>

      $$v = \frac{r(\omega_R + \omega_L)}{2}, \qquad \omega = \frac{r(\omega_R - \omega_L)}{L}.$$

      <p>The dynamics are the unicycle's; only the input parametrisation changed. This matters
      for constraints: a box constraint on wheel speeds, \(|\omega_R| \le \bar\omega\) and
      \(|\omega_L| \le \bar\omega\), is a diamond in \((v,\omega)\) space, not a box. Saturating
      \(v\) and \(\omega\) separately can command wheel speeds the motors cannot deliver.</p>

      <h2 id="bicycle">Kinematic and dynamic bicycle</h2>

      <p>Cars steer rather than turn in place, so the unicycle is the wrong model. The
      <strong>kinematic bicycle</strong> lumps each axle into a single wheel:</p>

      $$x = \begin{bmatrix} p_x \\ p_y \\ \psi \\ v\end{bmatrix}, \qquad
        u = \begin{bmatrix} a \\ \delta \end{bmatrix}, \qquad
        \dot{x} = \begin{bmatrix} v\cos\psi \\ v\sin\psi \\ \dfrac{v}{L}\tan\delta \\ a \end{bmatrix},$$

      <p>where \(\delta\) is the steering angle and \(L\) the wheelbase. The turn rate now
      depends on speed, and the steering limit \(|\delta| \le \delta_{\max}\) enforces a
      minimum turning radius \(R_{\min} = L/\tan\delta_{\max}\).</p>

      <figure class="nb-fig">
        <svg viewBox="0 0 520 160" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Kinematic bicycle model showing wheelbase and steering angle">
          <line x1="150" y1="98" x2="370" y2="98" stroke="#16181d" stroke-width="2.4"/>
          <rect x="135" y="89" width="30" height="9" rx="2.5" fill="#16181d"/>
          <g transform="rotate(-27 370 98)">
            <rect x="355" y="89" width="30" height="9" rx="2.5" fill="#0b5fc1"/>
          </g>
          <circle cx="150" cy="98" r="3.8" fill="#fff" stroke="#16181d" stroke-width="1.6"/>
          <circle cx="370" cy="98" r="3.8" fill="#fff" stroke="#16181d" stroke-width="1.6"/>
          <line x1="370" y1="98" x2="452" y2="98" stroke="#c8cfd8" stroke-width="1" stroke-dasharray="3 3"/>
          <line x1="370" y1="98" x2="443" y2="61" stroke="#0b5fc1" stroke-width="1.2" stroke-dasharray="3 3"/>
          <path d="M 412 98 A 42 42 0 0 0 407.4 78.9" fill="none" stroke="#0b5fc1" stroke-width="1.2"/>
          <text x="419" y="86" font-size="12.5" fill="#0b5fc1">&#948;</text>
          <g stroke="#5b6572" stroke-width="1">
            <line x1="150" y1="128" x2="370" y2="128"/>
            <line x1="150" y1="124" x2="150" y2="132"/>
            <line x1="370" y1="124" x2="370" y2="132"/>
          </g>
          <text x="260" y="145" text-anchor="middle" font-size="12.5" fill="#5b6572">L</text>
          <line x1="150" y1="86" x2="150" y2="56" stroke="#c8cfd8" stroke-width="1" stroke-dasharray="3 3"/>
          <text x="150" y="46" text-anchor="middle" font-size="12" fill="#5b6572">rear axle</text>
          <text x="370" y="46" text-anchor="middle" font-size="12" fill="#0b5fc1">steered front wheel</text>
        </svg>
        <figcaption>The kinematic bicycle assumes the wheels roll without slipping — a good assumption at parking-lot speeds and a bad one on a racetrack.</figcaption>
      </figure>

      <p>That no-slip assumption is exactly what fails at speed. The <strong>dynamic
      bicycle</strong> replaces it with body-frame velocities and tire forces: the state grows
      to include longitudinal and lateral velocity \(v_x, v_y\) and yaw rate \(r\), slip angles
      are computed at each axle,</p>

      $$\alpha_f = \delta - \arctan\!\left(\frac{v_y + \ell_f r}{v_x}\right), \qquad
        \alpha_r = -\arctan\!\left(\frac{v_y - \ell_r r}{v_x}\right),$$

      <p>and lateral forces follow a tire model — linear \(F_y = -C_\alpha \alpha\) for modest
      slip, or a Pacejka-style saturating curve near the friction limit. The planar dynamics
      are then</p>

      $$m(\dot v_x - v_y r) = F_{x}, \qquad
        m(\dot v_y + v_x r) = F_{y,f}\cos\delta + F_{y,r}, \qquad
        I_z \dot{r} = \ell_f F_{y,f}\cos\delta - \ell_r F_{y,r}.$$

      <p>Two practical warnings: the model is singular at \(v_x = 0\) because slip angles divide
      by speed, so implementations blend to the kinematic model at low speed; and the friction
      coefficient \(\mu\) is rarely known, which makes it a natural place for adaptive or robust
      methods.</p>

      <h2 id="pendulum">Pendulum, cart-pole, and friends</h2>

      <p>The canonical underactuated benchmarks. The <strong>pendulum</strong> with torque input:</p>

      $$m\ell^2\ddot\theta = u - b\dot\theta - mg\ell\sin\theta.$$

      <p>Nonlinear, control-affine, one DOF and one input — fully actuated, and interesting only
      because of the \(\sin\theta\) and torque limits: if \(|u| &lt; mg\ell\) the pendulum cannot
      be lifted directly and must be swung up, which is already a nontrivial nonlinear problem.</p>

      <p>The <strong>cart-pole</strong> has configuration \(q = (p, \theta)\) and a single
      horizontal force on the cart. It is the standard example of underactuation: the pole angle
      has no actuator of its own and is steered only through cart acceleration. The
      <strong>Acrobot</strong> and <strong>Pendubot</strong> are the two-link versions with one
      motor, and legged robots in flight phase share the same structure.</p>

      <h2 id="quadrotor">Quadrotor</h2>

      <p>A rigid body with four rotors. State: position \(p \in \mathbb{R}^3\), velocity
      \(v \in \mathbb{R}^3\), attitude \(R \in SO(3)\), body angular velocity
      \(\Omega \in \mathbb{R}^3\). Inputs: total thrust \(F \in \mathbb{R}\) and body moment
      \(M \in \mathbb{R}^3\).</p>

      $$\dot p = v, \qquad
        m\dot v = mg e_3 - F R e_3, \qquad
        \dot R = R\hat\Omega, \qquad
        J\dot\Omega + \Omega \times J\Omega = M,$$

      <p>where \(\hat\Omega\) is the skew-symmetric matrix with \(\hat\Omega a = \Omega \times a\)
      and \(e_3\) is the vertical unit vector.</p>

      <figure class="nb-fig">
        <svg viewBox="0 0 520 186" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A tilted quadrotor showing thrust along the body axis decomposed into vertical and horizontal components">
          <g transform="rotate(-22 260 110)">
            <line x1="196" y1="110" x2="324" y2="110" stroke="#16181d" stroke-width="3"/>
            <ellipse cx="196" cy="110" rx="20" ry="4.5" fill="none" stroke="#16181d" stroke-width="2"/>
            <ellipse cx="324" cy="110" rx="20" ry="4.5" fill="none" stroke="#16181d" stroke-width="2"/>
          </g>
          <line x1="260" y1="110" x2="222" y2="26" stroke="#0b5fc1" stroke-width="2.4"/>
          <path d="M 222 26 l 1.4 10.3 l 7.6 -4.4 z" fill="#0b5fc1"/>
          <text x="206" y="52" text-anchor="end" font-size="12.5" fill="#0b5fc1">F R e&#8323;</text>
          <line x1="260" y1="110" x2="260" y2="26" stroke="#5b6572" stroke-width="1.2" stroke-dasharray="4 3"/>
          <line x1="260" y1="26" x2="222" y2="26" stroke="#5b6572" stroke-width="1.2" stroke-dasharray="4 3"/>
          <text x="268" y="72" font-size="11.5" fill="#5b6572">holds it up</text>
          <text x="241" y="16" text-anchor="middle" font-size="11.5" fill="#5b6572">moves it sideways</text>
          <line x1="260" y1="110" x2="260" y2="164" stroke="#5b6572" stroke-width="2"/>
          <path d="M 260 164 l -4.4 -7.6 l 8.8 0 z" fill="#5b6572"/>
          <text x="268" y="152" font-size="12.5" fill="#5b6572">mg</text>
          <circle cx="260" cy="110" r="3.4" fill="#16181d"/>
        </svg>
        <figcaption>Thrust only ever points along the body axis. Horizontal motion has to be bought with attitude, which is what makes the quadrotor underactuated.</figcaption>
      </figure>

      <p>Six configuration degrees of freedom against four inputs. The rotational subsystem is
      fully actuated and fast; the translational subsystem is underactuated and slow, which is
      why almost every quadrotor stack is a cascade: an outer position loop picks a desired
      thrust vector, that vector defines a desired attitude, and an inner attitude loop tracks
      it at high rate.</p>

      <p>Two modelling choices worth flagging. Parametrising attitude with Euler angles is
      convenient but introduces gimbal singularities; working directly on \(SO(3)\) with
      rotation matrices, or with quaternions, avoids them at the cost of a slightly less
      familiar controller. And quadrotor dynamics are <em>differentially flat</em> in
      \((p_x, p_y, p_z, \psi)\) — every state and input can be written in terms of those four
      outputs and their derivatives — which is what makes minimum-snap trajectory generation
      so effective.</p>

      <h2 id="discrete">Discrete-time versions</h2>

      <p>Any of these becomes a discrete-time model once you fix a sample time. For the linear
      ones, use exact discretisation; the double integrator with sample time \(\Delta t\) is</p>

      $$x_{k+1} = \begin{bmatrix} I & \Delta t\, I \\ 0 & I \end{bmatrix} x_k
                + \begin{bmatrix} \tfrac{1}{2}\Delta t^2 I \\ \Delta t\, I \end{bmatrix} u_k,$$

      <p>which is exact under a zero-order hold, not an approximation. For the nonlinear ones,
      RK4 is the usual choice inside an MPC prediction model; Euler is acceptable for the
      unicycle at 50 Hz or faster but noticeably degrades the bicycle model during hard
      cornering.</p>

      <p>If you add process noise, the stochastic discrete-time form is
      \(x_{k+1} = F(x_k,u_k) + w_k\) with \(w_k\) zero-mean and covariance \(Q\) — the model an
      EKF or a particle filter expects.</p>

      <h2 id="compare">Side by side</h2>

      <div class="nb-table-wrap">
      <table>
        <thead>
          <tr><th>Model</th><th>\(n\)</th><th>\(m\)</th><th>Linear</th><th>Actuation</th><th>Typical use</th></tr>
        </thead>
        <tbody>
          <tr><td>Single integrator</td><td>2&ndash;3</td><td>2&ndash;3</td><td>yes</td><td>full</td><td>Multi-agent coordination, coverage, consensus</td></tr>
          <tr><td>Double integrator</td><td>4&ndash;6</td><td>2&ndash;3</td><td>yes</td><td>full</td><td>Collision avoidance, trajectory planning with inertia</td></tr>
          <tr><td>Unicycle</td><td>3</td><td>2</td><td>no</td><td>under</td><td>Ground robots, differential-drive platforms</td></tr>
          <tr><td>Kinematic bicycle</td><td>4</td><td>2</td><td>no</td><td>under</td><td>Low-speed autonomous driving, parking</td></tr>
          <tr><td>Dynamic bicycle</td><td>6&ndash;7</td><td>2&ndash;3</td><td>no</td><td>under</td><td>High-speed driving, racing, stability control</td></tr>
          <tr><td>Cart-pole</td><td>4</td><td>1</td><td>no</td><td>under</td><td>Benchmark for underactuated control</td></tr>
          <tr><td>Quadrotor</td><td>12&ndash;13</td><td>4</td><td>no</td><td>under</td><td>Aerial robotics, aggressive flight</td></tr>
          <tr><td>Manipulator</td><td>2k</td><td>k</td><td>no</td><td>full</td><td>Arms, computed torque, task-space control</td></tr>
        </tbody>
      </table>
      </div>

      <div class="nb-key">
        <p>Pick the simplest model whose failure mode you cannot tolerate. A single integrator
        is enough to study a formation; it is not enough to promise that two robots will not
        collide at speed. Most projects use more than one — a coarse model for planning, a
        finer one for tracking, and a finer one still for simulation.</p>
      </div>
"""


# --------------------------------------------------------------------------
# Page 3 — Control law design
# --------------------------------------------------------------------------

TOC_CONTROL = [
    ("what", "What a control law is"),
    ("pid", "PID"),
    ("state-feedback", "State feedback"),
    ("lqr", "LQR and LQG"),
    ("feedback-lin", "Feedback linearization"),
    ("lyapunov", "Lyapunov and CLF-QP"),
    ("cbf", "Safety filters"),
    ("mpc", "Model predictive control"),
    ("uncertain", "Control under uncertainty"),
    ("choosing", "Choosing a controller"),
]

BODY_CONTROL = r"""      <p>A control law is a rule that turns what you know into what you command. Everything
      else — stability proofs, tuning, constraint handling — is about which rule to pick and
      what you can promise about it.</p>

      <h2 id="what">What a control law is</h2>

      <p>In the general case a feedback law is a map</p>

      $$u = \pi(x, t), \qquad \text{or with a reference} \qquad u = \pi(x, x_d, t).$$

      <p><strong>Open-loop</strong> control computes \(u(t)\) ahead of time from the model
      alone. It is fine when the model is exact and nothing disturbs the system, which is to
      say never. <strong>Feedback</strong> measures the state and reacts, which is what buys
      robustness to model error and disturbance. In practice most controllers combine the
      two: a feedforward term from a planned trajectory, plus feedback on the tracking error.</p>

      <figure class="nb-fig">
        <svg viewBox="0 0 520 182" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Block diagram of a feedback control loop with disturbance and measurement">
          <line x1="30" y1="72" x2="80" y2="72" stroke="#16181d" stroke-width="1.6"/>
          <path d="M 80 72 l -8 -4 v 8 z" fill="#16181d"/>
          <text x="26" y="56" font-size="11.5" fill="#5b6572">reference</text>
          <circle cx="94" cy="72" r="13" fill="#fff" stroke="#16181d" stroke-width="1.6"/>
          <text x="94" y="77" text-anchor="middle" font-size="13" fill="#16181d">&#8722;</text>
          <line x1="107" y1="72" x2="150" y2="72" stroke="#16181d" stroke-width="1.6"/>
          <path d="M 150 72 l -8 -4 v 8 z" fill="#16181d"/>
          <text x="118" y="62" font-size="12" fill="#5b6572">e</text>
          <rect x="152" y="50" width="104" height="44" rx="4" fill="#eef4fc" stroke="#0b5fc1" stroke-width="1.4"/>
          <text x="204" y="70" text-anchor="middle" font-size="12.5" fill="#0b5fc1">controller</text>
          <text x="204" y="85" text-anchor="middle" font-size="11.5" fill="#0b5fc1">u = &#960;(x)</text>
          <line x1="256" y1="72" x2="308" y2="72" stroke="#16181d" stroke-width="1.6"/>
          <path d="M 308 72 l -8 -4 v 8 z" fill="#16181d"/>
          <text x="276" y="62" font-size="12" fill="#5b6572">u</text>
          <rect x="310" y="50" width="104" height="44" rx="4" fill="#fff" stroke="#16181d" stroke-width="1.6"/>
          <text x="362" y="70" text-anchor="middle" font-size="12.5" fill="#16181d">system</text>
          <text x="362" y="85" text-anchor="middle" font-size="11.5" fill="#16181d">x&#775; = f(x,u,d)</text>
          <line x1="362" y1="18" x2="362" y2="48" stroke="#5b6572" stroke-width="1.4" stroke-dasharray="4 3"/>
          <path d="M 362 48 l -4 -8 h 8 z" fill="#5b6572"/>
          <text x="370" y="26" font-size="12" fill="#5b6572">d</text>
          <line x1="414" y1="72" x2="492" y2="72" stroke="#16181d" stroke-width="1.6"/>
          <path d="M 492 72 l -8 -4 v 8 z" fill="#16181d"/>
          <text x="470" y="62" font-size="12" fill="#16181d">x</text>
          <line x1="452" y1="72" x2="452" y2="140" stroke="#16181d" stroke-width="1.4"/>
          <line x1="452" y1="140" x2="94" y2="140" stroke="#16181d" stroke-width="1.4"/>
          <line x1="94" y1="140" x2="94" y2="85" stroke="#16181d" stroke-width="1.4"/>
          <path d="M 94 85 l -4 8 h 8 z" fill="#16181d"/>
          <text x="240" y="158" text-anchor="middle" font-size="11.5" fill="#5b6572">measurement (or estimate x&#770; from an observer)</text>
        </svg>
        <figcaption>The loop that every controller on this page fits into. What changes is the box in the middle and what you can prove about it.</figcaption>
      </figure>

      <p>Design specifications usually fall into four groups, and they compete:</p>

      <ul>
        <li><strong>Stability.</strong> Does the error go to zero, and from how far away?
        Local, regional, or global; asymptotic or exponential.</li>
        <li><strong>Performance.</strong> Settling time, overshoot, tracking error, energy.</li>
        <li><strong>Constraints.</strong> Input saturation \(u \in \mathcal{U}\), state and
        safety constraints \(x \in \mathcal{X}\).</li>
        <li><strong>Robustness.</strong> How much model error and disturbance can the loop
        absorb before any of the above stops holding?</li>
      </ul>

      <h2 id="pid">PID</h2>

      <p>The model-free baseline. On a scalar error \(e = x_d - x\),</p>

      $$u = k_p e + k_i \int_0^t e(\tau)\,d\tau + k_d \dot{e}.$$

      <p>Proportional acts on present error, integral removes steady-state offset caused by
      constant disturbances or bias, derivative adds damping. It needs no model, which is its
      whole appeal, and it remains the right answer for well-behaved single-input loops:
      motor speed, altitude hold, heading hold.</p>

      <p>Its limits are equally clear. It does not know about constraints, it handles coupled
      multi-input systems only by tuning loops one at a time and hoping they do not interact,
      and it has no notion of prediction. Two implementation details that cause most real
      problems: integrator windup during saturation (fix with clamping or back-calculation),
      and derivative kick on step references (differentiate the measurement, not the error,
      and filter it).</p>

      <div class="nb-key">
        <p>A cascade of PID loops — fast inner loop on rate, slower outer loop on position —
        is still the most widely deployed architecture in robotics. Model-based methods
        usually replace the outer loop first.</p>
      </div>

      <h2 id="state-feedback">State feedback and pole placement</h2>

      <p>For \(\dot x = Ax + Bu\), the natural law is linear state feedback \(u = -Kx\), giving
      closed-loop dynamics \(\dot x = (A - BK)x\). Stability is now entirely a question of
      where the eigenvalues of \(A - BK\) sit.</p>

      <p>You can place them anywhere you like precisely when the pair \((A,B)\) is
      <strong>controllable</strong>:</p>

      $$\operatorname{rank}\begin{bmatrix} B & AB & A^2B & \cdots & A^{n-1}B \end{bmatrix} = n.$$

      <p>Controllability is a yes/no property of the model, and a failure of it is a modelling
      or hardware problem, not a tuning problem — no controller will recover a direction the
      input genuinely cannot reach.</p>

      <p>Pole placement is direct but unforgiving: fast poles demand large gains, large gains
      demand large inputs and amplify sensor noise, and the map from pole locations to
      behaviour is not intuitive above second order. Which is the argument for letting an
      optimisation choose the gains instead.</p>

      <h2 id="lqr">LQR and LQG</h2>

      <p>Rather than placing poles, penalise what you care about. The infinite-horizon
      linear quadratic regulator minimises</p>

      $$J = \int_0^\infty \left( x^\top Q x + u^\top R u \right) dt, \qquad Q \succeq 0,\ R \succ 0,$$

      <p>and the optimal law is static state feedback \(u = -Kx\) with \(K = R^{-1}B^\top P\),
      where \(P\) solves the algebraic Riccati equation</p>

      $$A^\top P + PA - PBR^{-1}B^\top P + Q = 0.$$

      <p>The discrete-time version is the same idea with a discrete Riccati equation, and is
      what you actually implement. Tuning moves from abstract pole locations to interpretable
      weights: \(Q\) says which state errors hurt, \(R\) says how expensive control is. LQR is
      also robust by construction in the single-input case — at least 60&deg; of phase margin
      and infinite gain margin.</p>

      <p>With noisy partial measurements, combine LQR with a Kalman filter and you get
      <strong>LQG</strong>. For linear systems the <em>separation principle</em> guarantees the
      combination is stable even though each half was designed alone. Worth knowing:
      LQG has no guaranteed robustness margins — the LQR margins do not survive the observer,
      which is what motivated loop transfer recovery and later \(H_\infty\) design.</p>

      <p>Two extensions used constantly in robotics: <strong>finite-horizon time-varying LQR</strong>
      for tracking a trajectory (linearize along it, solve the Riccati equation backwards), and
      <strong>iLQR/DDP</strong>, which iterates that process on the true nonlinear dynamics.</p>

      <h2 id="feedback-lin">Feedback linearization and computed torque</h2>

      <p>For a control-affine system \(\dot x = f(x) + g(x)u\), if \(g\) is invertible you can
      choose the input to cancel the nonlinearity outright:</p>

      $$u = g(x)^{-1}\big(v - f(x)\big) \quad \Longrightarrow \quad \dot{x} = v,$$

      <p>leaving a linear system in the new input \(v\), which you then close with LQR or PD.
      For manipulators this is <strong>computed torque</strong>:</p>

      $$u = M(q)\big(\ddot q_d - K_d \dot{e} - K_p e\big) + C(q,\dot q)\dot q + G(q),$$

      <p>which reduces tracking to \(\ddot e + K_d \dot e + K_p e = 0\) — a linear, decoupled
      error system.</p>

      <p>Three caveats. It requires full actuation, or at least an invertible input map, so it
      does not apply to quadrotors or cars in this form (partial feedback linearization does).
      It cancels the model, so it inherits every model error directly. And when the system has
      internal dynamics that are not linearized away, those <em>zero dynamics</em> must be
      stable on their own — cancelling what you can see is no help if what you cannot see
      diverges.</p>

      <h2 id="lyapunov">Lyapunov design and CLF-QP</h2>

      <p>The general nonlinear tool. Find a scalar \(V(x) &gt; 0\) that vanishes only at the
      target, then choose \(u\) to make it decrease. For a control-affine system,</p>

      $$\dot{V}(x,u) = \underbrace{\nabla V(x)^\top f(x)}_{L_f V(x)} + \underbrace{\nabla V(x)^\top g(x)}_{L_g V(x)} u,$$

      <p>which is <em>affine in \(u\)</em>. \(V\) is a <strong>control Lyapunov function</strong>
      if some admissible \(u\) can always make \(\dot V\) sufficiently negative, and the
      requirement</p>

      $$L_f V(x) + L_g V(x)\,u \le -\gamma\big(V(x)\big)$$

      <p>is a single linear inequality in \(u\). So you can ask for the smallest input that
      satisfies it,</p>

      $$u^\star = \arg\min_{u \in \mathcal{U}} \ \|u - u_{\text{nom}}\|^2
        \quad \text{s.t.} \quad L_f V + L_g V\,u \le -\gamma(V),$$

      <p>a quadratic program solvable in microseconds. This is the CLF-QP, and it is the
      template for the safety machinery below. Finding \(V\) is the hard part; for mechanical
      systems total energy is often a good first guess, and sum-of-squares programming can
      search for one systematically.</p>

      <h2 id="cbf">Safety filters and control barrier functions</h2>

      <p>Stability and safety are different requirements. Safety is <strong>forward invariance</strong>
      of a set: if you start inside \(\mathcal{C} = \{x : h(x) \ge 0\}\), you never leave it.
      A <strong>control barrier function</strong> enforces this with the condition</p>

      $$\underbrace{L_f h(x) + L_g h(x)\,u}_{\dot{h}} \ \ge\ -\alpha\big(h(x)\big),$$

      <p>for an extended class-\(\mathcal{K}\) function \(\alpha\). Far from the boundary
      (\(h\) large) the condition is slack; near it (\(h \to 0\)) it forces \(\dot h \ge 0\).
      Again affine in \(u\), so it slots into the same QP.</p>

      <figure class="nb-fig">
        <svg viewBox="0 0 520 178" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="A nominal controller feeding a quadratic program safety filter which then drives the robot">
          <rect x="16" y="46" width="108" height="46" rx="4" fill="#fff" stroke="#16181d" stroke-width="1.5"/>
          <text x="70" y="66" text-anchor="middle" font-size="12" fill="#16181d">performance</text>
          <text x="70" y="81" text-anchor="middle" font-size="12" fill="#16181d">controller</text>
          <line x1="124" y1="69" x2="176" y2="69" stroke="#16181d" stroke-width="1.6"/>
          <path d="M 176 69 l -8 -4 v 8 z" fill="#16181d"/>
          <text x="150" y="60" text-anchor="middle" font-size="11.5" fill="#5b6572">u&#8345;&#8338;&#8344;</text>
          <rect x="178" y="38" width="126" height="62" rx="4" fill="#eef4fc" stroke="#0b5fc1" stroke-width="1.6"/>
          <text x="241" y="60" text-anchor="middle" font-size="12" fill="#0b5fc1">min &#8214;u &#8722; u&#8345;&#8338;&#8344;&#8214;&#178;</text>
          <text x="241" y="78" text-anchor="middle" font-size="11.5" fill="#0b5fc1">s.t. h&#775; &#8805; &#8722;&#945;(h)</text>
          <text x="241" y="93" text-anchor="middle" font-size="11.5" fill="#0b5fc1">u &#8712; U</text>
          <line x1="304" y1="69" x2="356" y2="69" stroke="#16181d" stroke-width="1.6"/>
          <path d="M 356 69 l -8 -4 v 8 z" fill="#16181d"/>
          <text x="330" y="60" text-anchor="middle" font-size="11.5" fill="#5b6572">u</text>
          <rect x="358" y="46" width="108" height="46" rx="4" fill="#fff" stroke="#16181d" stroke-width="1.5"/>
          <text x="412" y="73" text-anchor="middle" font-size="12" fill="#16181d">robot</text>
          <line x1="412" y1="92" x2="412" y2="140" stroke="#16181d" stroke-width="1.4"/>
          <line x1="412" y1="140" x2="70" y2="140" stroke="#16181d" stroke-width="1.4"/>
          <line x1="70" y1="140" x2="70" y2="94" stroke="#16181d" stroke-width="1.4"/>
          <path d="M 70 94 l -4 8 h 8 z" fill="#16181d"/>
          <line x1="241" y1="140" x2="241" y2="102" stroke="#0b5fc1" stroke-width="1.4" stroke-dasharray="4 3"/>
          <path d="M 241 102 l -4 8 h 8 z" fill="#0b5fc1"/>
          <text x="252" y="128" font-size="11.5" fill="#5b6572">x</text>
        </svg>
        <figcaption>The filter changes the command only when the safety constraint is about to bind, which keeps the performance controller free the rest of the time.</figcaption>
      </figure>

      <p>The modular structure is the appeal: any nominal controller — PID, MPC, a learned
      policy — can be wrapped, and the filter intervenes minimally. The open problems are the
      ones that show up immediately in practice: choosing \(h\) so the safe set is actually
      invariant given input limits, handling constraints of relative degree greater than one
      (a position constraint on a double integrator does not depend on \(u\) at first
      differentiation), guaranteeing the QP stays feasible when safety and input limits
      conflict, keeping the resulting law Lipschitz so the closed loop is well posed, and
      composing many barriers without over-constraining the input.</p>

      <h2 id="mpc">Model predictive control</h2>

      <p>Rather than a fixed feedback law, solve an optimal control problem online at every
      step and apply only its first move:</p>

      $$\begin{aligned}
        \min_{u_{0:N-1}} \quad & \sum_{k=0}^{N-1} \ell(x_k, u_k) + V_f(x_N) \\
        \text{s.t.} \quad & x_{k+1} = F(x_k, u_k), \quad x_0 = x(t), \\
        & x_k \in \mathcal{X}, \quad u_k \in \mathcal{U}, \quad x_N \in \mathcal{X}_f.
      \end{aligned}$$

      <p>Apply \(u_0\), advance one step, re-measure, re-solve. That receding horizon is what
      turns an open-loop optimisation into feedback.</p>

      <figure class="nb-fig">
        <svg viewBox="0 0 520 194" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Receding horizon: a past trajectory, a shaded prediction window, and a planned future">
          <rect x="248" y="26" width="196" height="126" fill="#eef4fc"/>
          <line x1="40" y1="160" x2="490" y2="160" stroke="#c8cfd8" stroke-width="1"/>
          <line x1="248" y1="20" x2="248" y2="168" stroke="#0b5fc1" stroke-width="1.4"/>
          <text x="248" y="182" text-anchor="middle" font-size="11.5" fill="#0b5fc1">now</text>
          <path d="M 50 132 C 110 128 170 112 248 96" fill="none" stroke="#16181d" stroke-width="2"/>
          <path d="M 248 96 C 300 84 350 56 444 44" fill="none" stroke="#0b5fc1" stroke-width="2" stroke-dasharray="5 3"/>
          <path d="M 50 118 C 150 104 300 58 480 36" fill="none" stroke="#5b6572" stroke-width="1.2" stroke-dasharray="2 4"/>
          <circle cx="248" cy="96" r="4" fill="#0b5fc1"/>
          <g fill="#0b5fc1">
            <circle cx="287" cy="86" r="2.6"/><circle cx="326" cy="74" r="2.6"/>
            <circle cx="365" cy="62" r="2.6"/><circle cx="404" cy="51" r="2.6"/><circle cx="444" cy="44" r="2.6"/>
          </g>
          <text x="66" y="150" font-size="11.5" fill="#16181d">measured past</text>
          <text x="346" y="122" text-anchor="middle" font-size="11.5" fill="#0b5fc1">predicted over N steps</text>
          <text x="346" y="138" text-anchor="middle" font-size="11.5" fill="#0b5fc1">only the first input is applied</text>
          <text x="404" y="26" font-size="11.5" fill="#5b6572">reference</text>
        </svg>
        <figcaption>The whole plan is discarded at the next timestep. Recomputing from the new measurement is where the feedback comes from.</figcaption>
      </figure>

      <p>MPC is the natural choice when constraints matter, because they appear explicitly in
      the problem rather than being patched on afterwards. It handles multi-input coupling
      without loop-by-loop tuning, and it anticipates: it will slow down before a corner
      because it can see the corner.</p>

      <p>The costs are computational and theoretical. Linear dynamics with convex constraints
      give a QP that solves reliably at kilohertz rates; nonlinear dynamics give a nonconvex
      program that may return a local solution, or none, within the time budget. Stability is
      not automatic — it comes from a terminal cost \(V_f\) and terminal set
      \(\mathcal{X}_f\) chosen so the horizon cost is a Lyapunov function — and recursive
      feasibility, the guarantee that a solution existing now implies one exists next step,
      has to be designed in rather than assumed.</p>

      <h2 id="uncertain">Control under uncertainty</h2>

      <p>Every method above assumed the model. The extensions differ in what they assume about
      the error and what they promise in return.</p>

      <h3>Robust: bounded disturbance, worst-case guarantee</h3>

      <p>With \(d \in \mathcal{D}\) bounded, ask for a property that holds for every admissible
      disturbance. <strong>Input-to-state stability</strong> is the standard weakening of
      asymptotic stability: the state is driven to a neighbourhood of the target whose size is
      proportional to \(\|d\|_\infty\). <strong>Tube MPC</strong> plans a nominal trajectory,
      bounds the error set that any disturbance realisation can produce, and tightens the
      constraints by that set so the true state stays inside a tube around the plan.
      <strong>Sliding mode</strong> control uses a discontinuous law to reject matched
      disturbances exactly, at the price of chattering. <strong>Robust CBFs</strong> tighten
      the barrier condition by the worst-case disturbance term.</p>

      <p>The universal cost is conservatism: you pay for the worst case at all times.</p>

      <h3>Stochastic: known statistics, probabilistic guarantee</h3>

      <p>If the disturbance is random with known distribution, replace hard constraints with
      chance constraints \(\Pr[x_k \in \mathcal{X}] \ge 1 - \epsilon\) and minimise expected
      cost. Less conservative than robust design and often far more usable, but the guarantee
      is different in kind — a 99% chance constraint means a 1% violation rate, which may or
      may not be acceptable depending on what the violation is.</p>

      <h3>Adaptive: unknown parameters</h3>

      <p>When the uncertainty is a constant unknown \(\theta\) — a payload mass, a friction
      coefficient — estimate it online and feed the estimate to the controller. Model reference
      adaptive control and \(\mathcal{L}_1\) adaptive control are the classical routes.
      Adaptation improves tracking but does not by itself guarantee parameter convergence
      unless the signal is persistently exciting, which regulation tasks generally are not.</p>

      <h3>Learning: unknown structure</h3>

      <p>When the model is unknown or too complex to write down, fit the residual dynamics from
      data (Gaussian processes give calibrated uncertainty; neural networks give capacity) and
      either plan with the learned model or learn the policy directly. The design question is
      how much you are willing to trust the learned component. The common answer in safety-
      critical settings is: not much on its own, so wrap it in a filter or a robust MPC built
      on a model you do trust.</p>

      <h3>Estimation is part of the loop</h3>

      <p>If you do not measure the full state, an observer sits between sensors and controller —
      Luenberger for linear systems, EKF or UKF for nonlinear ones, moving-horizon estimation
      when constraints on the state matter. For linear systems you may design the two halves
      separately. For nonlinear systems you may not, and estimation error should be treated as
      another uncertainty the controller must tolerate.</p>

      <h2 id="choosing">Choosing a controller</h2>

      <div class="nb-table-wrap">
      <table>
        <thead>
          <tr><th>Situation</th><th>Reach for</th><th>Because</th></tr>
        </thead>
        <tbody>
          <tr><td>Single loop, no model, no constraints</td><td>PID</td><td>Cheap, well understood, usually enough</td></tr>
          <tr><td>Linear model, coupled states, no constraints</td><td>LQR</td><td>Optimal gains from interpretable weights</td></tr>
          <tr><td>Linear model, noisy partial measurement</td><td>LQG / Kalman + LQR</td><td>Separation principle applies</td></tr>
          <tr><td>Fully actuated manipulator</td><td>Computed torque</td><td>Cancels dynamics, leaves linear error system</td></tr>
          <tr><td>Nonlinear, control-affine, need a proof</td><td>CLF-QP</td><td>Lyapunov condition is linear in \(u\)</td></tr>
          <tr><td>Hard safety constraints</td><td>CBF safety filter</td><td>Set invariance, modular over any nominal law</td></tr>
          <tr><td>Constraints plus prediction</td><td>MPC</td><td>Constraints handled explicitly, anticipates ahead</td></tr>
          <tr><td>Bounded disturbance, worst case matters</td><td>Tube MPC, robust CBF, ISS design</td><td>Guarantee holds for every admissible disturbance</td></tr>
          <tr><td>Random disturbance, some risk acceptable</td><td>Stochastic MPC</td><td>Chance constraints avoid worst-case conservatism</td></tr>
          <tr><td>Unknown constant parameters</td><td>Adaptive control</td><td>Estimates online while controlling</td></tr>
          <tr><td>Underactuated, aggressive motion</td><td>Trajectory optimization, iLQR, flatness</td><td>Must exploit dynamics rather than cancel them</td></tr>
        </tbody>
      </table>
      </div>

      <div class="nb-key">
        <p>Two habits worth keeping. First, name the guarantee you want before choosing the
        method — "stable", "safe with probability 0.99", and "safe for all bounded
        disturbances" lead to different designs. Second, check that the guarantee survives
        implementation: sampling, input saturation, estimation error, and solver time limits
        each break proofs that were valid on paper.</p>
      </div>
"""


# --------------------------------------------------------------------------
# Landing page
# --------------------------------------------------------------------------

INDEX_TEMPLATE = """---
layout: default
title: Notes
---

{css}

{{% raw %}}
<div class="nb">

  <h1 class="nb-title">Notes</h1>
  <p class="nb-deck">Working notes on modelling and control for robotic systems &mdash;
  the vocabulary I keep coming back to, written down so I stop re-deriving it. They are
  organised as an overview rather than a course: enough to place a problem, with pointers
  to what to read next.</p>
  <hr class="nb-rule">

  <div class="nb-index">
{cards}
  </div>

  <p class="nb-foot">Corrections and suggestions are welcome by
  <a href="mailto:haejoonl@umich.edu">email</a>.</p>

</div>

<style>
.nb-index {{ display: grid; gap: 0; max-width: 760px; }}
.nb-card {{
  display: block; padding: 1.5rem 0; border-top: 1px solid var(--rule);
  text-decoration: none; color: inherit; border-bottom: 0;
}}
.nb-card:last-child {{ border-bottom: 1px solid var(--rule); }}
.nb-card:hover .nb-card-title {{ color: var(--accent); }}
.nb-card-row {{ display: flex; gap: 1.1rem; align-items: baseline; }}
.nb-card-num {{
  font-family: var(--sans); font-size: .95rem; color: var(--accent);
  font-variant-numeric: tabular-nums; flex: 0 0 auto;
}}
.nb-card-title {{
  font-family: var(--sans); font-size: 1.18rem; font-weight: 650;
  letter-spacing: -.01em; margin: 0 0 .35rem;
}}
.nb-card-desc {{ margin: 0 0 .6rem; color: var(--ink); max-width: 62ch; }}
.nb-card-topics {{ font-family: var(--sans); font-size: .82rem; color: var(--muted); }}
.nb-foot {{ font-family: var(--sans); font-size: .86rem; color: var(--muted); margin-top: 2.5rem; }}
.nb-foot a {{ color: var(--accent); text-decoration: none; }}
.nb-foot a:hover {{ text-decoration: underline; }}
@media (max-width: 640px) {{
  .nb-card-row {{ gap: .8rem; }}
}}
</style>
{{% endraw %}}
"""

CARD_TEMPLATE = """    <a class="nb-card" href="{href}">
      <div class="nb-card-row">
        <div class="nb-card-num">{num}</div>
        <div>
          <div class="nb-card-title">{title}</div>
          <p class="nb-card-desc">{desc}</p>
          <div class="nb-card-topics">{topics}</div>
        </div>
      </div>
    </a>"""

CARDS = [
    (
        "System modelling",
        "What a model is made of and the handful of distinctions that decide which "
        "controllers are available to you: linear or nonlinear, continuous or discrete "
        "time, fully actuated or underactuated, nominal or uncertain.",
        "state and input &middot; degrees of freedom &middot; discretisation &middot; "
        "linearization &middot; control-affine form &middot; disturbance models &middot; observability",
    ),
    (
        "Common dynamic models",
        "The small library of models that covers most of robotics, written in a common "
        "form with their dimensions, structure, and the assumptions that break them.",
        "single and double integrator &middot; unicycle &middot; differential drive &middot; "
        "kinematic and dynamic bicycle &middot; cart-pole &middot; quadrotor on SO(3)",
    ),
    (
        "Control law design",
        "How the standard controllers are built, what each one assumes, and what it "
        "promises &mdash; through to designing under disturbance, unknown parameters, and "
        "hard safety constraints.",
        "PID &middot; pole placement &middot; LQR and LQG &middot; feedback linearization "
        "&middot; CLF-QP &middot; control barrier functions &middot; MPC &middot; robust and "
        "stochastic design",
    ),
]


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------

PAGES = [
    ("system-modelling", "System modelling",
     "What a model is made of, and the distinctions &mdash; linear or nonlinear, "
     "continuous or discrete, actuated or underactuated, exact or uncertain &mdash; "
     "that decide what you can do with it.",
     TOC_SYSTEM, BODY_SYSTEM),
    ("dynamic-models", "Common dynamic models",
     "The models most robotics problems are actually written in, from the single "
     "integrator to a quadrotor on SO(3), with what each one assumes.",
     TOC_MODELS, BODY_MODELS),
    ("control-design", "Control law design",
     "From PID to model predictive control and safety filters: what each method needs "
     "from the model, and what it gives back.",
     TOC_CONTROL, BODY_CONTROL),
]


def target_paths(root, flat):
    """Return {slug: Path} for the three note pages."""
    if flat:
        return {slug: root / "notes-{0}.html".format(slug) for slug, _, _, _, _ in PAGES}
    return {slug: root / "notes" / "{0}.html".format(slug) for slug, _, _, _, _ in PAGES}


def build(root, flat):
    """Return {Path: file contents} for everything to be written."""
    paths = target_paths(root, flat)
    index_href = "notes.html" if flat else "../notes.html"
    out = {}

    for i, (slug, title, deck, toc, body) in enumerate(PAGES):
        prev_link = None
        next_link = None
        if i > 0:
            p_slug, p_title = PAGES[i - 1][0], PAGES[i - 1][1]
            prev_link = (paths[p_slug].name, p_title)
        if i < len(PAGES) - 1:
            n_slug, n_title = PAGES[i + 1][0], PAGES[i + 1][1]
            next_link = (paths[n_slug].name, n_title)

        out[paths[slug]] = make_page(title, deck, toc, body, prev_link, next_link, index_href)

    cards = "\n".join(
        CARD_TEMPLATE.format(
            href=paths[PAGES[i][0]].relative_to(root).as_posix(),
            num="{0:02d}".format(i + 1),
            title=title,
            desc=desc,
            topics=topics,
        )
        for i, (title, desc, topics) in enumerate(CARDS)
    )
    out[root / "notes.html"] = INDEX_TEMPLATE.format(css=CSS, cards=cards)
    return out


def check_layout_links(root):
    """Warn if the site layout uses relative nav links, which break in a subfolder."""
    layout = root / "_layouts" / "default.html"
    if not layout.exists():
        return None
    try:
        text = layout.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    suspects = []
    for candidate in ("publications.html", "research.html", "notes.html", "index.html"):
        for prefix in ('href="', "href='"):
            marker = prefix + candidate
            if marker in text:
                suspects.append(candidate)
                break
    return sorted(set(suspects))


def main():
    parser = argparse.ArgumentParser(
        description="Replace the Notes section of the site with generated lecture notes."
    )
    parser.add_argument("--root", default=".", help="site repo root (default: current directory)")
    parser.add_argument("--flat", action="store_true",
                        help="write notes-*.html at the repo root instead of a notes/ subfolder")
    parser.add_argument("--dry-run", action="store_true", help="print planned changes, write nothing")
    parser.add_argument("--no-backup", action="store_true", help="do not back up the existing notes.html")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not (root / "_config.yml").exists():
        print("error: no _config.yml in {0}".format(root), file=sys.stderr)
        print("       run this from your site repo root, or pass --root /path/to/repo", file=sys.stderr)
        return 1

    files = build(root, args.flat)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    print("site root: {0}".format(root))
    print("layout:    {0}\n".format("flat (notes-*.html)" if args.flat else "notes/ subfolder"))

    if args.dry_run:
        for path in sorted(files):
            rel = path.relative_to(root).as_posix()
            action = "overwrite" if path.exists() else "create"
            print("  {0:<10} {1:<38} {2:>7,d} bytes".format(action, rel, len(files[path])))
        print("\nnothing written (--dry-run)")
        return 0

    notes_index = root / "notes.html"
    if notes_index.exists() and not args.no_backup:
        backup = root / "notes.html.bak-{0}".format(stamp)
        shutil.copy2(notes_index, backup)
        print("  backed up  {0}".format(backup.name))

    for path in sorted(files):
        path.parent.mkdir(parents=True, exist_ok=True)
        existed = path.exists()
        path.write_text(files[path], encoding="utf-8")
        print("  {0:<10} {1}".format("updated" if existed else "wrote", path.relative_to(root).as_posix()))

    if not args.flat:
        suspects = check_layout_links(root)
        if suspects:
            print("\n  note: _layouts/default.html has relative nav links ({0}).".format(
                ", ".join(suspects)))
            print("        Those will 404 from inside notes/. Either add a leading slash")
            print("        in the layout, or re-run this script with --flat.")

    print("\nDone. Preview with:  bundle exec jekyll serve")
    print("Then open:           http://127.0.0.1:4000/notes.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())