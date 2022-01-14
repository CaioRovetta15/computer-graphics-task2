
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
import time
import math
import random

scene = Scene()

# Inicializando janela
window = gh.setWindow(640, 1280, "Trabalho 2")

program = gh.setGPU()

glEnable(GL_TEXTURE_2D)
qtd_texturas = 10
textures = glGenTextures(qtd_texturas)

scene.appendModel("House", "3dFiles/house/house2.obj", "3dFiles/house/wood.png")
scene.appendModel("Outlaw", "3dFiles/exterior/outlaw car/outlaw.obj", "3dFiles/exterior/outlaw car/outlaw.png")
scene.appendModel("Police", "3dFiles/exterior/police car/police.obj", "3dFiles/exterior/police car/police.png")
scene.appendModel("Sky", "3dFiles/sky/sky.obj", "3dFiles/sky/sky2.png")
scene.appendModel("Grass", "3dFiles/ground/grass/grass.obj", "3dFiles/ground/grass/nova.png")
scene.appendModel("Sofa", "3dFiles/interior/sofa/Triple_Sofa.obj", "3dFiles/interior/sofa/triple_sofa_fabric_bump.png")
scene.appendModel("Chair", "3dFiles/interior/chair/chair.obj", "3dFiles/interior/chair/wood.jpg")
scene.appendModel("Table","3dFiles/interior/mesa/Dining_Table_L150xW100xH75cm.obj","3dFiles/interior/mesa/Wood - Walnut 03 - Diffuse.png")
scene.appendModel("Man","3dFiles/exterior/man/simpleMan2.6.obj","3dFiles/exterior/man/person.png")
scene.appendModel("Concrete", "3dFiles/ground/grass/grass.obj", "3dFiles/ground/concrete/concrete.jpeg")

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

def noise():
    return random.random()

