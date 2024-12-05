class Curve:
	def __init__(self, Vd, Vm, Va, D, amax, dmax) -> None:
		# We split the movement in 3 phases: departure, max speed, arrival

		self.Vd = Vd
		self.Vm = Vm
		self.Va = Va

		self.D = D
		self.Dd = (Vm ** 2 - Vd ** 2) / (2 * amax)  # Departure distance
		self.Da = (Vm ** 2 - Va ** 2) / (2 * dmax)  # Arrival distance
		self.Dm = self.D - self.Dd - self.Da

		self.Td = 2 * self.Dd / (self.Vd + self.Vm)  # total time of departure phase
		self.Ta = 2 * self.Da / (self.Va + self.Vm)  # total time of arrival phase
		self.Tm = self.Dm / self.Vm

		self.T = self.Td + self.Tm + self.Ta

		self.Cd = (self.Vm - self.Vd) / self.Td  # Departure phase slope
		self.Ca = (self.Va - self.Vm) / self.Ta  # Arrival phase slope

	def V1(self,t):
		return self.Vd + self.Cd * t  # Velocity on departure phase equation
	def V2(self,t):
		return self.Vm  # Velocity on max speed phase equation
	def V3(self,t):
		return self.Va + self.Ca * (t - self.T)  # Velocity on arrival phase equation

	def PlannedVelocity(self, t):
		if t<self.T:
			return min(self.V1(t), self.V2(t), self.V3(t))
		else:
			return self.Va

	def PlannedTotalTime(self):
		return self.T

	def PlannedPosition(self, t):
     	# Phase 1: Departure
		if t <= self.Td:  
			return self.Vd * t + 0.5 * self.Cd * t ** 2
		# Phase 2: Max speed
		elif t <= self.Td + self.Tm:  
			t_m = t - self.Td
			return self.Dd + self.Vm * t_m
		# Phase 3: Arrival
		elif t <= self.T:  
			t_a = t - self.Td - self.Tm
			return self.Dd + self.Dm + self.Vm * t_a + 0.5 * self.Ca * t_a ** 2
		# After planned time, position remains at final distance D
		else:  
			return self.D