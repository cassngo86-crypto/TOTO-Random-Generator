import streamlit as st
import random
from collections import Counter
from itertools import combinations

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Advanced TOTO Generator", page_icon="🎯", layout="centered")

# Initialize HISTORICAL_DRAWS in session state so it persists and updates dynamically
if "historical_draws" not in st.session_state:
    st.session_state.historical_draws = [
        [11, 12, 24, 33, 38, 46], # 4185
        [11, 18, 25, 36, 39, 49], # 4184
        [7, 18, 32, 37, 41, 44],  # 4183
        [4, 8, 21, 25, 43, 46],   # 4182
        [6, 10, 25, 26, 34, 40],  # 4181
        [2, 3, 8, 16, 20, 47],    # 4180
        [7, 18, 19, 30, 36, 48],  # 4179
        [2, 6, 7, 31, 35, 39],    # 4178
        [3, 11, 13, 22, 28, 48],  # 4177
        [3, 5, 15, 23, 37, 42],   # 4176
        [3, 5, 9, 23, 43, 49],    # 4175
        [1, 3, 6, 12, 21, 41],    # 4174
        [4, 8, 10, 15, 16, 26],   # 4173
        [1, 2, 6, 9, 44, 48],     # 4172
        [14, 23, 29, 30, 39, 48], # 4171
        [1, 7, 8, 23, 30, 33],    # 4170
        [4, 12, 26, 30, 46, 47],  # 4169
        [4, 7, 22, 29, 33, 46],   # 4168
        [4, 25, 28, 33, 43, 48],  # 4167
        [3, 27, 34, 35, 38, 49],  # 4166
        [6, 14, 18, 22, 35, 36],  # 4165
        [12, 25, 33, 40, 43, 46], # 4164
        [7, 13, 14, 17, 40, 44],  # 4163
        [1, 5, 12, 15, 22, 42],   # 4162
        [6, 8, 28, 37, 41, 49],   # 4161
        [5, 9, 20, 23, 45, 46],   # 4160
        [24, 26, 30, 32, 37, 47], # 4159
        [8, 16, 17, 34, 38, 48],  # 4158
        [13, 24, 28, 34, 37, 44], # 4157
        [10, 15, 25, 43, 45, 49], # 4156
        [10, 15, 29, 31, 33, 49], # 4155
        [6, 18, 24, 26, 36, 48],  # 4154
        [4, 19, 40, 41, 46, 47]   # 4153
    ]

# --- SIDEBAR: DYNAMIC DATA ENTRY ---
st.sidebar.header("📝 Update Draw Data")
st.sidebar.write("Add the latest winning numbers to immediately update the data engine:")

# Numeric Inputs for the 6 numbers
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
    else:
        # Prepend to the top of our state list
        st.session_state.historical_draws.insert(0, new_draw)
        st.sidebar.success(f"Success! Added Draw: {new_draw}")

# Show total tracked dataset size
st.sidebar.info(f"Total historical draws tracked: {len(st.session_state.historical_draws)}")

# --- AUTOMATED ENGINE CALCULATIONS ---
def process_lottery_analytics(draws):
    """Calculates pools and weights dynamically based on updated historical draws."""
    # 1. Flatten all elements to aggregate frequency counts
    all_numbers = [num for draw in draws for num in draw]
    frequency_map = Counter(all_numbers)
    
    # 2. Derive Macro-pools dynamically based on criteria
    hot_pool = [n for n in range(1, 50) if frequency_map[n] >= 6]
    cold_pool = [n for n in range(1, 50) if frequency_map[n] <= 2]
    warm_pool = [n for n in range(1, 50) if n not in hot_pool and n not in cold_pool]
    
    # 3. Derive Co-occurrence Pair Matrix
    pair_counts = Counter()
    for draw in draws:
        for pair in combinations(sorted(draw), 2):
            pair_counts[pair] += 1
            
    partner_map = {}
    for (num1, num2), count in pair_counts.items():
        if count >= 2:
            partner_map.setdefault(num1, []).append((num2, count))
            partner_map.setdefault(num2, []).append((num1, count))
            
    return hot_pool, warm_pool, cold_pool, partner_map

