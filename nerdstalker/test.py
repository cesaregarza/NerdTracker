# %%
import plotly.graph_objects as go
from PIL import Image, ImageDraw

img = Image.open(r"F:\Dev\NerdTracker\assets\ShootHouse.png")

from ..assets.map_data import map_calibration_points, map_image_paths
from .heatmap.map_scaler import map_autoscaler

import os
import sqlalchemy as db
import pandas as pd
import numpy as np

db_data = {
    "username": "nerdtracker",
    "password": os.getenv("NERDDBPASSWORD"),
    "db_url":   "nerdtracker.cegarza.com:3306/nerd_tracker_sql_db"
}

db_data['password'] = "iwishiknewhowtopressmouse1"

def return_engine():
    db_url = f"{db_data['username']}:{db_data['password']}@{db_data['db_url']}"
    engine = db.create_engine(f"mysql+pymysql://{db_url}", pool_size=20)
    return engine

engine = return_engine()

# %%
sheng   = pd.read_sql("SELECT eg.* FROM engagements eg LEFT JOIN (SELECT DISTINCT match_id, map_id FROM players) pl ON pl.match_id = eg.match_id WHERE pl.map_id = 'mp_m_speed'", engine)
calibration_points = np.array(map_calibration_points["mp_m_speed"])
stform = map_autoscaler(calibration_points[:, 0, :], calibration_points[:, 1, :])

sheng[['ax1', 'ay1']] = stform.transform(sheng[['ax', 'ay']])
sheng[['vx1', 'vy1']] = stform.transform(sheng[['vx', 'vy']])

colorscale = [  [0.0, 'rgba(165, 0, 38, 0.0)'],
                [1e-1, 'rgba(165,0,38,.35)'],
                # [1e-4, 'rgba(180, 43, 32, 0.4)'],
                # [1e-3, 'rgba(210,128,19,0.45)'],
                # [1e-2, 'rgba(225,170,13,0.5)'],
                # [1e-1, 'rgba(240, 213, 6, 0.55)'],
                [1, 'rgba(255, 255, 0, 0.6)']]
# %%
letter = "a"
im_height = img.height
im_width  = img.width
fig = go.Figure()
fig.add_trace(
    go.Scattergl(
        x=eng3[f'{letter}x'],
        y=im_height - eng3[f'{letter}y'],
        # colorscale=colorscale,
        mode="markers",
        opacity=1,
        xaxis="x",
        yaxis="y",
        # nbinsx=100,
        # nbinsy=100,
    )
)

fig.update_xaxes(
    visible=False,
    range=[0, im_height]
)

fig.update_yaxes(
    visible=False,
    range=[0, im_height],
    scaleanchor="x"
)

fig.add_layout_image(
    dict(
        source=img,
        xref="x",
        yref="y",
        x=0,
        y=im_height,
        sizex=im_width,
        sizey=im_height,
        sizing="stretch",
        opacity=1,
        layer="below"
    )
)
margin = 30
fig.update_layout(
    margin={"l": margin, "r": margin, "t": margin, "b": margin}
)
fig.show(config={'doubleClick': 'reset'})
# %%
