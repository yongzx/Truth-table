from collections import OrderedDict

list1 = ["if A then B", "if B then C", "A", "not C"]

def split_into_list(s):
	remove_punc = str.maketrans("", "", ",.!")
	s = s.translate(remove_punc)

	def remove_if(list_x):
		list_x = [x for x in list_x if x != "if"]
		return list_x

	return remove_if(s.split(" "))

def change_into_package(list_x):
	tracking_idx = 0
	logic_package = []
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

	logic_package = change_into_package_helper(list_x)
	return logic_package

def identify_atomic_sentences(logical_sentences):
	atomic_sentences = OrderedDict()

	def helper(elem):
		if not isinstance(elem, list) :
			if elem not in ("then", "and", "or", "not"):
				atomic_sentences[elem] = None
		else:
			for e in elem:
				helper(e)

	for s in logical_sentences:
		helper(s)

	return atomic_sentences

def generate_truth_values_for_atomic_sentences(list_x):
	
	result = [[True], [False]]
	
	def generate_helper(list_x, idx):
		if idx < len(list_x):
			tmp = []
			nonlocal result
			while result:
				row = result.pop()
				row_1 = row[:] + [True]
				row_2 = row[:] + [False]
				tmp.append(row_1)
				tmp.append(row_2)
			result = tmp[:]
			generate_helper(list_x, idx+1)

	generate_helper(list_x, 1)

	truth_values_atomic_sentences = OrderedDict()
	def assign_to_atomic_sentences(result):
		idx = 0
		for s in list_x:
			truth_values_atomic_sentences[s] = [result[i][idx] for i in range(len(result))]
			idx += 1
	
	assign_to_atomic_sentences(result)
	return truth_values_atomic_sentences

class Node:
	def __init__(self, data):
		self.data = data
		self.desc = None
		self.negation = False
		self.desc_wo_negation = None
		self.truth_values_wo_negation = None
		self.left = None
		self.right = None
		self.p = None
		self.truth_values = None

class Tree:
	def __init__(self):
		self.root = None
		self.truth_tables_output = OrderedDict()

	def create_logic_tree(self, list_x):

		if len(list_x) == 1:
			self.root = Node(list_x[0])
			return self.root

		self.root = Node(list_x)
		if list_x[0] == "not" and isinstance(list_x[1], list):
			self.root.negation = True
			self.root.data = self.root.data[1]

		def create_logic_tree_helper(node):
			tmp_list = node.data[:]
			tmp_list_wo_not = [elem for elem in node.data if elem != "not"]
			if len(tmp_list_wo_not) == 1:
				node.negation = True
				node.data = tmp_list_wo_not[0]
				return
			node.data = tmp_list_wo_not[1]
			node.left = Node(tmp_list_wo_not[0])
			node.right = Node(tmp_list_wo_not[2])
			node.left.p, node.right.p = node, node

			for i in range(len(tmp_list)):
				if tmp_list[i] == "not":
					if tmp_list[i+1] == node.left.data:
						node.left.negation = True
					elif tmp_list[i+1] == node.right.data:
						node.right.negation = True

			if isinstance(node.left.data, list):
				create_logic_tree_helper(node.left)
			if isinstance(node.right.data, list):
				create_logic_tree_helper(node.right)

		create_logic_tree_helper(self.root)
		return self.root

	def assign_truth_values_to_node(self, atomic_truth_values_dict):
		
		def helper(node):
			if not node.truth_values:
				if not node.left and not node.right:
					node.truth_values = atomic_truth_values_dict[node.data]
					if node.negation:
						node.truth_values_wo_negation = node.truth_values[:]
						node.truth_values = [not t_value for t_value in node.truth_values]
				else:
					node.truth_values = []
					helper(node.left)
					helper(node.right)
					if node.data == "and":
						for i in range(len(node.left.truth_values)):
							node.truth_values.append(node.left.truth_values[i] and node.right.truth_values[i])
						if node.negation:
							node.truth_values_wo_negation = node.truth_values[:]
							node.truth_values = [not t_value for t_value in node.truth_values]	
					if node.data == "or":
						for i in range(len(node.left.truth_values)):
							node.truth_values.append(node.left.truth_values[i] or node.right.truth_values[i])
						if node.negation:
							node.truth_values_wo_negation = node.truth_values[:]
							node.truth_values = [not t_value for t_value in node.truth_values]	
					if node.data == "then":
						for i in range(len(node.left.truth_values)):
							node.truth_values.append((not node.left.truth_values[i]) or node.right.truth_values[i])
						if node.negation:
							node.truth_values_wo_negation = node.truth_values[:]
							node.truth_values = [not t_value for t_value in node.truth_values]	

		helper(self.root)	
		return self.root

	def describe(self, node):
		if node:
			self.describe(node.left)
			self.describe(node.right)
			if node.data not in ("then", "and", "or"):
				node.desc = node.data
				if node.negation:
					node.desc_wo_negation = node.desc
					node.desc = "~ " + node.desc
			else:
				if node.data == "then":
					node.desc = "( " + node.left.desc + " -> " + node.right.desc + " )"
					if node.negation:
						node.desc_wo_negation = node.desc
						node.desc = "~ " + node.desc
				elif node.data == "and":
					node.desc = "( " + node.left.desc + " ^ " + node.right.desc + " )"
					if node.negation:
						node.desc_wo_negation = node.desc
						node.desc = "~ " + node.desc
				elif node.data == "or":
					node.desc = "( " + node.left.desc + " V " + node.right.desc + " )"
					if node.negation:
						node.desc_wo_negation = node.desc
						node.desc = "~ " + node.desc

	def ordered_dict_is_empty(self):
		return self.truth_tables_output == OrderedDict()

	def truth_tables_complex_sent(self, node):
		if node and node.left and node.right:
			self.truth_tables_complex_sent(node.left)
			self.truth_tables_complex_sent(node.right)
			self.truth_tables_output[node.desc] = node.truth_values
			if node.negation:
				self.truth_tables_output[node.desc_wo_negation] = node.truth_values_wo_negation
		elif node.negation: # -> not "A" (i.e., negation of atomic sentences)
			self.truth_tables_output[node.desc] = node.truth_values

