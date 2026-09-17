"""Display metadata for measurement fields (master prompt §8), inches only.

Kept separate from the model so templates and forms can iterate consistently
without hard-coding the field list in more than one place.
"""
from __future__ import annotations

SHIRT_FIELDS = [
    ("shirt_length", "Length"),
    ("shirt_chest", "Chest"),
    ("shirt_shoulder", "Shoulder"),
    ("shirt_sleeves", "Sleeves"),
    ("shirt_neck", "Neck"),
]

PANT_FIELDS = [
    ("pant_length", "Length"),
    ("pant_waist", "Waist"),
    ("pant_hips", "Hips"),
    ("pant_mori", "Mori / pant end"),
]

ALL_FIELDS = SHIRT_FIELDS + PANT_FIELDS
