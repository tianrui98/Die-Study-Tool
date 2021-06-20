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
    cluster_name =  os.listdir(project_address) [0]
    cluster_address = os.path.join(project_address, cluster_name )

    #create cluster object
    return Cluster(folder_address = cluster_address)


