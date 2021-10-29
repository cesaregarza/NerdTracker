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
        [[-788.4292, 2300.2275],    [171, 642]],
        [[ 264.85834,2508.9119],    [141, 506]],
        [[-945.97455,1701.4312],    [249, 641]],
        [[1336.8588, 1702.8577],    [252, 352]],
        [[659.02216, -1248.1263],   [651, 440]],
        [[- 277.72818,-1395.3425],  [672, 573]]
    ],
    "mp_m_speed": [
        [[-763.9451,   688.8744],   [713,509]],
        [[-1632.9628, 2285.7134],   [440,664]],
        [[-555.8494,  2200.0884],   [435,471]],
        [[-846.9074,  260.04932],   [793,523]],
        [[-1525.6207,  1989.349],   [476,648]],
        [[-1538.0742, 3118.4974],   [265,655]],
        [[-991.1258,   1486.244],   [566,550]],
        [[-122.53425, 2862.4595],   [319,394]],
        [[-1061.43,      80.625],   [826,566]],
        [[-1104.04,    1648.633],   [541,570]],
        [[215.3582,    2512.055],   [382,331]],
        [[-752.875,    735.1619],   [709,510]]
    ]
}