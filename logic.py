from collections import OrderedDict

def split_into_list(s):
	"""
	Input: String
	Output: A list of variables and the connectives (in English)

	1.  Remove the punctuations from the sentence such as "if A, then B", but not parentheses.
	2. 	Split the sentence into a list of words composing the sentence.
	3.	Remove the word "if" from the list because the word "then" is sufficient to represent the relationship. 
		Moreover, the word "then" is sandwiched in the middle of the sentence, which makes it easier to create Logic Tree.
	4. 	Returns the list.
	"""
	remove_punc = str.maketrans("", "", ",.!")
	s = s.translate(remove_punc)

	def remove_if(list_x):
		list_x = [x for x in list_x if x != "if"]
		return list_x

	return remove_if(s.split(" "))

def replace_parentheses_with_list(list_x):
	"""
	Input: A list with entries within parentheses
	Output: A list with entries within the parentheses replaced with entries within lists

	1.	Detect the parentheses in the list, e.g., ['(', 'A', 'or', 'B', ')', 'and', 'C']
	2.	Put the entries within the parentheses into another list using recursive call. The main outermost list is called logic_package. 
		During the recusive call, we use result as a temporary list to store the entries within the parentheses.
	3.	At the end, for ['(', 'A', 'or', 'B', ')', 'and', 'C'], it returns the logic_package, [['A', 'or', 'B'], 'and', 'C']
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
	Output: A dictionary of atomic sentences

	1. 	First initialize the Ordered Dictionary atomic_sentences. I use Ordered Dictionary because I want to use dictionary for O(1) access time and for hashing,
		and most importantly, I want to retain the order of atomic sentences. In addition, I can use the set property of dictionary to avoid having 
		duplicated atomic sentences in atomic_sentences. 
	2.	Use the helper function. If the entries are one of the connective keywords "then", "and", "or" and "not".
		If they are, ignore them, Otherwise, put them into the dictionary atomic_sentences.
		If the entry is a list, do a recursive call using the helper function so as to identify if there is any unique atomic sentences within the list.
	3.	Return atomic_sentences.
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

def generate_truth_values_for_atomic_sentences(dict_atomic_sentences):
	"""
	Input: A dictionary which maps all the symbols of atomic sentences to None
	Output: A dictionary which maps all the symbols to their respective lists of truth values in different orders such that
			in a truth table, we can have distinct combinations of truth values in each row.

	1.	Initialize the result with two lists: one contains True and the other contains False.
	2.	Because the truth table will have 2^n rows for n atomic sentences, we can treat the list result as a queue.
		For each atomic sentence, dequeue all the items from the result is dequeued, and for each the item dequeued, which is a list of truth values, 
		duplicate the list into two lists and enqueue one with True and the other with False. Enqueue the lists into a temporary queue, which 
		becomes the result at the end of each loop of atomic sentence.
	3.	When step (2) ends, result stores all the rows of truth values combination in the truth table.
		However, it is better to map the atomic sentences to their columns of truth values because it is easier to print the truth value for a given
		row and column while printing the truth table.
	4. 	Initilize an Ordered Dictionary truth_values_atomic_sentences because I want to map the atomic sentences to their columns of truth values,
		and most importantly, I want to retain the order of atomic sentences.
	5.	Use a for-loop and list comprehension to generate the columns of truth values and map it to the atomic sentences.
	6. 	Return truth_values_atomic_sentences.
	"""
	
	result = [[True], [False]]
	
	def generate_helper(dict_atomic_sentences, idx):
		if idx < len(dict_atomic_sentences):
			tmp = []
			nonlocal result
			while result:
				row = result.pop()
				row_1 = row[:] + [True]
				row_2 = row[:] + [False]
				tmp.append(row_1)
				tmp.append(row_2)
			result = tmp[:]
			generate_helper(dict_atomic_sentences, idx+1)

	generate_helper(dict_atomic_sentences, 1)	# start from the second atomic sentence because the result is initialized as [[True], [False]] instead of [].

	truth_values_atomic_sentences = OrderedDict()
	def assign_to_atomic_sentences(result):
		col = 0
		for s in dict_atomic_sentences:
			truth_values_atomic_sentences[s] = [result[row][col] for row in range(len(result))]
			col += 1
	
	assign_to_atomic_sentences(result)
	return truth_values_atomic_sentences

class Node:
	"""
	Attributes:
	data : String - contains the symbol for atomic sentences (e.g., "A", "B", "C") and ordinary language of connectives("then", "and", "or").
	
	negation : Bool - whether the atomic sentence or the logical statement is negated
	truth_values : Ordered Dictionary - map the node's description, desc, to its column of truth values in the truth table. This takes into account of the negation. 
	
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

	"""
	This is a class for Logic Tree.
	A Logic Tree captures the negation, the connectives and the atomic sentences that are used to form the logical statements.
	For example, 
	Logical statement of "not ( A and B )".
	Logic Tree:

	(~)and  <- root
	 /	 \
	A 	  B

	Logical statement of "if ( A and B ), then C"
	Logic Tree:

		 then 	<- root
		/	 \
	  and 	  C
	 /	 \
	A 	  B
	"""

	def __init__(self):
		"""
		Attributes:
		root : Node - root of the Tree
		truth_tables_output : Ordered Dictionary that maps the premises and conclusion to their columns of truth values in the truth table.
		Ordered Dictionary is used to ensure that O(1) access time, and that the premises are put in order of complexity and that conclusion comes before premises.
		"""
		self.root = None
		self.truth_tables_output = OrderedDict()

	def create_logic_tree(self, list_x):
		"""
		Input: List of entries list_x that compose a statement, e.g., ["not", ["A", "and", "B"]]
		Output: Root of the tree. The Logic Tree is created.

		1.	Assign the list of entries list_x to the root.
		2.	The helper function is created to break down the list and assign each entry to each node.
			At the same time, the helper function establishes the hierachy of parent and child nodes.
		3.	If the node.data which at this stage is a list contains only one entry, it means the node represents an atomic sentence.
			Assign the node.data to the entry.
		4.	If the node.data which at this stage is a list contains two entries, the first entry must be a "not".
			Negate the node.negation, which initially is False, and assign the node.data to the second entry.
			Since the second entry may be a list, e.g. the second entry for this list ["not", ["A", "and", "B"]],
			we need to call the helper function on the node recursively. 
		5.	If step (3) and (4) are not carried out, we know that the node.data which at this stage is a list contains three or more than three entries. 
			We also know that "not" may exist in the list.
			
			The first step is to create a duplicate list but without "not" in within. This duplicate list tmp_list_wo_not will only have three entries,
			and the second entry must be a connective, i.e., either 'then", "or" or "and".
			The first and third entries in tmp_list_wo_not are made into left and right child nodes respectively, and the second entry 
			is made into a parent node as the parent node should connnect two child nodes to represent the relationship between the child nodes.

			The second step is to negate the child nodes. (Parent node is not negated because there is no "not" before the connective).

			The final step is to check if the child nodes are atomic sentences. If they are not, then the node.data will store a list.
			Therefore, we have to recursively call the helper function on the child nodes to break down the list. 
		"""
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
						node.left.negation = not node.left.negation
					elif tmp_list[i+1] == node.right.data:
						node.right.negation = not node.right.negation

			if isinstance(node.left.data, list):	#left child node is not atomic sentence
				create_logic_tree_helper(node.left)
			if isinstance(node.right.data, list):	#right child node is not atomic sentence
				create_logic_tree_helper(node.right)

		create_logic_tree_helper(self.root)
		return self.root

	def assign_truth_values_to_node(self, atomic_truth_values_dict):
		"""
		Input: An Ordered Dictionary atomic_truth_values_dict mapping atomic sentences to their respective columns of truth values.
		Output: Root of the tree. All the nodes in the tree are assigned to their columns of truth values in the truth table.

		1.	If the node's truth_values attribute is None, we have to assign its column of truth values to this truth_values attribute.
		2.	If the node is a leaf, it means the node is an atomic sentence. Therefore, we use the inputted atomic_truth_values_dict to assign
			the node's column of truth values to the node.truth_values attribute.
		3.	If the node is an internal node, it means the node represents the connective. We use the connective, which is stored in node.data, 
			to find the column of truth values for the node depending on whether the connective is a conjunction, disjunction or implication.

			Also, if the node is negated, we first store the columns of truth values that have not been negated into node.truth_values_wo_negation.
			Then, we negate all the truth value in the node.truth_values. The reason to store the truth values that are not negated is that
			in truth table, we may have to print both the logical statements that is not negated and that is negated.
		4. 	Return the root. 
		"""
		def helper(node):
			if not node.truth_values:
				if not node.left and not node.right:	#the node is a leaf
					node.truth_values = atomic_truth_values_dict[node.data]
					if node.negation:
						node.truth_values_wo_negation = node.truth_values[:]
						node.truth_values = [not t_value for t_value in node.truth_values]
				else: #node is an internal node, i.e., it has left and right child nodes
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
		"""
		Modifying method.
		Input: A node (must be root node to generate the truth table)
		Output: None. All the node.desc attributes are filled with descriptions of what the respective node means (in other words, the logical statement).
				Examples of description : ~ ( B -> C ), ( ( C V A ) ^ B ), ~ ~ ~ A

		1.  Base case: the node must be valid, i.e., not None.
		2.	Since the inputted node is from root node, and we need the description about the node's left and right child nodes before we can describe
			the node, recursively call the describe method on the node's left and right child nodes.
		3.	If the node itself is an atomic sentence, the description is the node.data, which is "A", "B", "C", etc.
		4.	If the node itself is not an atomic sentence, then its node.data must contain the connective "then", "and", or "or".
			Transform the connective into its symbol and sandwich it between the descriptions of left and right child nodes to represent the relationship between
			the left and right child nodes, which can be implication, conjunction or disjuntion.
		5.  For both step 3 and step 4,if there the node is negated, stores the description without the symbol ~ in node.desc_wo_negation
			This is because in the truth table, we may need to print out the description, or the logical statement in both not negated and negated from. 
			
			Next, store the negated form in node.desc by adding node.negation_count (which is an odd number) number of "~" in front of the original node.desc.
			
			If the node is not negated but the node.negation_count is more than 0, it means that there is double negation.
			Therefore we adding node.negation_count (which is an even number) number of "~" in front of the original node.desc.	
		"""
		if node:
			self.describe(node.left)
			self.describe(node.right)
			if node.data not in ("then", "and", "or"):	#atomic sentence
				node.desc = node.data
				if node.negation:
					node.desc_wo_negation = node.desc
					node.desc = "~ "*node.negation_count + node.desc
				if node.negation_count and not node.negation:
					node.desc = "~ "*node.negation_count + node.desc
			else:	#not an atomic sentence
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

	def ordered_dict_is_empty(self):
		"""
		Check if truth_tables_output is empty.
		The implication is that if truth_tables_output is empty, then the root is a leaf. 
		"""
		return self.truth_tables_output == OrderedDict()

	def truth_tables_complex_sent(self, node):
		"""
		Modifying method.
		Input: A node (must be root node to generate the truth table)
		Output: None. The ordered dictionary truth_tables_output of the tree is modified to map the all the nodes which will appear 
				in the truth table's header row to their respective columns of truth values.

		1.	If the node is not a leaf node, recursively call the function on its left and right child nodes.
			If the logical statement (which is the node) is being negated, map the logical statement which is not negated to the truth values which are not negated.
			Regardless of whether or not the node is negated, map the logical statement to its column of truth values.
		2.	If the node is a leaf node, check if its negation count is more than 0. If it is not, it means it is a simple atomic sentences, which already 
			exists in truth_values_atomic_sentences. Therefore, we can ig nore it.
			If the negation count is more than 0, we map the logical statement to its column of truth values.
		"""
		if node and node.left and node.right:	#not a leaf node
			self.truth_tables_complex_sent(node.left)
			self.truth_tables_complex_sent(node.right)
			if node.negation:
				self.truth_tables_output[node.desc_wo_negation] = node.truth_values_wo_negation
			self.truth_tables_output[node.desc] = node.truth_values
		elif node.negation_count: # includes ~ "A" (i.e., negation of atomic sentences) or ~ ~ "A" (i.e., double, triple...negation of the atomic sentences)
			self.truth_tables_output[node.desc] = node.truth_values

