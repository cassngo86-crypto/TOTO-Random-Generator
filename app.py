import streamlit as st
import random
from collections import Counter
from itertools import combinations

# 1. Historical Data (Draws 4153 to 4183) to calculate pair weights
HISTORICAL_DRAWS = [
    [11, 12, 24, 33, 38, 46],# 4185
    [11, 18, 25, 36, 39, 49],# 4184
    [7, 18, 32, 37, 41, 44], # 4183
    [4, 8, 21, 25, 43, 46],  # 4182
    [6, 10, 25, 26, 34, 40], # 4181
    [2, 3, 8, 16, 20, 47],   # 4180
    [7, 18, 19, 30, 36, 48], # 4179
    [2, 6, 7, 31, 35, 39],   # 4178
    [3, 11, 13, 22, 28, 48], # 4177
    [3, 5, 15, 23, 37, 42],  # 4176
    [3, 5, 9, 23, 43, 49],   # 4175
    [1, 3, 6, 12, 21, 41],   # 4174
    [4, 8, 10, 15, 16, 26],  # 4173
    [1, 2, 6, 9, 44, 48],    # 4172
    [14, 23, 29, 30, 39, 48],# 4171
    [1, 7, 8, 23, 30, 33],   # 4170
    [4, 12, 26, 30, 46, 47], # 4169
    [4, 7, 22, 29, 33, 46],  # 4168
    [4, 25, 28, 33, 43, 48], # 4167
    [3, 27, 34, 35, 38, 49], # 4166
    [6, 14, 18, 22, 35, 36], # 4165
    [12, 25, 33, 40, 43, 46],# 4164
    [7, 13, 14, 17, 40, 44], # 4163
    [1, 5, 12, 15, 22, 42],  # 4162
    [6, 8, 28, 37, 41, 49],  # 4161
    [5, 9, 20, 23, 45, 46],  # 4160
    [24, 26, 30, 32, 37, 47],# 4159
    [8, 16, 17, 34, 38, 48], # 4158
    [13, 24, 28, 34, 37, 44],# 4157
    [10, 15, 25, 43, 45, 49],# 4156
    [10, 15, 29, 31, 33, 49],# 4155
    [6, 18, 24, 26, 36, 48], # 4154
    [4, 19, 40, 41, 46, 47]  # 4153
]

# 2. Define macro-tier pools
HOT_POOL = [3, 4, 6, 15, 23, 30, 43, 48]
COLD_POOL = [11, 19, 20, 21, 27, 36]
WARM_POOL = [n for n in range(1, 50) if n not in HOT_POOL and n not in COLD_POOL]

def calculate_pair_weights(draws):
    """Generates a dictionary mapping each number to its most frequent partners."""
    pair_counts = Counter()
    for draw in draws:
        for pair in combinations(sorted(draw), 2):
            pair_counts[pair] += 1
            
    partner_map = {}
    for (n1, n2), count in pair_counts.items():
        if count >= 2:  # Only consider pairs that happened 2+ times
            partner_map.setdefault(n1, []).append((n2, count))
            partner_map.setdefault(n2, []).append((n1, count))
            
    return partner_map

# Run calculation once on script startup
PARTNER_WEIGHTS = calculate_pair_weights(HISTORICAL_DRAWS)

def is_balanced(combination):
    """Validation guardrails for sum and odd/even distribution."""
    total_sum = sum(combination)
    evens = len([n for n in combination if n % 2 == 0])
    
    if not (90 <= total_sum <= 196):
        return False
    if evens in [0, 1, 5, 6]:
        return False
    return True

def generate_pair_weighted_pick():
    """Generates a combination seeded by a strong historical pair constraint."""
    while True:
        anchor = random.choice(HOT_POOL)
        ticket = [anchor]
        
        has_partners = anchor in PARTNER_WEIGHTS and len(PARTNER_WEIGHTS[anchor]) > 0
        
        if has_partners:
            partners = PARTNER_WEIGHTS[anchor]
            weights = [p[1] for p in partners]
            chosen_partner = random.choices([p[0] for p in partners], weights=weights, k=1)[0]
            ticket.append(chosen_partner)
        
        while len(ticket) < 6:
            current_hot = [n for n in ticket if n in HOT_POOL]
            current_cold = [n for n in ticket if n in COLD_POOL]
            
            if len(current_hot) < 1:
                pool = [n for n in HOT_POOL if n not in ticket]
            elif len(current_cold) < 1:
                pool = [n for n in COLD_POOL if n not in ticket]
            else:
                pool = [n for n in WARM_POOL if n not in ticket]
                
            if not pool: 
                pool = [n for n in range(1, 50) if n not in ticket]
                
            ticket.append(random.choice(pool))
            
        final_combination = sorted(ticket)
        if is_balanced(final_combination):
            return final_combination

# --- STREAMLIT UI LAYOUT ---
st.set_page_config(page_title="Advanced TOTO Generator", page_icon="🎯", layout="centered")

st.title("🎯 Co-Occurrence Pair TOTO Generator")
st.markdown("""
This model constructs 6-number combinations using a **weighted random sampling** approach:
* **Seeded Strategy:** Pairs are anchored using historically frequent co-occurrence numbers (Draws 4153–4183).
* **Portfolio Constraints:** Targets a distribution of **1 Hot, 4 Warm, and 1 Cold** number.
* **Structural Guardrails:** Rejects extreme odd/even balances and limits the total ticket sum to between **100 and 175**.
""")

st.write("---")

# User Interactive Controls
num_tickets = st.slider("Select number of combinations to generate:", min_value=1, max_value=10, value=3)

if st.button("Generate Numbers", type="primary"):
    st.subheader("Your Generated Selection:")
    
    for i in range(num_tickets):
        ticket = generate_pair_weighted_pick()
        
        # Calculate individual ticket analytics for the user
        ticket_sum = sum(ticket)
        evens = len([n for n in ticket if n % 2 == 0])
        odds = 6 - evens
        
        # Turn the numbers into visual pill format strings
        formatted_numbers = "   ".join([f"`[{n:02d}]`" for n in ticket])
        
        # Display results cleanly inside standard UI containers
        st.info(f"**Set {i+1}:** {formatted_numbers} | **Sum:** {ticket_sum} | **Split (O/E):** {odds}:{evens}")
        
    st.balloons()
