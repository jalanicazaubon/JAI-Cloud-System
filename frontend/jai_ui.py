import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:5001"

def generate_summary(tasks):
    return f"You have {len(tasks)} tasks today."


st.title("JAI Lite")

uploaded_file = st.file_uploader(
    "Upload a handwritten schedule",
    type=["png", "jpg", "jpeg"],
)

if uploaded_file and st.session_state.get("file_id") != uploaded_file.file_id:
    with st.spinner("Reading your schedule..."):
        response = requests.post(
            f"{API_BASE_URL}/schedules/upload",
            files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
            timeout=120,
        )

    st.session_state.file_id = uploaded_file.file_id

    if response.ok:
        data = response.json()
        st.session_state.tasks = data.get("tasks", [])
        st.session_state.ocr = data.get("ocr", {})
    else:
        st.session_state.tasks = []
        st.session_state.ocr = {}
        st.error(f"Could not process schedule: {response.text}")

if uploaded_file:
    tasks = st.session_state.get("tasks", [])

    with st.expander("Raw OCR by day"):
        st.json(st.session_state.get("ocr", {}))

    if tasks: 
        edited_tasks = st.data_editor(
            tasks, 
            num_rows="dynamic", 
            use_container_width=True, 
            column_config={
                "day": st.column_config.SelectboxColumn(
                    "Day", 
                    options=[
                        "Sunday", 
                        "Monday", 
                        "Tuesday", 
                        "Wednesday", 
                        "Thursday", 
                        "Friday", 
                        "Saturday"
                    ], 
                    required=True
                ),
                "title": st.column_config.TextColumn(
                    "Task", 
                    required=True,
                ), 
                "time": st.column_config.TextColumn(
                    "Time", 
                )
            },
            hide_index=True
        )

        st.session_state.tasks = edited_tasks

    else:
        st.info("No tasks detected.")

    st.subheader("Summary")
    st.write(generate_summary(tasks))

    if st.button("Save Tasks"):
        for task in tasks:
            api_response = requests.post(f"{API_BASE_URL}/tasks", json=task, timeout=30)

            if api_response.status_code == 201:
                st.success(f"Saved: {task['title']}")
            else:
                st.error(
                    f"Failed: {task['title']} | "
                    f"Status: {api_response.status_code} | "
                    f"Response: {api_response.text}"
                )