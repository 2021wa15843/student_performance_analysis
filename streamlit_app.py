import streamlit_authenticator as stauth
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ✅ Use session state to track login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ✅ Show login form only if not logged in
if not st.session_state.logged_in:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "password123":
            st.session_state.logged_in = True
            st.success("Login successful!")
        else:
            st.error("Invalid username or password")

# ✅ Show dashboard only if logged in
if st.session_state.logged_in:
    st.title("📊 Student Performance Dashboard (Demo)")

    # Load CSV
    df = pd.read_csv("Student_Performance_Standard6to12_Final.csv")

    # ✅ Add Year column manually
    df['Year'] = 2024  # or 2024-2025 academic year

    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        years = ['All'] + sorted(df['Year'].unique())
        classes = ['All'] + sorted(df['Class'].unique())
        regions = ['All'] + sorted(df['Region'].unique())
        sections = ['All'] + sorted(df['Section'].unique())

        selected_year = st.selectbox("Select Year", years)
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
    if selected_year != 'All':
        filtered_df = filtered_df[filtered_df['Year'] == selected_year]
    if selected_class != 'All':
        filtered_df = filtered_df[filtered_df['Class'] == selected_class]
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['Region'] == selected_region]
    if selected_section != 'All':
        filtered_df = filtered_df[filtered_df['Section'] == selected_section]

    # KPIs with student count
    st.subheader("Key Performance Indicators")
    total_students = len(filtered_df)
    col1, col2, col3 = st.columns(3)
    col1.metric(f"Avg Previous Score (Students: {total_students})", round(filtered_df['Previous_Score'].mean(), 2))
    col2.metric(f"Avg Exam Score (Students: {total_students})", round(filtered_df['Exam_Score'].mean(), 2))
    col3.metric(f"Avg Attendance Rate (Students: {total_students})", round(filtered_df['Attendance_Rate'].mean(), 2))

    # -------------------------------
    # Quarterly Metrics Section
    # -------------------------------
    st.subheader("Quarterly Exam Score Metrics by Class (2024–2025)")

    if not filtered_df.empty:
        quarterly_scores = {'Class': [], 'Q1': [], 'Q2': [], 'Q3': [], 'Q4': []}

        for cls in sorted(filtered_df['Class'].unique()):
            class_df = filtered_df[filtered_df['Class'] == cls].copy()
            class_df = class_df.sort_values('Exam_Score').reset_index(drop=True)
            n = len(class_df)
            q1 = class_df.iloc[:n//4]['Exam_Score'].mean()
            q2 = class_df.iloc[n//4:n//2]['Exam_Score'].mean()
            q3 = class_df.iloc[n//2:3*n//4]['Exam_Score'].mean()
            q4 = class_df.iloc[3*n//4:]['Exam_Score'].mean()
            quarterly_scores['Class'].append(cls)
            quarterly_scores['Q1'].append(round(q1, 2))
            quarterly_scores['Q2'].append(round(q2, 2))
            quarterly_scores['Q3'].append(round(q3, 2))
            quarterly_scores['Q4'].append(round(q4, 2))

        qdf = pd.DataFrame(quarterly_scores)

        # Display table
        st.dataframe(qdf)

        # Create chart
        fig_quarterly = go.Figure()
        fig_quarterly.add_trace(go.Bar(x=qdf['Class'], y=qdf['Q1'], name='Q1 Avg Score'))
        fig_quarterly.add_trace(go.Bar(x=qdf['Class'], y=qdf['Q2'], name='Q2 Avg Score'))
        fig_quarterly.add_trace(go.Bar(x=qdf['Class'], y=qdf['Q3'], name='Q3 Avg Score'))
        fig_quarterly.add_trace(go.Bar(x=qdf['Class'], y=qdf['Q4'], name='Q4 Avg Score'))

        fig_quarterly.update_layout(
            title='Quarterly Exam Score Metrics by Class (2024–2025)',
            xaxis_title='Class',
            yaxis_title='Average Exam Score',
            barmode='group'
        )

        st.plotly_chart(fig_quarterly, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

    # -------------------------------
    # Performance by Class & Label Chart
    # -------------------------------
    st.subheader("Performance by Class and Performance Label")

    if not filtered_df.empty:
        grouped = filtered_df.groupby(['Class', 'Performance_Label'])['Exam_Score'].mean().reset_index()
        fig_label = px.bar(
            grouped,
            x='Class',
            y='Exam_Score',
            color='Performance_Label',
            barmode='group',
            title='Academic Year Performance by Class and Performance Label (2024–2025)',
            labels={'Exam_Score': 'Average Exam Score'}
        )
        st.plotly_chart(fig_label, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

    # -------------------------------
    # Existing Charts Section
    # -------------------------------
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

    # Top 10 Students
    st.subheader("Top 10 Students by Score Improvement")
    filtered_df['Score_Change'] = filtered_df['Exam_Score'] - filtered_df['Previous_Score']
    top_improved = filtered_df.sort_values('Score_Change', ascending=False).head(10)
    st.dataframe(top_improved[['Student_Unique_ID', 'Previous_Score', 'Exam_Score', 'Score_Change']])

    # Full filtered student records
    st.subheader("Filtered Student Records")
    st.dataframe(filtered_df)

    # Download button
    csv_data = filtered_df.to_csv(index=False)
    st.download_button("Download Filtered Data", csv_data, "filtered_students.csv", "text/csv")

    # Notify Staff
    st.subheader("Notify Staff")
    staff_email = "lavanya.ramamoorthy@gamil.com"
    st.info(f"Notification will be sent to: {staff_email}")
    if st.button("Notify Staff"):
        st.success(f"Notification logged for {staff_email}")
