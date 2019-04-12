""""
A class for keeping track of user information 

"""
class User:

	"""
	User attributes:
		id: Integer, user id
		name: String, first name 
		email: String, email 
		password: String, password (TODO: change after )
		skinInventory: dict, game -> skin mapping 

	"""
	def __init__(self, id, name, email, password, skinInventory):
		self.userID = id
		self.name = name
		self.email = email
		self.password = password
		self.skinInventory = skinInventory