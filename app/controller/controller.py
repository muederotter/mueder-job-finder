from app.view.view import View
from app.model.model import Model
import streamlit as st
from functools import partial

from app.logger import logger
from app.config import DB_PATH, OPENAI_KEY


class Controller:
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view

        self.initialize_preferences()
        self.run()

        self.set_callbacks()

    def initialize_preferences(self):
        # Fetch preferences from the database
        resume = self.model.preferencesDatabase.get("resume") or ""
        preferences = self.model.preferencesDatabase.get("preferences") or ""

        # Set initial values in session state
        if "resume" not in st.session_state:
            st.session_state["resume"] = resume
        if "preferences" not in st.session_state:
            st.session_state["preferences"] = preferences

    def set_callbacks(self):
        # Set callback functions in session state
        st.session_state["on_resume_change"] = self.model.preferencesDatabase.set("resume", self.view.resume)
        st.session_state["on_preferences_change"] = self.model.preferencesDatabase.set("preferences", self.view.preferences)

    def run(self):

        self.view.init_view()

        # Manual fetch button
        if self.view.fetch_jobs:
            # BUG: Spinner is in main column not on the sidebar under the fetch button
            with st.spinner("Fetching jobs..."):
                new_jobs = self.model.fetch_jobs_and_evaluate(self.view.filters, self.view.selected_model)
                if len(new_jobs) > 0:
                    self.view.sidebar.success(f"✅ Fetched {len(new_jobs)} jobs!")
                else:
                    self.view.sidebar.warning("⚠️ No new jobs found")

        # Re-evaluate jobs button
        if self.view.re_evaluate_button:
            with st.spinner("Re-evaluating jobs..."):
                # Get selected Model
                selected_model = self.view.selected_model

                self.model.re_evaluate_jobs(selected_model)
                # Refresh job table
                self.fill_table()
                st.success("✅ Re-evaluated jobs!")

        self.fill_table()

        # Update Job Count
        self.view.job_count.metric("Total Jobs", self.model.db.get_count())

    def fill_table(self):
        """
        Fill the job table in the main content area.
        """
        job_count = self.model.db.get_count()

        with self.view.main_column:
            if job_count == 0:
                st.info("No jobs in database yet. Click 'Fetch New Jobs' to get started!")
            else:
                jobs = self.model.db.table_df
                self.view.show_job_table(jobs, self.handle_evaluate)

    def handle_evaluate(self, job):
        # Perform AI evaluation, update model, then rerun UI
        pass

