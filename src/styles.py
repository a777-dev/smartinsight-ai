"""
styles.py — Design system for the Behavioral Intelligence Advisor.

Dark futuristic theme:
  • Deep navy / dark backgrounds
  • Glassmorphism cards (backdrop-filter + transparent surfaces)
  • Indigo primary + neon-cyan accent
  • Glowing borders and active elements
  • Plus Jakarta Sans headings / Inter body
  • Fluid entrance animations
"""
from __future__ import annotations

import streamlit as st


GLOBAL_CSS = """
<style>
  /* ── Fonts ──────────────────────────────────────────────────────────── */
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&family=Inter:wght@300;400;500;600;700&display=swap');

  /* ── Keyframes ──────────────────────────────────────────────────────── */
  @keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(22px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-18px); }
    to   { opacity: 1; transform: translateX(0); }
  }
  @keyframes orbFloat {
    0%, 100% { transform: translateY(0px) scale(1); }
    50%       { transform: translateY(-14px) scale(1.04); }
  }
  @keyframes borderGlow {
    0%, 100% { box-shadow: 0 -2px 16px rgba(99,102,241,0.30); }
    50%       { box-shadow: 0 -2px 28px rgba(34,211,238,0.40); }
  }
  @keyframes scalePop {
    from { opacity: 0; transform: scale(0.82); }
    to   { opacity: 1; transform: scale(1); }
  }
  @keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(99,102,241,0); }
    50%       { box-shadow: 0 0 10px 4px rgba(99,102,241,0.40); }
  }
  @keyframes pulseGlowGreen {
    0%, 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
    50%       { box-shadow: 0 0 10px 4px rgba(16,185,129,0.38); }
  }
  @keyframes pulseGlowAmber {
    0%, 100% { box-shadow: 0 0 0 0 rgba(245,158,11,0); }
    50%       { box-shadow: 0 0 10px 4px rgba(245,158,11,0.38); }
  }
  @keyframes pulseGlowDanger {
    0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
    50%       { box-shadow: 0 0 10px 4px rgba(239,68,68,0.38); }
  }

  /* ── CSS Variables ──────────────────────────────────────────────────── */
  :root {
    --bg:            #070C18;
    --bg2:           #0D1424;
    --bg3:           #111D2E;
    --fg:            #F0F4FF;
    --muted-fg:      #94A3B8;
    --soft-fg:       #64748B;
    --primary:       #6366F1;
    --primary-dim:   rgba(99,102,241,0.15);
    --primary-glow:  rgba(99,102,241,0.40);
    --cyan:          #22D3EE;
    --cyan-dim:      rgba(34,211,238,0.10);
    --secondary:     #10B981;
    --secondary-dim: rgba(16,185,129,0.13);
    --accent:        #F59E0B;
    --accent-dim:    rgba(245,158,11,0.12);
    --danger:        #EF4444;
    --danger-dim:    rgba(239,68,68,0.12);
    --purple:        #A78BFA;
    --border:        rgba(255,255,255,0.08);
    --border-bright: rgba(255,255,255,0.16);
    --surface:       rgba(255,255,255,0.04);
    --surface2:      rgba(255,255,255,0.07);
  }

  /* ── Global base ────────────────────────────────────────────────────── */
  html, body, [class*="css"] {
    font-family: 'Inter', ui-sans-serif, system-ui, sans-serif !important;
    color: var(--fg);
    background-color: var(--bg) !important;
  }

  .stApp {
    background-color: var(--bg) !important;
    background-image:
      radial-gradient(ellipse 80% 50% at 20% 0%, rgba(99,102,241,0.07) 0%, transparent 60%),
      radial-gradient(ellipse 60% 40% at 80% 100%, rgba(34,211,238,0.05) 0%, transparent 60%);
    background-attachment: fixed;
  }

  /* ── Container ──────────────────────────────────────────────────────── */
  .main .block-container {
    max-width: 1300px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
    padding-left:  clamp(0.9rem, 2.4vw, 2.2rem);
    padding-right: clamp(0.9rem, 2.4vw, 2.2rem);
    background: transparent !important;
  }

  /* ── Typography ─────────────────────────────────────────────────────── */
  h1, h2, h3, h4 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--fg) !important;
    letter-spacing: -0.022em;
    line-height: 1.1;
  }
  h1 { font-size: clamp(1.75rem, 4.2vw, 2.7rem); margin: 0.2rem 0 0.6rem; font-weight: 800; }
  h2 { font-size: clamp(1.2rem,  2.6vw, 1.65rem); margin-top: 1.5rem; font-weight: 700; }
  h3 { font-size: clamp(1.0rem,  2.0vw, 1.2rem);  font-weight: 700; }

  /* ── Horizontal rule ─────────────────────────────────────────────────── */
  hr { border: none; border-top: 1px solid var(--border); margin: 1.4rem 0; }

  /* ── Hero block ─────────────────────────────────────────────────────── */
  .hero-block {
    position: relative;
    border: 1px solid var(--border-bright);
    border-top: 3px solid var(--primary);
    background: linear-gradient(135deg, rgba(99,102,241,0.07) 0%, rgba(34,211,238,0.03) 100%);
    padding: clamp(1.1rem, 2.6vw, 2rem) clamp(1.1rem, 2.6vw, 2.2rem);
    margin-bottom: 1.4rem;
    overflow: hidden;
    backdrop-filter: blur(14px);
    animation: fadeSlideUp 0.55s cubic-bezier(0.22,1,0.36,1) both,
               borderGlow 4s ease-in-out 1.5s infinite;
  }
  .hero-block::before {
    content: '';
    position: absolute;
    right: -60px; top: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(99,102,241,0.14) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    animation: orbFloat 7s ease-in-out infinite;
  }
  .hero-block::after {
    content: '';
    position: absolute;
    right: 90px; top: 10px;
    width: 130px; height: 130px;
    background: radial-gradient(circle, rgba(34,211,238,0.12) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    animation: orbFloat 5s ease-in-out 1.5s infinite;
  }
  .hero-block .eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.22em;
    font-size: 0.68rem;
    font-weight: 700;
    color: var(--cyan);
    margin-bottom: 0.5rem;
    animation: fadeSlideUp 0.5s cubic-bezier(0.22,1,0.36,1) 0.1s both;
  }
  .hero-block h1 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: clamp(1.75rem, 4.4vw, 2.65rem);
    line-height: 1.05;
    margin: 0 0 0.65rem;
    animation: fadeSlideUp 0.6s cubic-bezier(0.22,1,0.36,1) 0.2s both;
    background: linear-gradient(120deg, #F0F4FF 0%, #F0F4FF 45%, var(--cyan) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .hero-block p {
    margin: 0;
    color: var(--muted-fg);
    font-size: clamp(0.94rem, 1.6vw, 1.04rem);
    line-height: 1.6;
    max-width: 76ch;
    animation: fadeSlideUp 0.6s cubic-bezier(0.22,1,0.36,1) 0.32s both;
  }

  /* ── Metric cards ────────────────────────────────────────────────────── */
  .metric-card {
    border: 1px solid var(--border);
    padding: 1.05rem 1.2rem 1rem;
    margin-bottom: 0.9rem;
    background: var(--surface);
    backdrop-filter: blur(14px);
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    animation: fadeSlideUp 0.55s cubic-bezier(0.22,1,0.36,1) both;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    cursor: default;
    position: relative;
    overflow: hidden;
  }
  .metric-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.025) 0%, transparent 55%);
    pointer-events: none;
  }
  .metric-card:hover {
    transform: translateY(-3px);
    border-color: var(--border-bright);
    box-shadow: 0 8px 30px rgba(99,102,241,0.18);
  }
  .metric-card:nth-child(1) { animation-delay: 0.05s; }
  .metric-card:nth-child(2) { animation-delay: 0.12s; }
  .metric-card:nth-child(3) { animation-delay: 0.19s; }
  .metric-card:nth-child(4) { animation-delay: 0.26s; }
  .metric-card:nth-child(5) { animation-delay: 0.33s; }
  .metric-card.accent-primary   { border-top: 3px solid var(--primary); box-shadow: inset 0 1px 0 rgba(99,102,241,0.12); }
  .metric-card.accent-secondary { border-top: 3px solid var(--secondary); box-shadow: inset 0 1px 0 rgba(16,185,129,0.12); }
  .metric-card.accent-warning   { border-top: 3px solid var(--accent);    box-shadow: inset 0 1px 0 rgba(245,158,11,0.10); }
  .metric-card.accent-accent    { border-top: 3px solid var(--accent);    box-shadow: inset 0 1px 0 rgba(245,158,11,0.10); }
  .metric-card.accent-danger    { border-top: 3px solid var(--danger);    box-shadow: inset 0 1px 0 rgba(239,68,68,0.10); }
  .metric-card .mc-label {
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-size: 0.67rem;
    color: var(--soft-fg);
    font-weight: 700;
  }
  .metric-card .mc-value {
    font-size: clamp(1.65rem, 3.2vw, 2.35rem);
    font-weight: 800;
    line-height: 1.08;
    color: var(--fg);
    word-break: break-word;
    font-family: 'Plus Jakarta Sans', sans-serif;
    animation: scalePop 0.45s cubic-bezier(0.34,1.56,0.64,1) 0.35s both;
  }
  .metric-card .mc-delta { font-size: 0.82rem; color: var(--muted-fg); }
  .metric-card .mc-scale {
    font-size: 0.72rem;
    color: var(--soft-fg);
    margin-top: 0.25rem;
    padding-top: 0.35rem;
    border-top: 1px solid var(--border);
    line-height: 1.4;
  }

  /* ── Section header ──────────────────────────────────────────────────── */
  .section-header {
    border-left: 3px solid var(--primary);
    padding: 0.55rem 0 0.55rem 0.9rem;
    margin: 1.6rem 0 0.9rem;
    animation: slideInLeft 0.5s cubic-bezier(0.22,1,0.36,1) both;
    position: relative;
  }
  .section-header::before {
    content: '';
    position: absolute;
    left: -3px; top: 0; bottom: 0; width: 3px;
    background: linear-gradient(180deg, var(--primary), var(--cyan));
    box-shadow: 0 0 14px rgba(99,102,241,0.60);
  }
  .section-header h2 {
    margin: 0;
    font-size: clamp(1.1rem, 2.4vw, 1.5rem);
    font-weight: 700;
    color: var(--fg) !important;
  }
  .section-header p {
    margin: 0.25rem 0 0;
    font-size: 0.88rem;
    color: var(--muted-fg);
    line-height: 1.5;
  }

  /* ── Score legend strip ──────────────────────────────────────────────── */
  .score-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 0.4rem 0 1rem;
  }
  .score-legend .sl-item {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.75rem;
    color: var(--muted-fg);
    font-weight: 500;
  }
  .score-legend .sl-dot { width: 10px; height: 10px; flex-shrink: 0; }

  /* ── Insight chips ───────────────────────────────────────────────────── */
  .insight-chip {
    border: 1px solid var(--border);
    border-left: 3px solid var(--secondary);
    padding: 0.85rem 1.05rem;
    margin-bottom: 0.6rem;
    background: var(--secondary-dim);
    color: var(--fg);
    line-height: 1.55;
    font-size: 0.93rem;
    backdrop-filter: blur(8px);
    animation: fadeSlideUp 0.5s cubic-bezier(0.22,1,0.36,1) both;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }
  .insight-chip:hover { transform: translateX(4px); box-shadow: -3px 0 14px rgba(16,185,129,0.28); }
  .insight-chip:nth-child(1) { animation-delay: 0.08s; }
  .insight-chip:nth-child(2) { animation-delay: 0.16s; }
  .insight-chip:nth-child(3) { animation-delay: 0.24s; }
  .insight-chip:nth-child(4) { animation-delay: 0.32s; }
  .insight-chip:nth-child(5) { animation-delay: 0.40s; }
  .insight-chip:nth-child(6) { animation-delay: 0.48s; }
  .insight-chip.warning { border-left-color: var(--accent); background: var(--accent-dim); }
  .insight-chip.warning:hover { box-shadow: -3px 0 14px rgba(245,158,11,0.28); }
  .insight-chip.danger  { border-left-color: var(--danger); background: var(--danger-dim); }
  .insight-chip.danger:hover  { box-shadow: -3px 0 14px rgba(239,68,68,0.28); }
  .insight-chip.info    { border-left-color: var(--primary); background: var(--primary-dim); }
  .insight-chip.info:hover    { box-shadow: -3px 0 14px rgba(99,102,241,0.28); }
  .insight-chip strong  { color: var(--fg); }

  /* ── Archetype cards ─────────────────────────────────────────────────── */
  .archetype-card {
    border: 1px solid var(--border);
    padding: 1rem 1.2rem;
    background: var(--surface);
    backdrop-filter: blur(14px);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: flex-start;
    gap: 0.9rem;
    flex-wrap: wrap;
    animation: fadeSlideUp 0.55s cubic-bezier(0.22,1,0.36,1) both;
    transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
  }
  .archetype-card:nth-child(1) { animation-delay: 0.05s; }
  .archetype-card:nth-child(2) { animation-delay: 0.13s; }
  .archetype-card:nth-child(3) { animation-delay: 0.21s; }
  .archetype-card:nth-child(4) { animation-delay: 0.29s; }
  .archetype-card:nth-child(5) { animation-delay: 0.37s; }
  .archetype-card:hover {
    border-color: rgba(99,102,241,0.45);
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(99,102,241,0.18);
  }
  .archetype-card .ac-icon {
    flex: 0 0 42px; width: 42px; height: 42px;
    line-height: 42px; text-align: center;
    font-weight: 800; font-size: 0.84rem;
    border-radius: 8px;
  }
  .archetype-card .ac-icon.burnout  { background: rgba(239,68,68,0.22);   color: #FCA5A5; }
  .archetype-card .ac-icon.hyper    { background: rgba(245,158,11,0.22);  color: #FCD34D; }
  .archetype-card .ac-icon.achiever { background: rgba(167,139,250,0.22); color: #C4B5FD; }
  .archetype-card .ac-icon.balanced { background: rgba(16,185,129,0.22);  color: #6EE7B7; }
  .archetype-card .ac-icon.low-risk { background: rgba(99,102,241,0.22);  color: #A5B4FC; }
  .archetype-card .ac-body          { flex: 1; min-width: 0; }
  .archetype-card h4 { margin: 0; font-size: 1.02rem; font-weight: 700; color: var(--fg) !important; }
  .archetype-card p  { margin: 0.3rem 0 0; color: var(--muted-fg); line-height: 1.5; font-size: 0.9rem; }

  /* ── Scale note ──────────────────────────────────────────────────────── */
  .scale-note {
    font-size: 0.76rem;
    color: var(--soft-fg);
    padding: 0.35rem 0.7rem;
    background: rgba(255,255,255,0.03);
    border-left: 3px solid rgba(255,255,255,0.10);
    margin: -0.3rem 0 0.8rem;
    line-height: 1.5;
  }

  /* ── Divider ─────────────────────────────────────────────────────────── */
  .divider-label {
    display: flex; align-items: center; gap: 0.7rem;
    margin: 1.4rem 0 1rem;
    color: var(--soft-fg);
    font-size: 0.74rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.15em;
  }
  .divider-label::before, .divider-label::after {
    content: ''; flex: 1; height: 1px; background: var(--border);
  }

  /* ── Pills ───────────────────────────────────────────────────────────── */
  .pill {
    display: inline-block;
    padding: 0.24rem 0.65rem;
    background: rgba(255,255,255,0.06);
    color: var(--muted-fg);
    border: 1px solid var(--border);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.67rem; font-weight: 700;
    margin: 0 0.3rem 0.4rem 0;
    white-space: nowrap;
    animation: fadeSlideUp 0.45s cubic-bezier(0.22,1,0.36,1) both;
    transition: transform 0.15s ease;
  }
  .pill:hover { transform: scale(1.06); }
  .pill.primary {
    background: rgba(99,102,241,0.18); color: #A5B4FC; border-color: rgba(99,102,241,0.42);
    animation: fadeSlideUp 0.45s cubic-bezier(0.22,1,0.36,1) 0.30s both,
               pulseGlow 2.8s ease-in-out 1.0s infinite;
  }
  .pill.secondary {
    background: rgba(16,185,129,0.16); color: #6EE7B7; border-color: rgba(16,185,129,0.42);
    animation: fadeSlideUp 0.45s cubic-bezier(0.22,1,0.36,1) 0.38s both,
               pulseGlowGreen 3.2s ease-in-out 1.2s infinite;
  }
  .pill.accent {
    background: rgba(245,158,11,0.16); color: #FCD34D; border-color: rgba(245,158,11,0.42);
    animation: fadeSlideUp 0.45s cubic-bezier(0.22,1,0.36,1) 0.46s both,
               pulseGlowAmber 3.5s ease-in-out 1.4s infinite;
  }
  .pill.danger {
    background: rgba(239,68,68,0.16); color: #FCA5A5; border-color: rgba(239,68,68,0.42);
    animation: fadeSlideUp 0.45s cubic-bezier(0.22,1,0.36,1) 0.54s both,
               pulseGlowDanger 3.0s ease-in-out 1.6s infinite;
  }
  .pill.purple {
    background: rgba(167,139,250,0.16); color: #C4B5FD; border-color: rgba(167,139,250,0.42);
    animation: fadeSlideUp 0.45s cubic-bezier(0.22,1,0.36,1) 0.62s both;
  }

  /* ── Buttons ─────────────────────────────────────────────────────────── */
  .stButton > button {
    background: linear-gradient(135deg, var(--primary), #4F46E5);
    color: #FFFFFF;
    border: 1px solid rgba(99,102,241,0.50);
    border-radius: 6px;
    padding: 0.78rem 1.3rem;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-size: 0.88rem;
    transition: background 200ms ease, transform 150ms ease, box-shadow 200ms ease;
    width: 100%;
    box-shadow: 0 0 20px rgba(99,102,241,0.22);
  }
  .stButton > button:hover {
    background: linear-gradient(135deg, #818CF8, var(--primary));
    transform: translateY(-1px);
    box-shadow: 0 6px 28px rgba(99,102,241,0.45);
  }
  .stButton > button:active { transform: scale(0.99); }

  /* ── Built-in metric ─────────────────────────────────────────────────── */
  div[data-testid="stMetric"] {
    border: 1px solid var(--border);
    border-top: 3px solid var(--primary);
    padding: 0.75rem 1rem;
    background: var(--surface);
    backdrop-filter: blur(12px);
  }
  div[data-testid="stMetricValue"] > div { color: var(--fg) !important; }
  div[data-testid="stMetricLabel"] > div { color: var(--muted-fg) !important; }

  /* ── Footer note ─────────────────────────────────────────────────────── */
  .footer-note {
    margin-top: 1.8rem;
    border: 1px solid var(--border);
    border-top: 2px solid rgba(255,255,255,0.06);
    padding: 1rem 1.2rem;
    color: var(--muted-fg);
    font-size: 0.88rem;
    line-height: 1.6;
    background: var(--surface);
    backdrop-filter: blur(8px);
  }

  /* ── Inputs & selects ────────────────────────────────────────────────── */
  div[data-baseweb="select"] > div,
  .stTextInput input,
  .stNumberInput input {
    border-radius: 6px !important;
    background: rgba(255,255,255,0.06) !important;
    border-color: var(--border-bright) !important;
    color: var(--fg) !important;
  }
  div[data-baseweb="select"] > div:focus-within,
  .stTextInput input:focus,
  .stNumberInput input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.22) !important;
  }
  div[data-testid="stSlider"] label {
    font-weight: 600;
    color: var(--fg) !important;
    font-size: 0.92rem;
  }

  /* ── Sidebar — dark futuristic ───────────────────────────────────────── */
  section[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
  }
  section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
  section[data-testid="stSidebar"] [data-testid="stSidebarNav"] span {
    font-weight: 600;
    color: var(--muted-fg) !important;
    font-family: 'Inter', sans-serif;
    font-size: 0.92rem;
    border-radius: 6px;
    transition: color 0.15s ease, background 0.15s ease;
  }
  section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
    background: rgba(99,102,241,0.10) !important;
    color: var(--fg) !important;
  }
  section[data-testid="stSidebar"] [aria-current="page"] {
    background: rgba(99,102,241,0.15) !important;
    border-left: 3px solid var(--primary) !important;
    color: var(--fg) !important;
    box-shadow: inset 0 0 12px rgba(99,102,241,0.08);
  }

  /* ── Sidebar collapse lock ───────────────────────────────────────────── */
  @media (min-width: 769px) {
    section[data-testid="stSidebar"] {
      min-width: 264px !important;
      width: 264px !important;
      transform: translateX(0) !important;
      visibility: visible !important;
    }
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="stSidebarCollapsedControl"],
    button[data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
      display: none !important;
      visibility: hidden !important;
    }
  }

  /* ── Plotly charts ───────────────────────────────────────────────────── */
  div[data-testid="stPlotlyChart"]        { width: 100% !important; }
  div[data-testid="stPlotlyChart"] > div  { width: 100% !important; }

  /* ── Expander ────────────────────────────────────────────────────────── */
  div[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    background: var(--surface) !important;
    backdrop-filter: blur(10px) !important;
  }
  div[data-testid="stExpander"] summary {
    font-weight: 600;
    color: var(--fg) !important;
    font-size: 0.92rem;
  }
  div[data-testid="stExpander"] > div { background: transparent !important; }

  /* ── Tabs ────────────────────────────────────────────────────────────── */
  .stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted-fg) !important;
    font-weight: 600;
  }
  .stTabs [aria-selected="true"] {
    color: var(--fg) !important;
    border-bottom-color: var(--primary) !important;
  }

  /* ── Alert / info boxes ──────────────────────────────────────────────── */
  div[data-testid="stAlert"] {
    background: rgba(99,102,241,0.08) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    color: var(--fg) !important;
    border-radius: 6px !important;
  }

  /* ── Dropdowns ───────────────────────────────────────────────────────── */
  [data-baseweb="popover"] { background: var(--bg2) !important; border: 1px solid var(--border) !important; }
  [data-baseweb="menu"]    { background: var(--bg2) !important; }
  [data-baseweb="option"]  { color: var(--fg) !important; }
  [data-baseweb="option"]:hover { background: rgba(99,102,241,0.12) !important; }

  /* ── Labels ──────────────────────────────────────────────────────────── */
  .stRadio label, .stCheckbox label { color: var(--fg) !important; }
  .stTextInput label, .stNumberInput label, .stSelectbox label { color: var(--muted-fg) !important; }
  .stMarkdown p { color: var(--muted-fg); }
  .stCaption    { color: var(--soft-fg) !important; font-size: 0.82rem !important; }

  /* ── Top header bar ──────────────────────────────────────────────────── */
  header[data-testid="stHeader"] {
    background: rgba(7,12,24,0.88) !important;
    backdrop-filter: blur(18px) !important;
    border-bottom: 1px solid var(--border) !important;
  }

  /* ── DataFrame ───────────────────────────────────────────────────────── */
  .stDataFrame {
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
  }

  /* ── Spinner ─────────────────────────────────────────────────────────── */
  div[data-testid="stSpinner"] > div { border-top-color: var(--primary) !important; }

  /* ── Scrollbar ───────────────────────────────────────────────────────── */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.22); }

  /* ── Mobile ──────────────────────────────────────────────────────────── */
  @media (max-width: 768px) {
    .main .block-container { padding-top: 0.6rem; padding-bottom: 2.4rem; }
    .hero-block { padding: 1rem; }
    .hero-block h1   { font-size: 1.7rem; }
    .hero-block p    { font-size: 0.93rem; }
    .metric-card     { padding: 0.85rem 1rem; margin-bottom: 0.7rem; }
    .metric-card .mc-value { font-size: 1.5rem; }
    .metric-card .mc-delta { font-size: 0.78rem; }
    .insight-chip    { font-size: 0.88rem; padding: 0.75rem 0.9rem; }
    .archetype-card  { padding: 0.85rem 1rem; }
    .archetype-card h4 { font-size: 0.98rem; }
    .archetype-card p  { font-size: 0.86rem; }
    .pill  { font-size: 0.62rem; padding: 0.2rem 0.5rem; }
    .footer-note { padding: 0.85rem 1rem; font-size: 0.84rem; }
    div[data-testid="stHorizontalBlock"] {
      flex-direction: column !important;
      gap: 0.2rem !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
      width: 100% !important;
      flex: 1 1 100% !important;
      min-width: 0 !important;
    }
  }

  /* ── Tablet ──────────────────────────────────────────────────────────── */
  @media (min-width: 769px) and (max-width: 1080px) {
    .hero-block h1         { font-size: 2.1rem; }
    .metric-card .mc-value { font-size: 1.75rem; }
  }
</style>
"""


