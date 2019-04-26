import js2py
import steampy 

# Example of a test trade 
# during sign up, steam account -> ETH wallet 

# User 1 
# In our app, User 1's credentials are provided on sign up 

# User 2 
# In our app, User 2's credentials are provided on sign up 

# Intermediary 
# We have the intermediary credentials 

# Parties agree on price & item 
# deploy smart contract @params : ETH UID1, ETH UID2, itemid, price
# buyer funds the trade 
# while time < 10m
	# if trade is funded
	# 	execute trade (transfer item from seller to buyer) 
	# 	if success:
	# 		transfer funds from buyer -> seller in smart contract 
	#	else: 
	# 		transfer funds back to the buyer 
	# 		return
	# else:
	# 	pass 
# return 