logical_sentences = [change_into_package(split_into_list(s)) for s in list1]
#print(logical_sentences)
atomic_sentences = identify_atomic_sentences(logical_sentences)
#print(atomic_sentences)
truth_values_atomic_sentences = generate_truth_values_for_atomic_sentences(atomic_sentences)
#print(truth_values_atomic_sentences)
logic_trees = []
logic_trees_complex = []
for s in logical_sentences:
	T = Tree()
	T.create_logic_tree(s)
	T.assign_truth_values_to_node(truth_values_atomic_sentences)
	T.describe(T.root)
	T.truth_tables_complex_sent(T.root)
	logic_trees_complex.append(T.truth_tables_output)
	logic_trees.append(T)
#print(logic_trees)
#print(logic_trees_complex)

def print_truth_table_validity():
	top_row = [t for t in truth_values_atomic_sentences.keys()] + ['|']
	for T in logic_trees:
		print(T.root.data)
		for v in T.truth_tables_output:
			if v not in top_row:
				top_row.append(v)
		if T.ordered_dict_is_empty():
			top_row.append(T.root.data)
	
	for t in top_row:
		print('%-15s' % t, end = "")

	print()
	valid = True
	all_premise_True_once = False
	for i in range(2**len(atomic_sentences)):
		activate_checking, all_premise_True = False, True
		for item in top_row[:len(top_row)-1]:
			if item in truth_values_atomic_sentences:
				print('%-15s' % truth_values_atomic_sentences[item][i], end = "")
				if activate_checking and not truth_values_atomic_sentences[item][i]:
					all_premise_True = False
			elif item  == "|":
				print('%-15s' % "", end = "")
				activate_checking = True
			else:
				for t in logic_trees_complex:
					if item in t:
						print('%-15s' % t[item][i], end = "")
						if activate_checking and not t[item][i]:
							all_premise_True = False
						break
		conclusion = top_row[-1]
		conclusion_truth_value = None
		if conclusion in truth_values_atomic_sentences:
			print('%-15s' %truth_values_atomic_sentences[conclusion][i], end = " ")
			conclusion_truth_value = truth_values_atomic_sentences[conclusion][i]
		else:
			for t in logic_trees_complex:
				if conclusion in t:
					print('%-15s' %t[conclusion][i], end = " ")
					conclusion_truth_value = t[conclusion][i]
					break
		
		if all_premise_True:
			all_premise_True_once = True

		if all_premise_True and not conclusion_truth_value:
			valid = False
		print()
		

	print("Is Valid" if valid and all_premise_True_once else "Not Valid")

print_truth_table_validity()
