
# Grupo:
#     Caio Brandolim Rovetta      11232156
#     Guilherme Soares Silvestre  11299832
#     Calvin Suzuki de Camargo    11232420

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import glm
import math
from PIL import Image
import glhandler as gh
from scene import Scene

scene = Scene()

# Inicializando janela
window = gh.setWindow(960, 1280, "Trabalho 2")

program = gh.setGPU()

glEnable(GL_TEXTURE_2D)
qtd_texturas = 10
textures = glGenTextures(qtd_texturas)

scene.appendModel("House", "3dFiles/house/house2.obj", "3dFiles/house/wood.png")
scene.appendModel("Outlaw", "3dFiles/exterior/outlaw car/outlaw.obj", "3dFiles/exterior/outlaw car/outlaw.png")
scene.appendModel("Police", "3dFiles/exterior/police car/police.obj", "3dFiles/exterior/police car/police.png")
scene.appendModel("Sky", "3dFiles/sky/sky.obj", "3dFiles/sky/sky2.png")
scene.appendModel("Grass", "3dFiles/ground/grass/grass.obj", "3dFiles/ground/grass/grass.jpeg")

vertices, textures, normals = scene.getVTN()

#  Enviando coordenadas de vértices, texturas e dados de iluminacao para a GPU
gh.setGPUBuffer(program, vertices, textures, normals)

glfw.set_key_callback(window, gh.key_event)
glfw.set_cursor_pos_callback(window, gh.mouse_event)
glfw.set_mouse_button_callback(window, gh.mouse_button_callback)

# Nesse momento, exibimos a janela.
glfw.show_window(window)
glfw.set_cursor_pos(window, gh.lastX, gh.lastY)
glEnable(GL_DEPTH_TEST)  # importante para 3D

while not glfw.window_should_close(window):

    glfw.poll_events()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glClearColor(0.2, 0.2, 0.2, 1.0)

    if gh.polygonal_mode == True:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    if gh.polygonal_mode == False:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)    

    # Exibe HOUSE
    r = glm.vec3( 1.0, 1.0, 0.0 )
    t = glm.vec3( 1.0, 0, 0.0 )
    s = glm.vec3( .15, .15, .15 )
    model_mat = gh.model(r, t, s, angle = 0)
    scene.drawModelbyName(program, "House", model_mat)

    # Exige CARRO
    r = glm.vec3( 1.0, 1.0, 0.0 )
    t = glm.vec3( 1.0, .01, 2.0 )
    s = glm.vec3( 0.4, 0.4, 0.4 )
    model_mat = gh.model( r, t, s, angle = 0)
    scene.drawModelbyName(program, "Outlaw", model_mat)


    # Exibe SKYBOX
    r = glm.vec3( 1.0, 1.0, 0.0 )
    t = glm.vec3( 0.0, -.5, 0.0 )
    s = glm.vec3( 500, 500, 500 )
    model_mat = gh.model( r, t, s, angle = 0)
    scene.drawModelbyName(program, "Sky", model_mat)

    # Exibe GRASS
    r = glm.vec3( 1.0, 0.0, 0.0 )
    t = glm.vec3( 0.0, 0.0, 0.0 )
    s = glm.vec3( 0.5, 0.5, 0.5)
    model_mat = gh.model( r, t, s, angle = 0)
    scene.drawModelbyName(program, "Grass", model_mat)

    # Exibe GRASS
    r = glm.vec3( 1.0, 0.0, 0.0 )
    t = glm.vec3( 0.0, 5.0, 0.0 )
    s = glm.vec3( 0.5, 0.5, 0.5)
    model_mat = gh.model( r, t, s, angle = 0)
    scene.drawModelbyName(program, "Grass", model_mat)
    # # Exibe o CHAO
    # r = glm.vec3( 1.0, 1.0, 0.0 )
    # t = glm.vec3( 1.0, -.01, 0.0 )
    # s = glm.vec3( 50, 50, 50 )
    # model_mat = gh.model( r, t, s, angle = 0)


    mat_view = gh.view()
    loc_view = glGetUniformLocation(program, "view")
    glUniformMatrix4fv(loc_view, 1, GL_FALSE, mat_view)

    mat_projection = gh.projection()
    loc_projection = glGetUniformLocation(program, "projection")
    glUniformMatrix4fv(loc_projection, 1, GL_FALSE, mat_projection)

    glfw.swap_buffers(window)

glfw.terminate()
