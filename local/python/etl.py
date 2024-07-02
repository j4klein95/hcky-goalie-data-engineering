import os
import pandas as pd
from sqlalchemy import create_engine, inspect, func, MetaData, Table, Column, Integer, String, Float, DateTime
import sys

# Check for the correct number of arguments
if len(sys.argv) != 2:
    print("Usage: python etl_script.py <DATABASE_URL>")
    sys.exit(1)

# Get the database URL from command-line arguments
DATABASE_URL = sys.argv[1]

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
MP_DIR = os.path.join(DATA_DIR, 'mp')
NST_DIR = os.path.join(DATA_DIR, 'nst')

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Define the table schema
def create_goalies_table(engine):
    metadata = MetaData()
    goalies_table = Table('goalies', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('source', String(50)),
        Column('season_type', String(50)),
        Column('year', String(20)),
        Column('player_name', String(100)),
        Column('team', String(50)),
        Column('games_played', Integer),
        Column('goals_against', Integer),
        Column('expected_goals_against', Float),
        Column('goals_saved_above_expected', Float),
        Column('goals_saved_above_expected_per_60', Float),
        Column('save_percentage_on_unblocked_shots', Float),
        Column('xsave_percentage_on_unblocked_shots', Float),
        Column('save_percentage_above_expected', Float),
        Column('save_percentage_on_shots_on_goal', Float),
        Column('gaa', Float),
        Column('xgaa', Float),
        Column('gaa_better_than_expected', Float),
        Column('wins_above_replacement', Float),
        Column('icetime_minutes', Integer),
        Column('rebounds_per_save', Float),
        Column('puck_freezes_per_save', Float),
        Column('goals_against_1', Integer),
        Column('saves_on_shots_on_goal', Integer),
        Column('saves_on_unblocked_shot_attempts', Integer),
        Column('percent_shot_attempts_blocked_by_teammates', Float),
        Column('percent_unblocked_shot_attempts_against_on_goal', Float),
        Column('expected_percent_unblocked_shot_attempts_against_on_goal', Float),
        Column('on_goal_percentage_above_expected', Float),
        Column('low_danger_unblocked_shot_attempt_save_percentage', Float),
        Column('xlow_danger_unblocked_shot_attempt_save_percentage', Float),
        Column('low_danger_unblocked_shot_attempt_save_percentage_above_expected', Float),
        Column('medium_danger_unblocked_shot_attempt_save_percentage', Float),
        Column('xmedium_danger_unblocked_shot_attempt_save_percentage', Float),
        Column('medium_danger_unblocked_shot_attempt_save_percentage_above_expected', Float),
        Column('high_danger_unblocked_shot_attempt_save_percentage', Float),
        Column('xhigh_danger_unblocked_shot_attempt_save_percentage', Float),
        Column('high_danger_unblocked_shot_attempt_save_percentage_above_expected', Float),
        Column('toi', String(50)),
        Column('shots_against', Integer),
        Column('saves', Integer),
        Column('sv_percentage', Float),
        Column('gsaa', Float),
        Column('xg_against', Float),
        Column('hd_shots_against', Integer),
        Column('hd_saves', Integer),
        Column('hd_goals_against', Integer),
        Column('hd_sv_percentage', Float),
        Column('hd_gaa', Float),
        Column('hd_gsaa', Float),
        Column('rush_attempts_against', Integer),
        Column('rebound_attempts_against', Integer),
        Column('avg_shot_distance', Float),
        Column('avg_goal_distance', Float),
        Column('created_at', DateTime, server_default=func.current_timestamp())
    )
    metadata.create_all(engine)

# Check if table exists and create if not
def ensure_table_exists(engine):
    inspector = inspect(engine)
    if not inspector.has_table('goalies'):
        create_goalies_table(engine)

