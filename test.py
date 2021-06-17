# import
from jaal import Jaal
import os
import pandas as pd
def load_got(filter_conections_threshold=10):
    """Load the Dataset
    Parameters
    -----------
    filter_conections_threshold: int
    """
    # resolve path
    this_dir, _ = os.path.split(__file__)
    # load the edge and node data
    edge_df = pd.read_csv(os.path.join(this_dir, "network", "network_edge_df.csv"))
    node_df = pd.read_csv(os.path.join(this_dir, "network", "network_node_df.csv"))
    # return 
    return edge_df, node_df

# load the data
edge_df, node_df = load_got()
# init Jaal and run server
Jaal(edge_df, node_df).plot()
