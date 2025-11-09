
Deployment Guide for School Dashboard

1. Install dependencies:
   pip install -r requirements.txt

2. Run locally:
   python app.py
   Open http://127.0.0.1:5000

3. Deploy on Render:
   - Create Web Service
   - Upload project or connect GitHub
   - Build command: pip install -r requirements.txt
   - Start command: python app.py

4. Deploy on Heroku:
   - Install Heroku CLI
   - heroku login
   - heroku create
   - git init
   - git add .
   - git commit -m "Initial commit"
   - git push heroku main
   - heroku open

5. Files needed:
   - Student_Performance_Standard6to12_Final.csv
   - student_performance_simple.pkl

6. Features:
   - Chart dropdown
   - KPIs
   - Interactive charts
   - Column filters
   - Export CSV
