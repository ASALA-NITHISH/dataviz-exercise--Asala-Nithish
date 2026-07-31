import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os  # <-- Added os import here

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Spotify Data Story", layout="wide")

# --- DESIGN CONSTANTS ---
CVD_BLUE = "#0072B2"
CVD_ORANGE = "#D55E00"
MUTED_GREY = "#CCCCCC"

def apply_clean_theme(fig):
    """Declutters charts for publication readiness."""
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        margin=dict(t=40, l=0, r=0, b=0)
    )
    return fig

# --- DATA LOADING ---
@st.cache_data
def load_data():
    # This automatically finds the folder where app.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # This connects your current folder to the 'data' folder and the CSV file
    file_path = os.path.join(current_dir, 'data', 'spotify-tracks-dataset-detailed.csv')
    
    # Read the dataset using the dynamically created path
    df = pd.read_csv(file_path).dropna()
    df['duration_min'] = df['duration_ms'] / 60000
    return df

df = load_data()

# --- SIDEBAR INTERACTIVITY ---
st.sidebar.title("Data Controls")
selected_genres = st.sidebar.multiselect(
    "Select Genres to Explore",
    options=df['track_genre'].unique(),
    default=['pop', 'rock', 'hip-hop', 'classical', 'jazz']
)

min_popularity = st.sidebar.slider("Minimum Popularity", 0, 100, 50)

# Filter Dataset
filtered_df = df[(df['track_genre'].isin(selected_genres)) & (df['popularity'] >= min_popularity)]

# --- MAIN DASHBOARD HEADER ---
st.title("🎧 The Anatomy of a Hit Track")
st.markdown("Exploring the multidimensional attributes of Spotify tracks to uncover what drives mainstream popularity.")

# High-level KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Tracks Analyzed", f"{len(filtered_df):,}")
col2.metric("Average Popularity", f"{filtered_df['popularity'].mean():.1f}")
col3.metric("Average Duration (Mins)", f"{filtered_df['duration_min'].mean():.2f}")

st.divider()

# --- TABS FOR MULTI-LEVEL EXPLORATION ---
tab1, tab2 = st.tabs(["Popularity & Duration", "Audio Signatures"])

with tab1:
    st.subheader("How does duration impact mainstream appeal?")
    
    # Visual 1: Duration Histogram
    fig1 = px.histogram(filtered_df, x='duration_min', nbins=40,
                       title='Track Length Distribution by Selected Genres',
                       color_discrete_sequence=[CVD_BLUE])
    fig1 = apply_clean_theme(fig1)
    fig1.update_layout(xaxis_title="Duration (Minutes)", yaxis_title="Track Count")
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.subheader("Energy and Loudness Profiling")
    
    # Visual 2: Scatter plot of Energy vs Loudness
    sample_data = filtered_df.sample(min(2000, len(filtered_df)), random_state=42)
    fig2 = px.scatter(sample_data, x='loudness', y='energy', color='explicit',
                     color_discrete_map={True: CVD_ORANGE, False: MUTED_GREY},
                     title='Explicitness Concentrates in High-Energy, High-Loudness Tracks',
                     opacity=0.7)
    fig2 = apply_clean_theme(fig2)
    fig2.update_layout(xaxis_title="Loudness (dB)", yaxis_title="Energy")
    st.plotly_chart(fig2, use_container_width=True)

    # Visual 3: Average Feature by Genre (Radar)
    st.subheader("Genre Audio Fingerprints")
    features = ['danceability', 'energy', 'valence', 'acousticness']
    
    radar_data = []
    # Limit to top 3 selected to avoid radar chart clutter
    for genre in selected_genres[:3]: 
        mean_vals = filtered_df[filtered_df['track_genre'] == genre][features].mean().values
        radar_data.append(go.Scatterpolar(r=mean_vals, theta=features, fill='toself', name=genre))

    fig3 = go.Figure(data=radar_data)
    fig3.update_layout(
        polar=dict(radialaxis=dict(visible=False)),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig3, use_container_width=True)