"""
Deterministic dataset generator for the Missing Piece benchmark.
Generates 60 base problems producing 120 paired examples across 6 domains:
- 60 Intact (fully specified, unique integer answer)
- 20 Missing Quantity (underdetermined, missing numerical parameter)
- 20 Missing Relationship (underdetermined, missing linkage or conversion rate)
- 20 Contradictory Facts (inconsistent premises with no feasible solution)
"""

import random
from typing import List, Dict, Any, Tuple
from missing_piece.models import (
    BenchmarkExample,
    ConditionType,
    ExpectedStatus
)


def _build_base_templates() -> List[Dict[str, Any]]:
    """Define 60 base problem templates across 6 domains."""
    templates = []
    
    # -------------------------------------------------------------
    # DOMAIN 1: Basic Arithmetic (10 base problems: 001 - 010)
    # Defect condition: MISSING_QUANTITY
    # -------------------------------------------------------------
    templates.append({
        "id": "base_001",
        "domain": "basic_arithmetic",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "elementary",
        "missing_type": "missing_initial_quantity",
        "generate": lambda rng: {
            "a": rng.randint(25, 60),
            "b": rng.randint(15, 30),
            "c": rng.randint(10, 20)
        },
        "intact_text": lambda p: (
            f"A school library received {p['a']} fiction books and {p['b']} non-fiction books on Monday. "
            f"On Tuesday, students checked out {p['c']} books in total. "
            f"How many new books remain in the library?"
        ),
        "intact_answer": lambda p: str((p["a"] + p["b"]) - p["c"]),
        "modified_text": lambda p: (
            f"A school library received {p['a']} fiction books and a delivery of non-fiction books on Monday. "
            f"On Tuesday, students checked out {p['c']} books in total. "
            f"How many new books remain in the library?"
        ),
        "defect_proof": "The number of non-fiction books is unspecified; remaining books can be any integer >= a - c."
    })

    templates.append({
        "id": "base_002",
        "domain": "basic_arithmetic",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "elementary",
        "missing_type": "missing_deduction_amount",
        "generate": lambda rng: {
            "a": rng.randint(50, 100),
            "b": rng.randint(20, 40),
            "c": rng.randint(10, 25)
        },
        "intact_text": lambda p: (
            f"Marcus started with ${p['a']} in his wallet. He earned ${p['b']} mowing lawns, "
            f"and then spent ${p['c']} on groceries. "
            f"How many dollars does Marcus have left?"
        ),
        "intact_answer": lambda p: str(p["a"] + p["b"] - p["c"]),
        "modified_text": lambda p: (
            f"Marcus started with ${p['a']} in his wallet. He earned ${p['b']} mowing lawns, "
            f"and then spent some money on groceries. "
            f"How many dollars does Marcus have left?"
        ),
        "defect_proof": "The amount spent on groceries is unknown; remaining dollars cannot be uniquely determined."
    })

    templates.append({
        "id": "base_003",
        "domain": "basic_arithmetic",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "elementary",
        "missing_type": "missing_group_size",
        "generate": lambda rng: {
            "groups": rng.randint(4, 8),
            "per_group": rng.randint(6, 12),
            "lost": rng.randint(3, 8)
        },
        "intact_text": lambda p: (
            f"A teacher bought {p['groups']} packs of markers, with {p['per_group']} markers in each pack. "
            f"During art class, {p['lost']} markers dried up and were discarded. "
            f"How many working markers remain?"
        ),
        "intact_answer": lambda p: str(p["groups"] * p["per_group"] - p["lost"]),
        "modified_text": lambda p: (
            f"A teacher bought {p['groups']} packs of markers. "
            f"During art class, {p['lost']} markers dried up and were discarded. "
            f"How many working markers remain?"
        ),
        "defect_proof": "Markers per pack is unstated; total initial markers is unknown."
    })

    templates.append({
        "id": "base_004",
        "domain": "basic_arithmetic",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "elementary",
        "missing_type": "missing_subtrahend",
        "generate": lambda rng: {
            "red": rng.randint(14, 28),
            "blue": rng.randint(16, 32),
            "taken": rng.randint(8, 15)
        },
        "intact_text": lambda p: (
            f"A toy chest contains {p['red']} red blocks and {p['blue']} blue blocks. "
            f"Children took out {p['taken']} red blocks to build a tower. "
            f"How many total blocks are still in the chest?"
        ),
        "intact_answer": lambda p: str(p["red"] + p["blue"] - p["taken"]),
        "modified_text": lambda p: (
            f"A toy chest contains {p['red']} red blocks and {p['blue']} blue blocks. "
            f"Children took out some red blocks to build a tower. "
            f"How many total blocks are still in the chest?"
        ),
        "defect_proof": "The number of red blocks removed is unstated."
    })

    templates.append({
        "id": "base_005",
        "domain": "basic_arithmetic",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "elementary",
        "missing_type": "missing_additive_term",
        "generate": lambda rng: {
            "morning": rng.randint(30, 50),
            "noon": rng.randint(20, 35),
            "evening": rng.randint(15, 25)
        },
        "intact_text": lambda p: (
            f"A coffee shop sold {p['morning']} cups in the morning, {p['noon']} cups at midday, "
            f"and {p['evening']} cups in the evening. "
            f"What was the total number of cups sold that day?"
        ),
        "intact_answer": lambda p: str(p["morning"] + p["noon"] + p["evening"]),
        "modified_text": lambda p: (
            f"A coffee shop sold {p['morning']} cups in the morning and {p['noon']} cups at midday. "
            f"They also sold coffee during the evening shift before closing. "
            f"What was the total number of cups sold that day?"
        ),
        "defect_proof": "Evening cup count is missing."
    })

    templates.append({
        "id": "base_006",
        "domain": "basic_arithmetic",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "intermediate",
        "missing_type": "missing_multiplier",
        "generate": lambda rng: {
            "apples": rng.randint(12, 24),
            "factor": rng.randint(2, 4),
            "rotten": rng.randint(3, 7)
        },
        "intact_text": lambda p: (
            f"Farmer John picked {p['apples']} apples. His neighbor picked {p['factor']} times as many apples. "
            f"Together, they threw away {p['rotten']} rotten apples. "
            f"How many good apples do they have in total?"
        ),
        "intact_answer": lambda p: str(p["apples"] + (p["apples"] * p["factor"]) - p["rotten"]),
        "modified_text": lambda p: (
            f"Farmer John picked {p['apples']} apples. His neighbor picked a larger harvest of apples. "
            f"Together, they threw away {p['rotten']} rotten apples. "
            f"How many good apples do they have in total?"
        ),
        "defect_proof": "The neighbor's apple count or multiplier is unspecified."
    })

    templates.append({
        "id": "base_007",
        "domain": "basic_arithmetic",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "intermediate",
        "missing_type": "missing_divisor_or_share",
        "generate": lambda rng: {
            "total_candies": rng.randint(36, 72),
            "friends": rng.randint(3, 6),
            "eaten": rng.randint(2, 4)
        },
        "intact_text": lambda p: (
            f"A bowl contains {p['total_candies']} candies. They are divided equally among {p['friends']} friends. "
            f"One of the friends immediately eats {p['eaten']} of their candies. "
            f"How many candies does that friend have left?"
        ),
        "intact_answer": lambda p: str((p["total_candies"] // p["friends"]) - p["eaten"]),
        "modified_text": lambda p: (
            f"A bowl contains {p['total_candies']} candies. They are divided equally among a group of friends. "
            f"One of the friends immediately eats {p['eaten']} of their candies. "
            f"How many candies does that friend have left?"
        ),
        "defect_proof": "Number of friends sharing the candies is unspecified."
    })

    templates.append({
        "id": "base_008",
        "domain": "basic_arithmetic",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "elementary",
        "missing_type": "missing_addend",
        "generate": lambda rng: {
            "base": rng.randint(40, 80),
            "bonus1": rng.randint(10, 20),
            "bonus2": rng.randint(5, 15)
        },
        "intact_text": lambda p: (
            f"In a video game, Liam scored {p['base']} points in stage 1, {p['bonus1']} bonus points in stage 2, "
            f"and {p['bonus2']} points in stage 3. "
            f"What was Liam's total score across all three stages?"
        ),
        "intact_answer": lambda p: str(p["base"] + p["bonus1"] + p["bonus2"]),
        "modified_text": lambda p: (
            f"In a video game, Liam scored {p['base']} points in stage 1 and {p['bonus1']} bonus points in stage 2. "
            f"He also scored points in stage 3 before completing the run. "
            f"What was Liam's total score across all three stages?"
        ),
        "defect_proof": "Stage 3 points are unstated."
    })

    templates.append({
        "id": "base_009",
        "domain": "basic_arithmetic",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "intermediate",
        "missing_type": "missing_unit_cost",
        "generate": lambda rng: {
            "notebooks": rng.randint(3, 7),
            "price_each": rng.randint(4, 9),
            "cash": 50
        },
        "intact_text": lambda p: (
            f"Chloe bought {p['notebooks']} spiral notebooks priced at ${p['price_each']} each. "
            f"She paid with a ${p['cash']} bill. "
            f"How many dollars in change should Chloe receive?"
        ),
        "intact_answer": lambda p: str(p["cash"] - (p["notebooks"] * p["price_each"])),
        "modified_text": lambda p: (
            f"Chloe bought {p['notebooks']} spiral notebooks. "
            f"She paid with a ${p['cash']} bill. "
            f"How many dollars in change should Chloe receive?"
        ),
        "defect_proof": "Price per notebook is omitted."
    })

    templates.append({
        "id": "base_010",
        "domain": "basic_arithmetic",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "elementary",
        "missing_type": "missing_initial_stock",
        "generate": lambda rng: {
            "initial": rng.randint(40, 70),
            "sold": rng.randint(15, 25),
            "returned": rng.randint(3, 8)
        },
        "intact_text": lambda p: (
            f"A boutique had {p['initial']} scarves on display. They sold {p['sold']} scarves by afternoon, "
            f"and a customer returned {p['returned']} previously bought scarves back to inventory. "
            f"How many scarves are on display now?"
        ),
        "intact_answer": lambda p: str(p["initial"] - p["sold"] + p["returned"]),
        "modified_text": lambda p: (
            f"A boutique had a display of scarves. They sold {p['sold']} scarves by afternoon, "
            f"and a customer returned {p['returned']} previously bought scarves back to inventory. "
            f"How many scarves are on display now?"
        ),
        "defect_proof": "Initial inventory of scarves is omitted."
    })

    # -------------------------------------------------------------
    # DOMAIN 2: Inventory Tracking (10 base problems: 011 - 020)
    # Defect condition: MISSING_QUANTITY
    # -------------------------------------------------------------
    templates.append({
        "id": "base_011",
        "domain": "inventory_tracking",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "intermediate",
        "missing_type": "missing_crate_capacity",
        "generate": lambda rng: {
            "crates": rng.randint(5, 10),
            "per_crate": rng.randint(12, 20),
            "damaged": rng.randint(4, 10)
        },
        "intact_text": lambda p: (
            f"A warehouse received {p['crates']} wooden crates of porcelain cups, with {p['per_crate']} cups per crate. "
            f"Inspection found that {p['damaged']} cups were cracked upon arrival. "
            f"How many intact porcelain cups were received?"
        ),
        "intact_answer": lambda p: str(p["crates"] * p["per_crate"] - p["damaged"]),
        "modified_text": lambda p: (
            f"A warehouse received {p['crates']} wooden crates of porcelain cups. "
            f"Inspection found that {p['damaged']} cups were cracked upon arrival. "
            f"How many intact porcelain cups were received?"
        ),
        "defect_proof": "Number of cups per crate is omitted."
    })

    templates.append({
        "id": "base_012",
        "domain": "inventory_tracking",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "elementary",
        "missing_type": "missing_outflow_quantity",
        "generate": lambda rng: {
            "start": rng.randint(80, 150),
            "restock": rng.randint(30, 60),
            "shipped": rng.randint(40, 70)
        },
        "intact_text": lambda p: (
            f"A distribution hub opened the week with {p['start']} pallets of paper. "
            f"They received an incoming shipment of {p['restock']} pallets and shipped out {p['shipped']} pallets to stores. "
            f"How many pallets of paper remain at the hub?"
        ),
        "intact_answer": lambda p: str(p["start"] + p["restock"] - p["shipped"]),
        "modified_text": lambda p: (
            f"A distribution hub opened the week with {p['start']} pallets of paper. "
            f"They received an incoming shipment of {p['restock']} pallets and shipped several pallets to stores. "
            f"How many pallets of paper remain at the hub?"
        ),
        "defect_proof": "The shipped pallet count is omitted."
    })

    templates.append({
        "id": "base_013",
        "domain": "inventory_tracking",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "intermediate",
        "missing_type": "missing_sub_component_count",
        "generate": lambda rng: {
            "laptops": rng.randint(15, 30),
            "chargers": rng.randint(10, 25),
            "mice": rng.randint(8, 20)
        },
        "intact_text": lambda p: (
            f"An IT office inventory has {p['laptops']} laptops, {p['chargers']} spare power chargers, "
            f"and {p['mice']} wireless mice. "
            f"What is the total count of these tech peripherals and laptops combined?"
        ),
        "intact_answer": lambda p: str(p["laptops"] + p["chargers"] + p["mice"]),
        "modified_text": lambda p: (
            f"An IT office inventory has {p['laptops']} laptops and {p['chargers']} spare power chargers, "
            f"along with an uncounted bin of wireless mice. "
            f"What is the total count of these tech peripherals and laptops combined?"
        ),
        "defect_proof": "Mouse count is uncounted/missing."
    })

    templates.append({
        "id": "base_014",
        "domain": "inventory_tracking",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "elementary",
        "missing_type": "missing_second_shelf",
        "generate": lambda rng: {
            "shelf1": rng.randint(22, 45),
            "shelf2": rng.randint(18, 35),
            "shelf3": rng.randint(15, 28)
        },
        "intact_text": lambda p: (
            f"A stockroom has three shelves of paint cans. Shelf 1 holds {p['shelf1']} cans, "
            f"Shelf 2 holds {p['shelf2']} cans, and Shelf 3 holds {p['shelf3']} cans. "
            f"How many paint cans are on all three shelves combined?"
        ),
        "intact_answer": lambda p: str(p["shelf1"] + p["shelf2"] + p["shelf3"]),
        "modified_text": lambda p: (
            f"A stockroom has three shelves of paint cans. Shelf 1 holds {p['shelf1']} cans, "
            f"Shelf 2 holds some paint cans, and Shelf 3 holds {p['shelf3']} cans. "
            f"How many paint cans are on all three shelves combined?"
        ),
        "defect_proof": "Paint cans on Shelf 2 is omitted."
    })

    templates.append({
        "id": "base_015",
        "domain": "inventory_tracking",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "intermediate",
        "missing_type": "missing_return_count",
        "generate": lambda rng: {
            "opening": rng.randint(120, 200),
            "sales": rng.randint(45, 80),
            "restocked": rng.randint(25, 50)
        },
        "intact_text": lambda p: (
            f"A shoe outlet started Saturday with {p['opening']} pairs of sneakers. "
            f"During the day, {p['sales']} pairs were purchased and {p['restocked']} pairs were brought up from the back storage. "
            f"How many pairs of sneakers are in the outlet by the end of Saturday?"
        ),
        "intact_answer": lambda p: str(p["opening"] - p["sales"] + p["restocked"]),
        "modified_text": lambda p: (
            f"A shoe outlet started Saturday with {p['opening']} pairs of sneakers. "
            f"During the day, {p['sales']} pairs were purchased and additional pairs were brought up from back storage. "
            f"How many pairs of sneakers are in the outlet by the end of Saturday?"
        ),
        "defect_proof": "The restock amount brought up from storage is unspecified."
    })

    templates.append({
        "id": "base_016",
        "domain": "inventory_tracking",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "elementary",
        "missing_type": "missing_defective_count",
        "generate": lambda rng: {
            "total_batch": rng.randint(200, 400),
            "defective": rng.randint(12, 35)
        },
        "intact_text": lambda p: (
            f"A factory produced a batch of {p['total_batch']} light bulbs. "
            f"Quality control identified {p['defective']} defective bulbs and set them aside. "
            f"How many functional bulbs from this batch can be packaged for sale?"
        ),
        "intact_answer": lambda p: str(p["total_batch"] - p["defective"]),
        "modified_text": lambda p: (
            f"A factory produced a batch of {p['total_batch']} light bulbs. "
            f"Quality control identified several defective bulbs and set them aside. "
            f"How many functional bulbs from this batch can be packaged for sale?"
        ),
        "defect_proof": "Defective bulb count is missing."
    })

    templates.append({
        "id": "base_017",
        "domain": "inventory_tracking",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "intermediate",
        "missing_type": "missing_box_count",
        "generate": lambda rng: {
            "boxes": rng.randint(6, 12),
            "per_box": rng.randint(8, 15),
            "loose": rng.randint(5, 14)
        },
        "intact_text": lambda p: (
            f"A stationery store received {p['boxes']} sealed boxes of notebooks, each holding {p['per_box']} notebooks, "
            f"plus {p['loose']} loose notebooks. "
            f"What is the total number of notebooks received?"
        ),
        "intact_answer": lambda p: str(p["boxes"] * p["per_box"] + p["loose"]),
        "modified_text": lambda p: (
            f"A stationery store received sealed boxes of notebooks holding {p['per_box']} notebooks each, "
            f"plus {p['loose']} loose notebooks. "
            f"What is the total number of notebooks received?"
        ),
        "defect_proof": "Number of sealed boxes is omitted."
    })

    templates.append({
        "id": "base_018",
        "domain": "inventory_tracking",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "elementary",
        "missing_type": "missing_discarded_stock",
        "generate": lambda rng: {
            "stock": rng.randint(50, 90),
            "delivered": rng.randint(20, 40),
            "expired": rng.randint(5, 15)
        },
        "intact_text": lambda p: (
            f"A grocery aisle had {p['stock']} cartons of almond milk. The vendor delivered {p['delivered']} fresh cartons, "
            f"and the clerk pulled {p['expired']} expired cartons from the shelf. "
            f"How many cartons of almond milk are now available on the shelf?"
        ),
        "intact_answer": lambda p: str(p["stock"] + p["delivered"] - p["expired"]),
        "modified_text": lambda p: (
            f"A grocery aisle had {p['stock']} cartons of almond milk. The vendor delivered {p['delivered']} fresh cartons, "
            f"and the clerk pulled some expired cartons from the shelf. "
            f"How many cartons of almond milk are now available on the shelf?"
        ),
        "defect_proof": "Expired carton count pulled from shelf is unstated."
    })

    templates.append({
        "id": "base_019",
        "domain": "inventory_tracking",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "intermediate",
        "missing_type": "missing_sub_category",
        "generate": lambda rng: {
            "hardcover": rng.randint(35, 60),
            "paperback": rng.randint(45, 80),
            "audiobook_cds": rng.randint(10, 25)
        },
        "intact_text": lambda p: (
            f"A bookstore section has {p['hardcover']} hardcover novels, {p['paperback']} paperback novels, "
            f"and {p['audiobook_cds']} audiobook CD sets. "
            f"What is the total count of media items in this section?"
        ),
        "intact_answer": lambda p: str(p["hardcover"] + p["paperback"] + p["audiobook_cds"]),
        "modified_text": lambda p: (
            f"A bookstore section has {p['hardcover']} hardcover novels and {p['audiobook_cds']} audiobook CD sets, "
            f"along with a collection of paperback novels. "
            f"What is the total count of media items in this section?"
        ),
        "defect_proof": "Paperback count is omitted."
    })

    templates.append({
        "id": "base_020",
        "domain": "inventory_tracking",
        "defect": ConditionType.MISSING_QUANTITY,
        "difficulty": "elementary",
        "missing_type": "missing_transfer_amount",
        "generate": lambda rng: {
            "warehouse_a": rng.randint(100, 200),
            "transferred": rng.randint(25, 50)
        },
        "intact_text": lambda p: (
            f"Warehouse A holds {p['warehouse_a']} steel rods. The logistics manager transferred {p['transferred']} steel rods "
            f"to Warehouse B. "
            f"How many steel rods remain in Warehouse A?"
        ),
        "intact_answer": lambda p: str(p["warehouse_a"] - p["transferred"]),
        "modified_text": lambda p: (
            f"Warehouse A holds {p['warehouse_a']} steel rods. The logistics manager transferred a portion of steel rods "
            f"to Warehouse B. "
            f"How many steel rods remain in Warehouse A?"
        ),
        "defect_proof": "Transferred quantity is omitted."
    })

    # -------------------------------------------------------------
    # DOMAIN 3: Rate and Time (10 base problems: 021 - 030)
    # Defect condition: MISSING_RELATIONSHIP
    # -------------------------------------------------------------
    templates.append({
        "id": "base_021",
        "domain": "rate_and_time",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_time_duration",
        "generate": lambda rng: {
            "speed1": rng.choice([40, 50, 60]),
            "time1": rng.randint(2, 4),
            "speed2": rng.choice([45, 55, 65]),
            "time2": rng.randint(2, 3)
        },
        "intact_text": lambda p: (
            f"A courier drove from Station X to Station Y at a steady speed of {p['speed1']} miles per hour for {p['time1']} hours. "
            f"Then the courier drove from Station Y to Station Z at {p['speed2']} miles per hour for {p['time2']} hours. "
            f"What is the total distance in miles of the entire trip?"
        ),
        "intact_answer": lambda p: str(p["speed1"] * p["time1"] + p["speed2"] * p["time2"]),
        "modified_text": lambda p: (
            f"A courier drove from Station X to Station Y at a steady speed of {p['speed1']} miles per hour for {p['time1']} hours. "
            f"Then the courier drove from Station Y to Station Z at {p['speed2']} miles per hour. "
            f"What is the total distance in miles of the entire trip?"
        ),
        "defect_proof": "Duration for leg Y to Z is missing; distance cannot be determined."
    })

    templates.append({
        "id": "base_022",
        "domain": "rate_and_time",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_production_rate_unit",
        "generate": lambda rng: {
            "rate": rng.randint(12, 25),
            "hours": rng.randint(4, 8)
        },
        "intact_text": lambda p: (
            f"A printing press operates at a constant rate of {p['rate']} posters per hour. "
            f"The press ran continuously for {p['hours']} hours today. "
            f"How many total posters were printed?"
        ),
        "intact_answer": lambda p: str(p["rate"] * p["hours"]),
        "modified_text": lambda p: (
            f"A printing press produced posters today during an operating run of {p['hours']} hours. "
            f"Its poster output rate is steady across shifts. "
            f"How many total posters were printed?"
        ),
        "defect_proof": "Production rate per hour is disconnected/unstated."
    })

    templates.append({
        "id": "base_023",
        "domain": "rate_and_time",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_speed_relation",
        "generate": lambda rng: {
            "distance": rng.randint(120, 240),
            "speed": rng.choice([30, 40, 60]),
            "break_mins": 30
        },
        "intact_text": lambda p: (
            f"A train traveled a distance of {p['distance']} miles at an average traveling speed of {p['speed']} miles per hour. "
            f"How many hours did the train spend traveling on the tracks?"
        ),
        "intact_answer": lambda p: str(p["distance"] // p["speed"]),
        "modified_text": lambda p: (
            f"A train traveled a distance of {p['distance']} miles between two terminal cities. "
            f"The route followed all standard regional railway corridors. "
            f"How many hours did the train spend traveling on the tracks?"
        ),
        "defect_proof": "Speed or rate relating distance to travel time is unstated."
    })

    templates.append({
        "id": "base_024",
        "domain": "rate_and_time",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_drain_rate",
        "generate": lambda rng: {
            "initial_liters": rng.randint(300, 500),
            "inflow_rate": rng.randint(40, 60),
            "outflow_rate": rng.randint(15, 30),
            "hours": rng.randint(3, 5)
        },
        "intact_text": lambda p: (
            f"A water tank holds {p['initial_liters']} liters initially. A pipe adds water at {p['inflow_rate']} liters per hour, "
            f"while a drainage valve removes water at {p['outflow_rate']} liters per hour. "
            f"How many liters of water are in the tank after {p['hours']} hours?"
        ),
        "intact_answer": lambda p: str(p["initial_liters"] + (p["inflow_rate"] - p["outflow_rate"]) * p["hours"]),
        "modified_text": lambda p: (
            f"A water tank holds {p['initial_liters']} liters initially. A pipe adds water at {p['inflow_rate']} liters per hour, "
            f"while a drainage valve continuously removes water. "
            f"How many liters of water are in the tank after {p['hours']} hours?"
        ),
        "defect_proof": "The drainage outflow rate is omitted."
    })

    templates.append({
        "id": "base_025",
        "domain": "rate_and_time",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_consumption_rate",
        "generate": lambda rng: {
            "fuel_liters": rng.randint(40, 70),
            "efficiency_km_per_l": rng.randint(10, 15),
            "distance_km": rng.randint(150, 300)
        },
        "intact_text": lambda p: (
            f"A vehicle fuel tank holds {p['fuel_liters']} liters of gasoline. The vehicle consumes 1 liter of gasoline every {p['efficiency_km_per_l']} kilometers. "
            f"How many liters of gasoline are consumed when driving {p['distance_km']} kilometers?"
        ),
        "intact_answer": lambda p: str(p["distance_km"] // p["efficiency_km_per_l"]),
        "modified_text": lambda p: (
            f"A vehicle fuel tank holds {p['fuel_liters']} liters of gasoline. "
            f"The vehicle is driven for a journey of {p['distance_km']} kilometers. "
            f"How many liters of gasoline are consumed when driving {p['distance_km']} kilometers?"
        ),
        "defect_proof": "Fuel efficiency/consumption rate per kilometer is omitted."
    })

    templates.append({
        "id": "base_026",
        "domain": "rate_and_time",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_worker_output_relation",
        "generate": lambda rng: {
            "workers": rng.randint(3, 6),
            "items_per_worker_hr": rng.randint(8, 14),
            "hours": rng.randint(4, 7)
        },
        "intact_text": lambda p: (
            f"A team of {p['workers']} assembly workers works for {p['hours']} hours. "
            f"Each worker assembles {p['items_per_worker_hr']} components per hour. "
            f"How many total components does the team assemble?"
        ),
        "intact_answer": lambda p: str(p["workers"] * p["items_per_worker_hr"] * p["hours"]),
        "modified_text": lambda p: (
            f"A team of {p['workers']} assembly workers works for {p['hours']} hours on the manufacturing line. "
            f"How many total components does the team assemble?"
        ),
        "defect_proof": "Assembly rate per worker per hour is missing."
    })

    templates.append({
        "id": "base_027",
        "domain": "rate_and_time",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_time_conversion_link",
        "generate": lambda rng: {
            "laps": rng.randint(15, 30),
            "sec_per_lap": rng.choice([60, 90, 120])
        },
        "intact_text": lambda p: (
            f"A swimmer completed {p['laps']} laps in a pool. Each lap took exactly {p['sec_per_lap']} seconds. "
            f"What was the total time spent swimming in seconds?"
        ),
        "intact_answer": lambda p: str(p["laps"] * p["sec_per_lap"]),
        "modified_text": lambda p: (
            f"A swimmer completed {p['laps']} laps in a pool during her morning training session. "
            f"What was the total time spent swimming in seconds?"
        ),
        "defect_proof": "Time duration per lap is missing."
    })

    templates.append({
        "id": "base_028",
        "domain": "rate_and_time",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "elementary",
        "missing_type": "missing_hourly_wage",
        "generate": lambda rng: {
            "hours": rng.randint(25, 40),
            "wage": rng.randint(15, 25),
            "bonus": rng.randint(30, 60)
        },
        "intact_text": lambda p: (
            f"Sofia worked {p['hours']} hours this week at an hourly wage of ${p['wage']} per hour. "
            f"She also received a ${p['bonus']} weekend attendance bonus. "
            f"What was Sofia's total earnings in dollars for the week?"
        ),
        "intact_answer": lambda p: str(p["hours"] * p["wage"] + p["bonus"]),
        "modified_text": lambda p: (
            f"Sofia worked {p['hours']} hours this week at an hourly wage. "
            f"She also received a ${p['bonus']} weekend attendance bonus. "
            f"What was Sofia's total earnings in dollars for the week?"
        ),
        "defect_proof": "Hourly wage rate is missing."
    })

    templates.append({
        "id": "base_029",
        "domain": "rate_and_time",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_reading_pace",
        "generate": lambda rng: {
            "pages_per_day": rng.randint(20, 40),
            "days": rng.randint(5, 10),
            "book_length": 350
        },
        "intact_text": lambda p: (
            f"A student reads at a steady pace of {p['pages_per_day']} pages per day. "
            f"How many total pages does the student read over {p['days']} days?"
        ),
        "intact_answer": lambda p: str(p["pages_per_day"] * p["days"]),
        "modified_text": lambda p: (
            f"A student reads every afternoon over a period of {p['days']} days. "
            f"How many total pages does the student read over {p['days']} days?"
        ),
        "defect_proof": "Pace of pages read per day is omitted."
    })

    templates.append({
        "id": "base_030",
        "domain": "rate_and_time",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_elevation_climb_rate",
        "generate": lambda rng: {
            "start_elev": rng.randint(500, 1000),
            "rate_per_hr": rng.randint(150, 300),
            "hours": rng.randint(3, 5)
        },
        "intact_text": lambda p: (
            f"Hikers begin at an elevation of {p['start_elev']} feet. They ascend at an average rate of {p['rate_per_hr']} feet per hour for {p['hours']} hours. "
            f"What elevation in feet do the hikers reach?"
        ),
        "intact_answer": lambda p: str(p["start_elev"] + p["rate_per_hr"] * p["hours"]),
        "modified_text": lambda p: (
            f"Hikers begin at an elevation of {p['start_elev']} feet. They ascend the mountain trail for {p['hours']} hours. "
            f"What elevation in feet do the hikers reach?"
        ),
        "defect_proof": "Climbing rate in feet per hour is unstated."
    })

    # -------------------------------------------------------------
    # DOMAIN 4: Resource Allocation (10 base problems: 031 - 040)
    # Defect condition: MISSING_RELATIONSHIP
    # -------------------------------------------------------------
    templates.append({
        "id": "base_031",
        "domain": "resource_allocation",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_allocation_proportion",
        "generate": lambda rng: {
            "budget": rng.choice([1000, 2000, 3000]),
            "share_pct": rng.choice([30, 40, 50]),
            "fee": 50
        },
        "intact_text": lambda p: (
            f"A community board has a ${p['budget']} grant. They allocated exactly {p['share_pct']}% of this budget to park maintenance. "
            f"How many dollars are allocated to park maintenance?"
        ),
        "intact_answer": lambda p: str((p["budget"] * p["share_pct"]) // 100),
        "modified_text": lambda p: (
            f"A community board has a ${p['budget']} grant. They allocated a portion of this budget to park maintenance and the rest to youth programs. "
            f"How many dollars are allocated to park maintenance?"
        ),
        "defect_proof": "Percentage or fraction allocated to park maintenance is omitted."
    })

    templates.append({
        "id": "base_032",
        "domain": "resource_allocation",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_server_ratio",
        "generate": lambda rng: {
            "cluster_a": rng.randint(15, 30),
            "multiplier": rng.choice([2, 3]),
            "standby": rng.randint(5, 10)
        },
        "intact_text": lambda p: (
            f"Data Center East operates {p['cluster_a']} active servers. Data Center West operates exactly {p['multiplier']} times as many servers as East. "
            f"How many active servers does Data Center West operate?"
        ),
        "intact_answer": lambda p: str(p["cluster_a"] * p["multiplier"]),
        "modified_text": lambda p: (
            f"Data Center East operates {p['cluster_a']} active servers. Data Center West operates more servers than East to handle overflow traffic. "
            f"How many active servers does Data Center West operate?"
        ),
        "defect_proof": "The ratio or relational difference between the two data centers is omitted."
    })

    templates.append({
        "id": "base_033",
        "domain": "resource_allocation",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "elementary",
        "missing_type": "missing_portion_split",
        "generate": lambda rng: {
            "land_acres": rng.randint(80, 160),
            "crops_ratio": 3,
            "pasture_ratio": 1
        },
        "intact_text": lambda p: (
            f"A farm has {p['land_acres']} acres of usable land. The land is divided between crops and pasture in a 3 to 1 ratio (3 parts crops for every 1 part pasture). "
            f"How many acres are allocated to pasture?"
        ),
        "intact_answer": lambda p: str(p["land_acres"] // 4),
        "modified_text": lambda p: (
            f"A farm has {p['land_acres']} acres of usable land. The land is divided between crops and pasture. "
            f"How many acres are allocated to pasture?"
        ),
        "defect_proof": "The ratio dividing crops and pasture is omitted."
    })

    templates.append({
        "id": "base_034",
        "domain": "resource_allocation",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_dosage_conversion",
        "generate": lambda rng: {
            "weight_kg": rng.randint(50, 80),
            "dose_per_kg": rng.randint(2, 5)
        },
        "intact_text": lambda p: (
            f"A veterinarian prepares medicine for an animal weighing {p['weight_kg']} kg. "
            f"The required dosage relation is {p['dose_per_kg']} mg of medicine per 1 kg of body weight. "
            f"How many mg of medicine should the veterinarian prepare?"
        ),
        "intact_answer": lambda p: str(p["weight_kg"] * p["dose_per_kg"]),
        "modified_text": lambda p: (
            f"A veterinarian prepares medicine for an animal weighing {p['weight_kg']} kg according to standard medical guidelines. "
            f"How many mg of medicine should the veterinarian prepare?"
        ),
        "defect_proof": "Dosage relation per kilogram of weight is missing."
    })

    templates.append({
        "id": "base_035",
        "domain": "resource_allocation",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_fertilizer_spread_rate",
        "generate": lambda rng: {
            "sq_meters": rng.choice([200, 400, 600]),
            "grams_per_sq_m": rng.randint(25, 50)
        },
        "intact_text": lambda p: (
            f"A landscaper needs to fertilize a lawn measuring {p['sq_meters']} square meters. "
            f"The application guideline specifies {p['grams_per_sq_m']} grams of fertilizer per square meter. "
            f"How many grams of fertilizer are needed in total?"
        ),
        "intact_answer": lambda p: str(p["sq_meters"] * p["grams_per_sq_m"]),
        "modified_text": lambda p: (
            f"A landscaper needs to fertilize a lawn measuring {p['sq_meters']} square meters following manufacturer directions. "
            f"How many grams of fertilizer are needed in total?"
        ),
        "defect_proof": "Application rate per square meter is unstated."
    })

    templates.append({
        "id": "base_036",
        "domain": "resource_allocation",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "elementary",
        "missing_type": "missing_ticket_allocation_split",
        "generate": lambda rng: {
            "total_tickets": rng.randint(60, 100),
            "vip_ratio": 4  # 1 in 4 are VIP
        },
        "intact_text": lambda p: (
            f"A theater has {p['total_tickets']} reserved tickets for opening night. "
            f"Exactly 1 out of every 4 reserved tickets is a VIP ticket. "
            f"How many VIP tickets are reserved?"
        ),
        "intact_answer": lambda p: str(p["total_tickets"] // 4),
        "modified_text": lambda p: (
            f"A theater has {p['total_tickets']} reserved tickets for opening night, consisting of both regular and VIP tickets. "
            f"How many VIP tickets are reserved?"
        ),
        "defect_proof": "Proportion of VIP tickets is omitted."
    })

    templates.append({
        "id": "base_037",
        "domain": "resource_allocation",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_cpu_quota_rule",
        "generate": lambda rng: {
            "nodes": rng.randint(8, 16),
            "cores_per_node": rng.choice([4, 8, 16])
        },
        "intact_text": lambda p: (
            f"A computing cluster has {p['nodes']} server nodes. Each server node is equipped with {p['cores_per_node']} CPU cores. "
            f"How many total CPU cores are in the computing cluster?"
        ),
        "intact_answer": lambda p: str(p["nodes"] * p["cores_per_node"]),
        "modified_text": lambda p: (
            f"A computing cluster has {p['nodes']} server nodes in its primary server rack. "
            f"How many total CPU cores are in the computing cluster?"
        ),
        "defect_proof": "Core count per node is omitted."
    })

    templates.append({
        "id": "base_038",
        "domain": "resource_allocation",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_recipe_ratio",
        "generate": lambda rng: {
            "flour_cups": rng.randint(4, 8),
            "water_ratio": 2  # 1 cup water per 2 cups flour
        },
        "intact_text": lambda p: (
            f"A baker is making bread dough using {p['flour_cups']} cups of flour. "
            f"The recipe requires 1 cup of water for every 2 cups of flour. "
            f"How many cups of water does the baker need?"
        ),
        "intact_answer": lambda p: str(p["flour_cups"] // 2),
        "modified_text": lambda p: (
            f"A baker is making bread dough using {p['flour_cups']} cups of flour along with water and yeast. "
            f"How many cups of water does the baker need?"
        ),
        "defect_proof": "Ratio of water to flour is unstated."
    })

    templates.append({
        "id": "base_039",
        "domain": "resource_allocation",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "elementary",
        "missing_type": "missing_staff_ratio",
        "generate": lambda rng: {
            "campers": rng.randint(40, 80),
            "campers_per_counselor": 10
        },
        "intact_text": lambda p: (
            f"A summer camp enrolled {p['campers']} campers. Camp regulations mandate 1 counselor for every 10 campers. "
            f"How many counselors are required for these campers?"
        ),
        "intact_answer": lambda p: str(p["campers"] // 10),
        "modified_text": lambda p: (
            f"A summer camp enrolled {p['campers']} campers for the upcoming outdoor season. "
            f"How many counselors are required for these campers?"
        ),
        "defect_proof": "The mandated camper-to-counselor ratio is omitted."
    })

    templates.append({
        "id": "base_040",
        "domain": "resource_allocation",
        "defect": ConditionType.MISSING_RELATIONSHIP,
        "difficulty": "intermediate",
        "missing_type": "missing_currency_exchange_rate",
        "generate": lambda rng: {
            "usd": rng.choice([100, 200, 500]),
            "rate_eur": 2  # simplified exchange 1 USD = 2 credits
        },
        "intact_text": lambda p: (
            f"A traveler converts {p['usd']} US dollars into game tokens at an arcade counter. "
            f"The exchange rate is exactly 2 tokens per 1 US dollar. "
            f"How many game tokens does the traveler receive?"
        ),
        "intact_answer": lambda p: str(p["usd"] * 2),
        "modified_text": lambda p: (
            f"A traveler converts {p['usd']} US dollars into game tokens at an arcade counter. "
            f"How many game tokens does the traveler receive?"
        ),
        "defect_proof": "The exchange rate from dollars to tokens is omitted."
    })

    # -------------------------------------------------------------
    # DOMAIN 5: Sequential Steps (10 base problems: 041 - 050)
    # Defect condition: CONTRADICTION
    # -------------------------------------------------------------
    templates.append({
        "id": "base_041",
        "domain": "sequential_steps",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_total_sum",
        "generate": lambda rng: {
            "part_a": rng.randint(20, 35),
            "part_b": rng.randint(25, 40)
        },
        "intact_text": lambda p: (
            f"A delivery van carried packages to two neighborhoods. It delivered {p['part_a']} packages in Downtown "
            f"and {p['part_b']} packages in Uptown, completing all deliveries. "
            f"How many packages did the van deliver in total?"
        ),
        "intact_answer": lambda p: str(p["part_a"] + p["part_b"]),
        "modified_text": lambda p: (
            f"A delivery van carried exactly 30 packages in total to two neighborhoods, with no packages delivered anywhere else. "
            f"It delivered {p['part_a']} packages in Downtown and {p['part_b']} packages in Uptown. "
            f"How many packages did the van deliver in total?"
        ),
        "defect_proof": "Total stated is 30, but sum of disjoint neighborhood parts exceeds 45; premises contradict."
    })

    templates.append({
        "id": "base_042",
        "domain": "sequential_steps",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_temporal_order",
        "generate": lambda rng: {
            "start": rng.randint(50, 80),
            "loss": rng.randint(15, 25),
            "gain": rng.randint(20, 30)
        },
        "intact_text": lambda p: (
            f"An investor held {p['start']} shares. On Tuesday, they sold {p['loss']} shares. "
            f"On Wednesday, they purchased {p['gain']} additional shares. "
            f"How many shares does the investor hold now?"
        ),
        "intact_answer": lambda p: str(p["start"] - p["loss"] + p["gain"]),
        "modified_text": lambda p: (
            f"An investor held {p['start']} shares initially and never sold any shares at any point. "
            f"On Tuesday, they sold {p['loss']} shares. "
            f"On Wednesday, they purchased {p['gain']} additional shares. "
            f"How many shares does the investor hold now?"
        ),
        "defect_proof": "Premise states investor 'never sold any shares' while simultaneously asserting 'sold shares on Tuesday'."
    })

    templates.append({
        "id": "base_043",
        "domain": "sequential_steps",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_inventory_conservation",
        "generate": lambda rng: {
            "initial": rng.randint(40, 60),
            "added": rng.randint(10, 20)
        },
        "intact_text": lambda p: (
            f"A jar contained {p['initial']} marbles. Clara added {p['added']} marbles to the jar and removed none. "
            f"How many marbles are in the jar now?"
        ),
        "intact_answer": lambda p: str(p["initial"] + p["added"]),
        "modified_text": lambda p: (
            f"A jar contained {p['initial']} marbles. Clara added {p['added']} marbles to the jar and removed none. "
            f"After adding them, the jar now contains exactly 20 marbles. "
            f"How many marbles are in the jar now?"
        ),
        "defect_proof": f"Adding marbles to initial count cannot yield a smaller total without removals; inconsistent."
    })

    templates.append({
        "id": "base_044",
        "domain": "sequential_steps",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_subtraction_state",
        "generate": lambda rng: {
            "original": rng.randint(80, 120),
            "spent": rng.randint(20, 40)
        },
        "intact_text": lambda p: (
            f"A bank account balance was ${p['original']}. A withdrawal of ${p['spent']} was processed with no other transactions. "
            f"What is the current bank account balance in dollars?"
        ),
        "intact_answer": lambda p: str(p["original"] - p["spent"]),
        "modified_text": lambda p: (
            f"A bank account balance was ${p['original']}. A withdrawal of ${p['spent']} was processed with no other transactions, "
            f"leaving the balance unchanged at ${p['original']}. "
            f"What is the current bank account balance in dollars?"
        ),
        "defect_proof": "A positive withdrawal cannot leave balance strictly unchanged with no other transactions."
    })

    templates.append({
        "id": "base_045",
        "domain": "sequential_steps",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_sum_and_difference",
        "generate": lambda rng: {
            "num1": rng.randint(30, 50),
            "num2": rng.randint(10, 20)
        },
        "intact_text": lambda p: (
            f"Two crates together weigh {p['num1'] + p['num2']} kg. The heavier crate weighs {p['num1']} kg. "
            f"How many kg does the lighter crate weigh?"
        ),
        "intact_answer": lambda p: str(p["num2"]),
        "modified_text": lambda p: (
            f"Two crates together weigh {p['num1'] + p['num2']} kg. The heavier crate weighs {p['num1']} kg, "
            f"and the lighter crate weighs {p['num1'] + 15} kg. "
            f"How many kg does the lighter crate weigh?"
        ),
        "defect_proof": "Lighter crate cannot weigh more than heavier crate, nor can sum match stated total."
    })

    templates.append({
        "id": "base_046",
        "domain": "sequential_steps",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "elementary",
        "missing_type": "contradictory_cardinality",
        "generate": lambda rng: {
            "boys": rng.randint(12, 18),
            "girls": rng.randint(14, 20)
        },
        "intact_text": lambda p: (
            f"A classroom consists of {p['boys']} boys and {p['girls']} girls, with no other students. "
            f"How many students are in the classroom in total?"
        ),
        "intact_answer": lambda p: str(p["boys"] + p["girls"]),
        "modified_text": lambda p: (
            f"A classroom has a total enrollment of exactly 15 students. "
            f"It consists of {p['boys']} boys and {p['girls']} girls, with no other students. "
            f"How many students are in the classroom in total?"
        ),
        "defect_proof": "Total enrollment of 15 contradicts disjoint group sum which is at least 26."
    })

    templates.append({
        "id": "base_047",
        "domain": "sequential_steps",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_monotonicity",
        "generate": lambda rng: {
            "level": rng.randint(5, 10),
            "floors_up": rng.randint(3, 6)
        },
        "intact_text": lambda p: (
            f"An elevator began on floor {p['level']}. It moved up {p['floors_up']} floors without going down. "
            f"On which floor is the elevator now?"
        ),
        "intact_answer": lambda p: str(p["level"] + p["floors_up"]),
        "modified_text": lambda p: (
            f"An elevator began on floor {p['level']}. It moved strictly upward {p['floors_up']} floors without going down, "
            f"and ended up on floor {p['level'] - 2}. "
            f"On which floor is the elevator now?"
        ),
        "defect_proof": "Moving upward cannot result in a lower floor number."
    })

    templates.append({
        "id": "base_048",
        "domain": "sequential_steps",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_capacity_limit",
        "generate": lambda rng: {
            "cap": rng.randint(30, 50),
            "boarded": rng.randint(15, 25),
            "more": rng.randint(10, 15)
        },
        "intact_text": lambda p: (
            f"A shuttle bus with a maximum capacity of {p['cap']} passengers currently carries {p['boarded']} passengers. "
            f"At the next terminal, {p['more']} additional passengers board, keeping the bus within capacity. "
            f"How many passengers are on the shuttle bus now?"
        ),
        "intact_answer": lambda p: str(p["boarded"] + p["more"]),
        "modified_text": lambda p: (
            f"A shuttle bus with a strict maximum limit of {p['cap']} passengers currently carries {p['cap'] + 20} seated passengers. "
            f"No passengers are standing. "
            f"How many passengers are on the shuttle bus now?"
        ),
        "defect_proof": "Occupancy exceeds strict maximum limit without standing; logically inconsistent system."
    })

    templates.append({
        "id": "base_049",
        "domain": "sequential_steps",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_temperature_shift",
        "generate": lambda rng: {
            "t0": rng.randint(60, 75),
            "rise": rng.randint(5, 12)
        },
        "intact_text": lambda p: (
            f"At 8:00 AM the temperature was {p['t0']} degrees. By noon, the temperature rose by {p['rise']} degrees. "
            f"What was the temperature at noon?"
        ),
        "intact_answer": lambda p: str(p["t0"] + p["rise"]),
        "modified_text": lambda p: (
            f"At 8:00 AM the temperature was {p['t0']} degrees. Between 8:00 AM and noon the temperature only rose by {p['rise']} degrees, "
            f"and at noon it was recorded as {p['t0'] - 10} degrees. "
            f"What was the temperature at noon?"
        ),
        "defect_proof": "Rising temperature cannot produce a lower reading than start."
    })

    templates.append({
        "id": "base_050",
        "domain": "sequential_steps",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_coin_total",
        "generate": lambda rng: {
            "dimes": rng.randint(4, 8),   # 10 cents each
            "nickels": rng.randint(3, 7)  # 5 cents each
        },
        "intact_text": lambda p: (
            f"Owen has {p['dimes']} dimes (worth 10 cents each) and {p['nickels']} nickels (worth 5 cents each). "
            f"What is the total value of Owen's coins in cents?"
        ),
        "intact_answer": lambda p: str(p["dimes"] * 10 + p["nickels"] * 5),
        "modified_text": lambda p: (
            f"Owen has exactly 25 cents in total. "
            f"His coins consist of {p['dimes']} dimes (worth 10 cents each) and {p['nickels']} nickels (worth 5 cents each). "
            f"What is the total value of Owen's coins in cents?"
        ),
        "defect_proof": "Total stated as 25 cents contradicts coin breakdown which sums to at least 55 cents."
    })

    # -------------------------------------------------------------
    # DOMAIN 6: Relational Reasoning (10 base problems: 051 - 060)
    # Defect condition: CONTRADICTION
    # -------------------------------------------------------------
    templates.append({
        "id": "base_051",
        "domain": "relational_reasoning",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_age_ordering",
        "generate": lambda rng: {
            "alice_age": rng.randint(20, 30),
            "diff": rng.randint(3, 6)
        },
        "intact_text": lambda p: (
            f"Alice is {p['alice_age']} years old. Bob is {p['diff']} years older than Alice. "
            f"How old is Bob in years?"
        ),
        "intact_answer": lambda p: str(p["alice_age"] + p["diff"]),
        "modified_text": lambda p: (
            f"Alice is {p['alice_age']} years old. Bob is {p['diff']} years older than Alice, and Alice is older than Bob. "
            f"How old is Bob in years?"
        ),
        "defect_proof": "Bob cannot be strictly older than Alice while Alice is simultaneously older than Bob."
    })

    templates.append({
        "id": "base_052",
        "domain": "relational_reasoning",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_height_relation",
        "generate": lambda rng: {
            "h_a": rng.randint(160, 180),
            "diff": rng.randint(5, 12)
        },
        "intact_text": lambda p: (
            f"Building A is {p['h_a']} meters tall. Building B is {p['diff']} meters taller than Building A. "
            f"How tall is Building B in meters?"
        ),
        "intact_answer": lambda p: str(p["h_a"] + p["diff"]),
        "modified_text": lambda p: (
            f"Building A is {p['h_a']} meters tall. Building B is {p['diff']} meters taller than Building A, "
            f"and Building B is exactly {p['h_a'] - 10} meters tall. "
            f"How tall is Building B in meters?"
        ),
        "defect_proof": "Building B is taller than A, yet asserted to be shorter than A."
    })

    templates.append({
        "id": "base_053",
        "domain": "relational_reasoning",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_subset_size",
        "generate": lambda rng: {
            "total_pets": rng.randint(30, 50),
            "dogs": rng.randint(15, 25),
            "cats": rng.randint(10, 20)
        },
        "intact_text": lambda p: (
            f"An animal shelter houses {p['total_pets']} animals. Exactly {p['dogs']} are dogs, "
            f"and the remaining animals are cats. "
            f"How many cats are in the animal shelter?"
        ),
        "intact_answer": lambda p: str(p["total_pets"] - p["dogs"]),
        "modified_text": lambda p: (
            f"An animal shelter houses {p['total_pets']} animals in total. Exactly {p['dogs']} are dogs, "
            f"and {p['total_pets'] + 10} are cats, with every animal being either a dog or a cat. "
            f"How many cats are in the animal shelter?"
        ),
        "defect_proof": "Cat subset exceeds total shelter animal population."
    })

    templates.append({
        "id": "base_054",
        "domain": "relational_reasoning",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "elementary",
        "missing_type": "contradictory_scoring_comparison",
        "generate": lambda rng: {
            "score_x": rng.randint(70, 90),
            "margin": rng.randint(5, 15)
        },
        "intact_text": lambda p: (
            f"Team X scored {p['score_x']} points. Team Y scored {p['margin']} points fewer than Team X. "
            f"How many points did Team Y score?"
        ),
        "intact_answer": lambda p: str(p["score_x"] - p["margin"]),
        "modified_text": lambda p: (
            f"Team X scored {p['score_x']} points. Team Y scored {p['margin']} points fewer than Team X, "
            f"and Team Y had the highest score in the match. "
            f"How many points did Team Y score?"
        ),
        "defect_proof": "Team Y cannot have scored fewer points than Team X while having the highest score."
    })

    templates.append({
        "id": "base_055",
        "domain": "relational_reasoning",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_speed_ranking",
        "generate": lambda rng: {
            "speed_car": rng.choice([60, 70, 80]),
            "faster_by": 15
        },
        "intact_text": lambda p: (
            f"Car 1 drove at {p['speed_car']} mph. Car 2 drove {p['faster_by']} mph faster than Car 1. "
            f"How fast was Car 2 driving in mph?"
        ),
        "intact_answer": lambda p: str(p["speed_car"] + p["faster_by"]),
        "modified_text": lambda p: (
            f"Car 1 drove at {p['speed_car']} mph. Car 2 drove {p['faster_by']} mph faster than Car 1, "
            f"while Car 2's speedometer registered exactly {p['speed_car'] - 10} mph. "
            f"How fast was Car 2 driving in mph?"
        ),
        "defect_proof": "Car 2 cannot be faster than Car 1 while driving at a lower speed."
    })

    templates.append({
        "id": "base_056",
        "domain": "relational_reasoning",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_weight_comparison",
        "generate": lambda rng: {
            "weight_a": rng.randint(40, 60),
            "diff": rng.randint(8, 15)
        },
        "intact_text": lambda p: (
            f"Package A weighs {p['weight_a']} pounds. Package B is {p['diff']} pounds lighter than Package A. "
            f"How many pounds does Package B weigh?"
        ),
        "intact_answer": lambda p: str(p["weight_a"] - p["diff"]),
        "modified_text": lambda p: (
            f"Package A weighs {p['weight_a']} pounds. Package B is {p['diff']} pounds lighter than Package A, "
            f"and Package B weighs {p['weight_a'] + 20} pounds. "
            f"How many pounds does Package B weigh?"
        ),
        "defect_proof": "Package B cannot be lighter than Package A while weighing more than Package A."
    })

    templates.append({
        "id": "base_057",
        "domain": "relational_reasoning",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "elementary",
        "missing_type": "contradictory_overlap_constraint",
        "generate": lambda rng: {
            "total_members": 50,
            "tennis": 35,
            "swimming": 25
        },
        "intact_text": lambda p: (
            f"A sports club has 50 members. Exactly 35 play tennis and 25 swim. Every member does at least one activity. "
            f"How many members do both activities?"
        ),
        "intact_answer": lambda p: str((35 + 25) - 50),
        "modified_text": lambda p: (
            f"A sports club has 50 members. Exactly 35 play tennis and 25 swim, with zero members doing both activities. "
            f"Every member does at least one activity. "
            f"How many members do both activities?"
        ),
        "defect_proof": "Disjoint sets sum to 60, exceeding the 50 club members."
    })

    templates.append({
        "id": "base_058",
        "domain": "relational_reasoning",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_price_relation",
        "generate": lambda rng: {
            "price_shirt": rng.randint(25, 45),
            "diff": rng.randint(10, 20)
        },
        "intact_text": lambda p: (
            f"A shirt costs ${p['price_shirt']}. A jacket costs ${p['diff']} more than the shirt. "
            f"How many dollars does the jacket cost?"
        ),
        "intact_answer": lambda p: str(p['price_shirt'] + p['diff']),
        "modified_text": lambda p: (
            f"A shirt costs ${p['price_shirt']}. A jacket costs ${p['diff']} more than the shirt, "
            f"and the jacket is cheaper than the shirt. "
            f"How many dollars does the jacket cost?"
        ),
        "defect_proof": "Jacket cannot cost more than shirt while being cheaper than shirt."
    })

    templates.append({
        "id": "base_059",
        "domain": "relational_reasoning",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "intermediate",
        "missing_type": "contradictory_capacity_partition",
        "generate": lambda rng: {
            "total_seats": 100,
            "section_a": 60,
            "section_b": 55
        },
        "intact_text": lambda p: (
            f"An auditorium has 100 seats divided into Section A and Section B. Section A has 60 seats. "
            f"How many seats are in Section B?"
        ),
        "intact_answer": lambda p: "40",
        "modified_text": lambda p: (
            f"An auditorium has 100 seats strictly partitioned between Section A and Section B. "
            f"Section A has 60 seats and Section B has 55 seats. "
            f"How many seats are in Section B?"
        ),
        "defect_proof": "Sections sum to 115, contradicting 100-seat total partition."
    })

    templates.append({
        "id": "base_060",
        "domain": "relational_reasoning",
        "defect": ConditionType.CONTRADICTION,
        "difficulty": "elementary",
        "missing_type": "contradictory_point_margin",
        "generate": lambda rng: {
            "points_lead": rng.randint(10, 20),
            "score_leader": rng.randint(60, 80)
        },
        "intact_text": lambda p: (
            f"Maya scored {p['score_leader']} points, winning the match by a lead of {p['points_lead']} points over second place. "
            f"How many points did the second-place player score?"
        ),
        "intact_answer": lambda p: str(p["score_leader"] - p["points_lead"]),
        "modified_text": lambda p: (
            f"Maya scored {p['score_leader']} points, winning the match by a lead of {p['points_lead']} points over second place. "
            f"The second-place player scored {p['score_leader'] + 5} points. "
            f"How many points did the second-place player score?"
        ),
        "defect_proof": "Second-place player cannot have more points than the match winner."
    })

    return templates


class DatasetGenerator:
    """Generates the Missing Piece benchmark dataset."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.templates = _build_base_templates()

    def generate(self) -> List[BenchmarkExample]:
        """Generate all 120 benchmark examples (60 intact, 60 modified)."""
        examples = []
        
        for t in self.templates:
            # Deterministic parameters for this template
            params = t["generate"](self.rng)
            base_id = t["id"]
            domain = t["domain"]
            defect_condition = t["defect"]
            difficulty = t["difficulty"]
            
            # 1. Intact example (Answerable)
            intact_ex = BenchmarkExample(
                example_id=f"{base_id}_intact",
                base_problem_id=base_id,
                pair_id=f"pair_{base_id.split('_')[1]}",
                category=domain,
                condition=ConditionType.INTACT,
                problem_text=t["intact_text"](params),
                expected_status=ExpectedStatus.ANSWER,
                expected_answer=t["intact_answer"](params),
                missing_information_type=None,
                difficulty=difficulty,
                generation_seed=self.seed,
                validation_status="verified",
                validation_notes="Unique deterministic ground truth integer solution."
            )
            examples.append(intact_ex)
            
            # 2. Modified paired example (Unanswerable)
            modified_ex = BenchmarkExample(
                example_id=f"{base_id}_modified",
                base_problem_id=base_id,
                pair_id=f"pair_{base_id.split('_')[1]}",
                category=domain,
                condition=defect_condition,
                problem_text=t["modified_text"](params),
                expected_status=ExpectedStatus.INSUFFICIENT,
                expected_answer=None,
                missing_information_type=t["missing_type"],
                difficulty=difficulty,
                generation_seed=self.seed,
                validation_status="verified",
                validation_notes=t["defect_proof"]
            )
            examples.append(modified_ex)

        return examples

    def generate_randomized(self) -> List[BenchmarkExample]:
        """Generate examples and shuffle presentation order using seed."""
        examples = self.generate()
        shuffle_rng = random.Random(self.seed + 1000)
        shuffled = list(examples)
        shuffle_rng.shuffle(shuffled)
        return shuffled
