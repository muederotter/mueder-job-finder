import sqlite3
from datetime import datetime

from app.model.jobDatabase import JobDatabase
from app.model.preferencesDatabase import PreferencesDatabase
from app.model.jobFetcher import JobFetcher
from app.model.aiRecommender import AIRecommender
from app.config import OPENAI_KEY, JOB_API

from app.logger import logger

class Model:
    def __init__(self, db_path="jobs.db"):
        self.db_path = db_path
        self.api_key = OPENAI_KEY
        self.job_api = JOB_API

        try:
            self.db = JobDatabase(db_path)
            self.preferencesDatabase = PreferencesDatabase(db_path)
            self.job_fetcher = JobFetcher(self.db, self.job_api)
        except Exception as e:
            logger.error(f"Database initialization error: {e}")

        self.ai_recommender = AIRecommender(self.api_key, self.preferencesDatabase)

    def fetch_jobs_and_evaluate(self, filters, selected_model):
        jobs = self.job_fetcher.fetch_and_store(filters)
        for job in jobs:
            evaluation = self.ai_recommender.evaluate(job, selected_model)
            job['score'] = evaluation['score']
            job['reason'] = evaluation['reason']

            # Store evaluation results
            self.db.edit_job(job['id'], 'score', job['score'])
            self.db.edit_job(job['id'], 'reason', job['reason'])

        return jobs

    def re_evaluate_jobs(self, selected_model):
        jobs = self.db.all_jobs
        for job in jobs:
            evaluation = self.ai_recommender.evaluate(job, selected_model)
            job['score'] = evaluation['score']
            job['reason'] = evaluation['reason']

            # Store evaluation results
            self.db.edit_job(job['id'], 'score', job['score'])
            self.db.edit_job(job['id'], 'reason', job['reason'])
