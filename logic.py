from collections import OrderedDict

def split_into_list(s):
	"""
	Input: String
	Output: A list of variables and the connectives (in English)

	This function first removes the punctuations from the sentence such as "if A, then B", but not parentheses.
	Next, it splits the sentence into a list of words composing the sentence.
	Then, it removes the word "if" from the list because the word "then" is sufficient to represent the relationship. 
		Moreover, the word "then" is in the middle of the sentence, which makes it easier to create Logic Tree.
	Finally, it returns the list.
	"""
	remove_punc = str.maketrans("", "", ",.!")
	s = s.translate(remove_punc)

	def remove_if(list_x):
		list_x = [x for x in list_x if x != "if"]
		return list_x

	return remove_if(s.split(" "))

def replace_parentheses_with_list(list_x):
	"""
	Input: A list
	Output: A list

	This function detects the parentheses in the list, e.g., ['(', 'A', 'or', 'B', ')', 'and', 'C']
	and putting the entries within the parentheses into another list using recursive call.
	At the end, it returns [['A', 'or', 'B'], 'and', 'C']
	"""
	tracking_idx = 0
	logic_package = []

	def replace_parentheses_with_list_helper(list_x):
		result = []
		nonlocal tracking_idx

		#when doesn't encounter parentheses, add it to the result list.
		#when encounters left parenthesis, recursively call the helper function to put the entries in the parentheses into a new result list.
		#when encounters right parenthesis, return the result list as all the entries in the parentheses have been put into the result list.

		while tracking_idx < len(list_x):
			if list_x[tracking_idx] not in ("(", ")"):
				result.append(list_x[tracking_idx])
				tracking_idx += 1

			elif list_x[tracking_idx] == '(':
				tracking_idx += 1
				result.append(replace_parentheses_with_list_helper(list_x))

			elif list_x[tracking_idx] == ')':
				tracking_idx += 1
				return result

		return result

	logic_package = replace_parentheses_with_list_helper(list_x)
	return logic_package

def identify_atomic_sentences(logical_sentences):
	"""
	Input: A list whose entries are the atomic sentences and the connectives in ordinary language.
	Output: A list of atomic sentences

	The function checks if the entries are one of the connective keywords "then", "and", "or" and "not".
	If they are, ignore them, Otherwise, put them into the list of atomic sentences.
	"""

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
	"""
	Attributes:
	data : String - contains the symbol for atomic sentences (e.g., "A", "B", "C") and ordinary language of connectives("then", "and", "or").
	
	negation : Bool - whether the atomic sentence or the logical statement within the parentheses is negated 
	truth_values : 
	truth_values_wo_negation : 
	
	desc : String - contains the symbol for atomic sentences (e.g., "A", "B", "C") or describe the relationship between the two chldren nodes(e.g., "A -> B", "A ^ B", "A V B") INCLUDING the negation symbol.
	desc_wo_negation: String - contains the symbol for atomic sentences (e.g., "A", "B", "C") or describe the relationship between the two chldren nodes(e.g., "A -> B", "A ^ B", "A V B") EXCLUDING the negation symbol.
	
	p : Node - parent node
	left : Node - left child's node
	right : Node - right child's node
	"""

	def __init__(self, data):
		self.data = data
		self.negation = False
		self.negation_count = 0
		self.truth_values = None
		self.truth_values_wo_negation = None
		self.desc = None
		self.desc_wo_negation = None
		self.left = None
		self.right = None
		self.p = None

