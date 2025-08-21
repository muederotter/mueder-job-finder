# 🦦 Mueder Job Finder

The **Mueder Job Finder** is a tool designed to help users with the job search process by providing relevant job listings, application tracking, and personalized AI-powered recommendations. The app can run locally for development or inside a Docker container on a Linux server.

> [!NOTE]
> This project is still in early development. This means that features may be incomplete, and the user experience may not be fully polished. We welcome feedback and contributions from the community to help improve the tool.

## Usage

The interface of the app is divided in three main sections:

1. **Job Search**: Users can search for job listings based on various criteria such as location, job title, and keywords.
2. **Job Database**: The app maintains a database of job listings that users can browse. Job title, description, a link and the AI Evaluation are displayed by default. The user can also display additional information such as company name, location, and job type by clicking on the eye icon in the top right corner.
3. **AI Parameters**: Users can adjust the parameters used by the AI to generate job recommendations and evaluations. This includes selecting the AI model, giving the AI their CV and some more information about their job preferences.

To search for jobs, press the **Fetch Jobs** button. The job API will start fetching job listings based on the user's search criteria and will use the specified AI parameters to generate a job score, which describes how well the job matches the user's profile. A reason for the score will also be provided.

## Quick start (developer)

These steps get the app running locally for development.

1. Create and activate a virtual environment (Windows PowerShell example):

```powershell
python -m venv .venv; .venv\Scripts\Activate.ps1
```

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

1. Copy example environment file and set secrets (optional):

```powershell
copy .env.example .env
# edit .env to add OPENAI_KEY and JOB_API_LINK
```

1. Run the Streamlit app:

```powershell
streamlit run main.py
```

Open the UI at the URL shown in the terminal (<http://localhost:8501>).

### Environment / Configuration

The app reads configuration from `.env` file with `app/config.py`. The environment variables are:

- OPENAI_KEY: API key for OpenAI API
- JOB_API_LINK: API endpoint for job listings
- REQUEST_ORIGIN: Origin URL for API requests

Keep secrets out of source control — use environment variables or a secrets manager in production.

### OpenAI API

The app uses the OpenAI API to provide AI-powered job recommendations and insights. Make sure to set the `OPENAI_KEY` environment variable with your API key.

> [!Important]
> To use the AI, you must provide an **OpenAI API key** and your account needs to have a **positive balance**.

In the app you can select your preferred model for job evaluation. Depending on the model, the result may be more accurate, but the cost may be higher.

During testing, I made the following observations:

- **gpt-4o-mini**: Cost is less than 0.01€ for 50 evaluations, but the response quality is mediocre.
- **o3-mini**: Cost was about 0.01€ per evaluation, with decent response quality.
- **gpt-5**: I did not use this model during testing out of fear of high costs. I still included it in the app for completeness.

With further development I would like the app to use smaller models for less critical evaluations to reduce costs. Jobs with a high score should be re-evaluated with more expensive models.

At some point the app should also generate a draft for a cover letter tailored to the job description. This would be a user-requested action, so it should use a more powerful model like **gpt-5**.

## Roadmap

- [ ] Create Docker image for easy deployment to user servers.
- [ ] Automatic daily job fetching and evaluation.
- [ ] Improve the evaluation process by re-evaluating high-scoring jobs with more expensive models on user request.
- [ ] Implement a cover letter generation feature using the **gpt-5** model.
- [ ] Add support for additional job platforms and APIs.
