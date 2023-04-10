# https://stackoverflow.com/questions/12029326 # Suggest an algorithm to traverse a B+ tree

def print_bplus_tree_leaf_nodes_inorder(root_node):
  """
  print leaf nodes of a B+ tree in-order
  """
  node = root_node
  while node.type == "branch":
    node = node.children[0] # go left to leftmost leaf node
  while node:
    assert node.type == "leaf"
    for idx, key in enumerate(node.keys): # loop keys of leaf node
      value = node.values[idx]
      print(f"{key}={value}", end=" ")
    node = node.right # go right to next leaf node
  print()

class BranchNode:
  def __init__(self, keys=[], children=[]):
    self.keys = keys
    self.children = children
    self.type = "branch"

class LeafNode:
  def __init__(self, keys=[], values=[]):
    self.keys = keys
    self.values = values
    self.right = None
    self.type = "leaf"

#     47_
# 123 456 789
# abc def ghi
root_node = BranchNode([4, 7, None], [
  LeafNode([1, 2, 3], ["a", "b", "c"]),
  LeafNode([4, 5, 6], ["d", "e", "f"]),
  LeafNode([7, 8, 9], ["g", "h", "i"]),
])

# set right pointers of leaf nodes
root_node.children[0].right = root_node.children[1]
root_node.children[1].right = root_node.children[2]
root_node.children[2].right = None

print_bplus_tree_leaf_nodes_inorder(root_node)

# result:
# 1=a 2=b 3=c 4=d 5=e 6=f 7=g 8=h 9=i 