def apply_styles() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ── Component builders ──────────────────────────────────────────────────────

def metric_card(
    label: str,
    value: str,
    delta: str | None = None,
    accent: str = "primary",
    scale: str | None = None,
) -> str:
    delta_html = f'<div class="mc-delta">{delta}</div>' if delta else ""
    scale_html = f'<div class="mc-scale">📐 {scale}</div>' if scale else ""
    return f"""
    <div class="metric-card accent-{accent}">
      <div class="mc-label">{label}</div>
      <div class="mc-value">{value}</div>
      {delta_html}
      {scale_html}
    </div>
    """


def hero(eyebrow: str, title: str, body: str) -> str:
    return f"""
    <div class="hero-block">
      <div class="eyebrow">{eyebrow}</div>
      <h1>{title}</h1>
      <p>{body}</p>
    </div>
    """


def insight_chip(text: str, tone: str = "default") -> str:
    classes = "insight-chip"
    if tone in {"warning", "danger", "info"}:
        classes += f" {tone}"
    return f'<div class="{classes}">{text}</div>'


def archetype_card(icon: str, title: str, body: str) -> str:
    archetype_class_map = {
        "BU": "burnout",
        "HC": "hyper",
        "SD": "achiever",
        "BA": "balanced",
        "LR": "low-risk",
    }
    icon_class = archetype_class_map.get(icon, "balanced")
    return f"""
    <div class="archetype-card">
      <div class="ac-icon {icon_class}">{icon}</div>
      <div class="ac-body">
        <h4>{title}</h4>
        <p>{body}</p>
      </div>
    </div>
    """


def section_header(title: str, description: str = "") -> str:
    desc_html = f'<p>{description}</p>' if description else ""
    return f"""
    <div class="section-header">
      <h2>{title}</h2>
      {desc_html}
    </div>
    """


def score_legend(items: list[tuple[str, str, str]]) -> str:
    dots = "".join(
        f'<div class="sl-item">'
        f'<div class="sl-dot" style="background:{color}"></div>'
        f'<span><strong>{label}</strong> {desc}</span>'
        f'</div>'
        for label, color, desc in items
    )
    return f'<div class="score-legend">{dots}</div>'


def scale_note(text: str) -> str:
    return f'<div class="scale-note">📐 {text}</div>'


def divider(label: str = "") -> str:
    return f'<div class="divider-label">{label}</div>'
