import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Archivist", page_icon="📚", layout="wide")
st.title("📚 Archivist")
st.caption("Your personal knowledge archive")


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
    st.sidebar.success(f"Backend connected — {health['archive_count']} archive(s)")
else:
    st.sidebar.error("Backend offline")
    st.stop()

tab_browse, tab_create = st.tabs(["Browse Archives", "Create New"])

with tab_create:
    with st.form("create_form"):
        title = st.text_input("Title")
        content = st.text_area("Content", height=200)
        tags = st.text_input("Tags (comma-separated)")
        submitted = st.form_submit_button("Save Archive")

    if submitted:
        if not title or not content:
            st.warning("Title and content are required.")
        else:
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            result = api_request(
                "post",
                "/archives",
                json={"title": title, "content": content, "tags": tag_list},
            )
            if result:
                st.success(f"Created archive: {result['title']}")
                st.rerun()

with tab_browse:
    archives = api_request("get", "/archives")
    if archives is not None:
        if not archives:
            st.info("No archives yet. Create one in the 'Create New' tab.")
        else:
            for entry in archives:
                with st.expander(f"**{entry['title']}** — {entry['created_at'][:10]}"):
                    if entry.get("tags"):
                        st.write("Tags: " + ", ".join(f"`{t}`" for t in entry["tags"]))
                    st.write(entry["content"])
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("Delete", key=f"del_{entry['id']}"):
                            api_request("delete", f"/archives/{entry['id']}")
                            st.rerun()
