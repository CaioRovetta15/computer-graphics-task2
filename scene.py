import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import glm

class Object:
    def __init__(self):
        # indices para desenhar
        self.begin_ind = None
        self.end_ind = None
        # indice da textura
        self.texture_id = None
        # transformação
        self.model = glm.mat4(1.0)
    
    def draw_model(self):
        glDrawArrays(GL_TRIANGLE, self.begin_ind, self.end_ind)