# 🎓 Engineering Degree OS

Engineering Degree OS is a Streamlit-based academic management application designed to help engineering students organize and track their degree progress.

## Features

- Dashboard and academic progress overview
- Semester Management (Semesters 1–8)
- Courses and Syllabus
- University Syllabus
- Academic / Leave Calendar
- Internal Assessments
- Status Tracker
- Scorecard
- Plan and Checklist
- Ask Degree AI using Google Gemini
- Data Admin

## Technologies Used

- Python
- Streamlit
- Pandas
- Google Gemini API
- Supabase
- GitHub
- Streamlit Community Cloud

## Project Structure

```text
engineering-degree-os/
├── app.py
├── requirements.txt
├── README.md
└── data/
    ├── semesters.csv
    ├── courses.csv
    ├── academic_calendar.csv
    ├── assessments.csv
    └── scores.csv
```

## Installation and Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/bshravya2007-design/engineering-degree-os.git
   ```

2. Open the project folder:

   ```bash
   cd engineering-degree-os
   ```

3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Create `.streamlit/secrets.toml` and configure your own credentials:

   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   SUPABASE_URL = "your-supabase-project-url"
   SUPABASE_PUBLISHABLE_KEY = "your-supabase-publishable-key"
   ```

5. Run the application:

   ```bash
   python -m streamlit run app.py
   ```

## Database

Supabase is used for user authentication and assessment score storage.

The `scores` table uses Row Level Security (RLS) policies to ensure authenticated users can access only their own records.

## Deployment

The application is deployed using Streamlit Community Cloud and connected to GitHub.

## Note

The CSV files contain sample academic data. Users can save their own assessment scores through the Supabase integration.

## Author

Engineering Degree OS — Academic Management Project.