import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# page config
st.set_page_config(
    page_title="NHL Performance Dashboard",
    page_icon="🏒",
    layout="wide"
)

# load data
@st.cache_data
def load_data():
    skater_preds = pd.read_csv(
        "https://github.com/casey-phelps36/csc310final/releases/tag/skaterpreds"
    )
    skaters = pd.read_csv(
        "https://github.com/casey-phelps36/csc310final/releases/tag/skatercsv"
    )
    goalies = pd.read_csv(
        "https://github.com/casey-phelps36/csc310final/releases/tag/goaliecsv"
    )

    skaters = skaters[skaters["situation"] == "all"]
    goalies = goalies[goalies["situation"] == "all"]
    skater_preds = skater_preds[skater_preds["situation"] == "all"]

    if "save_percentage" not in goalies.columns:
        goalies["save_percentage"] = 1 - (goalies["goals"] / goalies["ongoal"])

    return skaters, goalies, skater_preds


skaters, goalies, skater_preds = load_data()

st.title("NHL Performance Dashboard")
st.markdown("Analyze player statistics and predict future performance")

# column display name mappings
skater_column_names = {
    'name': 'Name',
    'team': 'Team',
    'position': 'Position',
    'games_played': 'Games Played',
    'I_F_goals': 'Goals',
    'I_F_primaryAssists': 'Primary Assists',
    'I_F_secondaryAssists': 'Secondary Assists',
    'I_F_points': 'Points',
    'points_per_game': 'PPG',
    'gameScore': 'Game Score',
    'predicted_points': 'Predicted Points'
}

goalie_column_names = {
    'name': 'Name',
    'team': 'Team',
    'games_played': 'Games Played',
    'goals': 'Goals Against',
    'ongoal': 'Shots Faced',
    'save_percentage': 'Save %',
    'gsax': 'GSAX',
    'goals_per_game': 'Goals/Game'
}

# tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["Skaters", "Goalies", "Compare Players", "Team Analysis"]
)

# skaters tab
with tab1:
    st.header("Skater Statistics")
    
    # filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        year_choice_s = st.selectbox(
            "Select Season",
            sorted(skaters["season"].unique(), reverse=True),
            key="skater_year"
        )
    
    with col2:
        team_choice_s = st.selectbox(
            "Filter by Team",
            ["All Teams"] + sorted(skaters["team"].dropna().unique()),
            key="skater_team"
        )
    
    with col3:
        pos_choice = st.selectbox(
            "Filter by Position",
            ["All"] + sorted(skaters["position"].dropna().unique())
        )
    
    # player name search
    search_name = st.text_input("Search Player Name", key="search_skater")
    
    # apply filters
    sk_filter = skaters[skaters["season"] == year_choice_s].copy()
    
    if team_choice_s != "All Teams":
        sk_filter = sk_filter[sk_filter["team"] == team_choice_s]
    
    if pos_choice != "All":
        sk_filter = sk_filter[sk_filter["position"] == pos_choice]
    
    if search_name.strip() != "":
        sk_filter = sk_filter[sk_filter["name"].str.contains(search_name, case=False, na=False)]
    
    # display summary stats
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", len(sk_filter))
    with col2:
        avg_ppg = sk_filter['points_per_game'].mean()
        st.metric("Avg PPG", f"{avg_ppg:.2f}")
    with col3:
        total_goals = sk_filter['I_F_goals'].sum()
        st.metric("Total Goals", int(total_goals))
    with col4:
        total_points = sk_filter['I_F_points'].sum()
        st.metric("Total Points", int(total_points))
    
    # display filtered data
    st.subheader(f"Results: {len(sk_filter)} players")
    
    # select key columns to display
    display_cols = ['name', 'team', 'position', 'games_played', 'I_F_goals', 
                   'I_F_primaryAssists', 'I_F_secondaryAssists', 'I_F_points', 
                   'points_per_game', 'gameScore']
    
    st.dataframe(
        sk_filter[display_cols].sort_values('I_F_points', ascending=False).rename(columns=skater_column_names),
        use_container_width=True,
        height=400
    )

    st.info("""
            - PPG = Points Per Game
        """)
    
    # top 10 scorers chart
    if len(sk_filter) > 0:
        st.markdown("---")
        st.subheader("Top 10 Point Leaders")
        top10 = sk_filter.nlargest(10, 'I_F_points')[['name', 'I_F_points', 'I_F_goals', 'I_F_primaryAssists']]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Goals', x=top10['name'], y=top10['I_F_goals']))
        fig.add_trace(go.Bar(name='Assists', x=top10['name'], y=top10['I_F_primaryAssists']))
        
        fig.update_layout(
            barmode='stack',
            xaxis_title="Player",
            yaxis_title="Count",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)


