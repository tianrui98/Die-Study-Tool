"""Functions that can run independently of tkinter
"""

import os
from objects import *

def open_cluster(project_address):
    """Open an unfinished cluster.
    Create a Cluster object

    Return: Cluster object
    """
    #TODO read log then open undone cluster
    all_clusters = [f for f in os.listdir(project_address) if not f.startswith('.')]
    cluster_name =  all_clusters[0]
    cluster_address = os.path.join(project_address, cluster_name )

    #create cluster object
    return Cluster(folder_address = cluster_address)


