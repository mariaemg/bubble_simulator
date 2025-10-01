import OpenGL.GL as gl
import OpenGL.GL.shaders as shaders  
import numpy as np
import os
from pathlib import Path

class MetaballRenderer: #Podría incluirlo en main pero lo hago aparte para que se vea más ordenado
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.shader_pipeline = None
        self.vertex_list = None
        self.is_initialized = False
        
        self._init_opengl_resources()
    
    def _init_opengl_resources(self): #cargar shaders
        vertex_source_path = Path(os.path.dirname(__file__)) / "shaders" / "vertex.glsl"
        fragment_source_path = Path(os.path.dirname(__file__)) / "shaders" / "fragment.glsl"
        
        with open(vertex_source_path, 'r') as f:
                vertex_source_code = f.read()
        with open(fragment_source_path, 'r') as f:
                fragment_source_code = f.read()
            
        #creamos la pipeline
        vertex_shader = shaders.compileShader(vertex_source_code, gl.GL_VERTEX_SHADER)
        fragment_shader = shaders.compileShader(fragment_source_code, gl.GL_FRAGMENT_SHADER)
        self.shader_pipeline = shaders.compileProgram(vertex_shader, fragment_shader)
        
        #definimos la geometría
        vertices = np.array([
            -1.0, -1.0, 0.0,  0.0, 0.0,  # inf izq
             1.0, -1.0, 0.0,  1.0, 0.0,  # inf der
             1.0,  1.0, 0.0,  1.0, 1.0,  # sup der
            -1.0,  1.0, 0.0,  0.0, 1.0   # sup izq
        ], dtype=np.float32)
        
        indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)
        
        #crear vertex array y buffer
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
        
        #crear element buffer
        self.ebo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW)
        
        #configurar atributos y sus posiciones
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 5 * 4, gl.ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 5 * 4, gl.ctypes.c_void_p(3 * 4))
        gl.glEnableVertexAttribArray(1)
        
        #desvinculamos
        gl.glBindVertexArray(0)
        
        #habilitar transparencia
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        self.is_initialized = True
    
    def render(self, bubbles, current_time):
        gl.glClearColor(0.05, 0.05, 0.15, 1.0)  #fondo azul oscuro
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        
        #utilizamos la pipeline 
        gl.glUseProgram(self.shader_pipeline)
        
        #obtenemos id de los uniforms y los enviamos
        time_loc = gl.glGetUniformLocation(self.shader_pipeline, "time")
        resolution_loc = gl.glGetUniformLocation(self.shader_pipeline, "resolution")
        
        if time_loc >= 0: #el >= verifica que se encontró el uniform
            gl.glUniform1f(time_loc, current_time)
        if resolution_loc >= 0:
            gl.glUniform2f(resolution_loc, self.width, self.height)
        
        max_bubbles = 125
        
        if bubbles:
            positions = np.array([[b.position[0], b.position[1]] for b in bubbles], dtype=np.float32)
            strengths = np.array([b.metaball_strength for b in bubbles], dtype=np.float32)
            colors = np.array([b.color for b in bubbles], dtype=np.float32)
            
            #hacemos que el tamaño de "bubbles" coincida con el máximo de burbujas
            num_actual_bubbles = len(bubbles)
            if num_actual_bubbles < max_bubbles:
                positions = np.pad(positions, ((0, max_bubbles - num_actual_bubbles), (0, 0)), 'constant')
                strengths = np.pad(strengths, (0, max_bubbles - num_actual_bubbles), 'constant')
                colors = np.pad(colors, ((0, max_bubbles - num_actual_bubbles), (0, 0)), 'constant')
            elif num_actual_bubbles > max_bubbles:
                positions = positions[:max_bubbles]
                strengths = strengths[:max_bubbles]
                colors = colors[:max_bubbles]
            
            #enviamos los arrays con las props de las burbujas
            pos_loc = gl.glGetUniformLocation(self.shader_pipeline, "bubblePositions")
            str_loc = gl.glGetUniformLocation(self.shader_pipeline, "bubbleStrengths")
            col_loc = gl.glGetUniformLocation(self.shader_pipeline, "bubbleColors")
            num_loc = gl.glGetUniformLocation(self.shader_pipeline, "numBubbles")
            
            if pos_loc >= 0:
                gl.glUniform2fv(pos_loc, max_bubbles, positions.flatten())
            if str_loc >= 0:
                gl.glUniform1fv(str_loc, max_bubbles, strengths)
            if col_loc >= 0:
                gl.glUniform3fv(col_loc, max_bubbles, colors.flatten())
            if num_loc >= 0:
                gl.glUniform1i(num_loc, min(num_actual_bubbles, max_bubbles))
        else:
            #si no hay burbujas enviamos arrays vacíos (para evitar errores)
            empty_positions = np.zeros((max_bubbles, 2), dtype=np.float32)
            empty_strengths = np.zeros(max_bubbles, dtype=np.float32)
            empty_colors = np.zeros((max_bubbles, 3), dtype=np.float32)
            
            pos_loc = gl.glGetUniformLocation(self.shader_pipeline, "bubblePositions")
            str_loc = gl.glGetUniformLocation(self.shader_pipeline, "bubbleStrengths")
            col_loc = gl.glGetUniformLocation(self.shader_pipeline, "bubbleColors")
            num_loc = gl.glGetUniformLocation(self.shader_pipeline, "numBubbles")
            
            if pos_loc >= 0:
                gl.glUniform2fv(pos_loc, max_bubbles, empty_positions.flatten())
            if str_loc >= 0:
                gl.glUniform1fv(str_loc, max_bubbles, empty_strengths)
            if col_loc >= 0:
                gl.glUniform3fv(col_loc, max_bubbles, empty_colors.flatten())
            if num_loc >= 0:
                gl.glUniform1i(num_loc, 0)
        
        #dibujamos el cuadrado que cubre la pantalla :D
        gl.glBindVertexArray(self.vao)
        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)
        gl.glBindVertexArray(0)

