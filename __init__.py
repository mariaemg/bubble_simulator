import os.path
import sys
from pathlib import Path

import pyglet
from pyglet import clock
from pyglet.window import key, mouse
import time
import OpenGL.GL as gl
import numpy as np
import click

from .simulation import BubbleSimulation
from .renderer import MetaballRenderer


@click.command("bubble_simulator", short_help='Metaball Bubble Simulator')
@click.option("--width", type=int, default=1200, help="Window width")
@click.option("--height", type=int, default=800, help="Window height")
def bubble_simulator(width, height):

    #Inicialización de la ventana y el estado
    window = pyglet.window.Window(width, height, caption="Metaball Bubble Simulator")
    
    #Variables de estado
    running = True
    
    simulation = BubbleSimulation(width, height)
    renderer = MetaballRenderer(width, height)
    
    start_time = time.time()
    fps = 60
    
    show_stats = False
    paused = False
    mouse_pressed = False
    mouse_x = 0
    mouse_y = 0
    
    frame_count = 0
    fps_history = []

    continuous_spawn = False
    spawn_timer = 0

    #Funciones auxiliares

    def add_initial_bubbles():
        #añade burbujas iniciales a la simulación
        for _ in range(12):
            simulation.add_bubble()

    def print_help():
        #muestra comandos de la simulación
        print("\n" + "="*50)
        print("     BUBBLE SIMULATOR CONTROLS")
        print("="*50)
        print("MOUSE CONTROLS:")
        print("   Left Click:    Explota burbuja existente o añade nueva burbuja")
        print("   Right Click:   Explosión de burbujas")
        print("   Mouse Drag:    Barrido de burbujas")
        print("   Mouse Move:    Repele a las burbujas")
        print()
        print("KEYBOARD CONTROLS:")
        print("   SPACE:         Añade 8 burbujas aleatorias")
        print("   C:             Elimina las burbujas")
        print("   P:             Pausa/Reanuda la simulación")
        print("   S:             Muestra estadísticas")
        print("   R:             Resetear simulación")
        print("   E:             Explosión de burbujas en el centro")
        print()
        print("MOUSE REPULSION CONTROLS:")
        print("   UP/DOWN:       Aumentar/Disminuir fuerza de repulsión")
        print("   LEFT/RIGHT:    Disminuir/Aumentar radio de repulsión")
        print()
        print("OTHER:")
        print("   H:             Mostrar esta información")
        print("="*50)
        print(f"Max burbujas: {simulation.max_bubbles}")
        print(f"Fuerza de repulsión: {simulation.mouse_repulsion_strength:.0f}")
        print(f"Radio de repulsión: {simulation.mouse_repulsion_radius:.0f}")
        print("="*50 + "\n")

    def print_stats():
        #muestra estadísticas actuales
        stats = simulation.get_simulation_stats()
        avg_fps = sum(fps_history) / len(fps_history) if fps_history else 0
        
        print(f"\n{'='*30}")
        print(f"   Estadísticas")
        print(f"{'='*30}")
        print(f"Burbujas:        {stats['total burbujas']:3d} / {simulation.max_bubbles}")
        print(f"Radio promedio:     {stats['radio promedio']:6.1f}")
        print(f"Rapidez promedio:      {stats['rapidez promedio']:6.1f}")
        print(f"Energía total:   {stats['energía total']:6.1f}")
        print(f"FPS:            {avg_fps:6.1f}")
        print(f"Frame:          {frame_count:6d}")
        print(f"Status:         {'PAUSED' if paused else 'RUNNING'}")
        print(f"Mouse Pos:      ({mouse_x:6.1f}, {mouse_y:6.1f})")
        print(f"Repulsion:      {simulation.mouse_repulsion_strength:.0f}")
        print(f"Radio repulsión:    {simulation.mouse_repulsion_radius:.0f}")
        print(f"{'='*30}\n")

  
    #Registro de eventos de la ventana

    @window.event
    def on_mouse_motion(x, y, dx, dy):
        nonlocal mouse_x, mouse_y
        mouse_x = x
        mouse_y = y
        simulation.update_mouse_position(x, y)
    
    @window.event
    def on_mouse_press(x, y, button, modifiers):
        nonlocal mouse_pressed, mouse_x, mouse_y
        mouse_pressed = True
        mouse_x = x
        mouse_y = y
        
        simulation.update_mouse_position(x, y)
        
        if button == mouse.LEFT:
            bubble_exploded = simulation.explode_bubble_at_position(x, y)
            if bubble_exploded:
                print("Burbuja explotada!")
            else:
                simulation.add_bubble_at_mouse(x, y)
                print("Nueva burbuja añadida")
                
        elif button == mouse.RIGHT:
            simulation.add_bubble_explosion(x, y, 10)
            print("Explosión de burbujas!")
    
    @window.event
    def on_mouse_release(x, y, button, modifiers):
        nonlocal mouse_pressed, continuous_spawn
        mouse_pressed = False
        continuous_spawn = False
    
    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        nonlocal mouse_x, mouse_y, continuous_spawn, frame_count
        mouse_x = x
        mouse_y = y
        
        simulation.update_mouse_position(x, y)
        
        if buttons & mouse.LEFT:
            continuous_spawn = True
            
            if frame_count % 3 == 0:
                if not simulation.explode_bubble_at_position(x, y):
                    simulation.add_bubble_at_mouse(x, y)
    
    @window.event
    def on_key_press(symbol, modifiers):
        nonlocal paused, show_stats
        
        if symbol == key.SPACE:
            for _ in range(8):
                simulation.add_bubble()
                
        elif symbol == key.C:
            simulation.clear_bubbles()
            print("Burbujas eliminadas")
            
        elif symbol == key.P:
            paused = not paused
            print(f"Simulación {'pausada' if paused else 'reanudada'}")
            
        elif symbol == key.S:
            show_stats = not show_stats
            print(f"Estadísticas {'habilitadas' if show_stats else 'deshabilitadas'}")
            
        elif symbol == key.R:
            simulation.clear_bubbles()
            add_initial_bubbles()
            print("Reseteo de la simulación")
            
        elif symbol == key.E:
            center_x, center_y = window.width // 2, window.height // 2
            simulation.add_bubble_explosion(center_x, center_y, 15)
            print("Explosión en el centro!")
            
        elif symbol == key.UP:
            simulation.mouse_repulsion_strength *= 1.2
            print(f"Fuerza de repulsión: {simulation.mouse_repulsion_strength:.0f}")
            
        elif symbol == key.DOWN:
            simulation.mouse_repulsion_strength *= 0.8
            print(f"Fuerza de repulsión: {simulation.mouse_repulsion_strength:.0f}")
            
        elif symbol == key.LEFT:
            simulation.mouse_repulsion_radius = max(50, simulation.mouse_repulsion_radius * 0.8)
            print(f"Radio de repulsión: {simulation.mouse_repulsion_radius:.0f}")
            
        elif symbol == key.RIGHT:
            simulation.mouse_repulsion_radius = min(400, simulation.mouse_repulsion_radius * 1.2)
            print(f"Radio de repulsión: {simulation.mouse_repulsion_radius:.0f}")
            
        elif symbol == key.H:
            print_help()

    @window.event
    def on_close():
        nonlocal running
        running = False #Señala que la aplicación no debe seguir renderizando
        
        #Desprograma la función de actualización
        clock.unschedule(update) 
        
        #Sale explícitamente de la aplicación Pyglet
        pyglet.app.exit()

    #Función de actualización
    def update(dt):
        nonlocal running, paused, mouse_x, mouse_y, continuous_spawn, spawn_timer, frame_count, fps_history
        if not running:
            return
            
        dt = min(dt, 1/30.0)
        
        simulation.update_mouse_position(mouse_x, mouse_y)
        
        if not paused:
            simulation.update(dt)
            
            if continuous_spawn:
                spawn_timer += dt
                if spawn_timer > 0.05:
                    if simulation.get_bubble_count() < simulation.max_bubbles:
                        simulation.add_bubble_at_mouse(mouse_x, mouse_y)
                    spawn_timer = 0
            
        frame_count += 1
        current_fps = 1.0 / dt if dt > 0 else 0
        fps_history.append(current_fps)
        
        if len(fps_history) > 60:
            fps_history.pop(0)
    
    @window.event
    def on_draw():
        nonlocal running, frame_count, show_stats, start_time
        
        if not running:
            return
            
        try:
            window.clear()
            
            current_time = time.time() - start_time
            
            renderer.render(simulation.bubbles, current_time)
            
            if show_stats and frame_count % 60 == 0: #para que no se sature, mostramos cada segundo
                print_stats()
                
        except gl.GLError as e:
            # Captura errores OpenGL, si la aplicación todavía se considera "corriendo"
            if running: 
                print(f"OpenGL error in render: {e}")
                running = False
                window.close() # Intenta cerrar la ventana de forma limpia

    #Inicio de la aplicación
    
    #Agregar burbujas iniciales al inicio
    add_initial_bubbles()
    
    #Programar la función de actualización
    clock.schedule_interval(update, 1/fps) # 60 FPS
    
    print("Bubble Simulator iniciado!")
    print("Presiona H para acceder a help")
    print("-" * 50)
    print_help() #Muestra la ayuda al inicio

    pyglet.app.run()
