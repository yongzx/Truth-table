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

s = split_into_list(s7)
L = LogicPackage()
L.change_into_package(s)
print(L.show_package())
