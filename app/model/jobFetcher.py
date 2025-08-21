import json
import requests

from app.model.jobDatabase import JobDatabase
from app.config import REQUEST_ORIGIN
from app.logger import logger

class JobFetcher:
    def __init__(self, db: JobDatabase, job_api: str):
        self.db = db
        self.job_api = job_api

    def fetch_and_store(self, filters):
        """Fetch jobs from API and store in database"""
        try:
            payload = {
                "LanguageCode": "EN",
                "SearchParameters": {
                    "FirstItem": 1,
                    "CountItem": 5000,
                    "BoundingBox": [],
                    "ZoomLevel": 0,
                    "GeoAggregation": True,
                    "CreateBoundingBox": True,
                    "Sort": [{"Direction": "ASC"}],
                },
                "SearchCriteria": filters,
            }

            params = {"data": json.dumps(payload)}
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Origin": REQUEST_ORIGIN,
                "Referer": REQUEST_ORIGIN,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            }

            logger.info("Fetching jobs from API...")
            resp = requests.get(self.API_URL, headers=headers, params=params, timeout=30)
            resp.raise_for_status()

            data = resp.json()
            items = data.get("SearchResult", {}).get("SearchResultItems", [])

            logger.info(f"Found {len(items)} jobs")

            new_jobs = []
            for item in items:
                try:
                    desc = item["MatchedObjectDescriptor"]

                    # Safely extract job data
                    job = {
                        "id": desc.get("ID", ""),
                        "title": desc.get("PositionTitle", ""),
                        "PositionURI": desc.get("PositionURI", ""),
                        "company": (
                            desc.get("ParentOrganizationName")
                            or desc.get("OrganizationName")
                            or "Unknown"
                        ),
                        "location": (
                            desc.get("PositionLocation", [{}])[0].get(
                                "DisplayName", "Unknown"
                            )
                        ),
                        "category": (
                            desc.get("JobCategory", [{}])[0].get("Name", "Unknown")
                        ),
                        "career_level": (
                            desc.get("CareerLevel", [{}])[0].get("Name", "Unknown")
                        ),
                        "start_date": desc.get("PositionStartDate", ""),
                        "description": (
                            desc.get("PositionFormattedDescription", [{}])[0].get(
                                "Tasks", ""
                            )
                        ),
                        "requirements": (
                            desc.get("PositionFormattedDescription", [{}])[0].get(
                                "Qualifications", ""
                            )
                        ),
                    }

                    job["eval_option"] = "Base"  # Default evaluation option

                    if job["id"] not in self.db.all_ids:
                        # Only insert if job ID is not already in the database
                        logger.info(f"Inserting job {job['id']}")
                        if job["id"]:  # Only store if we have an ID
                            self.db.insert_or_ignore(job)
                            new_jobs.append(job)

                except Exception as e:
                    logger.error(f"Error processing job item: {e} in line {e.__traceback__.tb_lineno}")
                    continue

            logger.info(f"Processed {len(new_jobs)} jobs")
            return new_jobs

        except Exception as e:
            logger.error(f"Fetch and store failed: {e}")
            return []