s1 = "if x, then y"
s2 = "x and y"
s3 = "x or y"
s4 = "( x or y ) and z"
s5 = "( x and ( y and z ) ) and a"
s6 = "if ( ( a and b ) and x ), then c"
s7 = "if ( x or ( a and b ) ), then c"

def split_into_list(s):
	remove_punc = str.maketrans("", "", ",.!")
	s = s.translate(remove_punc)
	return s.split(" ")

def remove_then(list_x):
	list_x = [x for x in list_x if x != "if"]
	return list_x

class LogicPackage:
	def __init__(self):
		self.logic_package = []

	def change_into_package(self, list_x):
		tracking_idx = 0
		
		def change_into_package_helper(list_x):
			result = []

			nonlocal tracking_idx
			while tracking_idx < len(list_x):
				if list_x[tracking_idx] not in ("(", ")"):
					result.append(list_x[tracking_idx])
					tracking_idx += 1

				elif list_x[tracking_idx] == '(':
					tracking_idx += 1
					result.append(change_into_package_helper(list_x))

				elif list_x[tracking_idx] == ')':
					tracking_idx += 1
					return result

			return result

		self.logic_package = change_into_package_helper(list_x)

	def show_package(self):
		return self.logic_package

class Node:
	def __init__(self, data):
		self.data = data
		self.left = None
		self.right = None
		self.p = None

class Tree:
	def __init__(self):
		self.root = None

	def create_logic_tree(self, list_x):
		self.root = Node(list_x)

		def create_logic_tree_helper(node):
			tmp = node.data
			node.data = tmp[1]
			node.left = Node(tmp[0])
			node.right = Node(tmp[2])

			if isinstance(node.left.data, list):
				create_logic_tree_helper(node.left)
			if isinstance(node.right.data, list):
				create_logic_tree_helper(node.right)

		create_logic_tree_helper(self.root)

def inorder_traversal(tree):
	if tree:
		inorder_traversal(tree.left)
		print(tree.data)
		inorder_traversal(tree.right)

def pre_order_traversal(tree):
	if tree:
		print(tree.data)
		pre_order_traversal(tree.left)
		pre_order_traversal(tree.right)

s = split_into_list(s7)
s = remove_then(s)
L = LogicPackage()
L.change_into_package(s)
l = (L.show_package())
print(l)
T = Tree()
T.create_logic_tree(l)
inorder_traversal(T.root)
print()
pre_order_traversal(T.root)
