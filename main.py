import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import xml.etree.ElementTree as ET
import base64
import io
import numpy as np

# App setup
app = dash.Dash(__name__)
server = app.server

# Dummy ride data
default_dist = np.cumsum(np.random.rand(300) * 10)
default_speed = np.linspace(2, 11, 300)

from cassetes_constants import cassettes


# Gear-speed conversion
def speed_from_gear(front, rear, rpm):
    return (front / rear) * rpm * 2.105 / 60  # m/s

# Plot builder
def create_plot(front, cassette, rpm_range, dist_vals, speed_vals):
    traces = [go.Scatter(x=dist_vals, y=speed_vals, mode='lines', name='Speed Profile', line=dict(color='black'))]

    for rear in cassette:
        vmin = speed_from_gear(front, rear, rpm_range[0])
        vmax = speed_from_gear(front, rear, rpm_range[1])
        traces.append(go.Scatter(
            x=np.concatenate([dist_vals, dist_vals[::-1]]),
            y=np.concatenate([[vmin]*len(dist_vals), [vmax]*len(dist_vals)]),
            fill='toself', mode='lines', name=f'{rear}t',
            line=dict(width=0), opacity=0.4
        ))


    xrange = [min(dist_vals), max(dist_vals)]
    return go.Figure(data=traces, layout=go.Layout(
        title='Optimal Gear Zones',
        xaxis=dict(title='Distance (m)',
            range=xrange),
        yaxis=dict(title='Speed (m/s)', range=[0, 15]),
        legend=dict(title='Rear Cog'),
        hovermode='closest',
        plot_bgcolor='white',
        paper_bgcolor='white'
    ))

# Layout
app.layout = html.Div([
    html.H2("Interactive Gear Plot (Dash + Plotly)"),
    html.Label("Upload TCX File"),
    dcc.Upload(
        id='upload-tcx',
        children=html.Button('Upload TCX File'),
        multiple=False
    ),
    html.Div(id='upload-status', style={'margin': '10px 0'}),

    html.Label("Cadence Midpoint (RPM)"),
    dcc.Slider(id="cadence-mid", min=60, max=100, step=1, value=75,
               marks={i: str(i) for i in range(60, 101, 5)}),

    html.Label("Cadence Interval Width (±RPM)"),
    dcc.Slider(id="cadence-width", min=1, max=15, step=1, value=5,
               marks={i: str(i) for i in range(1, 16, 2)}),

    html.Label("Cassette"),
    dcc.Dropdown(id="cassette", options=[{"label": k, "value": k} for k in cassettes],
                 value="Shimano CS-HG400 9s 11–34"),

    dcc.Graph(id="gear-graph", style={"height": "600px"}),

    # Store uploaded data
    dcc.Store(id="stored-ride-data")
])

# Handle file upload
@app.callback(
    Output("stored-ride-data", "data"),
    Output("upload-status", "children"),
    Input("upload-tcx", "contents"),
    prevent_initial_call=True
)
def parse_uploaded_tcx(contents):
    if not contents:
        return dash.no_update, "Using default demo data."

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    tree = ET.parse(io.BytesIO(decoded))
    root = tree.getroot()
    ns = {
        'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
        'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'
    }

    prev_dist = 0.
    dist_vals = []
    speed_vals = []
    commul_dist_vals_1 = []
    for pt in root.findall('.//tcx:Trackpoint', ns):
        dist_el = pt.find('tcx:DistanceMeters', ns)
        spd_el = pt.find('.//ns3:TPX/ns3:Speed', ns)
        if dist_el is not None and spd_el is not None:
            curr_dist = float(dist_el.text)

            commul_dist_vals_1.append(curr_dist)
            speed_vals.append(float(spd_el.text))

            delta_dist = curr_dist - prev_dist
            dist_vals.append(delta_dist)
            prev_dist = curr_dist

    commul_dist_vals_2 = []
    prev = 0.
    for i, val in enumerate(dist_vals):
        commul_dist_vals_2.append(prev+dist_vals[i])
        prev = commul_dist_vals_2[i]

    if speed_vals:
        sorted_pairs = sorted(zip(speed_vals, dist_vals), key=lambda x: x[0])
        speed_vals, dist_vals = zip(*sorted_pairs)
        speed_vals = list(speed_vals)
        dist_vals = list(dist_vals)

    commul_dist_vals = []
    prev = 0.
    for i, val in enumerate(dist_vals):
        commul_dist_vals.append(prev+dist_vals[i])
        prev = commul_dist_vals[i]

    if not dist_vals:
        return dash.no_update, "No valid data in file."

    return {"dist": commul_dist_vals, "speed": speed_vals}, "File parsed successfully."

# Plot update
@app.callback(
    Output("gear-graph", "figure"),
    Input("cadence-mid", "value"),
    Input("cadence-width", "value"),
    Input("cassette", "value"),
    Input("stored-ride-data", "data")
)
def update_plot(mid, width, cas, stored_data):
    rpm_range = (mid - width, mid + width)
    cassette = cassettes[cas]
    if stored_data:
        dist_vals = stored_data["dist"]
        speed_vals = stored_data["speed"]
    else:
        dist_vals, speed_vals = default_dist, default_speed

    return create_plot(front=46, cassette=cassette, rpm_range=rpm_range,
                       dist_vals=dist_vals, speed_vals=speed_vals)

# Run
if __name__ == "__main__":
    app.run(debug=True)
