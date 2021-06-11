import pathlib

base_path = pathlib.Path(__file__).parent

def construct_path(path):
    return str( (base_path / path).resolve())

map_remap = {
    "mp_deadzone":      "Arklov Peak",
    "mp_aniyah_tac":    "Aniyah Incursion",
    "mp_hackney_am":    "Hackney Yard",
    "mp_backlot2":      "Talsik Backlot",
    "mp_runner":        "Gun Runner",
    "mp_scrapyard":     "Abandoned Scrapyard",
    "mp_cave_am":       "Azhir Cave",
    "mp_crash2":        "Crash",
    "mp_oilrig":        "Petrov Oil Rig",
    "mp_hardhat":       "Hardhat",
    "mp_garden":        "Cheshire Park",
    "mp_rust":          "Rust",
    "mp_spear":         "Rammaza",
    "mp_hideout":       "Khandor Hideout",
    "mp_petrograd":     "St. Petrograd",
    "mp_shipment":      "Shipment",
    "mp_killhouse":     "Killhouse",
    "mp_m_speed":       "Shoothouse",
    "mp_harbor":        "Suldal Harbor",
    "mp_emporium":      "Atlas Superstore",
    "mp_vacant":        "Vacant",
    "mp_village2":      "Hovec Sawmill",
    "mp_broadcast2":    "Broadcast",
    "mp_piccadilly":    "Picadilly"
}


map_image_paths = {
    key: construct_path(f".\\{map_remap[key]}.png".replace(" ", "").replace(".", ""))
    for key in map_remap
}

map_calibration_points = {
    "mp_backlot2": [
        [[-788.4292, 2300.2275],  [171, 642]],
        [[ 264.85834,2508.9119],  [141, 506]],
        [[-945.97455,1701.4312],  [249, 641]],
        [[1336.8588, 1702.8577],  [252, 352]],
        [[659.02216, -1248.1263], [651, 440]],
        [[- 277.72818,-1395.3425],[672, 573]]
    ],
}

map_transformation_matrices = {
    "mp_backlot2": [
        [0.0004877938250862725, -0.13578215606845145, 482.02997349733283],
        [-0.13113726864176986, 0.0005792424381414331, 530.5625557574807],
        [0, 0, 1]
    ]

}