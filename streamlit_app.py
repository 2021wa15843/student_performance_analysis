import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit_authenticator as stauth
import yaml

# st.set_page_config(layout="wide")
# names = ['Admin', 'Teacher', 'Principal']
# usernames = ['admin', 'teacher', 'principal']
# passwords = ['password123', 'teacher123', 'principal123']
# hashed_passwords = stauth.Hasher().generate(passwords)
# authenticator = stauth.Authenticate(names, usernames, hashed_passwords, 'dashboard_cookie', 'random_key', cookie_expiry_days=30)
# name, authentication_status, username = authenticator.login('Login', 'main')

# # Load config
# with open('config.yaml') as file:
#     config = yaml.safe_load(file)
# authenticator = stauth.Authenticate(
#     config['credentials'],
#     config['cookie']['name'],
#     config['cookie']['key'],
#     config['cookie']['expiry_days']
# )
# # Correct location argument
# name, authentication_status, username = authenticator.login('Login', 'main')
# if authentication_status:
#     st.success(f"Welcome {name}")

st.set_page_config(layout="wide")
st.title("Login")
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if username == "admin" and password == "password123":
        st.success("Login successful!")        
        st.set_page_config(layout="wide")
        # Load local CSV file
        df = pd.read_csv("Student_Performance_Standard6to12_Final.csv")
        st.title("📊 Student Performance Dashboard (Demo)")
        
        # Sidebar filters
        with st.sidebar:
            st.header("Filters")
            classes = ['All'] + sorted(df['Class'].unique())
            regions = ['All'] + sorted(df['Region'].unique())
            sections = ['All'] + sorted(df['Section'].unique())
            # schools = ['All'] + sorted(df['School_Name'].unique())
        
            selected_class = st.selectbox("Select Class", classes)
            selected_region = st.selectbox("Select Region", regions)
            selected_section = st.selectbox("Select Section", sections)
            # selected_school = st.selectbox("Select School", schools)
        
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
        # if selected_school != 'All':
            # filtered_df = filtered_df[filtered_df['School_Name'] == selected_school]
        
        # # KPIs
        # st.subheader("Key Performance Indicators")
        # col1, col2, col3 = st.columns(3)
        # col1.metric("Avg Previous Score", round(filtered_df['Previous_Score'].mean(), 2))
        # col2.metric("Avg Exam Score", round(filtered_df['Exam_Score'].mean(), 2))
        # col3.metric("Avg Attendance Rate", round(filtered_df['Attendance_Rate'].mean(), 2))
        
        st.subheader("Key Performance Indicators")
        total_students = len(filtered_df)
        col1, col2, col3 = st.columns(3)
        col1.metric(f"Avg Previous Score (Students: {total_students})",round(filtered_df['Previous_Score'].mean(), 2))
        col2.metric(f"Avg Exam Score (Students: {total_students})",round(filtered_df['Exam_Score'].mean(), 2))
        col3.metric(f"Avg Attendance Rate (Students: {total_students})",round(filtered_df['Attendance_Rate'].mean(), 2))
        
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
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top 10 Students by Score Improvement
        st.subheader("Top 10 Students by Score Improvement")
        filtered_df['Score_Change'] = filtered_df['Exam_Score'] - filtered_df['Previous_Score']
        top_improved = filtered_df.sort_values('Score_Change', ascending=False).head(10)
        st.dataframe(top_improved[['Student_Unique_ID','Previous_Score','Exam_Score','Score_Change']])
        
        # Full filtered student records
        st.subheader("Filtered Student Records")
        st.dataframe(filtered_df)
        
        # CSV download
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data",
            data=csv_data,
            file_name="filtered_students.csv",
            mime="text/csv"
        )
        
        # Notify Staff (Display Email)
        st.subheader("Notify Staff")
        staff_email = "lavanya.ramamoorthy@gamil.com"
        st.info(f"Notification will be sent to: {staff_email}")
        
        if st.button("Notify Staff"):
            st.success(f"Notification logged for {staff_email}")

elif authentication_status == False:
    st.error("Username or password is incorrect")

