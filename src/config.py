"""
Game Configuration & 4-Category Scoring Tables (4 to 40 Total Scale)
"""

SKIN_TONES = [
    {"name": "Warm Cream",        "rgb": (255, 230, 185), "points": 5},
    {"name": "Golden Tan",        "rgb": (220, 170, 120), "points": 6},
    {"name": "Deep Espresso",     "rgb": (90, 55, 35),    "points": 8},
    {"name": "Porcelain",         "rgb": (255, 240, 235), "points": 4},
    {"name": "Olive",             "rgb": (175, 150, 105), "points": 7},
    {"name": "Pastel Blue",       "rgb": (170, 210, 255), "points": 9},
    {"name": "Alien Slime Green", "rgb": (140, 235, 130), "points": 10},
    {"name": "Ashen Grey",        "rgb": (165, 165, 175), "points": 1},
]

BOOT_TYPES = [
    {"name": "None (Barefoot)", "points": 1},
    {"name": "Sneaker",         "points": 2},
    {"name": "Hiking",          "points": 3},
    {"name": "Chelsea",         "points": 4},
    {"name": "Steel-Toe Work",  "points": 5},
    {"name": "Combat",          "points": 6},
    {"name": "Cowboy",          "points": 8},
    {"name": "Go-Go Platform",  "points": 9},
    {"name": "Fuzzy Yeti",      "points": 10},
]

BOOT_COLORS = [
    {"name": "Tan Suede",       "rgb": (195, 145, 95),  "points": 2},
    {"name": "Matte Black",     "rgb": (38, 38, 42),    "points": 3},
    {"name": "Stark White",     "rgb": (245, 245, 248), "points": 4},
    {"name": "Rich Oxblood",    "rgb": (125, 24, 36),   "points": 6},
    {"name": "Metallic Silver", "rgb": (192, 198, 206), "points": 7},
    {"name": "Electric Blue",   "rgb": (25, 110, 255),  "points": 8},
    {"name": "Hot Pink",        "rgb": (255, 105, 180), "points": 9},
    {"name": "Neon Lime",       "rgb": (57, 255, 20),   "points": 10},
]

STICKY_MATERIALS = [
    {"name": "None (Clean)",          "rgb": (0, 0, 0),       "points": 1},
    {"name": "Swamp Mud",             "rgb": (92, 64, 38),    "points": 4},
    {"name": "Melted Marshmallow",    "rgb": (250, 248, 245), "points": 5},
    {"name": "Bubblegum",             "rgb": (255, 105, 180), "points": 6},
    {"name": "Tree Sap",              "rgb": (195, 130, 20),  "points": 7},
    {"name": "Maple Syrup",           "rgb": (210, 140, 40),  "points": 8},
    {"name": "Wet Cement",            "rgb": (132, 136, 140), "points": 9},
    {"name": "Radioactive Ectoplasm", "rgb": (50, 255, 130),  "points": 10},
]

QUESTIONS = [
    {
        "title": "STEP 1 OF 4: CHOOSE YOUR SKIN TONE",
        "subtitle": "Sets the base hue and contrast of your blob leg & foot.",
        "options": SKIN_TONES,
    },
    {
        "title": "STEP 2 OF 4: CHOOSE YOUR BOOT SILHOUETTE",
        "subtitle": "Watch the blob foot look like it fits the footwear structure.",
        "options": BOOT_TYPES,
    },
    {
        "title": "STEP 3 OF 4: CHOOSE YOUR BOOT COLOR",
        "subtitle": "Bold pigments either harmonise or clash violently.",
        "options": BOOT_COLORS,
    },
    {
        "title": "STEP 4 OF 4: CHOOSE STICKY MATERIAL",
        "subtitle": "Slather a chaotic substance over the entire fit.",
        "options": STICKY_MATERIALS,
    },
]