# goalies
with tab2:
    st.header("Goalie Statistics")
    
    # filters
    col1, col2 = st.columns(2)
    
    with col1:
        year_choice_g = st.selectbox(
            "Select Season",
            sorted(goalies["season"].unique(), reverse=True),
            key="goalie_year"
        )
    
    with col2:
        team_choice_g = st.selectbox(
            "Filter by Team",
            ["All Teams"] + sorted(goalies["team"].dropna().unique()),
            key="goalie_team"
        )
    
    # name search
    search_name_g = st.text_input("Search Goalie Name", key="search_goalie")
    
    # apply filters
    gk_filter = goalies[goalies["season"] == year_choice_g].copy()
    
    if team_choice_g != "All Teams":
        gk_filter = gk_filter[gk_filter["team"] == team_choice_g]
    
    if search_name_g.strip() != "":
        gk_filter = gk_filter[gk_filter["name"].str.contains(search_name_g, case=False, na=False)]
    
    # display summary stats
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Goalies", len(gk_filter))
    with col2:
        avg_sv = gk_filter['save_percentage'].mean()
        st.metric("Avg Save %", f"{avg_sv:.3f}")
    with col3:
        total_saves = (gk_filter['ongoal'] - gk_filter['goals']).sum()
        st.metric("Total Saves", int(total_saves))
    with col4:
        avg_gsax = gk_filter['gsax'].mean()
        st.metric("Avg GSAX", f"{avg_gsax:.1f}")
    
    # display filtered data
    st.subheader(f"Results: {len(gk_filter)} goalies")
    
    display_cols_g = ['name', 'team', 'games_played', 'goals', 'ongoal', 
                     'save_percentage', 'gsax', 'goals_per_game']
    
    st.dataframe(
        gk_filter[display_cols_g].sort_values('save_percentage', ascending=False).rename(columns=goalie_column_names),
        use_container_width=True,
        height=400
    )   

    st.info("""
            - GSAX = Goals Saved Above Expected
        """)
    
    # top 10 goalies chart
    if len(gk_filter) > 0:
        st.markdown("---")
        st.subheader("Top 10 Goalies by Save %")
        top10_g = gk_filter.nlargest(10, 'save_percentage')[['name', 'save_percentage', 'games_played']]
        
        fig = px.bar(top10_g, x='name', y='save_percentage', 
                    title="Save Percentage",
                    labels={'save_percentage': 'Save %', 'name': 'Goalie'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


# compare skaters tab
with tab3:
    st.header("Compare Players")
    
    col1, col2 = st.columns(2)
    
    with col1:
        p1 = st.selectbox("Select Player 1", sorted(skater_preds["name"].unique()), key="p1")
    
    with col2:
        p2 = st.selectbox("Select Player 2", sorted(skater_preds["name"].unique()), key="p2")
    
    if p1 and p2:
        p1_data = skater_preds[skater_preds["name"] == p1].iloc[0]
        p2_data = skater_preds[skater_preds["name"] == p2].iloc[0]
        
        st.markdown("---")

        # about predictions
        st.info("""
            **About Predicted Points:** 
            - Predictions are for the **2025-26 season**
            - Based on **2024-25 season performance**
            - Model trained on 16 years of NHL data (2008-2024)
            - Uses Random Forest algorithm with 500 trees
        """)
        
        # side-by-side comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"{p1}")
            st.metric("Team", p1_data["team"])
            st.metric("Position", p1_data["position"])
            st.metric("Games Played", int(p1_data["games_played"]))
            st.metric("2024-25 Season Points", int(p1_data["I_F_points"]))
            st.metric("2025-26 Predicted Points", f"{p1_data['predicted_points']:.1f}")
            st.metric("Goals", int(p1_data["I_F_goals"]))
            st.metric("Assists", int(p1_data["I_F_primaryAssists"] + p1_data["I_F_secondaryAssists"]))
            st.metric("PPG", f"{p1_data['points_per_game']:.2f}")
        
        with col2:
            st.subheader(f"{p2}")
            st.metric("Team", p2_data["team"])
            st.metric("Position", p2_data["position"])
            st.metric("Games Played", int(p2_data["games_played"]))
            st.metric("2024-25 Season Points", int(p2_data["I_F_points"]))
            st.metric("2025-26 Predicted Points", f"{p2_data['predicted_points']:.1f}")
            st.metric("Goals", int(p2_data["I_F_goals"]))
            st.metric("Assists", int(p2_data["I_F_primaryAssists"] + p2_data["I_F_secondaryAssists"]))
            st.metric("PPG", f"{p2_data['points_per_game']:.2f}")
        
        # comparison chart
        st.markdown("---")
        st.subheader("Statistical Comparison")
        
        compare_data = pd.DataFrame({
            'Stat': ['Goals', 'Assists', 'Points', 'Predicted Points', 'Game Score'],
            p1: [
                p1_data['I_F_goals'],
                p1_data['I_F_primaryAssists'] + p1_data['I_F_secondaryAssists'],
                p1_data['I_F_points'],
                p1_data['predicted_points'],
                p1_data['gameScore']
            ],
            p2: [
                p2_data['I_F_goals'],
                p2_data['I_F_primaryAssists'] + p2_data['I_F_secondaryAssists'],
                p2_data['I_F_points'],
                p2_data['predicted_points'],
                p2_data['gameScore']
            ]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name=p1, x=compare_data['Stat'], y=compare_data[p1]))
        fig.add_trace(go.Bar(name=p2, x=compare_data['Stat'], y=compare_data[p2]))
        
        fig.update_layout(barmode='group', height=400, xaxis_title="Statistic", yaxis_title="Value")
        st.plotly_chart(fig, use_container_width=True)


# team analysis tab
with tab4:
    st.header("Team Performance Analysis")
    
    team = st.selectbox("Select Team", sorted(skaters["team"].unique()))
    
    team_skaters = skater_preds[skater_preds["team"] == team].copy()
    
    if len(team_skaters) > 0:
        # team summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Players", len(team_skaters))
        with col2:
            total_points = team_skaters['I_F_points'].sum()
            st.metric("Total Points", int(total_points))
        with col3:
            predicted_total = team_skaters['predicted_points'].sum()
            st.metric("Predicted Total", f"{predicted_total:.0f}")
        with col4:
            avg_ppg = team_skaters['points_per_game'].mean()
            st.metric("Avg PPG", f"{avg_ppg:.2f}")
        
        st.markdown("---")

        # about predictions
        st.info("""
            **About Predictions:** 
            - Predictions are for the **2025-26 season**
            - Based on **2024-25 season performance**
            - Model trained on 16 years of NHL data (2008-2024)
            - Uses Random Forest algorithm with 500 trees
        """)
        
        # predicted points by player
        st.subheader("Predicted Points by Player")
        
        team_sorted = team_skaters.sort_values('predicted_points', ascending=False).head(15)
        
        fig = px.bar(
            team_sorted,
            x='name',
            y='predicted_points',
            title=f"{team} - Top 15 Players by Predicted Points",
            labels={'predicted_points': 'Predicted Points', 'name': 'Player'},
            color='predicted_points',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        

# footer
st.markdown("---")
st.caption("NHL Performance Dashboard | Data: 2008-2024 | Predictions by Random Forest ML")# touch
