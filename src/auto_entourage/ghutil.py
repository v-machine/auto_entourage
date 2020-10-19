"""Custom Grasshopper Utilities Module
"""
__author__ = "Vincent Mai"
__version__ = "2020.10.05"

import System
import Rhino.RhinoDoc
import scriptcontext as sc
from Grasshopper import DataTree
import ghpythonlib.treehelpers as th

class RhinoDocContext:
    """Context Manager to enter the RhinoDoc.ActiveDoc Context
    """
    def __init__(self):
        self.ghdoc = sc.doc
        self.rhinodoc = Rhino.RhinoDoc.ActiveDoc

    def __enter__(self):
        sc.doc = self.rhinodoc

    def __exit__(self, type, value, traceback):
        sc.doc = self.ghdoc

class NewLayerContext:
    """Context Manager to call a function in a new layer
    """
    def __init__(self, layer_name):
        self.layer_name = layer_name

    def __enter__(self):
        self.__deleteLayer(self.layer_name)
        self.__createAndSetCurrentLayer(self.layer_name)

    def __exit__(self, type, value, traceback):
        self.__resetLayer()

    def __createAndSetCurrentLayer(self, layer_name):
        """Creates a new layer and set it as the current layer
        """
        with RhinoDocContext():
            layer = sc.doc.Layers.FindName(layer_name)
            if layer is None:
                layer_idx = sc.doc.Layers.Add(layer_name, System.Drawing.Color.Black)
            else:
                layer_idx = layer.Index
            sc.doc.Layers.SetCurrentLayerIndex(layer_idx, True)
            
    def __resetLayer(self):
        """Resets current layer to the default (first) layer
        """
        with RhinoDocContext():
            sc.doc.Layers.SetCurrentLayerIndex(0, True)
            
    def __deleteLayer(self, layer_name):
        """Deletes a layer and all objects inside
        """
        with RhinoDocContext():
            rhinoObjects = sc.doc.Objects.FindByLayer(layer_name)
            if rhinoObjects:
                for obj in rhinoObjects:
                    sc.doc.Objects.Delete(obj)
            sc.doc.Layers.SetCurrentLayerIndex(0, True)
            sc.doc.Layers.Delete(sc.doc.Layers.FindName(layer_name), True)

class TreeHandler:
    """Decorating class to handle trees as args for user define functions
    """
    def __init__(self, func):
        self.func = func
        
    def __call__(self, *args, **kwargs):
        args = map(TreeHandler.toTree, args)
        for arg in args:
            arg.SimplifyPaths()
        depths = [self.__treeDepth(t) for t in args]
        trees = [th.tree_to_list(arg, lambda x: x) for arg in args]
        return th.list_to_tree(self.__ghtree_handler(trees, depths))

    def __treeDepth(self, t):
        """returns the depth of the gh tree"""
        path = t.Path(t.BranchCount-1)
        return len(str(path).split(";"))

    def __intertwine(self, trees):
        """intertwine two trees with equal depth
        """
        result = []
        for i in range(max([len(t) for t in trees])): 
            items = [t[min(i, len(t)-1)] for t in trees]
            if isinstance(items[0], list):
                result.append(self.__intertwine(items))
            else:
                result.append(self.func(*items))
        return result

    def __ghtree_handler(self, trees, depths):
        """Returns appropriate GH Tree by explicit looping
        """
        max_depth = max(depths)
        for idx, d in enumerate(depths):
            for j in range(max_depth-d):
                trees[idx] = [trees[idx]]
        return self.__intertwine(trees)
    
    @staticmethod
    def toTree(arg):
        """Converts object to Grasshopper.DataTree
        """
        if isinstance(arg, DataTree[object]):
            return arg
        else:
            if not isinstance(arg, list):
                return th.list_to_tree([arg])
            else:
                return th.list_to_tree(arg)
    
    @staticmethod
    def topologyTree(tree):
        """Returns the tree's topology in an equivalently structure
            Example:
                >>> branchDataSize([[a, b, c], [x, y]])
                >>> tree {1; 1}
        """
        def __listBranchSize(tree):
            if isinstance(tree, DataTree[object]):
                tree.SimplifyPaths()
                tree = th.tree_to_list(tree, lambda x: x) 
            result = []
            for b in tree:
                if isinstance(b[0], list):
                    result.append(__listBranchSize(b))
                result.append([len(b)])
            return result
        return th.list_to_tree(__listBranchSize(tree))
