class Curve:
	def __init__(self, departure_speed: float, max_speed: float, arrival_speed: float, total_distance: float, acceleration_max: float, decceleration_max: float) -> None:
		# We split the movement in 3 phases: departure, max speed, arrival

		self.departure_speed = departure_speed
		self.mid_speed = max_speed
		self.arrival_speed = arrival_speed

		self.total_distance = total_distance
		self.departure_distance = (max_speed ** 2 - departure_speed ** 2) / (2 * acceleration_max)  # Departure total_distance
		self.arrival_distance = (max_speed ** 2 - arrival_speed ** 2) / (2 * decceleration_max)  # Arrival total_distance
		self.mid_distance = self.total_distance - self.departure_distance - self.arrival_distance

		self.departure_time = 2 * self.departure_distance / (self.departure_speed + self.mid_speed)  # total time of departure phase
		self.arrival_time = 2 * self.arrival_distance / (self.arrival_speed + self.mid_speed)  # total time of arrival phase
		self.mid_time = self.mid_distance / self.mid_speed

		self.total_time = self.departure_time + self.mid_time + self.arrival_time

		self.Cd = (self.mid_speed - self.departure_speed) / self.departure_time  # Departure phase slope
		self.Ca = (self.arrival_speed - self.mid_speed) / self.arrival_time  # Arrival phase slope

	def V1(self,t):
		return self.departure_speed + self.Cd * t  # Velocity on departure phase equation
	def V2(self,t):
		return self.mid_speed  # Velocity on max speed phase equation
	def V3(self,t):
		return self.arrival_speed + self.Ca * (t - self.total_time)  # Velocity on arrival phase equation

	def PlannedVelocity(self, t):
		if t<self.total_time:
			return min(self.V1(t), self.V2(t), self.V3(t))
		else:
			return self.arrival_speed

	def PlannedTotalTime(self):
		return self.total_time

	def PlannedPosition(self, t):
		# Phase 1: Departure
		if t <= self.departure_time:
			return self.departure_speed * t + 0.5 * self.Cd * t ** 2
		# Phase 2: Max speed
		elif t <= self.departure_time + self.mid_time:
			t_m = t - self.departure_time
			return self.departure_distance + self.mid_speed * t_m
		# Phase 3: Arrival
		elif t <= self.total_time:
			t_a = t - self.departure_time - self.mid_time
			return self.departure_distance + self.mid_distance + self.mid_speed * t_a + 0.5 * self.Ca * t_a ** 2
		# After planned time, position remains at final total_distance
		else:  
			return self.total_distance