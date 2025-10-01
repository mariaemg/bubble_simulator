import time
import numpy as np


class Bubble:
    #clase que representa a las burbujas en la simulación :)

    def __init__(
        self,
        radius,
        position,
        speed,
        min_radius=3.0, #después, desaparece
        max_speed=300.0,
        mode="split", #se divide
        density=400.0,
        color=None,
    ):
        #iniciar una "instancia" de burbuja
        self.max_speed = max_speed
        self.position = position.copy()
        self.speed = speed.copy()
        self.radius = radius
        self.min_radius = min_radius

        self.t0 = time.time()
        self.t = time.time()
        self.last_split_time = time.time()

        self.mode = mode
        self.to_split = False
        self.exploding = False

        self.density = density
        self.set_weight()
        self.set_resistance()

        #propiedades de la burbuja
        self.lifetime = np.random.uniform(60, 120)
        self.age = 0
        self.base_radius = radius
        
        #propiedades visuales para la metaball/burbuja
        self.metaball_strength = radius * radius * 2
        
        #guardar el color
        self.color = np.array(color if color is not None else [0.4, 0.7, 1.0], dtype=np.float32)

    def get_norm_speed(self): #retorna rapidez
        return np.linalg.norm(self.speed)

    def set_resistance(self): #configura resistencia basada en la densidad y el radio
        self.resistance = 0.002 * self.density * (self.radius ** 0.5)
        self.energy = 20 * self.resistance  #configura la energía en base a la resistencia
        self.remaining_energy = self.energy
        #es como la capacidad para soportar las colisiones

    def set_weight(self): #calcula el "peso" (representativo) de la burbuja
        self.weight = self.density * 3.14159 * self.radius ** 2

    def is_point_inside(self, point): #chequea si un punto está dentro del radio de la burbuja
        distance = np.linalg.norm(self.position - point)
        return distance <= self.radius

    def explode(self): #hace explotar a la burbuja, o más bien la prepara para ello
        self.exploding = True
        self.remaining_energy = 0  #fuerza la división
        self.to_split = True
        #impulso de velocidad
        explosion_force = np.random.uniform(100, 200)
        angle = np.random.uniform(0, 2 * np.pi)
        self.speed += np.array([
            np.cos(angle) * explosion_force,
            np.sin(angle) * explosion_force
        ])
        #limita la velocidad
        speed_mag = np.linalg.norm(self.speed)
        if speed_mag > self.max_speed:
            self.speed = (self.speed / speed_mag) * self.max_speed

    def update_pos(self, bubbles, dt): #actualiza posición de la partícula
        #actualiza edad
        self.age += dt
        
        #fuerza de "flotabilidad", para dinamismo
        flotage_force = np.array([0, 80])
        self.speed += flotage_force * dt / self.weight
        
        #turbulencia para más dinamismo
        turbulence = np.array([
            np.random.uniform(-20, 20),
            np.random.uniform(-10, 10)
        ])
        self.speed += turbulence * dt
        
        #fuerza de arrastre (para que no aceleren infinitamente)
        drag_coefficient = 0.05
        drag_force = -drag_coefficient * self.speed * np.linalg.norm(self.speed)
        self.speed += drag_force * dt
        
        #nueva posición
        new_position = self.position + dt * self.speed

        #chequear colisiones con otras burbujas
        if self.mode != "overlap":
            for other in bubbles:
                if other != self:
                    distance = np.linalg.norm(new_position - other.position)
                    if distance <= (self.radius + other.radius):
                        #burbujas colisionando
                        self.handle_collision(other, distance)

        #actualizar posición pos-colisiones
        self.position = new_position
        
        #actualizar fuerza de la "metaball" en base a la edad
        age_factor = max(0.3, 1.0 - (self.age / self.lifetime))  #30% fuerza como min
        self.metaball_strength = self.base_radius * self.base_radius * age_factor * 2
        
        #condiciones supervivencia
        return (self.age < self.lifetime and 
                self.radius > self.min_radius and 
                np.linalg.norm(self.speed) < self.max_speed * 2)

    def handle_collision(self, other, distance): #maneja colisiones entre burbujas
        if distance == 0:
            return
            
        relative_velocity = self.speed - other.speed
        normal_vector = (self.position - other.position) / distance

        if np.dot(relative_velocity, normal_vector) < 0: #chequea si las burbujas se acercan
            m1 = self.weight
            m2 = other.weight
            v1 = np.linalg.norm(self.speed)
            v2 = np.linalg.norm(other.speed)

            restitution = 0.8 #rebote con algo de pérdida de energía
            
            #calcular nuevas velocidades
            new_speed_a = self.speed - (1 + restitution) * (m2 / (m1 + m2)) * np.dot(relative_velocity, normal_vector) * normal_vector
            new_speed_b = other.speed + (1 + restitution) * (m1 / (m1 + m2)) * np.dot(relative_velocity, normal_vector) * normal_vector
            #calculadas con la fórmula vista en clase! :D (clase 17)

            new_speed_a = np.clip(new_speed_a, -self.max_speed, self.max_speed)
            new_speed_b = np.clip(new_speed_b, -other.max_speed, other.max_speed)

            if self.mode == "split":
                #calcula energía transferida
                e_transferred_a_b = 0.5 * m1 * (v1**2 - np.linalg.norm(new_speed_a) ** 2)
                e_transferred_b_a = 0.5 * m2 * (v2**2 - np.linalg.norm(new_speed_b) ** 2)

                for b, e in [(self, e_transferred_b_a), (other, e_transferred_a_b)]:
                    b.remaining_energy -= e * 0.5
                    if (
                        b.radius > b.min_radius * 3  #radio min para dividirse
                        and b.remaining_energy < b.resistance * 0.5 #poca energía
                        and time.time() - b.t0 > 1.0  #periodo de "gracia" inicial
                        and time.time() - b.last_split_time > 2.0  #periodo entre divisiones
                        and np.random.random() < 0.3  #división ocurre con 30% de prob
                    ):
                        b.to_split = True

            self.speed = new_speed_a
            other.speed = new_speed_b

    def split(self): #divide la burbuja en 2
        self.last_split_time = time.time()

        #calcular propiedades de las nuevas burbujas
        new_radius = self.radius / 1.4
        
        #matrices de rotación, se alejan en direcciones opuestas
        cos45 = np.sqrt(2) / 2
        sin45 = np.sqrt(2) / 2
        rotate_45_up = np.array([[cos45, -sin45], [sin45, cos45]])
        rotate_45_down = np.array([[cos45, sin45], [-sin45, cos45]])

        #vector perpendicular al vector velocidad
        if np.linalg.norm(self.speed) > 0:
            perp_vector = np.array([self.speed[1], -self.speed[0]])
            offset = perp_vector / np.linalg.norm(perp_vector) * new_radius * 1.5
        else:
            offset = np.array([new_radius * 1.5, 0])
        #offset evita colisiones instantáneas

        #salen disparadas dinámicamente
        split_energy = 50
        split_velocity = offset / np.linalg.norm(offset) * split_energy

        #crear nueva burbuja
        color_variation = self.color + np.random.uniform(-0.1, 0.1, 3)
        color_variation = np.clip(color_variation, 0, 1)

        new_bubble = Bubble(
            radius=new_radius,
            position=self.position + offset,
            speed=np.dot(rotate_45_up, self.speed) + split_velocity,
            min_radius=self.min_radius,
            max_speed=self.max_speed,
            mode=self.mode,
            density=self.density,
            color=color_variation,
        )

        #actualizar props de la burbuja original
        self.radius = new_radius
        self.base_radius = new_radius
        self.position = self.position - offset
        self.remaining_energy = self.energy * 0.8 #se restaura para que no se divida automáticamente
        self.speed = np.dot(rotate_45_down, self.speed) - split_velocity
        self.set_weight()
        self.set_resistance()

        #actualizar fuerza de metaball
        self.metaball_strength = self.base_radius * self.base_radius * 2

        #evitar que se vuelva a dividir en el mismo frame
        self.to_split = False
        self.exploding = False
        return new_bubble

    def __str__(self): #para ver la info de cada burbuja, en caso de
        return (
            f"Burbuja: \n"
            f"\tPosición: {self.position}, \n"
            f"\tRapidez: {self.speed} | {self.get_norm_speed():.2f}, \n"
            f"\tRadio: {self.radius:.2f}, \n"
            f"\tPeso: {self.weight:.2f}, \n"
            f"\tEdad: {self.age:.2f}/{self.lifetime:.2f}, \n"
            f"\tColor: {self.color}"
        )