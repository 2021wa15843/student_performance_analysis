
import streamlit as st
import pandas as pd
import joblib
import plotly.express as px

# Load data and model
df = pd.read_csv("Student_Performance_Standard6to12_Final.csv")
model = joblib.load("student_performance_simple.pkl")

st.title("📊 Student Performance Dashboard")

# Filters
classes = ['All'] + sorted(df['Class'].unique())
regions = ['All'] + sorted(df['Region'].unique())
sections = ['All'] + sorted(df['Section'].unique())

selected_class = st.selectbox("Select Class", classes)
selected_region = st.selectbox("Select Region", regions)
selected_section = st.selectbox("Select Section", sections)
chart_type = st.selectbox("Select Chart Type", [
    "Performance Label Distribution",
    "Score Trend by Student",
    "Average Score by Class",
    "Attendance vs Exam Score",
    "Growth vs Decline"
])

# Apply filters
filtered_df = df.copy()
if selected_class != 'All':
    filtered_df = filtered_df[filtered_df['Class'] == selected_class]
if selected_region != 'All':
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]
if selected_section != 'All':
    filtered_df = filtered_df[filtered_df['Section'] == selected_section]

# KPIs
st.subheader("KPIs")
st.write(f"**Average Previous Score:** {round(filtered_df['Previous_Score'].mean(), 2)}")
st.write(f"**Average Exam Score:** {round(filtered_df['Exam_Score'].mean(), 2)}")
st.write(f"**Average Attendance Rate:** {round(filtered_df['Attendance_Rate'].mean(), 2)}")

# Chart
if chart_type == "Performance Label Distribution":
    label_counts = filtered_df['Performance_Label'].value_counts().reset_index()
    label_counts.columns = ['Performance_Label', 'Count']
    fig = px.pie(label_counts, names='Performance_Label', values='Count')
elif chart_type == "Score Trend by Student":
    fig = px.line(filtered_df, x='Student_Unique_ID', y=['Previous_Score', 'Exam_Score'])
elif chart_type == "Average Score by Class":
    avg_score_by_class = filtered_df.groupby('Class')['Exam_Score'].mean().reset_index()
    fig = px.bar(avg_score_by_class, x='Class', y='Exam_Score')
elif chart_type == "Attendance vs Exam Score":
    fig = px.scatter(filtered_df, x='Attendance_Rate', y='Exam_Score', color='Performance_Label')
elif chart_type == "Growth vs Decline":
    filtered_df['Score_Change'] = filtered_df['Exam_Score'] - filtered_df['Previous_Score']
    fig = px.bar(filtered_df, x='Student_Unique_ID', y='Score_Change',
                 color=filtered_df['Score_Change'] > 0, color_discrete_map={True: 'green', False: 'red'})

st.plotly_chart(fig)