def print_truth_table(truth_values_atomic_sentences, logic_trees, logic_trees_complex):
	"""
	Input: 1. A dictionary truth_values_atomic_sentences which maps each symbol of atomic sentence to their respective lists of truth values.
		   2. A list of logic trees
		   3. A dictionary logic_trees_complex which maps all the logical statements possibly formed from the logic_trees (excluding atomic sentences)
			  to their respective lists of truth values.	

	Output: Return None. Print the truth table.

	1.	Generate the first row, the header row, which are all the symbols for the atomic sentences and statements
	2.  Print the first row from step (1).
	3.  Print out the truth values across the row by using nested for-loops.
	"""
	top_row = [t for t in truth_values_atomic_sentences.keys()] + ['|']	# symbols for atomic sentences
	
	for T in logic_trees:
		for v in T.truth_tables_output:	# this loop appends all the descriptions of internal nodes in the logical tree into top_row
			if v not in top_row:
				top_row.append(v)
		if T.ordered_dict_is_empty():	# this is for the case where the root is the leaf.
			top_row.append(T.root.data)
	
	for t in top_row:
		print('%-15s' % t, end = "")

	print()
	for row in range(2**len(truth_values_atomic_sentences)):	# 2**len(atomic_sentences) is equivalent to the number of rows
		# for each column in the header row
		for item in top_row:
			# if the column is a symbol for atomic sentences
			# print out the truth value for the symbol at the particular row
			if item in truth_values_atomic_sentences:
				print('%-15s' % truth_values_atomic_sentences[item][row], end = "")
			
			elif item  == "|":
				print('%-15s' % "", end = "")
			
			# if the column is a logical statement
			# print out the truth value for the logical statement at the particular row
			else:
				for t in logic_trees_complex:
					if item in t:
						print('%-15s' % t[item][row], end = "")
						break
		print()