chron0 = time.time()
while not glfw.window_should_close(window):

    chron = time.time()-chron0
    glfw.poll_events()

    print( gh.cameraPos )

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glClearColor(0.2, 0.2, 0.2, 1.0)

    if gh.polygonal_mode == True:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    if gh.polygonal_mode == False:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)    

    # Exibe HOUSE
    r = glm.vec3( 1.0, 1.0, 0.0 )
    t = glm.vec3( 0.0, 0.03, 0.0 )
    s = glm.vec3( .15, .15, .15 )
    model_mat = gh.model(r, t, s, angle = 0)
    scene.drawModelbyName(program, "House", model_mat=model_mat, ka = 0.3, kd = 1.0)

    f = 0.15
    w = 2*3.14*f
    R = 6

    # Exige CARRO
    r = glm.vec3( 0.0, 1.0, 0.0 )
    t = glm.vec3( R*math.cos(w*chron), 0.02, R*math.sin(w*chron)-1)
    s = glm.vec3( 0.4, 0.4, 0.4 )
    model_mat = gh.model( r, t, s, angle = -(90+w*chron*180/3.14) + noise()*0.1)
    scene.drawModelbyName(program, "Outlaw", model_mat=model_mat, ka = 0.2, kd = 1.0)

    # Exige CARRO
    r = glm.vec3( 0.0, 1.0, 0.0 )
    t = glm.vec3( R*math.cos(w*chron-40*3.14/180), 0.02, R*math.sin(w*chron-40*3.14/180))
    s = glm.vec3( 0.4, 0.4, 0.4 )
    model_mat = gh.model( r, t, s, angle = 90-w*chron*180/3.14 + noise()*0.1)
    scene.drawModelbyName(program, "Outlaw", model_mat=model_mat, ka = 0.2, kd = 1.0)

    # Exige Police
    r = glm.vec3( 0.0, 1.0, 0.0 )
    t = glm.vec3( R*math.cos(w*chron-30*3.14/180), 0.02, R*math.sin(w*chron-30*3.14/180))
    s = glm.vec3( 0.4, 0.4, 0.4 )
    model_mat = gh.model( r, t, s, angle = 90-w*chron*180/3.14 + noise()*0)
    scene.drawModelbyName(program, "Police", model_mat=model_mat, ka = 0.2, kd = 1.5)

    # Exibe SKYBOX
    r = glm.vec3( 1.0, 1.0, 0.0 )
    t = glm.vec3( 0.0, -.5, 0.0 )
    s = glm.vec3( 500, 500, 500 )
    model_mat = gh.model( r, t, s, angle = 0)
    scene.drawModelbyName(program, "Sky", model_mat=model_mat, ka = 1, kd = 0)

    # Exibe GRASS
    r = glm.vec3( 1.0, 0.0, 0.0 )
    t = glm.vec3( 0.0, 0.0, 0.0 )
    s = glm.vec3( 0.5, 0.5, 0.5)
    model_mat = gh.model( r, t, s, angle = 0)
    scene.drawModelbyName(program, "Grass", model_mat=model_mat, ka = 0.5, kd = 0.7)

    # Exibe Sofa
    r = glm.vec3( 0.0, 1.0, 0.0 )
    t = glm.vec3( 1.0, 0.0, 0.0 )
    s = glm.vec3( 0.3, 0.3, 0.3)
    model_mat = gh.model( r, t, s, angle = -90)
    scene.drawModelbyName(program, "Sofa", model_mat=model_mat, ka = 0.7, kd = 0.7)

    # Exibe Chair
    r = glm.vec3( 0.0, 1.0, 0.0 )
    t = glm.vec3( 0.0, 0.0, -0.25 )
    s = glm.vec3( 0.07, 0.07, 0.07)
    model_mat = gh.model( r, t, s, angle = -90)
    scene.drawModelbyName(program, "Chair", model_mat=model_mat, ka = 0.7, kd = 0.7)
    
    # Exibe Chair
    r = glm.vec3( 0.0, 1.0, 0.0 )
    t = glm.vec3( 0.1, 0.0, 0.1 )
    s = glm.vec3( 0.07, 0.07, 0.07)
    model_mat = gh.model( r, t, s, angle = 210)
    scene.drawModelbyName(program, "Chair", model_mat=model_mat, ka = 0.7, kd = 0.7)

    # Exibe Chair
    r = glm.vec3( 0.0, 1.0, 0.0 )
    t = glm.vec3( -0.2, 0.0, 0.25 )
    s = glm.vec3( 0.07, 0.07, 0.07)
    model_mat = gh.model( r, t, s, angle = 90)
    scene.drawModelbyName(program, "Chair", model_mat=model_mat, ka = 0.7, kd = 0.7)

    # Exibe Mesa
    r = glm.vec3( 0.0, 1.0, 0.0 )
    t = glm.vec3( -0.1, 0.0, 0.0 )
    s = glm.vec3( 0.003, 0.003, 0.003)
    model_mat = gh.model( r, t, s, angle = 0)
    scene.drawModelbyName(program, "Table", model_mat=model_mat, ka = 0.7, kd = 0.7)

    # Exibe o Vanderley
    r = glm.vec3( 0.0, 1.0, 0.0 )
    t = glm.vec3( 0.5, 0.25, 3.0 )
    s = glm.vec3( 0.1, 0.1, 0.1)
    model_mat = gh.model( r, t, s, angle = 0)
    scene.drawModelbyName(program, "Man", model_mat=model_mat, ka = 0.7, kd = 0.7)

    # Exibe o Vanderley
    r = glm.vec3( 0.0, 1.0, 0.0 )
    t = glm.vec3( 0.3, 0.25, 0.0 )
    s = glm.vec3( 0.1, 0.1, 0.1)
    model_mat = gh.model( r, t, s, angle = 0)
    scene.drawModelbyName(program, "Man", model_mat=model_mat, ka = 0.7, kd = 0.7)

    # Exibe o Vanderley
    r = glm.vec3( 0.0, 1.0, 0.0 )
    t = glm.vec3( 0.0, 0.25, 3.0 )
    s = glm.vec3( 0.1, 0.1, 0.1)
    model_mat = gh.model( r, t, s, angle = 90)
    scene.drawModelbyName(program, "Man", model_mat=model_mat, ka = 0.7, kd = 0.7)

    # Exibe o Vanderley
    r = glm.vec3( 0.0, 1.0, 0.0 )
    t = glm.vec3( 0.1, 0.25, 2.8 )
    s = glm.vec3( 0.1, 0.1, 0.1)
    model_mat = gh.model( r, t, s, angle = 45)
    scene.drawModelbyName(program, "Man", model_mat=model_mat, ka = 0.7, kd = 0.7)

    # Exibe GRASS
    r = glm.vec3( 1.0, 0.0, 0.0 )
    t = glm.vec3( 0.0, 0.01, 0.0 )
    s = glm.vec3( 0.2, 0.2, 0.2)
    model_mat = gh.model( r, t, s, angle = 0)
    scene.drawModelbyName(program, "Concrete", model_mat=model_mat, ka = 0.5, kd = 0.7)



    mat_view = gh.view()
    loc_view = glGetUniformLocation(program, "view")
    glUniformMatrix4fv(loc_view, 1, GL_FALSE, mat_view)

    mat_projection = gh.projection()
    loc_projection = glGetUniformLocation(program, "projection")
    glUniformMatrix4fv(loc_projection, 1, GL_FALSE, mat_projection)

    loc_light_pos = glGetUniformLocation(program, "lightPos")  # recuperando localizacao da variavel lightPos na GPU
    glUniform3f(loc_light_pos, 10.0*math.cos(chron), 30.0, -10.0*math.sin(chron))  # posicao da fonte de luz

    glfw.swap_buffers(window)

glfw.terminate()
