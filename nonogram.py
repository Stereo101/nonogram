import copy
	
#Generates all possible fillings of a given sequence (ex 2 1 1 1) into a # of spots
def picRowFill(sequence,spots):
	minReqSpace = sum(sequence) + len(sequence) - 1
	if(not sequence):
		yield [0]*spots
	#Base case, fill exactly
	elif(spots == minReqSpace):
		a = []
		for s in sequence:
			a += [1]*s
			a += [0]
		del a[-1]
		yield a
	#put first thing down, recurse the rest
	else:
		spareSpace = spots - minReqSpace
		e = sequence[0]
		for i in range(0,spareSpace+1):
			for r in picRowFill(sequence[1:],spots-i-e-1):
				if(r):
					yield [0]*i + [1]*e + [0] + r
				else:
					yield [0]*i + [1]*e + [0]*(spots-e-i)

#Takes a list of possible fillings, and squashes matches into a single representation
#
#1 for all fillings matched with 1
#0 for all fillings matched with 0
#? for all fillings didn't match
def squashResults(r):
	f_col_mismatch = lambda col: any(r[x][col] != r[x+1][col] for x in range(len(r)-1))
	return ["?" if f_col_mismatch(i) else r[0][i] for i in range(len(r[0]))]
	
#Test if a certain filling is matches a template
#ex. 1?? matches 100 and 110 but not 011
def testResultCompat(WIP,A):
	return all(WIP[i] == "?" or WIP[i] == A[i] for i in range(len(WIP)))

#Rejects all fillings which do not matches the template.
#	by rejecting some fillings, squashing becomes more effective
def filterResults(WIP,results):
	return [r for r in results if testResultCompat(WIP,r)]
	

class Grid:
	def __init__(self,height,width,rowInfo=None,colInfo=None):
		self.height = height
		self.width = width
		self.colPerms = []
		self.rowPerms = []
		self.branchDepth = 0
		permutationCounter = 0
		
		#Generate all possible col/row perms according to spec at start for later filtering
		if(rowInfo is not None and colInfo is not None):
			for i in range(width):
				self.colPerms.append(list(picRowFill(colInfo[i],height)))
				permutationCounter += len(self.colPerms[i][-1])
			
			for i in range(height):
				self.rowPerms.append(list(picRowFill(rowInfo[i],width)))
				permutationCounter += len(self.rowPerms[i][-1])

		self.g = []
		self.reformedCol = [True]*width
		self.reformedRow = [True]*height
		for i in range(height):
			self.g.append(["?"]*width)
	
	def getRow(self,i):
		return self.g[i]
		
	def getCol(self,k):
		c = []
		for i in range(self.height):
			c.append(self.g[i][k])
		return c
		
	def setRow(self,i,A):
		updated = False
		for k in range(len(A)):
			if(self.g[i][k] != A[k]):
				updated = True
				self.g[i][k] = A[k]
				self.reformedCol[k] = True
		self.reformedRow[i] = False
		return updated
		
	def setCol(self,i,A):
		updated = False
		for k in range(len(A)):
			if(self.g[k][i] != A[k]):
				updated = True
				self.g[k][i] = A[k]
				self.reformedRow[k] = True
		self.reformedCol[i] = False
		return updated
	
	def show(self):
		showDict = {0:".",1:"x","?":" "}
		for i in range(len(self.g)):
			for k in range(len(self.g[i])):
				c = self.g[i][k]
				print(showDict[c],end=" ")
			print()
		print("_"*(self.width*2+1))
			
	def solve(self,silent=False):
		while True:
			#Filter, Squash, Update across rows/cols until solved
			updated = False
			for i in range(self.width):
				if(not self.reformedCol[i]):
					continue
				col = self.getCol(i)
				self.colPerms[i] = filterResults(col,self.colPerms[i])
				if(not self.colPerms[i]):
					return False
				squash = squashResults(self.colPerms[i])
				updated = updated or self.setCol(i,squash)
				
			for i in range(self.height):
				if(not self.reformedRow[i]):
					continue
				row = self.getRow(i)
				self.rowPerms[i] = filterResults(row,self.rowPerms[i])
				if(not self.rowPerms[i]):
					return False
				squash = squashResults(self.rowPerms[i])
				updated = updated or self.setRow(i,squash)
			
			if(self.isSolved()):
				self.show()
				print("Solved...")
				input()
				return True
					
			#If we made an update to the grid,
			#	try to make another before we branch
			if updated and not silent:
				print("\n")
				self.show()
			else:
				#Failed to update, branch
				branchCount, branchType, branchIndex = self.findMinBranch()
				if not silent: print("BRANCHING",branchCount,branchType,branchIndex)
				for i in range(branchCount):
					c = self.copy()
					c.branchDepth += 1
					if(branchType == "row"):
						c.setRow(branchIndex,c.rowPerms[branchIndex][i])
						c.rowPerms[branchIndex] = [c.rowPerms[branchIndex][i]]
						
					else:
						c.setCol(branchIndex,c.colPerms[branchIndex][i])
						c.colPerms[branchIndex] = [c.colPerms[branchIndex][i]]
						
					if(c.solve(silent=silent)):
						return True
				return False
	
	def copy(self):
		return copy.deepcopy(self)

	def findMinBranch(self):
		minBranch = float("INF")
		minType = None
		minIndex = 0
		for i in range(len(self.colPerms)):
			L = len(self.colPerms[i])
			if L > 1 and L < minBranch:
				minBranch = L
				minIndex = i
				minType = "col"
				
		for i in range(len(self.rowPerms)):
			L = len(self.rowPerms[i])
			if L > 1 and L < minBranch:
				minBranch = L
				minIndex = i
				minType = "row"
		return minBranch,minType,minIndex
			
	def isSolved(self):
		for i in range(self.height):
			for k in range(self.width):
				if(self.g[i][k] == "?"):
					return False
		return True
	
