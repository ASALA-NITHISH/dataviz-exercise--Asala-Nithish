import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Netflix Dashboard",
    page_icon="🎬",
    layout="wide"
)


df = pd.read_csv("data/netflix_titles.csv")

df["date_added"] = pd.to_datetime(
    df["date_added"],
    errors="coerce"
)

df["year_added"] = df["date_added"].dt.year
df["month_added"] = df["date_added"].dt.month_name()

# ==========================================================
# Sidebar Filters
# ==========================================================

st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/7/75/Netflix_icon.svg",
    width=100
)

st.sidebar.title("Dashboard Filters")
content_type = st.sidebar.multiselect(
    "Select Content Type",
    options=df["type"].dropna().unique(),
    default=df["type"].dropna().unique()
)

country_list = sorted(df["country"].dropna().unique())

selected_country = st.sidebar.selectbox(
    "Select Country",
    ["All"] + country_list
)

rating_list = sorted(df["rating"].dropna().unique())

selected_rating = st.sidebar.selectbox(
    "Select Rating",
    ["All"] + rating_list
)
st.title("🎬 Netflix Data Visualization Dashboard")

st.markdown("---")

# ==========================================================
# Apply Filters
# ==========================================================

filtered_df = df[df["type"].isin(content_type)]

if selected_country != "All":
    filtered_df = filtered_df[
        filtered_df["country"] == selected_country
    ]

if selected_rating != "All":
    filtered_df = filtered_df[
        filtered_df["rating"] == selected_rating
    ]


# ==========================================================
# Search by Title
# ==========================================================

search = st.sidebar.text_input("🔍 Search Title")

if search:
    filtered_df = filtered_df[
        filtered_df["title"].str.contains(search, case=False, na=False)
    ]

# ------------------------------------------------
# Dashboard KPIs
# ------------------------------------------------

st.subheader("Dashboard Overview")

total_titles = len(filtered_df)
total_movies = len(filtered_df[filtered_df["type"] == "Movie"])
total_tvshows = len(filtered_df[filtered_df["type"] == "TV Show"])
total_countries = filtered_df["country"].nunique()

col1, col2, col3, col4 = st.columns(4)

col1.metric("🎬 Total Titles", total_titles)
col2.metric("🎥 Movies", total_movies)
col3.metric("📺 TV Shows", total_tvshows)
col4.metric("🌍 Countries", total_countries)

st.markdown("---")

st.subheader("Netflix Dataset")

st.dataframe(filtered_df.head())
csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Dataset",
    data=csv,
    file_name="filtered_netflix_data.csv",
    mime="text/csv",
)

# ------------------------------------------------
# Movies vs TV Shows
# ------------------------------------------------

st.markdown("---")

st.subheader("Movies vs TV Shows")

type_count = filtered_df["type"].value_counts().reset_index()
type_count.columns = ["Type", "Count"]

fig = px.pie(
    type_count,
    names="Type",
    values="Count",
    title="Distribution of Netflix Content",
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Set2
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# Top 10 Countries
# ------------------------------------------------

st.markdown("---")

st.subheader("Top 10 Countries with Netflix Content")

country_df = (
    filtered_df["country"]
    .dropna()
    .str.split(", ")
    .explode()
    .value_counts()
    .head(10)
    .reset_index()
)

country_df.columns = ["Country", "Count"]

fig = px.bar(
    country_df,
    x="Count",
    y="Country",
    orientation="h",
    color="Count",
    title="Top 10 Countries",
    color_continuous_scale="Reds"
)

fig.update_layout(yaxis={"categoryorder": "total ascending"})

st.plotly_chart(fig, use_container_width=True)
# ------------------------------------------------
# Content Added by Year
# ------------------------------------------------

st.markdown("---")

st.subheader("Netflix Content Added Over the Years")

year_df = (
    filtered_df["year_added"]
    .dropna()
    .astype(int)
    .value_counts()
    .sort_index()
    .reset_index()
)

year_df.columns = ["Year", "Count"]

fig = px.line(
    year_df,
    x="Year",
    y="Count",
    markers=True,
    title="Number of Titles Added Each Year"
)

fig.update_traces(line=dict(width=3))

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Ratings Distribution
# ==========================================================

st.markdown("---")

st.subheader("Content Ratings Distribution")

rating_df = (
    filtered_df["rating"]
    .dropna()
    .value_counts()
    .reset_index()
)

rating_df.columns = ["Rating", "Count"]

fig = px.bar(
    rating_df,
    x="Rating",
    y="Count",
    color="Count",
    color_continuous_scale="Blues",
    title="Distribution of Netflix Ratings"
)

fig.update_layout(
    xaxis_title="Rating",
    yaxis_title="Number of Titles"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Movie Duration Distribution
# ==========================================================

st.markdown("---")

st.subheader("Movie Duration Distribution")

# Keep only movies
movies = filtered_df[filtered_df["type"] == "Movie"].copy()

# Convert duration to numeric
movies["duration"] = (
    movies["duration"]
    .str.replace(" min", "", regex=False)
)

movies["duration"] = pd.to_numeric(
    movies["duration"],
    errors="coerce"
)

movies = movies.dropna(subset=["duration"])

fig = px.histogram(
    movies,
    x="duration",
    nbins=30,
    title="Distribution of Movie Durations",
    labels={"duration": "Duration (Minutes)"},
    color_discrete_sequence=["orange"]
)

fig.update_layout(
    xaxis_title="Duration (Minutes)",
    yaxis_title="Number of Movies"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.caption(
    "Netflix Data Visualization Dashboard | Built with Streamlit, Pandas & Plotly"
)