from config_loader import CONFIG
from geometry import OrientedPoint
from curve import Curve

class MovementSupervisor:
    def __init__(self, profile_name: str, linear_speed: float, angular_speed: float):
        """
        Initialise le superviseur en chargeant le profil spécifié depuis config.json.
    
        :param profile_name: Nom du profil à utiliser (high_speed, cruise_speed, low_speed).
        """
        self.profile = CONFIG.SPEED_PROFILES[profile_name] # Profil de vitesse à changer, refaire config.json
        if not self.profile:
            raise ValueError(f"Profil '{profile_name}' non trouvé dans la configuration.")
        
        self.trajectory = [] # Liste de points sous la forme [((x, y), θ), ...] à récupérer depuis pathfinder.py
        self.cumulative_distances = [] # Liste des distances cumulées entre chaque point de la trajectoire
        
        self.linear_speed = linear_speed
        self.angular_speed = angular_speed
        self.linear_curve = None
        self.angular_curve = None

    def set_trajectory(self, trajectory):
        """
        Définit la trajectoire à suivre.

        :param trajectory: Liste de points sous la forme [((x, y), θ), ...].
        """
        self.trajectory = trajectory
        self.cumulative_distances = [0]
        total_distance = 0
        for i in range(1, len(self.trajectory)):
            x1, y1 = self.trajectory[i - 1][0]
            x2, y2 = self.trajectory[i][0]
            total_distance += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            self.cumulative_distances.append(total_distance)

    def update_current_state(self, current_position: OrientedPoint, current_velocity):
        """
        Met à jour la position et la vitesse actuelles du robot.

        :param current_position: OrientedPoint ((x, y), θ) représentant la position actuelle.
        :param current_velocity: Tuple (v_lin, v_ang) représentant les vitesses actuelles.
        """
        self.current_position = current_position
        self.linear_speed = current_velocity[0]
        self.angular_speed = current_velocity[1]

    def compute_future_state(self, t):
        """
        Calcule le point et les vitesses désirés dans t secondes.

        :param t: Temps en secondes pour le calcul du futur état.
        :return: Tuple (((x, y), θ), (linear_speed_desired, angular_speed_desired))
        """
        self._initialize_curves()
        future_position = self._calculate_future_position(t)
        future_velocity = self._calculate_future_velocity(t)
        return future_position, future_velocity

    def _initialize_curves(self):
        """
        Initialise les courbes de mouvement pour les vitesses linéaire et angulaire.
        """
        # Calculer la distance totale linéaire D
        total_linear_distance = self.cumulative_distances[-1]
        
        # Pour simplifier, on suppose que le robot suit une trajectoire plane sans rotation pour le mouvement linéaire
        # Pour le mouvement angulaire, on calcule la différence totale d'angle
        total_angular_distance = abs(self.trajectory[-1][1] - self.trajectory[0][1])
        
        # Paramètres du profil
        Vd_lin = self.linear_speed
        Vm_lin = self.profile["max_linear_speed"]
        Va_lin = 0.0 # On suppose que le robot s'arrête à la fin du mouvement
        Dd_lin = total_linear_distance * 0.1 #distance linéaire de départ
        Da_lin = total_linear_distance * 0.1 #distance linéaire d'arrivée
        
        Vd_ang = self.angular_speed
        Vm_ang = self.profile["max_angular_speed"]
        Va_ang = 0.0 # On suppose que le robot s'arrête à la fin du mouvement
        Dd_ang = total_angular_distance * 0.1 #distance angulaire de départ
        Da_ang = total_angular_distance * 0.1 #distance angulaire d'arrivée
        
        # Créer les objets Curve pour les mouvements linéaire et angulaire
        self.linear_curve = Curve(Vd_lin, Vm_lin, Va_lin, total_linear_distance, Dd_lin, Da_lin)
        self.angular_curve = Curve(Vd_ang, Vm_ang, Va_ang, total_angular_distance, Dd_ang, Da_ang)
        
    def _calculate_future_position(self, t):
        """
        Calcule la position future du robot à l'instant t.
        """
        # Distance parcourue à l'instant t
        s = self.linear_curve.PlannedPosition(t)
        
        # Si la distance dépasse la distance totale, on limite à la fin de la trajectoire
        if s >= self.cumulative_distances[-1]:
            return self.trajectory[-1]
        
        # Trouver le segment correspondant à la distance s
        for i in range(1, len(self.cumulative_distances)):
            if self.cumulative_distances[i] >= s:
                # Interpolation linéaire entre les points i-1 et i
                s1 = self.cumulative_distances[i - 1]
                s2 = self.cumulative_distances[i]
                ratio = (s - s1) / (s2 - s1)
                
                (x1, y1), theta1 = self.trajectory[i - 1]
                (x2, y2), theta2 = self.trajectory[i]
                
                x = x1 + ratio * (x2 - x1)
                y = y1 + ratio * (y2 - y1)
                theta = theta1 + ratio * (theta2 - theta1)
                
                return ((x, y), theta)
        # Si on n'a pas trouvé (ce qui ne devrait pas arriver), on retourne le dernier point
        return self.trajectory[-1]

    def _calculate_future_velocity(self, t):
        """
        Calcule la vitesse future du robot à l'instant t.
        """
        v_linear = self.linear_curve.PlannedVelocity(t)
        v_angular = self.angular_curve.PlannedVelocity(t)
        return (v_linear, v_angular)
