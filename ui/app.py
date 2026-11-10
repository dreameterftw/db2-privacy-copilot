"""
Db2 Privacy Copilot - Landing Page

Professional multi-page Streamlit application with authentication flow.
"""
import streamlit as st
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Db2 Privacy Copilot",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS
st.markdown("""
<style>
    /* Hide sidebar on landing page */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Hero section */
    .hero {
        text-align: center;
        padding: 60px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .hero h1 {
        font-size: 3.5em;
        margin-bottom: 20px;
        font-weight: 700;
    }
    
    .hero p {
        font-size: 1.3em;
        opacity: 0.95;
        max-width: 800px;
        margin: 0 auto;
    }
    
    /* Feature cards */
    .feature-card {
        background: white;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s, box-shadow 0.3s;
        border-left: 4px solid #667eea;
        margin-bottom: 20px;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 3em;
        margin-bottom: 15px;
    }
    
    .feature-title {
        font-size: 1.5em;
        font-weight: 600;
        margin-bottom: 10px;
        color: #333;
    }
    
    .feature-desc {
        color: #666;
        line-height: 1.6;
    }
    
    /* CTA Button */
    .cta-button {
        display: inline-block;
        padding: 15px 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 30px;
        text-decoration: none;
        font-size: 1.2em;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        transition: transform 0.3s, box-shadow 0.3s;
    }
    
    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Stats section */
    .stat-box {
        text-align: center;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 10px;
        margin: 10px;
    }
    
    .stat-number {
        font-size: 2.5em;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        color: #666;
        font-size: 1.1em;
        margin-top: 5px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 40px 20px;
        color: #999;
        border-top: 1px solid #eee;
        margin-top: 60px;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero">
    <h1>🔒 Db2 Privacy Copilot</h1>
    <p>AI-Powered DPDP & GDPR Compliance for IBM Db2</p>
    <p style="font-size: 1.1em; margin-top: 20px;">
        Automatically discover, classify, and manage personal data with human-in-the-loop safety
    </p>
</div>
""", unsafe_allow_html=True)

# Quick Stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">150+</div>
        <div class="stat-label">Tests Passing</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">60+</div>
        <div class="stat-label">Security Checks</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">85%+</div>
        <div class="stat-label">PII Detection</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">100%</div>
        <div class="stat-label">Audit Coverage</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Feature Section
st.markdown("## 🚀 Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">Auto Discovery</div>
        <div class="feature-desc">
            Automatically maps your database schema, foreign keys, and safe deletion order using graph analysis.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🏷️</div>
        <div class="feature-title">AI Classification</div>
        <div class="feature-desc">
            Detects PII (email, phone, Aadhaar, PAN, health data) using AI-powered pattern matching with 85%+ accuracy.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">✅</div>
        <div class="feature-title">Bitemporal Consent</div>
        <div class="feature-desc">
            Track consent with both business time and system time — "what was valid when, as we knew it then."
        </div>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🗑️</div>
        <div class="feature-title">Safe Erasure</div>
        <div class="feature-desc">
            AI plans, humans approve, deterministic guardrail validates — every erasure request is reviewed and audited.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🛡️</div>
        <div class="feature-title">Security Guardrail</div>
        <div class="feature-desc">
            Blocks SQL injection, DDL commands, and unsafe operations. 60+ attack scenarios tested and blocked.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📝</div>
        <div class="feature-title">Audit Chain</div>
        <div class="feature-desc">
            SHA256 hash-chained audit log — any tampering is immediately detected. Cryptographically verifiable.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# How It Works
st.markdown("## 🔄 How It Works")

st.markdown("""
<div style="background: #f8f9fa; padding: 30px; border-radius: 12px; margin: 20px 0;">
    <h3 style="text-align: center; margin-bottom: 30px;">Simple 4-Step Process</h3>
    
    <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
        <div style="text-align: center; max-width: 200px; margin: 15px;">
            <div style="font-size: 3em;">1️⃣</div>
            <h4>Discovery</h4>
            <p>AI scans your database schema and identifies relationships</p>
        </div>
        <div style="text-align: center; max-width: 200px; margin: 15px;">
            <div style="font-size: 3em;">2️⃣</div>
            <h4>Classification</h4>
            <p>Detects PII columns with confidence scores</p>
        </div>
        <div style="text-align: center; max-width: 200px; margin: 15px;">
            <div style="font-size: 3em;">3️⃣</div>
            <h4>Review</h4>
            <p>DPO reviews and approves erasure plans</p>
        </div>
        <div style="text-align: center; max-width: 200px; margin: 15px;">
            <div style="font-size: 3em;">4️⃣</div>
            <h4>Execute</h4>
            <p>Safe execution with full audit trail</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# CTA Section
st.markdown("""
<div style="text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin: 40px 0;">
    <h2 style="color: white; margin-bottom: 20px;">Ready to Get Started?</h2>
    <p style="color: white; font-size: 1.2em; margin-bottom: 30px;">
        Access the dashboard and start managing your data privacy compliance
    </p>
</div>
""", unsafe_allow_html=True)

# Center the button using columns
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("🚀 Launch Dashboard", type="primary", use_container_width=True):
        st.switch_page("pages/1_🔐_Login.py")

st.markdown("<br>", unsafe_allow_html=True)

# Technology Stack
st.markdown("## 🛠️ Technology Stack")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Backend & Database:**
    - IBM Db2 (with temporal tables)
    - FastAPI (REST API)
    - Python 3.11+
    - NetworkX (graph analysis)
    """)

with col2:
    st.markdown("""
    **AI & Security:**
    - Sentence Transformers (PII detection)
    - Deterministic SQL guardrail
    - SHA256 audit chain
    - CrewAI (agent orchestration)
    """)

st.markdown("<br>", unsafe_allow_html=True)

# Compliance Section
st.markdown("## ⚖️ Compliance")

col1, col2 = st.columns(2)

with col1:
    st.info("""
    **DPDP Act 2023 (India)**
    
    ✅ Right to Erasure  
    ✅ Consent Management  
    ✅ Purpose Limitation  
    ✅ Data Minimization  
    ✅ Accountability (Audit Trail)
    """)

with col2:
    st.info("""
    **GDPR (EU) - Partial**
    
    ✅ Right to Erasure (Art. 17)  
    ✅ Consent (Art. 7)  
    ✅ Data Protection by Design  
    ⚠️ Right to Access (planned)  
    ⚠️ Data Portability (planned)
    """)

# Footer
st.markdown("""
<div class="footer">
    <p><strong>Db2 Privacy Copilot</strong> | Decision Support Tool (Not Legal Advice)</p>
    <p>Built with ❤️ for data privacy compliance</p>
    <p>
        <a href="https://github.com/dreameterftw/db2-privacy-copilot" target="_blank" style="color: #667eea; text-decoration: none;">
            View on GitHub
        </a> | 
        <a href="/Help" style="color: #667eea; text-decoration: none;">Documentation</a>
    </p>
    <p style="font-size: 0.9em; color: #bbb;">© 2026 All rights reserved | MIT License</p>
</div>
""", unsafe_allow_html=True)
