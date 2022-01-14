
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


# Inicializando janela

window = gh.setWindow(960, 1280, "Trabalho 2")

program = gh.setGPU()

loc_color = glGetUniformLocation(program, "color")

glEnable(GL_TEXTURE_2D)
qtd_texturas = 10
textures = glGenTextures(qtd_texturas)

# A lista abaixo armazena todos os vertices carregados dos arquivos

vertices_list = []
normals_list = []
textures_coord_list = []

# Vamos carregar cada modelo e definir funções para desenhá-los

modelo = gh.load_model_from_file('3dFiles/house/house2.obj')

# inserindo vertices do modelo no vetor de vertices
for face in modelo['faces']:
    for vertice_id in face[0]:
        vertices_list.append(modelo['vertices'][vertice_id-1])
    for texture_id in face[1]:
        textures_coord_list.append(modelo['texture'][texture_id-1])
    for normal_id in face[2]:
        normals_list.append(modelo['normals'][normal_id-1])
print('Processando modelo cube.obj. Vertice final:', len(vertices_list))
size_of_house = len(vertices_list)

gh.load_texture_from_file(0, '3dFiles/house/wood.png')

modelo = gh.load_model_from_file('3dFiles/exterior/outlaw car/outlaw.obj')
for face in modelo['faces']:
    for vertice_id in face[0]:
        vertices_list.append(modelo['vertices'][vertice_id-1])
    for texture_id in face[1]:
        textures_coord_list.append(modelo['texture'][texture_id-1])
    for normal_id in face[2]:
        normals_list.append(modelo['normals'][normal_id-1])
print('Processando modelo cube.obj. Vertice final:', len(vertices_list))

gh.load_texture_from_file(1, '3dFiles/exterior/outlaw car/Car Texture 1.png')
size_of_car = len(vertices_list)-size_of_house

vertices = np.zeros(4+len(vertices_list), [("position", np.float32, 3)])
vertices_list.append( (+0.5, 0, -0.8) )
vertices_list.append( (+0.5, 0, +0.8) )
vertices_list.append( (-0.5, 0, -0.8) )
vertices_list.append( (-0.5, 0, +0.8) )

vertices['position'] = vertices_list

textures = np.zeros(len(textures_coord_list), [("position", np.float32, 2)])  # duas coordenadas
textures['position'] = textures_coord_list

# Dados de iluminação: vetores normais
normals = np.zeros(len(normals_list), [("position", np.float32, 3)])  # três coordenadas
normals['position'] = normals_list

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

    gh.draw_model(program, 0, size_of_house, 0)

    gh.draw_model(program, size_of_house, size_of_car, 1)

    mat_model = gh.model(0, 1, 1, 0, 0, -.1, 0, 50, 50, 50)
    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)
    R, G, B = 1, 0, 0
    glUniform4f(loc_color, R, G, B, 1.0)
    glDrawArrays(GL_TRIANGLE_STRIP, size_of_car+size_of_house, len(vertices))

    mat_view = gh.view()
    loc_view = glGetUniformLocation(program, "view")
    glUniformMatrix4fv(loc_view, 1, GL_FALSE, mat_view)

    mat_projection = gh.projection()
    loc_projection = glGetUniformLocation(program, "projection")
    glUniformMatrix4fv(loc_projection, 1, GL_FALSE, mat_projection)

    glfw.swap_buffers(window)

glfw.terminate()
