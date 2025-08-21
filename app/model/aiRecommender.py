from openai import OpenAI
import json

from app.model.preferencesDatabase import PreferencesDatabase

from app.logger import logger


class AIRecommender:
    def __init__(self, api_key: str, preferences_db: PreferencesDatabase):
        self.client = OpenAI(api_key=api_key)
        self.preferences_db = preferences_db

    def evaluate(self, job, selected_model):
        """Evaluate job match using AI"""
        prompt = f"""
            Sie sind ein Assistent für eine Jobvermittlung.
            Lebenslauf des Clienten:
            {self.preferences_db.get('resume') or 'Kein Lebenslauf vorhanden'}

            Stellenanzeige:
            Titel: {job['title']}
            Unternehmen: {job['company']}
            Standort: {job['location']}
            Kategorie: {job['category']}
            Startdatum: {job['start_date']}
            Beschreibung: {job['description']}
            Anforderungen: {job['requirements']}

            Benutzerpräferenzen: {self.preferences_db.get('preferences') or 'Keine Benutzerpräferenzen vorhanden'}

            Bewerten Sie den Übereinstimmungsgrad von 1 bis 10 und erklären Sie die Übereinstimmung. Ausgabe-JSON: {{ "score": int, "reason": str }}.
            """

        try:
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "user", "content": prompt}]
            )

            if response.choices[0].message.content.startswith("```json"):
                # Sometimes the AI returns the job in .md format
                response.choices[0].message.content = response.choices[0].message.content[7:-3]
            
            response = json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"AI evaluation failed: {e}")
            logger.error(f"Response: {response.choices[0].message.content if hasattr(response, 'choices') else response}")
            return {"score": 0, "reason": "Evaluation failed"}

        logger.info(f"Response: {response}")
        logger.info(f"Type: {type(response)}")
        return response
    def draft_cover_letter(self, job, resume_text):
        """Generate cover letter draft"""
        prompt = f"""
            Schreibe einen Entwurf für ein Bewerbungsschreiben.
            Lebenslauf des Bewerbers:
            {resume_text}

            Jobdetails:
            Titel: {job['title']}
            Unternehmen: {job['company']}
            Beschreibung: {job['description']}
            """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Cover letter generation failed: {e}")
            return "Failed to generate cover letter"