def check_validity(list_of_trees):
	"""
	Input: A list of the logic trees formed from the list of given statements.
	Output: String - whether the argument is valid or invalid.

	1. 	Since we are only interested in the combination of truth values of the premises and conclusion when we check validity,
		and the truth values of premises and conclusions are stored in the roots of the logical trees, we first append their 
		truth values into the list list_validity.
	2.  Use nested for loops to compare if there is any case when all the premises are True and the conclusion is False.
		If so, we can break out of the for loops and assign "Not Valid" to the variable is_valid.
		
		Otherwise, if there is no case when all the premises are True and the conclusion is False, and there is a case
		when all the premises and conclusion are True, then assign "Is Valid" to the variable is_valid.
		
		Otherwise, if there is no cases when all the premises and conclusion are True, the variable is_valid remains its
		initial value: (all the statements are) "Not Logically Connected"
	3.  Return is_valid
	"""
	list_validity = []
	for T in list_of_trees:
		list_validity.append(T.root.truth_values)

	is_valid = "Not Logically Connected"
	for col in range(len(list_validity[0])):
		premises_all_valid = True
		for row in range(len(list_validity)-1):
			if not list_validity[row][col]:
				premises_all_valid = False
				break
		if not premises_all_valid:
			continue

		if premises_all_valid and list_validity[-1][col]:
			is_valid = "Is Valid"
		elif premises_all_valid and not list_validity[-1][col]:
			is_valid = "Not Valid"
			break
			
	return is_valid


