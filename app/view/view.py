import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from st_aggrid.shared import JsCode
from functools import partial


class View:
    def __init__(self):
        st.set_page_config(page_title="🦦 MuederJobFinder", layout="wide")
        self._sidebar = st.sidebar

    def init_view(self):
        self.sidebar_setup()
        self.main_content()

    def sidebar_setup(self):
        self._sidebar.header("🔎 Jobs durchsuchen")
        loc = self._sidebar.text_input("Ort", "722092")
        dist = self._sidebar.number_input(
            "Distanz (mi)", value=20, min_value=1, max_value=100
        )
        cat = self._sidebar.number_input("Job Kategorie Code", value=42, min_value=1)
        level = self._sidebar.number_input("Karriere Level Code", value=25, min_value=1)

        self._filters = [
            {"CriterionName": "PositionLocation", "CriterionValue": [str(loc)]},
            {
                "CriterionName": "PositionLocation.Distance",
                "CriterionValue": [str(dist)],
            },
            {"CriterionName": "JobCategory.Code", "CriterionValue": [cat]},
            {"CriterionName": "CareerLevel.Code", "CriterionValue": [level]},
            {"CriterionName": "PublicationLanguage.Code", "CriterionValue": ["DE"]},
        ]

        self._fetch_jobs = st.sidebar.button("🔄 Jobs durchsuchen")

    def main_content(self):
        """
        Main content area for the job search application.
        """

        st.title("🦦 MuederJobFinder")

        self._main_column, self._right_sidebar = st.columns([2, 1])

        self.fill_right_sidebar()

    def fill_right_sidebar(self):
        with self._right_sidebar:
            st.subheader("📊 Database Status")
            self.job_count = st.metric("Total Jobs", 0)

            st.subheader("👤 Your Profile")
            self.resume = st.text_area(
                "Resume/CV",
                height=200,
                placeholder="Paste your resume text here...",
                value=st.session_state.get("resume", ""),
                on_change=self.update_resume,
            )
            self.preferences = st.text_area(
                "Job Preferences",
                placeholder="e.g., remote work, flexible hours...",
                value=st.session_state.get("preferences", ""),
                on_change=self.update_preferences,
            )

            # Select Model
            self._model_select = st.selectbox(
                "Select Model", ["gpt-4o-mini", "o3-mini", "gpt-5"]
            )

            # Re-Evaluate Button
            self._re_evaluate_button = st.button("🔃 Re-Evaluate Jobs")

    def show_job_table(self, jobs: pd.DataFrame, on_evaluate_click):
        """
        jobs: DataFrame with columns
        - id, title, company, location, score (int or None), evaluated (bool)
        on_evaluate_click: callback taking job_id when user clicks Evaluate
        """
        if not isinstance(jobs, pd.DataFrame):
            try:
                jobs = pd.DataFrame(jobs)
            except Exception as e:
                raise ValueError(
                    "Input data must be convertible to a Pandas DataFrame."
                ) from e

        column_config = {
            "id": None,
            "PositionURI": st.column_config.LinkColumn("URI", display_text="Link"),
            "company": None,
            "location": None,
            "category": None,
            "career_level": None,
            "start_date": None,
            "description": None,
            "requirements": None,
            "fetched_at": None,
            "score": st.column_config.ProgressColumn(
                "Score", format="%.1f", width=80, min_value=0, max_value=10
            ),
            "eval_option": None,
            "PublicationStartDate": st.column_config.DateColumn(
                "Publication Start Date", format="DD-MM-YYYY"
            ),
            "PublicationEndDate": st.column_config.DateColumn(
                "Publication End Date", format="DD-MM-YYYY"
            ),
        }

        # If table is already filled, clear it
        if hasattr(self, "_job_table"):
            self._job_table.empty()

        self._job_table = st.dataframe(
            jobs,
            column_config=column_config,
            hide_index=True,
            use_container_width=True,
            height=700,
        )

    def update_resume(self):
        st.session_state["resume"] = self.resume

    def update_preferences(self):
        st.session_state["preferences"] = self.preferences

    @property
    def filters(self) -> dict:
        return self._filters

    @property
    def sidebar(self):
        return self._sidebar

    @property
    def fetch_jobs(self):
        return self._fetch_jobs

    @property
    def selected_model(self):
        return self._model_select

    @property
    def re_evaluate_button(self):
        return self._re_evaluate_button

    @property
    def main_column(self):
        return self._main_column

    @property
    def right_sidebar(self):
        return self._right_sidebar
