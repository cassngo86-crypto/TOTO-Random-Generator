import streamlit as st
import random
import os
import requests
import base64
from collections import Counter
from itertools import combinations

# --- GITHUB REPOSITORY CONFIGURATION ---
# Replace these with your actual GitHub username and repository name
GITHUB_USER = "cassngo86-crypto "
GITHUB_REPO = "toto-random-generator"
FILE_PATH = "draws_database.txt"
# Pulls the secret token securely from your Streamlit dashboard settings
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")

DB_FILE = "draws_database.txt"

def load_draws():
    """Reads the saved draw history from the local text file fallback database."""
    if not os.path.exists(DB_FILE):
        return [[11, 12, 24, 33, 38, 46]]
    draws = []
    with open(DB_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                draws.append([int(x) for x in line.split(",")])
    return draws

def save_new_draw(new_draw_list):
    """Prepends a new draw result locally and pushes the file update to GitHub."""
    current_draws = load_draws()
    current_draws.insert(0, new_draw_list)
    
    # 1. Update the local container file copy
    file_content = ""
    for draw in current_draws:
        file_content += ",".join(map(str, draw)) + "\n"
        
    with open(DB_FILE, "w") as f:
        f.write(file_content)
        
    # 2. Push directly to GitHub using the GitHub API
    if GITHUB_TOKEN:
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{FILE_PATH}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # We need to get the file's current "sha" fingerprint to modify it
        res = requests.get(url, headers=headers)
        sha = res.json().get("sha", "") if res.status_code == 200 else ""
        
        # Package the commit payload
        payload = {
            "message": f"Automated update: Added draw {new_draw_list}",
            "content": base64.b64encode(file_content.encode("utf-8")).decode("utf-8"),
            "sha": sha
        }
        
        # Send the commit to your GitHub repository
        requests.put(url, json=payload, headers=headers)

# Initialize historical data in session state from the permanent file structure
if "historical_draws" not in st.session_state:
    st.session_state.historical_draws = load_draws()

# --- SIDEBAR: DYNAMIC DATA ENTRY ---
st.sidebar.header("📝 Update Draw Data")
st.sidebar.write("Add latest winning numbers to permanently save to text database:")

col1, col2, col3 = st.sidebar.columns(3)
with col1: n1 = st.number_input("Num 1", min_value=1, max_value=49, value=1)
with col2: n2 = st.number_input("Num 2", min_value=1, max_value=49, value=2)
with col3: n3 = st.number_input("Num 3", min_value=1, max_value=49, value=3)

col4, col5, col6 = st.sidebar.columns(3)
with col4: n4 = st.number_input("Num 4", min_value=1, max_value=49, value=4)
with col5: n5 = st.number_input("Num 5", min_value=1, max_value=49, value=5)
with col6: n6 = st.number_input("Num 6", min_value=1, max_value=49, value=6)

if st.sidebar.button("Add New Draw Result", use_container_width=True):
    new_draw = sorted(list(set([n1, n2, n3, n4, n5, n6])))
    if len(new_draw) != 6:
        st.sidebar.error("Error: Duplicate numbers detected. Please enter 6 unique numbers.")
    elif new_draw == st.session_state.historical_draws[0]:
        st.sidebar.warning("This exact draw is already registered as the latest result.")
    else:
        # Save to the text file database permanently
        save_new_draw(new_draw)
        # Reload state cache from file
        st.session_state.historical_draws = load_draws()
        st.sidebar.success(f"Saved permanently! Added Draw: {new_draw}")
        st.rerun()

# --- AUTOMATED ENGINE CALCULATIONS ---
def process_lottery_analytics(draws):
    all_numbers = [num for draw in draws for num in draw]
    frequency_map = Counter(all_numbers)
    
    hot_pool = [n for n in range(1, 50) if frequency_map[n] >= 8]
    cold_pool = [n for n in range(1, 50) if frequency_map[n] <= 3]
    warm_pool = [n for n in range(1, 50) if n not in hot_pool and n not in cold_pool]
    
    pair_counts = Counter()
    for draw in draws:
        for pair in combinations(sorted(draw), 2):
            pair_counts[pair] += 1
            
    partner_map = {}
    for num1, num2 in pair_counts.keys():
        count = pair_counts[(num1, num2)]
        if count >= 2:
            partner_map.setdefault(num1, []).append((num2, count))
            partner_map.setdefault(num2, []).append((num1, count))
            
    return hot_pool, warm_pool, cold_pool, partner_map

HOT_POOL, WARM_POOL, COLD_POOL, PARTNER_WEIGHTS = process_lottery_analytics(st.session_state.historical_draws)

# --- VALIDATION ENGINE ---
def is_balanced(combination):
    total_sum = sum(combination)
    evens = len([n for n in combination if n % 2 == 0])
    if not (84 <= total_sum <= 199):
        return False
    if evens in [0, 1, 5, 6]:
        return False
    return True

def generate_pair_weighted_pick():
    active_hot = HOT_POOL if HOT_POOL else [3, 4, 6, 8, 15, 23, 30, 43, 46, 48]
    active_cold = COLD_POOL if COLD_POOL else [2, 9, 17, 20, 21, 29, 27, 31, 40, 42, 45]
    active_warm = WARM_POOL if WARM_POOL else [n for n in range(1, 50) if n not in active_hot and n not in active_cold]

    previous_draw_numbers = st.session_state.historical_draws[0]

    while True:
        ticket = []
        
        # 1. FORCED REPEATER SEED (100% Guarantee)
        repeater_number = random.choice(previous_draw_numbers)
        ticket.append(repeater_number)

        # 2. TARGET STRATEGY COUNTS (20% Hot, 20% Cold, 60% Warm)
        while len(ticket) < 6:
            current_hot = [n for n in ticket if n in active_hot]
            current_cold = [n for n in ticket if n in active_cold]
            
            if len(current_hot) < 1:
                pool = [n for n in active_hot if n not in ticket]
            elif len(current_cold) < 1:
                pool = [n for n in active_cold if n not in ticket]
            else:
                pool = [n for n in active_warm if n not in ticket and n not in previous_draw_numbers]
                
            if not pool: 
                pool = [n for n in range(1, 50) if n not in ticket]
                
            ticket.append(random.choice(pool))
            
        final_combination = sorted(ticket)
        if is_balanced(final_combination):
            return final_combination

# --- WEB APP MAIN LAYOUT UI ---
st.title("🎯 Co-Occurrence Pair TOTO Generator")

latest_draw = st.session_state.historical_draws[0]
formatted_latest = " - ".join([f"{n:02d}" for n in latest_draw])

st.success(f"✅ **Database Status:** Connected | **Latest Tracked Draw:** `[ {formatted_latest} ]` | **Total History:** {len(st.session_state.historical_draws)} draws")

st.markdown("""
This model constructs 6-number combinations dynamically using an **automated engine**:
* 🔥 **Hot Pool:** Freq $\ge 6$ | ❄️ **Cold Pool:** Freq $\le 2$ | 📈 **Warm Pool:** Everything else (excluding previous draw numbers).
""")

with st.expander("📊 View Dynamically Calculated Frequency Pools", expanded=False):
    st.write(f"**Hot Pool ({len(HOT_POOL)} numbers):** `{sorted(HOT_POOL)}`")
    st.write(f"**Cold Pool ({len(COLD_POOL)} numbers):** `{sorted(COLD_POOL)}`")
    st.write(f"**Warm Pool ({len(WARM_POOL)} numbers):** `{sorted(WARM_POOL)}`")

st.write("---")

num_tickets = st.slider("Select number of combinations to generate:", min_value=1, max_value=10, value=3)

if st.button("Generate Numbers", type="primary"):
    st.subheader("Your Generated Selection:")
    
    for i in range(num_tickets):
        ticket = generate_pair_weighted_pick()
        ticket_sum = sum(ticket)
        ticket_ave = ticket_sum / len(ticket)
        evens = len([n for n in ticket if n % 2 == 0])
        odds = 6 - evens
        
        formatted_numbers = "   ".join([f"`[{n:02d}]`" for n in ticket])
        st.info(f"**Set {i+1}:** {formatted_numbers} | **Sum:** {ticket_sum} | **Avg:** {ticket_ave:.1f} | **Split (O/E):** {odds}:{evens}")
        
    st.balloons()
