import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Archivist", page_icon="\U0001f916", layout="wide")
st.title("\U0001f916 Archivist")
st.caption("Create and manage your AI agents")

ROLE_OPTIONS = ["assistant", "researcher", "coder", "analyst", "writer", "custom"]


def api_request(method, path, **kwargs):
    try:
        resp = getattr(requests, method)(f"{API_URL}{path}", **kwargs)
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        st.error("Cannot connect to the backend. Make sure the API is running on port 8000.")
        return None
    except requests.HTTPError as e:
        st.error(f"API error: {e.response.status_code} — {e.response.text}")
        return None


health = api_request("get", "/health")
if health:
    st.sidebar.success(
        f"Backend connected — {health['total_agents']} agent(s), "
        f"{health['active_agents']} active"
    )
else:
    st.sidebar.error("Backend offline")
    st.stop()

tab_agents, tab_create = st.tabs(["My Agents", "Create Agent"])

with tab_create:
    with st.form("create_form"):
        name = st.text_input("Agent Name")
        description = st.text_area("Description", height=100, placeholder="What does this agent do?")
        role = st.selectbox("Role", ROLE_OPTIONS)
        instructions = st.text_area(
            "Instructions",
            height=150,
            placeholder="System prompt or behavioural instructions for the agent...",
        )
        tags = st.text_input("Tags (comma-separated)", placeholder="e.g. productivity, research")
        submitted = st.form_submit_button("Create Agent")

    if submitted:
        if not name:
            st.warning("Agent name is required.")
        else:
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            result = api_request(
                "post",
                "/agents",
                json={
                    "name": name,
                    "description": description,
                    "role": role,
                    "instructions": instructions,
                    "tags": tag_list,
                },
            )
            if result:
                st.success(f"Created agent: {result['name']}")
                st.rerun()

with tab_agents:
    agents = api_request("get", "/agents")
    if agents is not None:
        if not agents:
            st.info("No agents yet. Create one in the 'Create Agent' tab.")
        else:
            for agent in agents:
                status_icon = "\U0001f7e2" if agent["status"] == "active" else "⚪"
                with st.expander(
                    f"{status_icon} **{agent['name']}** — {agent['role']} — {agent['created_at'][:10]}"
                ):
                    st.markdown(f"**Status:** `{agent['status']}`")
                    if agent.get("description"):
                        st.markdown(f"**Description:** {agent['description']}")
                    if agent.get("tags"):
                        st.write("**Tags:** " + ", ".join(f"`{t}`" for t in agent["tags"]))
                    if agent.get("instructions"):
                        st.markdown("**Instructions:**")
                        st.code(agent["instructions"], language=None)

                    col1, col2 = st.columns(2)
                    with col1:
                        toggle_label = "Deactivate" if agent["status"] == "active" else "Activate"
                        if st.button(toggle_label, key=f"toggle_{agent['id']}"):
                            api_request("post", f"/agents/{agent['id']}/toggle")
                            st.rerun()
                    with col2:
                        if st.button("Delete", key=f"del_{agent['id']}"):
                            api_request("delete", f"/agents/{agent['id']}")
                            st.rerun()
