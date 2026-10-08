from flask import request
import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:5001"

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

COLUMN_CONFIG = {
    "select": st.column_config.CheckboxColumn("Select", help="Select tasks to delete", default=False),
    "completed": st.column_config.CheckboxColumn("Done", help="Mark task as completed",),
    "day": st.column_config.SelectboxColumn("Day", options=DAYS, required=True),
    "title": st.column_config.TextColumn("Task", required=True),
    "time": st.column_config.TextColumn("Time"),
}

def generate_summary(tasks):
    total = len(tasks)
    completed = sum(1 for task in tasks if task.get("completed", False))
    remaining = total - completed 

    return f"You have {remaining} tasks remaining."

def load_tasks():
    try:
        response = requests.get(f"{API_BASE_URL}/tasks", timeout=30)
    except request.RequestException as e:
        st.error(f"Could not reach the server: {e}")
        return []
    
    if not response.ok:
        st.error(f"Could not load tasks: {response.text}")
        []
    return response.json()

def save_tasks(new_tasks):
    for task in new_tasks:
        response = requests.post(f"{API_BASE_URL}/tasks", json=task, timeout=30)

        if not response.ok: 
            st.error(
                f"Failed: {task['title']} | "
                f"Status: {response.status_code} | "
                f"Response: {response.text}"
            )

# ============================================================
# SESSION STATE
# ============================================================

st.session_state.setdefault("pending_tasks", None)
st.session_state.setdefault("last_file_id", None)
st.session_state.setdefault("uploader_key", 0)
st.session_state.setdefault("flash", None)
st.session_state.setdefault("flash_type", None)

st.title("JAI Lite")

if st.session_state.flash:
    if st.session_state.flash_type == "create":
        st.success(st.session_state.flash)
    elif st.session_state.flash_type == "update":
        st.warning(st.session_state.flash)
    elif st.session_state.flash_type == "delete": 
        st.error(st.session_state.flash)

    st.session_state.flash = None
    st.session_state.flash_type = None

# ============================================================
# UPLOAD HANDWRITTEN SCHEDULE
# ============================================================

uploaded_file = st.file_uploader(
    "Upload a handwritten schedule",
    type=["png", "jpg", "jpeg"],
    key=f"uploader_{st.session_state.uploader_key}",
)

if uploaded_file and uploaded_file.file_id != st.session_state.last_file_id:
    st.session_state.last_file_id = uploaded_file.file_id
    with st.spinner("Reading your schedule..."):
        response = requests.post(
            f"{API_BASE_URL}/schedules/upload",
            files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
            timeout=120,
        )
    if response.ok:
        data = response.json()
        st.session_state.pending_tasks = [
            {**task, "completed": task.get("completed", False)}
            for task in data.get("tasks", [])
        ]
    else:
        st.session_state.pending_tasks = None
        st.error(f"Could not process schedule: {response.text}")

# ============================================================
# REVIEW NEW TASKS 
# ============================================================

if st.session_state.pending_tasks is not None:
    st.header("New Tasks")
    st.caption("Review and edit, then save to add them to your list.")

    new_tasks = st.data_editor(
        st.session_state.pending_tasks,
        num_rows="dynamic",
        width="stretch",
        hide_index=True,
        key=f"new_tasks_editor{st.session_state.uploader_key}",
    )

    save, discard = st.columns(2)

    if save.button("Save", type="primary", width="stretch"):        
        response = save_tasks(new_tasks)

        st.session_state.flash = f"Created {len(new_tasks)} new tasks."
        st.session_state.flash_type = "create"
        st.session_state.pending_tasks = None
        st.session_state.last_file_id = None
        st.session_state.uploader_key += 1 # clear the uploader
        st.rerun()

    if discard.button("Discard", width="stretch"):
        st.session_state.pending_tasks = None 
        st.session_state.last_file_id = None
        st.session_state.uploader_key += 1
        st.rerun()

# ============================================================
# MAIN TABLE (always loaded from the backend)
# ============================================================

tasks = load_tasks()

editor_tasks = []

for task in tasks:
    editor_tasks.append({
        "select": False,
        "task_id": task["task_id"],
        "day": task["day"],
        "title": task["title"],
        "time": task["time"],
        "completed": task.get("completed", False),
    })

st.subheader("Existing Tasks")

if tasks: 
    tasks_editor = st.data_editor(
        editor_tasks, 
        width="stretch",
        column_config=COLUMN_CONFIG,
        disabled=["task_id"],
        hide_index=True,
        key="existing_tasks_editor"
    )

# ============================================================
# UPDATE TASKS
# ============================================================

    fields = ["day", "title", "time", "completed"]
    original_task = {
        task["task_id"]: task 
        for task in tasks
    }

    updated_tasks = []

    for row in tasks_editor: 
        original_data = original_task[row["task_id"]]
        if any(row.get(field) != original_data.get(field) for field in fields):
            updated_tasks.append(row)

    if updated_tasks:
        if st.button("Update", type="primary"):
            for row in updated_tasks: 
                body = {field: row.get(field) for field in fields}
                response = requests.put(f"{API_BASE_URL}/tasks/{row['task_id']}", json=body, timeout=30)
            
                if not response.ok:
                    st.error(f"Failed to update {row['title']}: {response.text}")

            st.session_state.flash  = (
                f"Updated: {', '.join(task['title'] for task in updated_tasks)}"
            )
            st.session_state.flash_type = "update"

            st.rerun()

# ============================================================
# DELETE TASKS
# ============================================================

    selected_tasks = [
        row for row in tasks_editor
        if row["select"]
    ]

    if selected_tasks: 
        if st.button("Delete", type="secondary"):
            for task  in selected_tasks:
                response = requests.delete(
                    f"{API_BASE_URL}/tasks/{task['task_id']}",
                    timeout=30
                )

                if not response.ok:
                    st.error(f"Falided to delete {row['title']}: {response.text}")

            st.session_state.flash  = (
                f"Deleted: {', '.join(task['title'] for task in selected_tasks)}"
            )
            st.session_state.flash_type = "delete"

            st.rerun()

    st.subheader("Summary")
    st.write(generate_summary(tasks))
else:
    st.info("No Tasks yet. Upload a schedule to get started")