###########################################################################################################################################

# Input Format : List. The last entry is the conclusion. The other entries are the premises
# there is no outermost parentheses
# When applies parentheses, ensure that there are spaces after the left parenthesis and before right parenthesis
# When apply negation, use parentheses.

sample1 = ["if A, then B", "A", "B"]
sample2 = ["if A, then B", "not ( B )", "not ( A )"]
sample3 = ["if A, then B", "if B, then C", "if A, then C"]
sample3_A = ["if A, then B", "if B, then C", "if C, then A"]
sample4 = ["A or B", "not ( A )", "B"]
sample5 = ["not ( not ( not ( not ( A ) ) ) )", "A"]
sample6 = ["A", "A or B"]
sample7 = ["A and B", "A"]

sample8 = ["( if p, then q ) and ( if r, then s )", "p or r", "q or s"] #is Valid

def answer_truth_table_validity(list_of_statements):
	"""
	Input: List of Statements (Argument). 
	Output: Return none. Print truth table and the validity of the arguments.

	1.  Break all the statements into lists of atomic sentences and connectives.
	2. 	Identify all the atomic sentences.
	3.  Generate lists of truth values for the atomic sentences and map different atomic sentences to columns of truth values created such that 
		when the columns of truth values of atomic sentences are displayed in the truth table, each row has distinct combination of truth values.
	4.	For the lists taken from step (1), create a Logic Tree for each list. Find out the truth values for each node as well as their descriptions.
	    Map all the internal nodes to their respective truth values using truth_tables_complex_sent method.
	5. 	Append all the logic trees into the list logic_trees and append the mapping from step (4) to the list logic_trees_complex.
	6.  Print the truth table using the function print_truth_table.
	7.  Check the validity using the function check_validty, and print it.
	"""
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
		logic_trees.append(T)
		logic_trees_complex.append(T.truth_tables_output)

	print_truth_table(truth_values_atomic_sentences, logic_trees, logic_trees_complex)
	print("Premises: ", list_of_statements[:-1], "\nConclusion: ", list_of_statements[-1], "\n", check_validity(logic_trees))

answer_truth_table_validity(sample3)
print()
answer_truth_table_validity(sample3_A)