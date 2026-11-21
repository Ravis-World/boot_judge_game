"""
Style-Weighted randomised 4-40 Tier-List & Roast Judge Engine
randomises category point values based on the chosen style's aesthetic range,
keeps the 4-category breakdown and 4-40 total score 100% synchronized,
and ensures all tier titles and judge dialogue match the exact result.
"""

import json
import os
import random

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
COMBOS_FILE = os.path.join(CURRENT_DIR, "combos.json")


def _load_combos():
    """Loads the combo definitions from src/combos.json."""
    try:
        with open(COMBOS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("combos", [])
    except Exception:
        return []


def _roll_style_points(base_pts, spread=2, min_val=1, max_val=10):
    """
    randomises a category score (1-10) around its style's base affinity
    so similar styles roll within a cohesive range while keeping variety.
    """
    low = max(min_val, base_pts - spread)
    high = min(max_val, base_pts + spread)
    return random.randint(low, high)


def _build_tier_and_roast(total_score, skin_name, footwear_desc, sticky_name, is_barefoot, custom_roast=None):
    """
    Builds an accurate tier title and dialogue string that always matches
    the exact randomised total_score (4-40) and player selections.
    """
    if total_score >= 35:
        tier_title = f"GOD-TIER ({total_score}/40): AVANT-GARDE ICON"
        default_roast = (
            f"A staggering {total_score}/40! Pairing {skin_name.lower()} skin with "
            f"{footwear_desc} and {sticky_name.lower()} breaks every rule of fashion in the best way."
        )
    elif total_score >= 27:
        tier_title = f"A-TIER ({total_score}/40): HIGH-FASHION HAZARD"
        default_roast = (
            f"Scored {total_score}/40! Bold, messy, and unforgettable—the "
            f"{sticky_name.lower()} transforms {footwear_desc} into pure runway drama."
        )
    elif total_score >= 18:
        tier_title = f"B-TIER ({total_score}/40): CHAOTIC NEUTRAL"
        default_roast = (
            f"A solid {total_score}/40. Mixing {skin_name.lower()} skin, {footwear_desc}, "
            f"and {sticky_name.lower()} shouldn't work, yet you're somehow pulling it off."
        )
    elif total_score >= 10:
        tier_title = f"C-TIER ({total_score}/40): PLAYGROUND ACCIDENT"
        default_roast = (
            f"Only {total_score}/40. This looks less like high fashion and more like "
            f"stepping in {sticky_name.lower()} on the way to work."
        )
    else:
        tier_title = f"F-TIER ({total_score}/40): AGGRESSIVELY MID"
        default_roast = (
            f"Bottom of the chart at {total_score}/40. Even with {sticky_name.lower()}, "
            f"{footwear_desc} on {skin_name.lower()} skin is way too tame for the runway."
        )

    if custom_roast:
        roast_text = custom_roast.format(
            score=total_score,
            skin=skin_name.lower(),
            footwear=footwear_desc,
            sticky=sticky_name.lower(),
        )
    else:
        roast_text = default_roast

    return tier_title, roast_text


def evaluate_fit(skin, boot, color, sticky):
    """
    Evaluates the fit by randomising point values weighted by the selected style.
    - When barefoot ("None (Barefoot)"), boot color is skipped and scored as 0/10.
    - Total score (4-40) is strictly derived from the sum of the 4 category rolls
      so the bars, total score, tier rank, and dialogue never contradict each other.
    """
    is_barefoot = (boot["name"] == "None (Barefoot)")
    effective_color_name = None if is_barefoot else color["name"]

    player_choice = {
        "skin": skin["name"],
        "boot": boot["name"],
        "color": effective_color_name,
        "sticky": sticky["name"],
    }

    combos = _load_combos()
    best_match = None
    best_key = (-1, -1)

    for combo in combos:
        criteria = combo.get("criteria", {})
        if not criteria:
            continue

        if all(player_choice.get(cat) == val for cat, val in criteria.items()):
            specificity = len(criteria)
            weight = combo.get("max_score", combo.get("score", 20))
            match_key = (specificity, weight)
            if match_key > best_key:
                best_key = match_key
                best_match = combo

    # Roll randomised points per category weighted by the chosen style
    skin_pts = _roll_style_points(skin["points"], spread=2, min_val=1, max_val=10)
    boot_pts = _roll_style_points(boot["points"], spread=2, min_val=1, max_val=10)
    color_pts = 0 if is_barefoot else _roll_style_points(color["points"], spread=2, min_val=1, max_val=10)
    sticky_pts = _roll_style_points(sticky["points"], spread=2, min_val=1, max_val=10)

    # If a named style combo matched, nudge the rolled categories into that combo's target range
    if best_match and "score_range" in best_match:
        low_target, high_target = best_match["score_range"]
        target_total = random.randint(low_target, high_target)

        # Distribute target_total naturally across active categories (1-10 each)
        active_indices = [0, 1, 3] if is_barefoot else [0, 1, 2, 3]
        rolled = [skin_pts, boot_pts, color_pts, sticky_pts]

        # Clamp initial active rolls to [1, 10]
        for idx in active_indices:
            rolled[idx] = max(1, min(10, rolled[idx]))

        # Adjust step-by-step until sum equals target_total while staying within 1..10
        guard = 0
        while sum(rolled[i] for i in active_indices) != target_total and guard < 200:
            guard += 1
            cur_sum = sum(rolled[i] for i in active_indices)
            idx = random.choice(active_indices)
            if cur_sum < target_total and rolled[idx] < 10:
                rolled[idx] += 1
            elif cur_sum > target_total and rolled[idx] > 1:
                rolled[idx] -= 1

        skin_pts, boot_pts, color_pts, sticky_pts = rolled

    # Enforce strict 4..40 total matching the exact sum of the 4 bars
    raw_sum = skin_pts + boot_pts + color_pts + sticky_pts
    if raw_sum < 4:
        # Top up active categories so minimum total is always 4
        active_indices = [0, 1, 3] if is_barefoot else [0, 1, 2, 3]
        rolled = [skin_pts, boot_pts, color_pts, sticky_pts]
        while sum(rolled[i] for i in active_indices) < 4:
            idx = random.choice(active_indices)
            if rolled[idx] < 10:
                rolled[idx] += 1
        skin_pts, boot_pts, color_pts, sticky_pts = rolled

    total_score = max(4, min(40, skin_pts + boot_pts + color_pts + sticky_pts))

    breakdown = [
        ("Skin Tone Synergy", skin_pts),
        ("Boot Silhouette", boot_pts),
        ("Boot Color Pop", color_pts),
        ("The Stick Factor", sticky_pts),
    ]

    footwear_desc = "bare blob feet" if is_barefoot else f"{color['name'].lower()} {boot['name']} boots"

    if best_match:
        combo_name = best_match["name"]
        tier_title, roast_text = _build_tier_and_roast(
            total_score=total_score,
            skin_name=skin["name"],
            footwear_desc=footwear_desc,
            sticky_name=sticky["name"],
            is_barefoot=is_barefoot,
            custom_roast=best_match.get("roast"),
        )
        return breakdown, total_score, combo_name, tier_title, roast_text

    combo_name = (
        f"Barefoot with {sticky['name']}"
        if is_barefoot
        else f"{color['name']} {boot['name']} with {sticky['name']}"
    )
    tier_title, roast_text = _build_tier_and_roast(
        total_score=total_score,
        skin_name=skin["name"],
        footwear_desc=footwear_desc,
        sticky_name=sticky["name"],
        is_barefoot=is_barefoot,
    )
    return breakdown, total_score, combo_name, tier_title, roast_text