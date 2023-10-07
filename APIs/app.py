from zipfile import ZipFile
from utils import *
from graph_ts import ExpertSim, EdgeID
from flask import Flask, jsonify, request, flash
from flask_cors import CORS

from pathlib import Path
from werkzeug.utils import secure_filename
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from functools import wraps

import networkx as nx
import plotly.io as pio

MAX_TAU = 200
COLOR_SCALE = 'Viridis'
UPLOAD_FOLDER = './upload'
ALLOWED_EXTENSIONS = {'.zip'}

global mem_dgcm
mem_dgcm = None

app = Flask(__name__)

################################################################
# region PREP
def cors_header(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response, status = func(*args, **kwargs)
        headers = {'access_control_allow_origin': '*'}
        return response, status, headers
    return wrapper


cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

upload_path = Path(app.config['UPLOAD_FOLDER'])
upload_path.mkdir(parents=True, exist_ok=True)


# endregion 
################################################################

################################
# region LOAD 
@app.route('/api/all_graphs', methods=['POST'])
@cors_header
def all_graphs():
    extract_all_zips(upload_path)
    graph_json_paths = list(upload_path.glob('./*/graph_info.json'))

    # Extract the parent directories of these files
    directories_with_graph_json = [p.parent for p in graph_json_paths]

    # Extract names of the directories
    directory_names = [dir_.name for dir_ in directories_with_graph_json]

    return jsonify(directory_names), 200


@app.route('/api/load_graph', methods=['POST'])
@cors_header
def load_dgcm():
    global mem_dgcm
    data = request.get_json()
    if "graph_name" not in data:
        return "Should give a valid path to the dynamic graph", 400
    
    mem_dgcm = ExpertSim.from_path(Path(UPLOAD_FOLDER)/data["graph_name"])
    data = dgraph_to_visjs(mem_dgcm, MAX_TAU)
    return jsonify(data), 200

@app.route('/api/upload', methods=['POST', 'OPTIONS'])
@cors_header
def upload_file():
    if request.method in {'POST', 'OPTIONS'}:
        if 'file' not in request.files:
            return f"No file part", 400
        
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return f"No selected file", 400
        
        if file and Path(file.filename).suffix in ALLOWED_EXTENSIONS:
            filename = secure_filename(file.filename)

            file.save(upload_path/filename)
            extract_all_zips(upload_path)
            return jsonify({'graph_name': f"{Path(filename).stem}"}), 200

    return f"invalid request type {request.method}", 400

# endregion
################################

################################
# region CREATION PIPELINE 
@app.route('/api/new', methods=['POST'])
@cors_header
def create():
    pass

# endregion
################################

################################
# region EDIT
@app.route('/api/data')
@cors_header
def get_data():
    global mem_dgcm
    data = dgraph_to_visjs(mem_dgcm, MAX_TAU)
    return jsonify(data), 200

@app.route('/api/edit/add_node', methods=['POST'])
@cors_header
def add_node():
    global mem_dgcm
    data = request.get_json() 
    
    if 'nodeName' not in data:
        return 'Error: Missing parameter in the request JSON.', 400

    # node =  data['nodeName']
    # node_type = data['nodeType']
    # node_bounds = [int(i) for i in data['bounds']]
    # offset = data['offset']
    # memo = data['memo']
    # is_todo = data['is_todo']
    
    # node_attr = {
    #     'type': node_type,
    #     'range': node_bounds,
    #     'offset': offset,
    #     'memo': memo,
    #     'is_todo': is_todo
    # }
    
    n = data['nodeName']
    try:
        mem_dgcm.add_node(n, **data['attr'])
    except Exception as e:
        return f"{type(e)}: {str(e)}", 400

    print(mem_dgcm.nodes[n])
    response_data = {"id": n, 
                     "label": n, 
                     "title": str(mem_dgcm.nodes[n]), 
                     "type": mem_dgcm.nodes[n]['type'],
                     "shape": 'circle',
                     "mass": 0.5,}
    
    return jsonify(response_data), 200

@app.route('/api/query/get_node', methods=['POST'])
@cors_header
def get_node():
    global mem_dgcm
    data = request.get_json() 
    if 'nodeName' not in data:
        return 'Error: Missing "lag" parameter in the request JSON.', 400

    u = data['nodeName']
    response_data = mem_dgcm.nodes[u]
    return jsonify(response_data), 200


@app.route('/api/edit/update_node', methods=['POST'])
@cors_header
def update_node():
    global mem_dgcm
    data = request.get_json()
    if 'nodeName' not in data:
        return 'Error: Missing parameters nodeName in the request JSON.', 400
    
    n = data['nodeName']
    nx.set_node_attributes(mem_dgcm, {n: data['attr']})
    
    response_data = {"id": n, 
                     "label": n, 
                     "title": mem_dgcm.nodes[n],
                     "type": mem_dgcm.nodes[n]['type'],
                     "shape": 'circle',
                     "mass": 0.5}
    return jsonify(response_data), 200


@app.route('/api/edit/add_edge', methods=['POST'])
@cors_header
def add_edge():
    global mem_dgcm
    data = request.get_json()
    if 'from' not in data or 'to' not in data or 'lag' not in data:
        return 'Error: Missing parameters in the request JSON.', 400
    
    node_from = data['from']
    node_to = data['to']
    lag = int(data['lag'])
    data['lag'] = int(data['lag'])
    if lag > MAX_TAU:
        return 'Error: lag exceeds max tau', 400
    
    try:
        parse_attr(data['attr'])
        mem_dgcm.add_edge(node_from, node_to, lag, **data['attr'])
    except Exception as e:
        return jsonify(f"{type(e)}: {str(e)}"), 400
    
    response_data = get_edge_opts_for_vsn(node_from, node_to, lag, mem_dgcm[node_from][node_to][lag], max_tau=MAX_TAU, colorscale=COLOR_SCALE)
    
    return jsonify(response_data), 200


@app.route('/api/query/get_edge', methods=['POST'])
@cors_header
def get_edge():
    global mem_dgcm
    data = request.get_json()
    if 'eid' not in data:
        return 'Error: Missing parameters eid in the request JSON.', 400
    
    eid = EdgeID.from_string(data['eid'])
                      
    lag, u = eid.lag_origins[0]
    v = eid.target
    
    response_data = mem_dgcm[u][v][lag]
    return jsonify(response_data), 200


@app.route('/api/edit/update_edge', methods=['POST'])
@cors_header
def update_edge():
    global mem_dgcm
    data = request.get_json()
    if 'attr' not in data:
        return 'Error: Missing parameters eid or attr in the request JSON.', 400
    
    u, v, lag = data['from'], data['to'], int(data['lag'])
    old_lag = int(data['old_lag'])
    
    parse_attr(data['attr'])
    if old_lag != lag:
        mem_dgcm.remove_edge(u, v, old_lag)
        mem_dgcm.add_edge(u, v, lag, **data['attr'])
    else:
        nx.set_edge_attributes(mem_dgcm, {(u, v, lag): data['attr']})
    
    response_data = get_edge_opts_for_vsn(u, v, lag, mem_dgcm[u][v][lag], max_tau=MAX_TAU, colorscale=COLOR_SCALE)
    return jsonify(response_data), 200


@app.route('/api/edit/remove_edge', methods=['POST'])
@cors_header
def remove_edge():
    global mem_dgcm
    data = request.get_json()
    if 'eid' not in data:
        return 'Error: Missing parameters eid in the request JSON.', 400
    
    eid = EdgeID.from_string(data['eid'])
                            
    lag, u = eid.lag_origins[0]
    v = eid.target
    
    mem_dgcm.remove_edge(u, v, lag)
    
    return 'success', 200
    
    
@app.route('/api/edit/remove_node', methods=['POST'])
@cors_header
def remove_node():
    global mem_dgcm
    data = request.get_json()
    if 'nodeName' not in data:
        return 'Error: Missing parameters eid in the request JSON.', 400

    n = data['nodeName']
    mem_dgcm.remove_node(n)

    return 'success', 200


# endregion EDIT
################################

################################
# region simulation 

@app.route('/api/sim_plot', methods=['POST'])
@cors_header
def get_sim_plot():
    global mem_dgcm
    simopt = request.get_json()
    
    if "len" not in simopt: 
        return 'Error: Missing parameters in the request JSON.', 400
    
    df = mem_dgcm.simulate_process(int(simopt["len"]))
    fig = make_subplots(rows=len(df.columns), cols=1, shared_xaxes=True, vertical_spacing=0.02)

    for i, column in enumerate(df.columns):
        fig.add_trace(go.Scatter(x=df.index, y=df[column], name=column, mode='lines'), row=i+1, col=1)
        fig.update_yaxes(title_text=column, row=i+1, col=1)

    # Generate the offline plot
    plot_div = pio.to_html(fig, full_html=False)

    print("done!")
    # Export the plot as a div element
    return jsonify(plot_div), 200
        
@app.route('/api/plotly', methods=['POST'])
@cors_header
def get_plotly_json():
    global mem_dgcm
    simopt = request.get_json()
    
    if "len" not in simopt: 
        return 'Error: Missing parameters in the request JSON.', 400
    
    df = mem_dgcm.simulate_process(int(simopt["len"]))
    fig = make_subplots(rows=len(df.columns), cols=1, shared_xaxes=True, vertical_spacing=0.02)

    for i, column in enumerate(df.columns):
        fig.add_trace(go.Scatter(x=df.index, y=df[column], name=column, mode='lines'), row=i+1, col=1)
        fig.update_yaxes(title_text=column, row=i+1, col=1)
        
    fig.update_layout(
        margin=dict(l=40, r=10, t=10, b=10),  # Adjust these values as desired
        autosize=True
    )

    # convert to json
    fig_json = pio.to_json(fig)

    print("done!")
    
    return fig_json, 200
        

# endregion 
########################################################



if __name__ == '__main__':
    app.run(debug=True)