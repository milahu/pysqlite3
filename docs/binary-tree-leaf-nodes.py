def print_binary_tree_leaf_nodes_inorder(root_node):
  """
  print leaf nodes of a binary tree in-order
  https://www.geeksforgeeks.org/inorder-tree-traversal-without-recursion/
  """
  def is_leaf(node):
    return node.left == None and node.right == None
  node = root_node
  stack = []
  while True:
    if node:
      stack.append(node)
      node = node.left # go left
    elif stack:
      node = stack.pop() # go up
      if is_leaf(node):
        print(node.value, end=" ")
      node = node.right # go right
    else:
      break
  print()

class Node:
  def __init__(self, value, left=None, right=None):
    self.value = value
    self.left = left
    self.right = right

#    4
#  2   6
# 1 3 5 7
root_node = Node(
  value=4,
  left=Node(
    value=2,
    left=Node(1),
    right=Node(3),
  ),
  right=Node(
    value=6,
    left=Node(5),
    right=Node(7),
  ),
)

print_binary_tree_leaf_nodes_inorder(root_node)

# result:
# 1 3 5 7
