import json
import random
import os
import json
import random

def generate_curriculum(num_items_per_skill=15):
    curriculum = []
    
    # Localized vocabulary for generation
    items = [
        {"en": "mangoes", "fr": "mangues", "kin": "imyembe", "img_prefix": "mangoes"},
        {"en": "goats", "fr": "chèvres", "kin": "ihene", "img_prefix": "goats"},
        {"en": "cows", "fr": "vaches", "kin": "inka", "img_prefix": "cows"},
        {"en": "tomatoes", "fr": "tomates", "kin": "inyanya", "img_prefix": "tomatoes"}
    ]

    # Counting (Age 5-6, Diff 1-3)
    for i in range(1, num_items_per_skill + 1):
        obj = random.choice(items)
        count = random.randint(2, 10)
        curriculum.append({
            "id": f"C{i:03d}",
            "skill": "counting",
            "difficulty": random.randint(1, 3),
            "age_band": "5-6",
            "stem_en": f"How many {obj['en']}?",
            "stem_fr": f"Combien de {obj['fr']}?",
            "stem_kin": f"{obj['kin'].capitalize()} zingahe?", # Simplified kin phrasing for counting
            "visual": f"{obj['img_prefix']}_{count}",
            "answer_int": count,
            "tts_en": f"tts/en/c{i:03d}.wav",
            "tts_fr": f"tts/fr/c{i:03d}.wav",
            "tts_kin": f"tts/kin/c{i:03d}.wav"
        })

    # Number Sense (Age 6-8, Diff 2-5)
    for i in range(1, num_items_per_skill + 1):
        n1, n2 = random.sample(range(1, 20), 2)
        ans = max(n1, n2)
        curriculum.append({
            "id": f"N{i:03d}",
            "skill": "number_sense",
            "difficulty": random.randint(2, 5),
            "age_band": "6-7" if ans <= 10 else "7-8",
            "stem_en": f"Which number is bigger: {n1} or {n2}?",
            "stem_fr": f"Quel nombre est plus grand: {n1} ou {n2}?",
            "stem_kin": f"Ni iyihe nimero nini: {n1} cyangwa {n2}?",
            "visual": f"compare_{n1}_{n2}",
            "answer_int": ans
        })

    # Addition (Age 6-9, Diff 3-8)
    for i in range(1, num_items_per_skill + 1):
        n1, n2 = random.randint(1, 20), random.randint(1, 20)
        ans = n1 + n2
        curriculum.append({
            "id": f"A{i:03d}",
            "skill": "addition",
            "difficulty": min(8, (n1 + n2) // 5 + 2),
            "age_band": "6-7" if ans <= 10 else ("7-8" if ans <= 20 else "8-9"),
            "stem_en": f"{n1} plus {n2} equals?",
            "stem_fr": f"{n1} plus {n2} égale?",
            "stem_kin": f"{n1} + {n2} ni angahe?",
            "visual": f"add_{n1}_{n2}",
            "answer_int": ans
        })

    # Subtraction (Age 7-9, Diff 3-9)
    for i in range(1, num_items_per_skill + 1):
        n1 = random.randint(5, 50)
        n2 = random.randint(1, n1 - 1)
        ans = n1 - n2
        curriculum.append({
            "id": f"S{i:03d}",
            "skill": "subtraction",
            "difficulty": min(9, n1 // 5 + 2),
            "age_band": "7-8" if n1 <= 15 else "8-9",
            "stem_en": f"{n1} minus {n2} equals?",
            "stem_fr": f"{n1} moins {n2} égale?",
            "stem_kin": f"{n1} - {n2} ni angahe?",
            "visual": f"sub_{n1}_{n2}",
            "answer_int": ans
        })

    # Word Problems (Age 8-9, Diff 5-9)
    for i in range(1, num_items_per_skill + 1):
        obj = random.choice(items)
        n1 = random.randint(10, 50)
        n2 = random.randint(2, 9)
        ans = n1 + n2
        curriculum.append({
            "id": f"W{i:03d}",
            "skill": "word_problem",
            "difficulty": random.randint(5, 9),
            "age_band": "8-9",
            "stem_en": f"You have {n1} {obj['en']} and find {n2} more. How many {obj['en']} do you have?",
            "stem_fr": f"Tu as {n1} {obj['fr']} et tu en trouves {n2} de plus. Combien de {obj['fr']} as-tu?",
            "stem_kin": f"Ufite {obj['kin']} {n1} ukabona izindi {n2}. Ubu ufite {obj['kin']} zingahe?",
            "visual": f"wp_add_{n1}_{n2}_{obj['img_prefix']}",
            "answer_int": ans
        })

    return curriculum

# Generate and output to JSON



full_dataset = generate_curriculum(15)

# Define the path
output_dir = "data/T3.1_Math_Tutor"
output_file = os.path.join(output_dir, "curriculum_full.json")

# Create the directories if they don't exist
os.makedirs(output_dir, exist_ok=True)

# Save the file
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(full_dataset, f, indent=2, ensure_ascii=False)

print(f"Successfully generated {len(full_dataset)} curriculum items.")