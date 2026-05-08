import sqlite3
import random
import statistics

# 1. Setup SQLite connection in your current folder
db_name = 'choredistro_ml_dataset.db'
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Create the streamlined table schema
cursor.execute('''
    CREATE TABLE IF NOT EXISTS chore_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chore_name TEXT,
        chore_difficulty INTEGER,
        zain_pts INTEGER,
        jasmine_pts INTEGER,
        justin_pts INTEGER,
        chloe_pts INTEGER,
        assigned_to TEXT
    )
''')

# Clear any existing data so you get a fresh 4000 rows each time
cursor.execute('DELETE FROM chore_assignments')

# 2. Define the choreDistro variables
members = ['Zain', 'Jasmine', 'Justin', 'Chloe']
points_tracker = {member: 0 for member in members}
target_rows = 4000

# Chores mapped to the 10-100 difficulty scale
chores_by_difficulty = {
    10: ["Wipe Counters", "Water Plants", "Check Mail"],
    20: ["Empty Dishwasher", "Sweep Kitchen", "Take out Trash"],
    30: ["Vacuum Living Room", "Clean Mirrors", "Dust Shelves"],
    40: ["Clean Bathroom Sink", "Fold Laundry", "Mop Kitchen"],
    50: ["Clean Toilet", "Wash Car", "Clean Windows"],
    60: ["Cook Dinner", "Scrub Bathtub", "Organize Pantry"],
    70: ["Mow Lawn", "Clean Fridge", "Weed Garden"],
    80: ["Deep Clean Garage", "Shovel Snow", "Wash All Bedding"],
    90: ["Power Wash Driveway", "Clean Gutters", "Paint a Room"],
    100: ["Full Spring Cleaning", "Move Heavy Furniture", "Clear Attic"]
}

# 3. Generate the balanced data
for _ in range(target_rows):
    # Simulate a weekly reset (roughly every 20 chores assigned)
    if random.randint(1, 20) == 1:
        points_tracker = {member: 0 for member in members}

    # Pick a random difficulty and chore
    difficulty = random.randint(1, 10) * 10
    chore_name = random.choice(chores_by_difficulty[difficulty])

    # Figure out the perfect assignment to minimize point variance across the family
    best_member = None
    lowest_variance = float('inf')

    for member in members:
        # Create a temporary copy of the current scores to test the math
        test_points = list(points_tracker.values())
        member_idx = members.index(member)
        test_points[member_idx] += difficulty
        
        # Calculate the variance
        current_variance = statistics.variance(test_points)
        
        if current_variance < lowest_variance:
            lowest_variance = current_variance
            best_member = member

    # Insert the snapshot of everyone's points BEFORE the chore is added
    cursor.execute('''
        INSERT INTO chore_assignments (
            chore_name, chore_difficulty, zain_pts, jasmine_pts, justin_pts, chloe_pts, assigned_to
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        chore_name, 
        difficulty, 
        points_tracker['Zain'], 
        points_tracker['Jasmine'], 
        points_tracker['Justin'], 
        points_tracker['Chloe'], 
        best_member
    ))

    # Update the actual points tracker for the winner before looping to the next chore
    points_tracker[best_member] += difficulty

# 4. Inject Missing Values (NULLs) to simulate messy real-world data
cursor.execute("SELECT id FROM chore_assignments")
all_ids = [row[0] for row in cursor.fetchall()]

# Calculate 5% of your total rows
num_to_corrupt = int(len(all_ids) * 0.05)

# Randomly select IDs to receive missing values
difficulty_missing_ids = random.sample(all_ids, num_to_corrupt)
justin_pts_missing_ids = random.sample(all_ids, num_to_corrupt)

# Execute the updates (Setting values to NULL)
for row_id in difficulty_missing_ids:
    cursor.execute("UPDATE chore_assignments SET chore_difficulty = NULL WHERE id = ?", (row_id,))

for row_id in justin_pts_missing_ids:
    cursor.execute("UPDATE chore_assignments SET justin_pts = NULL WHERE id = ?", (row_id,))

# Save and close the database
conn.commit()
conn.close()

print(f"Success! {target_rows} optimized rows written to {db_name}.")
print(f"Injected NULL values into {num_to_corrupt} rows for difficulty and {num_to_corrupt} rows for Justin's points.")