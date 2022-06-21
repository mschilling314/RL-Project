import common


DIRS = [[[1, 0], [0, -1], [0, 1]],
		[[0, 1], [-1, 0], [1, 0]],
		[[-1, 0], [0, -1], [0, 1]],
		[[0, -1], [-1, 0], [1, 0]]]


ACTIONS= list(range(1, 9))


THRESH = 0.001


class cs:
	sizzle = [6, 6]
	battery_drop_cost = 1
	delivery_fee = 0
	dronerepair_cost = 0


def find_start(board):
	for y in range(cs.sizzle[0]):
		for x in range(cs.sizzle[1]):
			if board[y][x] == common.constants.PIZZA:
				return y, x


def bounds_check(x, y):
	res = True
	if x < 0 or x >= cs.sizzle[1]:
		res = False
	if y < 0 or y >= cs.sizzle[0]:
		res = False
	return res


# return [list of ([y, x], prob)]
def next_states(x, y, a):
	if a == common.constants.EXIT:
		return [[[y,x], 1]]
	res = []
	ind = a % 4
	for i in range(3):
		yn = y + DIRS[ind][i][1]
		xn = x + DIRS[ind][i][0]
		if not bounds_check(xn, yn):
			xn = x
			yn = y
		if i == 0:
			if a > 4:
				res.append([[yn, xn], 0.8])
			else:
				res.append([[yn, xn], 0.7])
		else:
			if a > 4:
				res.append([[yn, xn], 0.1])
			else:
				res.append([[yn, xn], 0.15])
	return res


def get_reward(values, x, y, a):
	reward = 0
	if a in {common.constants.SON, common.constants.NON, common.constants.WON, common.constants.EON}:
		livcost = 2*cs.battery_drop_cost
	else:
		livcost = cs.battery_drop_cost
	ns = next_states(x, y, a)
	for s in ns:
		xo = s[0][1]
		yo = s[0][0]
		p = s[1]
		reward += p * (-livcost + cs.gam * values[yo][xo])
	return reward


def print_2d_array(arr):
	print()
	for a in arr:
		print(a)
	print()
	return


def tie_breaker(curr, new):
	if curr > 4 and new < 5:
		res = new
	elif 0 < new and new < curr:
		res = new
	elif curr == 0:
		res = new
	else:
		res = curr
	return res


def drone_flight_planner (board, policies, values, delivery_fee, battery_drop_cost, dronerepair_cost, discount):
	# PUT YOUR CODE HERE
	# access the map using "board[y][x]"
	# access the policies using "policies[y][x]"
	# access the values using "values[y][x]"
	# y between 0 and 5
	# x between 0 and 5
	# function must return the value of the cell corresponding to the starting position of the drone
	# 
	cs.sizzle[0] = len(board)
	cs.sizzle[1] = len(board[0])
	cs.battery_drop_cost = battery_drop_cost
	cs .dronerepair_cost = dronerepair_cost
	cs .delivery_fee = delivery_fee
	cs.gam = discount
	yo, xo = find_start(board)

	new_values = []
	for y in range(cs.sizzle[0]):
		t1 = []
		for x in range(cs.sizzle[1]):
			t1.append(0)
		new_values.append(t1)
	converge = False
	while not converge:
		# for all x,y
		for y in range(cs.sizzle[0]):
			for x in range(cs.sizzle[1]):
				# if we've found a delivery square
				if board[y][x] == common.constants.CUSTOMER:
					new_values[y][x] = delivery_fee
					policies[y][x] = common.constants.EXIT
				# if we've found a rival square
				elif board[y][x] == common.constants.RIVAL:
					new_values[y][x] = -1 * dronerepair_cost
					policies[y][x] == common.constants.EXIT
				# otherwise
				else:
					vmax = get_reward(values, x, y, ACTIONS[0])
					for a in ACTIONS:
						v = get_reward(values, x, y, a)
						if v >= vmax:
							new_values[y][x] = v
							if v == vmax:
								# troubleshoot this
								policies[y][x] = tie_breaker(policies[y][x], a)
							else:
								policies[y][x] = a
							vmax = v
		tot = True
		for y in range(cs.sizzle[0]):
			for x in range(cs.sizzle[1]):
				n = abs(values[y][x] - new_values[y][x])
				if n > THRESH:
					tot = False
		converge = tot
		for y in range(cs.sizzle[0]):
			for x in range(cs.sizzle[1]):
				values[y][x] = new_values[y][x]
	return values[yo][xo]
