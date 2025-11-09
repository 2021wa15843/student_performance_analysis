
from flask import Flask, render_template, request, send_file
import pandas as pd
import joblib
import plotly.express as px
import os

app = Flask(__name__)

df = pd.read_csv("Student_Performance_Standard6to12_Final.csv")
model = joblib.load("student_performance_simple.pkl")

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    chart_types = [
        "Performance Label Distribution",
        "Score Trend by Student",
        "Average Score by Class",
        "Attendance vs Exam Score",
        "Growth vs Decline"
    ]
    selected_chart = request.form.get('Chart', chart_types[0])

    avg_scores = {
        'Average Previous Score': round(df['Previous_Score'].mean(), 2),
        'Average Exam Score': round(df['Exam_Score'].mean(), 2),
        'Average Attendance Rate': round(df['Attendance_Rate'].mean(), 2)
    }

    if selected_chart == "Performance Label Distribution":
        label_counts = df['Performance_Label'].value_counts().reset_index()
        label_counts.columns = ['Performance_Label', 'Count']
        fig = px.pie(label_counts, names='Performance_Label', values='Count')
    elif selected_chart == "Score Trend by Student":
        fig = px.line(df, x='Student_Unique_ID', y=['Previous_Score', 'Exam_Score'])
    elif selected_chart == "Average Score by Class":
        avg_score_by_class = df.groupby('Class')['Exam_Score'].mean().reset_index()
        fig = px.bar(avg_score_by_class, x='Class', y='Exam_Score')
    elif selected_chart == "Attendance vs Exam Score":
        fig = px.scatter(df, x='Attendance_Rate', y='Exam_Score', color='Performance_Label')
    elif selected_chart == "Growth vs Decline":
        df['Score_Change'] = df['Exam_Score'] - df['Previous_Score']
        fig = px.bar(df, x='Student_Unique_ID', y='Score_Change',
                     color=df['Score_Change'] > 0, color_discrete_map={True: 'green', False: 'red'})

    chart_html = fig.to_html(full_html=False)
    students = df.to_dict(orient='records')
    return render_template("dashboard.html", chart_types=chart_types, selected_chart=selected_chart,
                           avg_scores=avg_scores, students=students, chart_html=chart_html)

@app.route('/export_csv', methods=['POST'])
def export_csv():
    df.to_csv("static/charts/filtered_students.csv", index=False)
    return send_file("static/charts/filtered_students.csv", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
