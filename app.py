"""IntelliGrade: Air-Gapped Pedagogical Question Classifier & Cognitive Auditor."""

import json
import pandas as pd
import streamlit as st

from src.config import get_config, update_config
from src.models import (
    BLOOMS_COLORS,
    BLOOMS_DESCRIPTIONS,
    BloomsLevel,
    QuestionEvaluation,
)
from src.ollama_client import client
from src.ui_components import (
    CUSTOM_CSS,
    compute_exam_balance_health,
    generate_html_dossier,
    render_blooms_hierarchy_html,
    render_cognitive_radar,
    render_difficulty_gauge,
    render_difficulty_histogram,
    render_distribution_chart,
)

# Set page layout and metadata
st.set_page_config(
    page_title="IntelliGrade | Cognitive Exam Classifier",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom styling tokens
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Preset academic questions across all 6 Revised Bloom's Taxonomy tiers
SAMPLE_QUESTIONS = {
    "Level 1 (Remember)": "Define Newton's First Law of Motion and state its mathematical representation.",
    "Level 2 (Understand)": "Explain how a Transformer neural network utilizes self-attention mechanisms to process long-range dependencies.",
    "Level 3 (Apply)": "Calculate the terminal velocity of a 2cm steel sphere falling through glycerin, given viscosity = 1.41 Pa·s and sphere density = 7800 kg/m³.",
    "Level 4 (Analyze)": "Compare and contrast SQL relational schemas with NoSQL document stores under high-write throughput and complex transactional requirements.",
    "Level 5 (Evaluate)": "Critique the statistical validity and real-world clinical implications of relying exclusively on p-values (p < 0.05) in multi-center clinical trials.",
    "Level 6 (Create)": "Design an air-gapped, privacy-preserving federated learning architecture for collaborative disease diagnosis across multiple competing hospitals without leaking patient identity.",
}


def main():
    cfg = get_config()

    # --- SIDEBAR: NODE INFRASTRUCTURE & SETTINGS ---
    with st.sidebar:
        st.markdown("### 🎓 **IntelliGrade**")
        st.markdown(
            "<span class='subtitle-badge'>AIR-GAPPED COGNITIVE AUDIT</span>",
            unsafe_allow_html=True,
        )

        st.markdown("#### 🌐 Local LLM Node Status")

        # Mock Mode toggle
        mock_mode_input = st.toggle(
            "Offline Mock Engine (Air-Gap Simulation)",
            value=cfg.mock_mode,
            help="Toggle between live LAN Ollama host and the built-in offline pedagogical engine.",
        )
        if mock_mode_input != cfg.mock_mode:
            update_config(mock_mode=mock_mode_input)
            st.rerun()

        # Connection health badge
        if cfg.mock_mode:
            st.markdown(
                '<div class="status-pill status-mock">⚡ OFFLINE MOCK MODE ACTIVE</div>',
                unsafe_allow_html=True,
            )
            st.caption("Operating offline using built-in linguistic heuristics.")
        else:
            is_online, health_msg, models = client.check_health()
            if is_online:
                st.markdown(
                    f'<div class="status-pill status-online">🟢 LAN NODE CONNECTED</div>',
                    unsafe_allow_html=True,
                )
                st.caption(f"Host online ({len(models)} model(s) installed)")
            else:
                st.markdown(
                    f'<div class="status-pill status-mock">⚠️ HOST UNREACHABLE</div>',
                    unsafe_allow_html=True,
                )
                st.caption("Ollama server down or not accessible on this subnet.")

        st.divider()

        # Endpoint Configuration
        st.markdown("#### ⚙️ LAN Node Configuration")
        endpoint_input = st.text_input(
            "Ollama Server URL",
            value=cfg.ollama_server_url,
            help="HTTP endpoint of the Dell server on the local subnet.",
        )
        model_input = st.text_input(
            "Target Model",
            value=cfg.model_name,
            help="Model identifier loaded on Ollama (e.g., llama3:8b).",
        )

        col_cfg1, col_cfg2 = st.columns(2)
        with col_cfg1:
            if st.button("Save Config", use_container_width=True):
                update_config(ollama_server_url=endpoint_input, model_name=model_input)
                st.success("Config updated!")
        with col_cfg2:
            if st.button("Ping Node", use_container_width=True):
                with st.spinner("Pinging host..."):
                    online, msg, mods = client.check_health()
                    if online:
                        st.success(f"Online: {len(mods)} models")
                    else:
                        st.error("Ping failed. Check IP & port.")

        st.divider()

        # Bloom's Taxonomy Reference expander
        with st.expander("📖 Revised Bloom's Rubric"):
            st.markdown(
                """
                - **L1 Remember**: Knowledge retrieval, defining, listing.
                - **L2 Understand**: Comprehending, explaining, summarizing.
                - **L3 Apply**: Executing procedures, solving problems.
                - **L4 Analyze**: Differentiating parts, examining trade-offs.
                - **L5 Evaluate**: Defending judgments, critiquing standards.
                - **L6 Create**: Designing novel architectures, synthesis.
                """
            )

    # --- MAIN PAGE HEADER ---
    st.markdown('<h1 class="main-title">IntelliGrade Cognitive Classifier</h1>', unsafe_allow_html=True)
    st.markdown(
        "Privacy-first, air-gapped pedagogical audit pipeline mapping exam questions to "
        "**Revised Bloom's Taxonomy (Levels 1-6)** with objective **Difficulty Calibration (1.0-10.0)**."
    )

    tab_single, tab_batch, tab_architecture = st.tabs(
        ["📝 Single Question Audit", "📂 Batch Assessment Pipeline", "🛡️ Air-Gap & Architecture"]
    )

    # =========================================================================
    # TAB 1: SINGLE QUESTION AUDIT
    # =========================================================================
    with tab_single:
        st.markdown("### Evaluate Academic Examination Question")

        # Presets selector
        col_preset, col_clear = st.columns([4, 1])
        with col_preset:
            selected_preset = st.selectbox(
                "⚡ Quick Load Sample Benchmark Questions:",
                options=["Select a benchmark preset..."] + list(SAMPLE_QUESTIONS.keys()),
            )

        initial_text = ""
        if selected_preset != "Select a benchmark preset...":
            initial_text = SAMPLE_QUESTIONS[selected_preset]

        question_input = st.text_area(
            "Enter examination question text:",
            value=initial_text,
            height=120,
            placeholder="Type or paste an exam question here (e.g., 'Compare and contrast CPU and GPU architectures for matrix multiplications...').",
        )

        btn_analyze = st.button("🚀 Analyze Cognitive Metrics", type="primary", use_container_width=True)

        if btn_analyze:
            # Guard against empty/blank input BEFORE calling the model
            if not question_input or not question_input.strip():
                st.error("Please enter a question before classifying.")
                st.session_state["single_result"] = None
            else:
                with st.spinner("Classifying cognitive depth and calibrating difficulty metrics..."):
                    st.session_state["single_result"] = client.evaluate_question(question_input)

        if "single_result" in st.session_state and st.session_state["single_result"]:
            result: QuestionEvaluation = st.session_state["single_result"]

            # Visual cognitive step bar
            st.markdown("#### 🎯 Cognitive Hierarchy Placement")
            st.markdown(render_blooms_hierarchy_html(result.blooms_level), unsafe_allow_html=True)

            if result.error_message:
                st.info(f"ℹ️ System Notice: {result.error_message}")

            # Metrics Row
            col_left, col_right = st.columns([1, 1])

            with col_left:
                # Gauge visualization
                gauge_fig = render_difficulty_gauge(result.difficulty_score)
                st.plotly_chart(gauge_fig, use_container_width=True)

            with col_right:
                # Level Card
                lvl_color = BLOOMS_COLORS[result.blooms_level]
                st.markdown(
                    f"""
                    <div class="pedagogy-card" style="border-left: 6px solid {lvl_color};">
                        <div class="card-title">
                            <span style="font-size: 1.4rem;">🏷️</span>
                            <span style="color: {lvl_color}; font-size: 1.3rem;">Level {result.blooms_level_index}: {result.blooms_level.value}</span>
                        </div>
                        <div class="card-content" style="margin-bottom: 0.8rem;">
                            {BLOOMS_DESCRIPTIONS[result.blooms_level]}
                        </div>
                        <div>
                            <strong>Cognitive Action Verbs:</strong><br/>
                            {''.join([f'<span class="tag-pill verb-pill">{v}</span>' for v in result.action_verbs]) if result.action_verbs else '<span style="opacity:0.6;">Implicit directive</span>'}
                        </div>
                        <div style="margin-top: 0.5rem;">
                            <strong>Key Domain Concepts:</strong><br/>
                            {''.join([f'<span class="tag-pill keyword-pill">{k}</span>' for k in result.keywords_identified]) if result.keywords_identified else '<span style="opacity:0.6;">General domain</span>'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Structured Pedagogical Cards
            col_p1, col_p2 = st.columns(2)

            with col_p1:
                st.markdown(
                    f"""
                    <div class="pedagogy-card" style="border-top: 4px solid #3b82f6;">
                        <div class="card-title" style="color: #60a5fa;">
                            <span>🧠</span> Pedagogical Reasoning
                        </div>
                        <div class="card-content">
                            {result.pedagogical_reasoning}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_p2:
                st.markdown(
                    f"""
                    <div class="pedagogy-card" style="border-top: 4px solid #10b981;">
                        <div class="card-title" style="color: #34d399;">
                            <span>💡</span> Actionable Improvement Suggestions
                        </div>
                        <div class="card-content">
                            {result.improvement_suggestions}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Cognitive Elevator Section
            if result.cognitive_elevations:
                st.markdown("#### 🚀 Cognitive Elevator: Rephrasing for Higher Bloom Tiers")
                cols_elev = st.columns(len(result.cognitive_elevations))
                for idx_elev, (elev_lvl, elev_text) in enumerate(result.cognitive_elevations.items()):
                    with cols_elev[idx_elev]:
                        st.markdown(
                            f"""
                            <div class="pedagogy-card" style="border-top: 3px solid #8b5cf6; min-height: 140px;">
                                <div class="card-title" style="color: #a78bfa; font-size: 0.95rem;">
                                    <span>⤴️</span> {elev_lvl}
                                </div>
                                <div class="card-content" style="font-size: 0.88rem;">
                                    <em>"{elev_text}"</em>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            # Footer metadata & raw JSON expander
            st.caption(
                f"Evaluated via **{result.evaluation_source}** | "
                f"Latency: **{result.latency_seconds or 0.0}s**"
            )

            with st.expander("🔍 View Raw Evaluation Audit Payload (JSON)"):
                st.code(json.dumps(result.model_dump(), indent=2), language="json")

    # =========================================================================
    # TAB 2: BATCH ASSESSMENT PIPELINE
    # =========================================================================
    with tab_batch:
        st.markdown("### Batch Examination Paper Auditing")
        st.markdown("Upload a CSV paper or paste a list of examination questions for automated batch analysis.")

        batch_input_mode = st.radio(
            "Batch Input Method:",
            ["Paste Question List", "Upload CSV File"],
            horizontal=True,
        )

        questions_to_process = []

        if batch_input_mode == "Paste Question List":
            sample_batch = (
                "Define the law of conservation of momentum.\n"
                "Explain the role of backpropagation in training artificial neural networks.\n"
                "Calculate the maximum bending moment for a simply supported beam with a central point load of 15kN.\n"
                "Compare and contrast optimistic and pessimistic concurrency control in database transactions.\n"
                "Evaluate the safety constraints and ethical tradeoffs of autonomous vehicles in emergency situations.\n"
                "Design a distributed ledger consensus algorithm optimized for low-power IoT devices."
            )
            raw_text = st.text_area(
                "Questions (one question per line):",
                value=sample_batch,
                height=160,
            )
            questions_to_process = [line.strip() for line in raw_text.splitlines() if line.strip()]

        else:
            uploaded_file = st.file_uploader("Upload CSV containing question list", type=["csv"])
            if uploaded_file:
                try:
                    df_upload = pd.read_csv(uploaded_file)
                    st.dataframe(df_upload.head(3), use_container_width=True)
                    # Allow user to choose question column
                    col_choice = st.selectbox(
                        "Select column containing question text:",
                        options=df_upload.columns.tolist(),
                    )
                    questions_to_process = df_upload[col_choice].dropna().astype(str).tolist()
                except Exception as e:
                    st.error(f"Error reading CSV: {e}")

        st.info(f"Loaded **{len(questions_to_process)}** question(s) for evaluation.")

        btn_run_batch = st.button("⚡ Run Batch Cognitive Audit", type="primary", disabled=len(questions_to_process) == 0)

        if btn_run_batch:
            # Guard against empty/blank input BEFORE calling the model
            valid_questions = [q for q in questions_to_process if q and q.strip()]
            if not valid_questions:
                st.error("Please provide at least one valid non-empty question before running batch evaluation.")
                st.session_state["batch_results"] = None
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_ui(current, total, item_res):
                    progress_bar.progress(current / total)
                    status_text.text(f"Evaluated question {current}/{total}: {item_res.question[:45]}...")

                results = client.evaluate_batch(
                    valid_questions,
                    progress_callback=update_ui,
                )
                st.session_state["batch_results"] = results
                status_text.success(f"Batch evaluation complete! {len(results)} questions audited.")

        if "batch_results" in st.session_state and st.session_state["batch_results"]:
            batch_results = st.session_state["batch_results"]

            # Summary Metrics & Pedagogical Balance Assessment
            diffs = [r.difficulty_score for r in batch_results]
            avg_diff = round(sum(diffs) / len(diffs), 2) if diffs else 0.0
            bal_score, bal_status, bal_color, bal_critique = compute_exam_balance_health(batch_results)

            st.markdown("#### 📊 Batch Pedagogical Overview")
            col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
            col_m1.metric("Total Questions", len(batch_results))
            col_m2.metric("Mean Difficulty", f"{avg_diff} / 10")

            # Most common level
            lvl_counts = {}
            for r in batch_results:
                lvl = r.blooms_level.value
                lvl_counts[lvl] = lvl_counts.get(lvl, 0) + 1
            dominant_lvl = max(lvl_counts, key=lvl_counts.get) if lvl_counts else "N/A"
            col_m3.metric("Dominant Tier", dominant_lvl)
            col_m4.metric("Exam Balance Index", f"{bal_score}%")
            col_m5.metric("Curricular Status", bal_status)

            # Pedagogical Critique Box
            st.markdown(
                f"""
                <div class="pedagogy-card" style="border-left: 5px solid {bal_color}; margin-top: 0.8rem; margin-bottom: 1.2rem;">
                    <strong>Curricular Assessment Critique:</strong> {bal_critique}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Visual Charts in 3 Columns
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                st.plotly_chart(render_distribution_chart(batch_results), use_container_width=True)
            with col_c2:
                st.plotly_chart(render_difficulty_histogram(batch_results), use_container_width=True)
            with col_c3:
                st.plotly_chart(render_cognitive_radar(batch_results), use_container_width=True)

            # Results Table
            table_data = []
            for idx, r in enumerate(batch_results, start=1):
                table_data.append({
                    "#": idx,
                    "Question": r.question,
                    "Bloom's Level": r.blooms_level.value,
                    "Tier Index": r.blooms_level_index,
                    "Difficulty": r.difficulty_score,
                    "Action Verbs": ", ".join(r.action_verbs),
                    "Pedagogical Reasoning": r.pedagogical_reasoning,
                    "Improvement Suggestions": r.improvement_suggestions,
                })

            df_results = pd.DataFrame(table_data)
            st.markdown("#### 📋 Detailed Cognitive Audit Results")
            st.dataframe(df_results, use_container_width=True)

            # Export Options
            st.markdown("#### 💾 Export Audit Reports")
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            with col_exp1:
                csv_data = df_results.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Download Results as CSV",
                    data=csv_data,
                    file_name="intelligrade_cognitive_audit.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with col_exp2:
                json_data = json.dumps([r.model_dump() for r in batch_results], indent=2).encode("utf-8")
                st.download_button(
                    "📥 Download Full Audit as JSON",
                    data=json_data,
                    file_name="intelligrade_audit_report.json",
                    mime="application/json",
                    use_container_width=True,
                )
            with col_exp3:
                html_report = generate_html_dossier(batch_results).encode("utf-8")
                st.download_button(
                    "📄 Download QA Dossier (HTML)",
                    data=html_report,
                    file_name="intelligrade_qa_dossier.html",
                    mime="text/html",
                    use_container_width=True,
                )

    # =========================================================================
    # TAB 3: AIR-GAP & ARCHITECTURE
    # =========================================================================
    with tab_architecture:
        st.markdown("### Air-Gapped Network Topology & Governance Architecture")
        st.markdown(
            """
            IntelliGrade is engineered specifically to eliminate data-leakage risks when evaluating 
            confidential, unreleased university examination papers.
            """
        )

        col_arch1, col_arch2 = st.columns([3, 2])
        with col_arch1:
            st.markdown(
                """
                #### System Pipeline Architecture
                ```
                ┌─────────────────────────────────────────────────────────┐
                │             AIR-GAPPED INSTITUTIONAL LAN                │
                │                                                         │
                │   [ Dedicated Compute Node ]    [ Orchestration Node ]  │
                │        Dell Host Server            HP OmniBook Client   │
                │    ┌──────────────────────┐    ┌─────────────────────┐  │
                │    │   Ollama Daemon      │    │  Streamlit Frontend │  │
                │    │  (llama3:8b Engine)  │    │  Audit Dashboard    │  │
                │    │                      │    │                     │  │
                │    │  PORT 11434 (LAN)    │◄───│  src/ollama_client  │  │
                │    └──────────────────────┘    └─────────────────────┘  │
                │                ▲                          ▲             │
                │                │                          │             │
                └────────────────┼──────────────────────────┼─────────────┘
                                 X                          X
                   ==============================================
                            PUBLIC CLOUD (STRICTLY BLOCKED)
                   ==============================================
                ```
                """
            )

        with col_arch2:
            st.markdown(
                """
                <div class="pedagogy-card">
                    <div class="card-title">🔒 Institutional Governance Guarantees</div>
                    <ul style="padding-left: 1.2rem; font-size: 0.9rem; line-height: 1.7;">
                        <li><strong>Zero Cloud Telemetry:</strong> All evaluation payloads stay on the private subnet.</li>
                        <li><strong>FERPA / GDPR Compliant:</strong> Examination drafts never leave institutional boundaries.</li>
                        <li><strong>Offline High-Fidelity Mock Engine:</strong> Allows continuous auditing even if the Ollama node undergoes routine hardware maintenance.</li>
                        <li><strong>Deterministic Low-Temp Inference:</strong> Temperature calibrated to 0.1 for consistent pedagogical scoring.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()
        st.markdown("#### Real-time Node Diagnostics")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.write("**Current Server URL:**", cfg.ollama_server_url)
            st.write("**Active Model:**", cfg.model_name)
            st.write("**Request Timeout:**", f"{cfg.request_timeout}s")
            st.write("**Retry Backoff:**", f"{cfg.max_retries} attempts ({cfg.backoff_factor}x factor)")

        with col_d2:
            st.write("**Mock Mode:**", "Enabled" if cfg.mock_mode else "Disabled")
            st.write("**Auto-Fallback:**", "Enabled" if cfg.auto_mock_fallback else "Disabled")
            status_desc = "Offline Simulation Mode" if cfg.mock_mode else "Connected to LAN host"
            st.write("**Operating State:**", status_desc)


if __name__ == "__main__":
    main()