# Function to process and load data
def load_data_to_db(file_path, source, season_type, year):
    df = pd.read_csv(file_path)
    df['source'] = source
    df['season_type'] = season_type
    df['year'] = year
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('%', 'percentage')
    df.rename(columns={
        'name': 'player_name', 
        'player': 'player_name', 
        'gp': 'games_played',
        'sv%': 'sv_percentage',
        'hdsv%': 'hd_sv_percentage',
        'icetime_(minutes)': 'icetime_minutes',
        'low_danger_unblocked_shot_attempt_save%_above_expected': 'low_danger_unblocked_shot_attempt_save_percentage_above_expected',
        'medium_danger_unblocked_shot_attempt_save%_above_expected': 'medium_danger_unblocked_shot_attempt_save_percentage_above_expected',
        'high_danger_unblocked_shot_attempt_save%_above_expected': 'high_danger_unblocked_shot_attempt_save_percentage_above_expected',
        'goals_against.1': 'goals_against_1'
    }, inplace=True)

    # Convert percentage strings to floats
    percentage_columns = [
        'percent_shot_attempts_blocked_by_teammates', 
        'percent_unblocked_shot_attempts_against_on_goal', 
        'expected_percent_unblocked_shot_attempts_against_on_goal', 
        'on_goal_percentage_above_expected'
    ]
    
    for col in percentage_columns:
        if col in df.columns:
            df[col] = df[col].str.rstrip('%').astype(float) / 100

    # Ensure the dataframe has all the columns defined in the table schema
    required_columns = [
        'source', 'season_type', 'year', 'player_name', 'team', 'games_played', 'goals_against',
        'expected_goals_against', 'goals_saved_above_expected', 'goals_saved_above_expected_per_60',
        'save_percentage_on_unblocked_shots', 'xsave_percentage_on_unblocked_shots',
        'save_percentage_above_expected', 'save_percentage_on_shots_on_goal', 'gaa', 'xgaa',
        'gaa_better_than_expected', 'wins_above_replacement', 'icetime_minutes', 'rebounds_per_save',
        'puck_freezes_per_save', 'goals_against_1', 'saves_on_shots_on_goal', 'saves_on_unblocked_shot_attempts',
        'percent_shot_attempts_blocked_by_teammates', 'percent_unblocked_shot_attempts_against_on_goal',
        'expected_percent_unblocked_shot_attempts_against_on_goal', 'on_goal_percentage_above_expected',
        'low_danger_unblocked_shot_attempt_save_percentage', 'xlow_danger_unblocked_shot_attempt_save_percentage',
        'low_danger_unblocked_shot_attempt_save_percentage_above_expected', 'medium_danger_unblocked_shot_attempt_save_percentage',
        'xmedium_danger_unblocked_shot_attempt_save_percentage', 'medium_danger_unblocked_shot_attempt_save_percentage_above_expected',
        'high_danger_unblocked_shot_attempt_save_percentage', 'xhigh_danger_unblocked_shot_attempt_save_percentage',
        'high_danger_unblocked_shot_attempt_save_percentage_above_expected', 'toi', 'shots_against', 'saves',
        'sv_percentage', 'gsaa', 'xg_against', 'hd_shots_against', 'hd_saves', 'hd_goals_against', 'hd_sv_percentage',
        'hd_gaa', 'hd_gsaa', 'rush_attempts_against', 'rebound_attempts_against', 'avg_shot_distance', 'avg_goal_distance',
        'created_at'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    
    df = df[required_columns]

    df.to_sql('goalies', engine, if_exists='append', index=False)

# Function to extract metadata from file name
def extract_metadata(file_name):
    parts = file_name.split('_')
    source = parts[0]
    season_type = parts[1].replace(' ', '_').lower()
    year = parts[2].split('.')[0]
    return source, season_type, year

# Ensure the table exists
ensure_table_exists(engine)

# Load data from mp directory
for file_name in os.listdir(MP_DIR):
    if file_name.endswith('.csv'):
        file_path = os.path.join(MP_DIR, file_name)
        source, season_type, year = extract_metadata(file_name)
        load_data_to_db(file_path, source, season_type, year)

# Load data from nst directory
for file_name in os.listdir(NST_DIR):
    if file_name.endswith('.csv'):
        file_path = os.path.join(NST_DIR, file_name)
        source, season_type, year = extract_metadata(file_name)
        load_data_to_db(file_path, source, season_type, year)

print("Data loading complete.")
