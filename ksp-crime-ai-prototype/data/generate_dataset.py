"""
Synthetic KSP Crime Dataset Generator
--------------------------------------
Generates a realistic (but entirely fictional) crime records dataset for
prototype/demo purposes only. No real FIR data, real persons, or real
locations are used. All names, IDs, and addresses are randomly generated.

Run: python3 generate_dataset.py
Output: writes JSON files into ../data_seed/ (firs.json, accused.json,
victims.json, locations.json, links.json)
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

OUT_DIR = Path(__file__).parent / "data_seed"
OUT_DIR.mkdir(exist_ok=True)

# ---- Reference lists (fictional, for demo realism only) ----
STATIONS = [
    "Cubbon Park PS", "Whitefield PS", "Yeshwanthpur PS", "Jayanagar PS",
    "Indiranagar PS", "Rajajinagar PS", "KR Puram PS", "Basavanagudi PS",
    "Malleshwaram PS", "HSR Layout PS",
]
AREAS = [
    ("Cubbon Park", 12.9763, 77.5929), ("Whitefield", 12.9698, 77.7500),
    ("Yeshwanthpur", 13.0284, 77.5540), ("Jayanagar", 12.9308, 77.5838),
    ("Indiranagar", 12.9719, 77.6412), ("Rajajinagar", 12.9915, 77.5527),
    ("KR Puram", 13.0068, 77.6970), ("Basavanagudi", 12.9422, 77.5738),
    ("Malleshwaram", 13.0035, 77.5709), ("HSR Layout", 12.9116, 77.6389),
]
CRIME_TYPES = [
    "Chain Snatching", "Vehicle Theft", "Burglary", "Cybercrime - Financial Fraud",
    "Assault", "Cheating & Forgery", "Drug Peddling (NDPS)", "Robbery",
    "Extortion", "Missing Person",
]
MODUS_OPERANDI = {
    "Chain Snatching": "Two-wheeler borne, target lone pedestrian, snatch and flee",
    "Vehicle Theft": "Duplicate key / lock picking, targets parked two-wheelers",
    "Burglary": "Entry via rear window during working hours, house left unattended",
    "Cybercrime - Financial Fraud": "OTP/phishing call impersonating bank official",
    "Assault": "Altercation escalating from personal dispute",
    "Cheating & Forgery": "Fake investment scheme via social media",
    "Drug Peddling (NDPS)": "Small-quantity street-level sale near college campus",
    "Robbery": "Group of 2-3, knife shown, cash/phone taken",
    "Extortion": "Threat calls demanding money citing past dispute",
    "Missing Person": "Left home voluntarily / last seen near bus stand",
}
CASE_STATUS = ["Under Investigation", "Chargesheet Filed", "Case Closed - Convicted",
               "Case Closed - Acquitted", "Pending Court Trial"]
GENDERS = ["Male", "Female"]
OCCUPATIONS = ["Daily wage worker", "Auto driver", "Student", "IT employee",
               "Shopkeeper", "Unemployed", "Delivery agent", "Private security guard"]
FIRST_NAMES_M = ["Ravi", "Suresh", "Manjunath", "Naveen", "Praveen", "Ganesh",
                  "Anil", "Vinay", "Srinivas", "Gopal", "Shivkumar", "Dilip"]
FIRST_NAMES_F = ["Lakshmi", "Sunita", "Kavya", "Deepa", "Anitha", "Radha",
                  "Shalini", "Pooja", "Bhavana", "Geeta"]
LAST_NAMES = ["Kumar", "Reddy", "Gowda", "Naidu", "Shetty", "Rao", "Iyer", "Patil"]

def rand_name(gender):
    fn = random.choice(FIRST_NAMES_M if gender == "Male" else FIRST_NAMES_F)
    return f"{fn} {random.choice(LAST_NAMES)}"

def rand_date(start_days_ago=730, end_days_ago=0):
    d = random.randint(end_days_ago, start_days_ago)
    return (datetime(2026, 7, 20) - timedelta(days=d)).strftime("%Y-%m-%d")

def rand_phone():
    return f"9{random.randint(100000000, 999999999)}"

N_FIRS = 220
N_REPEAT_OFFENDERS = 14  # some accused appear in multiple FIRs -> creates network structure

# ---- Build a pool of "repeat offenders" first so they can recur across FIRs ----
repeat_offenders = []
for i in range(N_REPEAT_OFFENDERS):
    gender = random.choice(GENDERS)
    repeat_offenders.append({
        "accused_id": f"ACC{1000+i}",
        "name": rand_name(gender),
        "age": random.randint(18, 45),
        "gender": gender,
        "occupation": random.choice(OCCUPATIONS),
        "phone": rand_phone(),
        "prior_convictions": random.randint(1, 5),
    })

firs, accused_all, victims_all, locations_all, links = [], [], [], [], []
accused_index = {a["accused_id"]: a for a in repeat_offenders}
next_acc_id = 2000

for i in range(N_FIRS):
    fir_id = f"FIR/{2024 + i // 120}/{1000 + i}"
    area_name, lat, lng = random.choice(AREAS)
    crime_type = random.choice(CRIME_TYPES)
    station = random.choice(STATIONS)
    date = rand_date()
    status = random.choices(CASE_STATUS, weights=[35, 20, 15, 10, 20])[0]

    loc_id = f"LOC{1000+i}"
    locations_all.append({
        "location_id": loc_id, "area": area_name, "latitude": lat + random.uniform(-0.01, 0.01),
        "longitude": lng + random.uniform(-0.01, 0.01), "station": station,
    })

    # victim
    v_gender = random.choice(GENDERS)
    victim_id = f"VIC{1000+i}"
    victims_all.append({
        "victim_id": victim_id, "name": rand_name(v_gender), "age": random.randint(16, 70),
        "gender": v_gender, "occupation": random.choice(OCCUPATIONS),
    })

    # accused: 30% chance pull from repeat-offender pool (creates network links), else new
    if repeat_offenders and random.random() < 0.35:
        acc = random.choice(repeat_offenders)
        acc_id = acc["accused_id"]
    else:
        gender = random.choice(GENDERS)
        acc_id = f"ACC{next_acc_id}"
        next_acc_id += 1
        new_acc = {
            "accused_id": acc_id, "name": rand_name(gender), "age": random.randint(18, 55),
            "gender": gender, "occupation": random.choice(OCCUPATIONS),
            "phone": rand_phone(), "prior_convictions": random.choice([0, 0, 0, 1]),
        }
        accused_index[acc_id] = new_acc
        accused_all.append(new_acc)

    firs.append({
        "fir_id": fir_id, "date": date, "crime_type": crime_type,
        "modus_operandi": MODUS_OPERANDI[crime_type], "station": station,
        "location_id": loc_id, "victim_id": victim_id, "accused_id": acc_id,
        "status": status,
        "narrative": f"On {date}, a case of {crime_type.lower()} was reported at {station} "
                     f"in the {area_name} area. {MODUS_OPERANDI[crime_type]}. "
                     f"Investigation status: {status}.",
    })
    links.append({"fir_id": fir_id, "accused_id": acc_id, "victim_id": victim_id, "location_id": loc_id})

accused_all = repeat_offenders + accused_all

with open(OUT_DIR / "firs.json", "w") as f: json.dump(firs, f, indent=2)
with open(OUT_DIR / "accused.json", "w") as f: json.dump(accused_all, f, indent=2)
with open(OUT_DIR / "victims.json", "w") as f: json.dump(victims_all, f, indent=2)
with open(OUT_DIR / "locations.json", "w") as f: json.dump(locations_all, f, indent=2)
with open(OUT_DIR / "links.json", "w") as f: json.dump(links, f, indent=2)

print(f"Generated {len(firs)} FIRs, {len(accused_all)} accused ({N_REPEAT_OFFENDERS} repeat offenders), "
      f"{len(victims_all)} victims, {len(locations_all)} locations.")
print(f"Output written to: {OUT_DIR}")
