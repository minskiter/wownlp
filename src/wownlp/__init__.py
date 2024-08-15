import random
import os
import sys
import importlib

def set_seed(seed: int = 42):
    """
    set seed

    Args:
        seed (int, optional): the seed of random. Defaults to 42.
    """
    random.seed(seed)
    os.environ['PYTHONHASHSEED']=str(seed)
    os.environ["CUBLAS_WORKSPACE_CONFIG"]=":16:8"
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.enabled = False
        # scatter_add_cuda_kernel does not have a deterministic implementation
        # torch.use_deterministic_algorithms(True)
    except ImportError:
        pass
  
def is_in_notebook():
    """
    Check if in notebook environment

    Returns:
        bool: True if it is in a notebook, otherwise False.
    """
    try:
        # Test adapted from tqdm.autonotebook: https://github.com/tqdm/tqdm/blob/master/tqdm/autonotebook.py
        get_ipython = sys.modules["IPython"].get_ipython
        if "IPKernelApp" not in get_ipython().config:
            raise ImportError("console")
        if "VSCODE_PID" in os.environ:
            raise ImportError("vscode")
        if "DATABRICKS_RUNTIME_VERSION" in os.environ and os.environ["DATABRICKS_RUNTIME_VERSION"] < "11.0":
            # Databricks Runtime 11.0 and above uses IPython kernel by default so it should be compatible with Jupyter notebook
            # https://docs.microsoft.com/en-us/azure/databricks/notebooks/ipython-kernel
            raise ImportError("databricks")

        return importlib.util.find_spec("IPython") is not None
    except (AttributeError, ImportError, KeyError):
        return False  