def parseInput(inp):
	rowInfo,colInfo = inp.split("/")
	
	rows = rowInfo.split(",")
	cols = colInfo.split(",")
	
	print("ROWS",len(rows),"COLS",len(cols))
	
	for i in range(len(rows)):
		rows[i] = [int(x) for x in rows[i].split()]
	
	for i in range(len(cols)):
		cols[i] = [int(x) for x in cols[i].split()]
		
	grid = Grid(len(rows),len(cols),rows,cols)
	return grid
	
	
def main():
	puzz = "7,2 3,2 3,2 3,5 3,2 2 2 3,2 2 1 3 3,1 1 2 1 5,1 2 1 2 2 1,3 1 1 2 1,2 1 3 1,2 1 2 1 1,6 1 1,3 2 1,1 3 1/1 2 2,2 2 4,3 2 1 1 1,1 3 1 1 1,1 7 1,1 2 1 1 2,2 1 1 2 4,1 1 1 2,2 2 1 3,2 1 1 2 1,3 2 2 1,3 3 2,5 3,3,9"
	
	puzz2 = "3 1,3 2 1,1 2 2 1,1 2 3,1 4 4,1 2 1 1 2,2 1 1 2,3 1 3 2,2 1 1 2,2 1 1 2 1,1 2 1 2 3,1 1 1 5 1 1,4 1 2 1,1 1 3 3 1,1 3 3 1/1 1 3,5 1 1,6 3,2 2 1 1,2 1 4 2 2,6 1 2,1 1 1 4,1 1,1 3 1,2 1 4,1 4 1 6,1 2 3 2,5 2 1,7 1,2 3 1"
	
	puzz3 = "4 2 2,1 2 1 2,4 4 1,2 1 2 2,5 2 2,1 2 2 1,5 3,1 2 3,8 1,3 1 5,7 4,3 7,2 2 4,1 2 1 1,3 1 1/4 4,1 3 3 1,1 1 2 2 2,1 1 1 1 2 2,1 2 7,2 3 4,1 2 2 1 3,5 3 4,1 2 3 2 1,2 2 1 4,5 6 1,8,1 2,2,1"
	
	puzz4 = "4,3 2,3 6,2 7,1 1 1 1 2,2 1 1 1 1,1 2 2 1 1,1 4 3,2 4 1,2 3 3,2 7,1 4,4 3,6 2,1 1 3 2/2 1,3 3,3 1 1,2 1 1 1,1 1 1 2,2 2 1 1 2,1 1 1 1 2,4 2 1 3,1 7 1 2,1 2 1 1 1,5 1 2,3 4 2,3 1 4,4 6,2 3"
	
	puzz5 = "4,3 2,1 2,2 6,1 4 2 2,3 2 1 2,2 3 2 1,1 2 2 1,1 1 2 1 3,3 2 1 2 1,3 1 2 2 1,3 2 1 2 2,3 2 1 2 2,3 1 2 1,3 2 1 2 1/2 2 7,1 1 2 6,1 1 10,1 1,1 1 9,1 1 4 2 1,1 1 1 1 1,1 1 1 8,1 1 1 1,3 1 2,3 1 4 1,1 1 1 1 1,2 1 1,2 5,4 3"
	
	pepe1 = "8 4,2 4 3,2 2 2,2 1 3,1 5 4 2,1 3 6 1,2 4 2 4 2,1 1 2 1 2 2,1 2 1 2 8,18,2 1 2,1 3 2,2 4,4 9,1 10 2,4 3,1 4 10 2,3 4 2,2 2,2 4,13 1,2,1 4,3 6,12/3 2,2 1,2 3 2,2 1 3 1 1,1 2 2 2 1 2 1,1 1 1 2 2 2 1,1 6 2 1 2 1,1 1 1 2 1 1 1 1,1 1 1 1 1 2 1 1,1 1 4 1 1 1 1,2 2 3 1 1 1 1,2 1 2 1 2 1 1,3 5 1 1 1 2,2 5 1 1 1 2,1 1 1 1 1 1 1,1 2 3 2 1 1 1,2 1 4 1 1 1 1 1,1 1 1 2 1 1 1 1 2,4 1 2 1 1 2 1,2 4 1 1 1 1,2 4 2 2 1 2,3 6 1 4,3 8,2 3 2"
	
	wtf1 = "1 2 1 1 1 1 1 1,2 1 1 1 1 1 1 2,1,2 1 1 2 1 2 1,1 1 1 2 1 1 1,1,18,1 1,1 2 1 2 1 1 2,1 1 1 2 1 1 1,1,2 1 1 2 1 2 1,1 1 1 2 1 1 1,1,18,1 1,1 2 1 2 1 1 2,1 1 1 2 1 1 1/3 2 3 2 1,1 1 2 1 1 2 1,1 1 1 1 1 1 1,1 1 1 1 1 1 1,1 1 1 1 1 1 1,1 1 1 1 1 1 1,1 1 1 1 1 1 1,1 1 1 1 1 1 1,1 1 1 1 1 1 1,1 1 1 1 1 1 1,1 1 1 1 1 1 1,1 1 1 1 1 1 1,1 1 1 1 1 1 1,1 1 1 1 1 1 1,1 1 1 1 1 1 1,1 1 1 1 1 1 1,1 1 1 1 1 1 1,2 1 3 1 3"
	
	hard1 = "1 1,2,1 1,1 2,1 1/2,1 1,3,1 2,1"
	hard2 = "4,4,1,1 1,1/1,2 1,2 1,2 1,1 1"
	
	grid = parseInput(pepe1)
	grid.solve()
	
main()