# Run automated pipeline on current active state data
HOT_POOL, WARM_POOL, COLD_POOL, PARTNER_WEIGHTS = process_lottery_analytics(st.session_state.historical_draws)

# --- VALIDATION ENGINE ---
def is_balanced(combination):
    """Validation guardrails for sum and odd/even distribution."""
    total_sum = sum(combination)
    evens = len([n for n in combination if n % 2 == 0])
    
    # Dynamic guardrails mapping the global limits of your dataset 
    if not (84 <= total_sum <= 199):
        return False
    if evens in [0, 1, 5, 6]:
        return False
    return True
#
def generate_pair_weighted_pick():
    """Generates a combination seeded by a strong historical pair constraint."""
    # Prevent crashing if automated calculations empty out specific strategy segments
    active_hot = HOT_POOL if HOT_POOL else [3, 4, 6, 8, 15, 23, 30, 43, 46, 48]
    active_cold = COLD_POOL if COLD_POOL else [2, 9, 17, 20, 21, 29, 27, 31, 40, 42, 45]
    active_warm = WARM_POOL if WARM_POOL else [n for n in range(1, 50) if n not in active_hot and n not in active_cold]

    while True:
        anchor = random.choice(active_hot)
        ticket = [anchor]
        
        has_partners = anchor in PARTNER_WEIGHTS and len(PARTNER_WEIGHTS[anchor]) > 0
        
        if has_partners:
            partners = PARTNER_WEIGHTS[anchor]
            weights = [p[1] for p in partners]
            chosen_partner = random.choices([p[0] for p in partners], weights=weights, k=1)[0]
            ticket.append(chosen_partner)
        
        # Step C: Fill the remaining slots dynamically from remaining macro-pools
        while len(ticket) < 6:
            current_hot = [n for n in ticket if n in active_hot]
            current_cold = [n for n in ticket if n in active_cold]
            
            # Determine which pool to draw from based on probabilities and current counts
            if len(current_hot) < 1 and random.random() < 0.30:  # 30% chance to anchor a hot number
                pool = [n for n in active_hot if n not in ticket]
            elif len(current_cold) < 2 and random.random() < 0.40:  # 40% chance to pick a cold number
                pool = [n for n in active_cold if n not in ticket]
            else:
                pool = [n for n in active_warm if n not in ticket]
                
            # Safety fallback: if the chosen pool ended up empty, default to warm or any available numbers
            if not pool: 
                pool = [n for n in active_warm if n not in ticket]
            if not pool: 
                pool = [n for n in range(1, 50) if n not in ticket]
                
            ticket.append(random.choice(pool))
            
        final_combination = sorted(ticket)
        if is_balanced(final_combination):
            return final_combination
            
# --- WEB APP MAIN LAYOUT UI ---
st.title("🎯 Co-Occurrence Pair TOTO Generator")
st.markdown("""
This model constructs 6-number combinations dynamically using an **automated engine** built on your rules:
* 🔥 **Hot Numbers:** Automatically identified when appearing **$\ge 6$ times** in active data.
* ❄️ **Cold Numbers:** Automatically identified when appearing **$\le 2$ times** in active data.
* 📈 **Warm Numbers:** Everything else in between.
""")

# Dashboard Metrics Preview Expander
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
        ticket_ave = average(ticket)
        evens = len([n for n in ticket if n % 2 == 0])
        odds = 6 - ev
        
        formatted_numbers = "   ".join([f"`[{n:02d}]`" for n in ticket])
        st.info(f"**Set {i+1}:** {formatted_numbers} | **Sum:** {ticket_sum}| **Average:** {ticket_ave} | **Split (O/E):** {odds}:{evens}")
        
    st.balloons()