class Tree:

	def __init__(self):
		"""
		Attributes:
		root : Node - root of the Tree
		truth_tables_output : Ordered Dictionary - output for the premises and conclusion

		Ordered Dictionary is used to ensure that O(1) access time, and that the premises are put in order of complexity and that conclusion comes before premises.
		"""
		self.root = None
		self.truth_tables_output = OrderedDict()

	def create_logic_tree(self, list_x):

		self.root = Node(list_x)

		#build the tree using a helper function
		def create_logic_tree_helper(node):
			
			if len(node.data) == 1:
				node.data = node.data[0]
				return 

			if len(node.data) == 2:
				node.data = node.data[1]
				node.negation = not node.negation
				node.negation_count += 1
				create_logic_tree_helper(node)
				return

			
			tmp_list = node.data[:]
			tmp_list_wo_not = [elem for elem in node.data if elem != "not"]

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
					node.desc = "~ "*node.negation_count + node.desc
				if node.negation_count and not node.negation:
					node.desc = "~ "*node.negation_count + node.desc
			else:
				if node.data == "then":
					node.desc = "( " + node.left.desc + " -> " + node.right.desc + " )"
					if node.negation:
						node.desc_wo_negation = node.desc
						node.desc = "~ "*node.negation_count + node.desc
					if node.negation_count and not node.negation:
						node.desc = "~ "*node.negation_count + node.desc
				elif node.data == "and":
					node.desc = "( " + node.left.desc + " ^ " + node.right.desc + " )"
					if node.negation:
						node.desc_wo_negation = node.desc
						node.desc = "~ "*node.negation_count + node.desc
					if node.negation_count and not node.negation:
						node.desc = "~ "*node.negation_count + node.desc
				elif node.data == "or":
					node.desc = "( " + node.left.desc + " V " + node.right.desc + " )"
					if node.negation:
						node.desc_wo_negation = node.desc
						node.desc = "~ "*node.negation_count + node.desc
					if node.negation_count and not node.negation:
						node.desc = "~ "*node.negation_count + node.desc

	#check if the truth_tables_output is empty.
	def ordered_dict_is_empty(self):
		return self.truth_tables_output == OrderedDict()


	def truth_tables_complex_sent(self, node):
		if node and node.left and node.right:
			self.truth_tables_complex_sent(node.left)
			self.truth_tables_complex_sent(node.right)
			if node.negation:
				self.truth_tables_output[node.desc_wo_negation] = node.truth_values_wo_negation
			self.truth_tables_output[node.desc] = node.truth_values
		elif node.negation_count: # -> not "A" (i.e., negation of atomic sentences)
			self.truth_tables_output[node.desc] = node.truth_values

def print_truth_table(truth_values_atomic_sentences, logic_trees, atomic_sentences, logic_trees_complex):
	top_row = [t for t in truth_values_atomic_sentences.keys()] + ['|']
	for T in logic_trees:
		#print(T.root.data)
		for v in T.truth_tables_output:
			if v not in top_row:
				top_row.append(v)
		if T.ordered_dict_is_empty():
			top_row.append(T.root.data)
	
	for t in top_row:
		print('%-15s' % t, end = "")

	print()
	for i in range(2**len(atomic_sentences)):
		for item in top_row:
			if item in truth_values_atomic_sentences:
				print('%-15s' % truth_values_atomic_sentences[item][i], end = "")
			elif item  == "|":
				print('%-15s' % "", end = "")
			else:
				for t in logic_trees_complex:
					if item in t:
						print('%-15s' % t[item][i], end = "")
						break
		print()

def check_validity(list_of_trees):
	list_validity = []
	for T in list_of_trees:
		list_validity.append(T.root.truth_values)

	is_valid = "not logically connected"
	for col in range(len(list_validity[0])):
		premises_all_valid = True
		for row in range(len(list_validity)-1):
			if not list_validity[row][col]:
				premises_all_valid = False
				break
		if not premises_all_valid:
			continue

		if premises_all_valid and list_validity[-1][col]:
			is_valid = "is Valid"
		elif premises_all_valid and not list_validity[-1][col]:
			is_valid = "Not Valid"
			break
			
	return is_valid

sample1 = ["if A then B", "if B then C", "not ( A )", "not ( C )"]
sample2 = ["not ( not ( not ( A or B ) ) )", "A"]
sample3 = ["not ( not ( A ) and not ( B ) )", "A or B"]

def answer_truth_table_validity(list_of_statements):
	logical_sentences = [replace_parentheses_with_list(split_into_list(s)) for s in list_of_statements]
	atomic_sentences = identify_atomic_sentences(logical_sentences)
	truth_values_atomic_sentences = generate_truth_values_for_atomic_sentences(atomic_sentences)
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

	print_truth_table(truth_values_atomic_sentences, logic_trees, atomic_sentences, logic_trees_complex)
	print(list_of_statements, check_validity(logic_trees))

answer_truth_table_validity(sample2)



