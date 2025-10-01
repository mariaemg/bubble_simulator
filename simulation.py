import numpy as np
import random
from .bubble_agent import Bubble


class BubbleSimulation: #"mundo" que define y gestiona la simulación de las burbujas
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.bubbles = []
        self.mouse_pos = np.array([width//2, height//2])  #posición base
        
        #parámetros para realismo y dinamismo
        self.gravity = np.array([0, -50])
        self.air_resistance = 0.01
        self.spawn_rate = 0.08
        self.max_bubbles = 125
        
        #repulsión del mouse
        self.mouse_repulsion_strength = 15000.0
        self.mouse_repulsion_radius = 150.0
        
        #añadir efecto de viento
        self.wind_strength = 30.0
        self.wind_direction = np.array([1, 0])
        self.wind_change_timer = 0
        
    def update_mouse_position(self, mouse_x, mouse_y): #actualizar posición del mouse para efecto de repulsión
        self.mouse_pos = np.array([mouse_x, mouse_y])
        
    def add_bubble(self, x=None, y=None, radius=None, speed=None): #añadir burbuja
        if x is None:
            x = random.uniform(50, self.width - 50)
        if y is None:
            y = random.uniform(50, self.height - 50)
        if radius is None:
            radius = random.uniform(20, 40)
        if speed is None:
            speed = np.array([
                random.uniform(-150, 150),
                random.uniform(-100, 150)
            ])
        
        position = np.array([x, y], dtype=float)
        
        #colores bonitos y aleatorios :D
        colors = [
            [0.2, 0.8, 1.0],  # celeste
            [0.1, 1.0, 0.7],  # turquesa
            [0.9, 0.2, 1.0],  # morado
            [0.2, 1.0, 0.2],  # verde
            [1.0, 0.7, 0.1],  # naranjo
            [1.0, 0.2, 0.5],  # rosado
        ]
        
        bubble = Bubble(
            radius=radius,
            position=position,
            speed=speed,
            min_radius=5.0,
            max_speed=400.0,
            mode="split",
            density=200.0,
            color=random.choice(colors)
        )
        
        self.bubbles.append(bubble)
        return bubble
    
    def apply_mouse_repulsion(self, bubble): #aplicar repulsión
        to_bubble = bubble.position - self.mouse_pos
        distance = np.linalg.norm(to_bubble)
        
        #solo aplicar repulsión si está dentro del radio y el cursor no está justo encima
        if distance < self.mouse_repulsion_radius and distance > 1.0:
            #Calcular la fuerza de repulsión basada en la distancia
            #Fuerza más fuerte cuando está más cerca, pero con control mejor
            distance_factor = max(0.1, distance / self.mouse_repulsion_radius)  #0.1 a 1.0
            force_magnitude = self.mouse_repulsion_strength * (1.0 - distance_factor) / (distance + 10.0)
            
            #Normalizar dirección y aplicar fuerza
            direction = to_bubble / distance
            repulsion_force = direction * force_magnitude
            
            #Aplicar fuerza
            bubble.speed += repulsion_force * 0.016  # Equivalente a 60 FPS
            
            #Agregar un poco de fuerza perpendicular para efecto de remolino más sutil
            perpendicular = np.array([-direction[1], direction[0]])
            swirl_force = perpendicular * force_magnitude * 0.008
            bubble.speed += swirl_force
            #sin esta fuerza, el movimiento sería como muy robótico, en una sola dirección
            
            #Limitar velocidad máxima
            speed_magnitude = np.linalg.norm(bubble.speed)
            if speed_magnitude > bubble.max_speed:
                bubble.speed = (bubble.speed / speed_magnitude) * bubble.max_speed
    
    def apply_wind_effect(self, bubble, dt): #efecto de viento para movimiento más realista
        wind_effect = self.wind_strength * (1.0 + 20.0 / bubble.radius) #las más pequeñas son más afectadas
        wind_force = self.wind_direction * wind_effect
        
        #aplicar la fuerza
        bubble.speed += wind_force * dt
    
    def update_wind(self, dt): #actualiza dirección y fuerza del viento
        self.wind_change_timer += dt
        if self.wind_change_timer > 2.0:  #lo modifica viento cada 2 segundos
            angle = random.uniform(0, 2 * np.pi) #dirección random
            self.wind_direction = np.array([np.cos(angle), np.sin(angle)])
            self.wind_strength = random.uniform(20, 50)
            self.wind_change_timer = 0
    
    def find_bubble_at_position(self, x, y): #encuentra burbuja en la posición dada
        point = np.array([x, y])
        clicked_bubbles = []
        
        for bubble in self.bubbles:
            if bubble.is_point_inside(point):
                clicked_bubbles.append(bubble)
        
        if clicked_bubbles:
            #si hay muchas retorna la más grande
            return max(clicked_bubbles, key=lambda b: b.radius)
        return None
    
    def explode_bubble_at_position(self, x, y): #explota burbuja en la posición dada
        bubble = self.find_bubble_at_position(x, y)
        if bubble:
            #pasa el color de la burbuja a la original a las burbujitas que salgan de la explosión
            self.create_explosion_at_position(bubble.position, bubble.radius, bubble.color)
            
            #remover burbuja original
            if bubble in self.bubbles:
                self.bubbles.remove(bubble)
            
            print(f"Burbuja explotada en ({x:.0f}, {y:.0f})")
            return True
        return False
    
    def create_explosion_at_position(self, position, original_radius, original_color):
        #crea explosión de burbujas en la posición dada
        fragment_count = random.randint(4, 8) #número de fragmentos
        
        for _ in range(fragment_count):
            #posición random alrededor del punto de explosión
            angle = random.uniform(0, 2 * np.pi)
            distance = random.uniform(0, original_radius * 1.5)
            offset = np.array([
                np.cos(angle) * distance,
                np.sin(angle) * distance
            ])
            fragment_pos = position + offset
            
            #impulso inicial
            explosion_angle = random.uniform(0, 2 * np.pi)
            explosion_speed = random.uniform(150, 300)
            fragment_speed = np.array([
                np.cos(explosion_angle) * explosion_speed,
                np.sin(explosion_angle) * explosion_speed
            ])
            
            #fragmento con un poco de variación de radio
            fragment_radius = random.uniform(5, original_radius * 0.4)
            
            #usar color original con pequeña variación
            fragment_color = original_color.copy()
            color_variation = np.random.uniform(-0.1, 0.1, 3)
            fragment_color += color_variation
            fragment_color = np.clip(fragment_color, 0.0, 1.0)  #Mantener en rango válido
            
            fragment = Bubble(
                radius=fragment_radius,
                position=fragment_pos,
                speed=fragment_speed,
                min_radius=3.0,
                max_speed=400.0,
                mode="split",
                density=150.0,  #fragmentos ligeros
                color=fragment_color
            )
            
            self.bubbles.append(fragment)
    
    def update(self, dt): #actualizar la simulación!

        self.update_wind(dt) #actualizar viento

        alive_bubbles = [] #actualizar burbujas
        new_bubbles = []
        
        for bubble in self.bubbles:
            self.apply_mouse_repulsion(bubble)
            
            self.apply_wind_effect(bubble, dt)

            turbulence = np.array([   #turbulencia random
                random.uniform(-50, 50),
                random.uniform(-25, 25)
            ])
            bubble.speed += turbulence * dt

            is_alive = bubble.update_pos(self.bubbles, dt)
            
            if is_alive:
                alive_bubbles.append(bubble)
                
                if hasattr(bubble, 'to_split') and bubble.to_split: #chequear si debería dividirse
                    new_bubble = bubble.split()
                    if new_bubble:
                        new_bubbles.append(new_bubble)
        
        #añadir burbujas que surgieron de las divisiones
        self.bubbles = alive_bubbles + new_bubbles
        
        #spawnear burbujas random
        if (len(self.bubbles) < self.max_bubbles and 
            random.random() < self.spawn_rate * dt):
            self.add_bubble()
        #la segunda condición da una probabilidad constante indep. de los fps, usada en muchas sim. a tiempo real :D

        #limitar total de burbujas
        if len(self.bubbles) > self.max_bubbles:
            #eliminar las más viejas
            self.bubbles.sort(key=lambda b: getattr(b, 'age', 0))
            self.bubbles = self.bubbles[:self.max_bubbles]
    
    def add_bubble_at_mouse(self, mouse_x, mouse_y): #añadir burbuja en la posición del mouse
        #añadir offset, y se aleja del cursor
        offset_angle = random.uniform(0, 2 * np.pi)
        offset_distance = random.uniform(30, 60)
        offset = np.array([
            np.cos(offset_angle) * offset_distance,
            np.sin(offset_angle) * offset_distance
        ])
    
        away_velocity = offset * 3
        base_velocity = np.array([
            random.uniform(-50, 50),
            random.uniform(-25, 75)
        ])
        
        bubble = self.add_bubble(
            mouse_x + offset[0], 
            mouse_y + offset[1],
            radius=random.uniform(25, 35),
            speed=away_velocity + base_velocity
        )
        
        return bubble
    
    def add_bubble_explosion(self, mouse_x, mouse_y, count=10): #explosión de burbujas
        for i in range(count):
            #patrón circular de explosión
            angle = (2 * np.pi * i) / count + random.uniform(-0.3, 0.3)
            distance = random.uniform(40, 100)
            
            pos_x = mouse_x + np.cos(angle) * distance
            pos_y = mouse_y + np.sin(angle) * distance
            
            #impulso de velocidad
            speed_magnitude = random.uniform(200, 350)
            speed = np.array([
                np.cos(angle) * speed_magnitude,
                np.sin(angle) * speed_magnitude
            ])
            
            self.add_bubble(
                pos_x,
                pos_y,
                radius=random.uniform(15, 30),
                speed=speed
            )
    
    def clear_bubbles(self): #elimina todas las burbujas
        self.bubbles.clear()
        print("Todas las burbujas han sido eliminadas")
    
    def get_bubble_count(self): #entrega número actual de burbujas
        return len(self.bubbles)
    
    def get_simulation_stats(self): #entrega estadísticas de la simulación
        if not self.bubbles:
            return {
                'total burbujas': 0,
                'radio promedio': 0,
                'rapidez promedio': 0,
                'energía total': 0
            }
        
        total_radius = sum(b.radius for b in self.bubbles)
        total_speed = sum(b.get_norm_speed() if hasattr(b, 'get_norm_speed') else np.linalg.norm(b.speed) for b in self.bubbles)
        total_energy = sum(getattr(b, 'remaining_energy', 0) for b in self.bubbles)
        
        return {
            'total burbujas': len(self.bubbles),
            'radio promedio': total_radius / len(self.bubbles),
            'rapidez promedio': total_speed / len(self.bubbles),
            'energía total': total_energy
        }