import streamlit as st
import requests
import json

# Page config
st.set_page_config(
    page_title="AI GitHub Issue Assistant",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Styling
st.markdown("""
    <style>
    .main {
        max-width: 700px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 AI-Powered GitHub Issue Assistant")
st.markdown("Analyze GitHub issues instantly with AI-powered insights")

# Backend URL (change if deployed)
BACKEND_URL = "http://localhost:8000"

# Input section
st.subheader("📝 Enter Issue Details")
col1, col2 = st.columns([3, 1])

with col1:
    repo_url = st.text_input(
        "GitHub Repo URL",
        placeholder="https://github.com/owner/repo",
        label_visibility="collapsed"
    )

with col2:
    issue_number_input = st.text_input(
        "Issue #",
        placeholder="Enter issue number",
        label_visibility="collapsed"
    )

# Analyze button
if st.button("🔍 Analyze Issue", type="primary", use_container_width=True):
    if not repo_url or not issue_number_input:
        st.error("Please enter both repo URL and issue number")
    else:
        # Validate issue number is a valid integer
        try:
            issue_number = int(issue_number_input)
        except ValueError:
            st.error("❌ Issue number must be a valid number (e.g., 1, 42, 123)")
            st.stop()
        
        with st.spinner("Analyzing issue with AI..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/analyze-issue",
                    json={"repo_url": repo_url, "issue_number": issue_number},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Store in session state for display
                    st.session_state.analysis = data
                    st.session_state.show_raw = False
                    st.session_state.show_copy_json = False
                    
                else:
                    error_msg = response.json().get("detail", response.text)
                    st.error(f"Error: {error_msg}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Make sure it's running at http://localhost:8000")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Display results
if "analysis" in st.session_state:
    st.divider()
    st.subheader("📊 Analysis Results")
    
    data = st.session_state.analysis
    
    # Summary
    with st.container(border=True):
        st.markdown("**📋 Summary**")
        st.write(data.get("summary", "N/A"))
    
    # Type and Priority in columns
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**🏷️ Type**")
            st.write(data.get("type", "N/A"))
    
    with col2:
        with st.container(border=True):
            st.markdown("**⚡ Priority**")
            st.write(data.get("priority_score", "N/A"))
    
    # Labels
    with st.container(border=True):
        st.markdown("**🏷️ Suggested Labels**")
        labels = data.get("suggested_labels", [])
        if labels:
            cols = st.columns(len(labels))
            for i, label in enumerate(labels):
                with cols[i]:
                    st.markdown(f"`{label}`")
        else:
            st.write("No labels suggested")
    
    # Impact
    with st.container(border=True):
        st.markdown("**💥 Potential Impact**")
        st.write(data.get("potential_impact", "N/A"))
    
    st.divider()
    
    # Buttons row 
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Copy JSON", use_container_width=True):
            st.session_state.show_copy_json = True
            st.toast("Copied to clipboard!", icon="✅")
    
    with col2:
        if st.button("👁️ View Raw JSON", use_container_width=True):
            st.session_state.show_raw = not st.session_state.show_raw
    
    with col3:
        if st.button("🔄 New Analysis", use_container_width=True):
            if "analysis" in st.session_state:
                del st.session_state.analysis
            st.rerun()
    
    # ✅JSON - Break out of container with expander
    if st.session_state.get("show_copy_json", False):
        st.markdown("### 📋 JSON Output")
        # Use columns spanning full width to expand content
        st.code(json.dumps(data, indent=2), language="json", line_numbers=True)
    
    # Show raw JSON
    if st.session_state.get("show_raw", False):
        st.markdown("### Raw JSON Output")
        st.json(data)


# Footer
st.divider()
st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9em;">
    Made by Dhruva B A
    </div>
    """, unsafe_allow_html=True)
