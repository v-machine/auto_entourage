"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

__author__ = "Vincent Mai"
__version__ = "2020.10.05"

from Grasshopper import DataTree
import ghpythonlib.treehelpers as th

class TreeHandler:
    """Decorating class to handle trees as args for user define functions
    
        Example:
            @treeHandler
            def user_define_func(t1, t2):
                pass
    """
    def __init__(self, func):
        self.func = func
        
    def __call__(self, *args, **kwargs):
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
        # for i in range(max([len(t) for t in trees])): 
        # for i in range(max(trees, key=lambda x: len(x))):
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
    def branchDataSize(tree):
        """Returns an equivalently structured GH_Tree of  num of points
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