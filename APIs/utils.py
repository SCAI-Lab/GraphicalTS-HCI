import sys
sys.path.insert(1, '../dyn_graph_syn/src')
import json
import plotly.colors as colors
import numpy as np
from pathlib import Path
from zipfile import ZipFile
import os

MAX_TAU = 16


def parse_attr(attr):
    to_del = []
    for key, val in attr.items():
        if val is None: 
            to_del.append(key)
            continue
        if key in {'input_len', 'effect_len'}:
            attr[key] = int(val)
        if key == 'scale':
            attr[key] = float(val)
            
    for k in to_del:
        del attr[k]


def get_edge_opts_for_vsn(u, v, t, data, color_ref=None, max_tau=MAX_TAU, colorscale=None, with_attr=False, graph_obj=None):
    if color_ref is None:
        my_color = get_color_for_lag(t, max_tau=max_tau, colorscale=colorscale)
    else:
        my_color = color_ref[t]
    response = {"id": f"O%{u}%L%{t}%D%{v}", 
                "to": v, 
                "from": u, 
                "arrows": 'to',
                "lag": t,
                "title": str(data),
                "color": {"color":my_color}
                }
    if with_attr:
        response.update(data)
    return response

def dgraph_to_visjs(dgraph, max_tau):
    self_loop_counts = {n: 0 for n in dgraph.nodes}
    
    color_ref = get_colors_for_lags(dgraph.lags, max_tau=max_tau)
    nodes = []
    edges = []
    for n, data in dgraph.nodes(data=True):
        node_info = str(data)
        nodes.append({"id": n, 
                      "label": n, 
                      "type": data['type'],
                      "title": node_info, 
                      "shape": 'circle',
                      "mass": 0.5})
    
    for u, v, t, data in dgraph.edges(keys=True, data=True):
        # 1. the basic def of the edge
        edge_opt = get_edge_opts_for_vsn(u, v, t, data, color_ref)
        # 2. self loop counts
        if u == v: 
            self_loop_counts[u] += 1;
            if self_loop_counts[u] > 1:
                edge_opt["selfReference"] = {"size": 20,
                                             "angle": np.pi/self_loop_counts[u],
                                             "renderBehindTheNode": True}
            
        edges.append(edge_opt)
    

    result = dict(nodes=nodes, edges=edges)
    package = {"graph": result,
               "lags": dgraph.lags,
               "colors": color_ref
               }
    
    return package


def get_colors_for_lags(lags, max_tau=None, colorscale='Viridis'):
    if max_tau is None:
        max_tau = np.linalg.norm(lags)
    color_vals = np.array(lags)
    generated_colors = colors.sample_colorscale(colorscale, color_vals/max_tau)
    generated_colors = {lags[i]: generated_colors[i] for i in range(len(lags))}
    return generated_colors

def get_color_for_lag(lag, max_tau, colorscale='Viridis'):
    return colors.sample_colorscale(colorscale, lag/max_tau)


# TODO: check if the zip format is correct
def extract_all_zips(base_path):
    base_path = Path(base_path)
    
    data_zips = list(base_path.glob("*.zip"))
    
    for dzip in data_zips:
        with ZipFile(dzip, 'r') as zip_ref:
            zip_ref.extractall(base_path)
        try:
            os.remove(dzip)
            print(f'Successfully deleted {dzip}')
        except Exception as e:
            print(f'Error occurred while deleting file {dzip}: {str(e)}')


