
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

glEnable(GL_TEXTURE_2D)
qtd_texturas = 10
textures = glGenTextures(qtd_texturas)

# A lista abaixo armazena todos os vertices carregados dos arquivos

vertices_list = []
normals_list = []
textures_coord_list = []

# Vamos carregar cada modelo e definir funções para desenhá-los

modelo = gh.load_model_from_file('3dFiles/')

# inserindo vertices do modelo no vetor de vertices
print('Processando modelo cube.obj. Vertice inicial:', len(vertices_list))
for face in modelo['faces']:
    for vertice_id in face[0]:
        vertices_list.append(modelo['vertices'][vertice_id-1])
    for texture_id in face[1]:
        textures_coord_list.append(modelo['texture'][texture_id-1])
    for normal_id in face[2]:
        normals_list.append(modelo['normals'][normal_id-1])
print('Processando modelo cube.obj. Vertice final:', len(vertices_list))

gh.load_texture_from_file(0, 'Car_1.png')

vertices = np.zeros(len(vertices_list), [("position", np.float32, 3)])
vertices['position'] = vertices_list

textures = np.zeros(len(textures_coord_list), [("position", np.float32, 2)])  # duas coordenadas
textures['position'] = textures_coord_list

# Dados de iluminação: vetores normais
normals = np.zeros(len(normals_list), [("position", np.float32, 3)])  # três coordenadas
normals['position'] = normals_list

#  Enviando coordenadas de vértices, texturas e dados de iluminacao para a GPU
gh.setGPUBuffer(program, vertices, textures, normals)

firstMouse, isRightButtonPressed = True, False
yaw, pitch = -90.0, 0.0
lastX, lastY = gh.largura/2, gh.altura/2

def key_event(window, key, scancode, action, mods):

    cameraSpeed = 0.05
    if key == 87 and (action == 1 or action == 2):  # tecla W
        gh.cameraPos += cameraSpeed * gh.cameraFront

    if key == 83 and (action == 1 or action == 2):  # tecla S
        gh.cameraPos -= cameraSpeed * gh.cameraFront

    if key == 65 and (action == 1 or action == 2):  # tecla A
        gh.cameraPos -= glm.normalize(glm.cross(gh.cameraFront, gh.cameraUp)) * cameraSpeed

    if key == 68 and (action == 1 or action == 2):  # tecla D
        gh.cameraPos += glm.normalize(glm.cross(gh.cameraFront, gh.cameraUp)) * cameraSpeed

    if key == 80 and action == 1 and gh.polygonal_mode == True:
        gh.polygonal_mode = False
    else:
        if key == 80 and action == 1 and gh.polygonal_mode == False:
            gh.polygonal_mode = True

    if key == 265 and (action == 1 or action == 2):  # tecla cima
        gh.ka_inc += 0.05

    if key == 264 and (action == 1 or action == 2):  # tecla baixo
        gh.kd_inc += 0.05

def mouse_event(window, xpos, ypos):
    global firstMouse, yaw, pitch, lastX, lastY, isRightButtonPressed
    if firstMouse :
        lastX = xpos
        lastY = ypos
        firstMouse = False

    if not isRightButtonPressed : 
        lastX = xpos
        lastY = ypos
        return

    xoffset = xpos - lastX
    yoffset = lastY - ypos
    lastX = xpos
    lastY = ypos

    sensitivity = 0.15
    xoffset *= sensitivity
    yoffset *= sensitivity

    yaw -= xoffset
    pitch -= yoffset

    if pitch >= 90.0:
        pitch = 90.0
    if pitch <= -90.0:
        pitch = -90.0

    front = glm.vec3()
    front.x = math.cos(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    front.y = math.sin(glm.radians(pitch))
    front.z = math.sin(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    gh.cameraFront = glm.normalize(front)

def mouse_button_callback(window, button, action, mods):

    global isRightButtonPressed

    if button == 0 and action == 1:
        isRightButtonPressed = True
        print("Right button clicked")
    if button == 0 and action == 0:
        isRightButtonPressed = False
        print("Right button released")

glfw.set_key_callback(window, key_event)
glfw.set_cursor_pos_callback(window, mouse_event)
glfw.set_mouse_button_callback(window, mouse_button_callback)

# Nesse momento, exibimos a janela.
glfw.show_window(window)
glfw.set_cursor_pos(window, lastX, lastY)

glEnable(GL_DEPTH_TEST)  # importante para 3D

ang = 0.0

loc_light_pos = glGetUniformLocation(program, "lightPos")  # recuperando localizacao da variavel lightPos na GPU
glUniform3f(loc_light_pos, -1.5, 1.7, 2.5)  # posicao da fonte de luz

while not glfw.window_should_close(window):

    glfw.poll_events()

    ang += 0.005

    glUniform3f(loc_light_pos, 4, 0.0, 4)  # posicao da fonte de luz

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glClearColor(0.2, 0.2, 0.2, 1.0)

    if gh.polygonal_mode == True:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    if gh.polygonal_mode == False:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    gh.desenha_caixa(program, 0, len(vertices))

    mat_view = gh.view()
    loc_view = glGetUniformLocation(program, "view")
    glUniformMatrix4fv(loc_view, 1, GL_FALSE, mat_view)

    mat_projection = gh.projection()
    loc_projection = glGetUniformLocation(program, "projection")
    glUniformMatrix4fv(loc_projection, 1, GL_FALSE, mat_projection)

    glfw.swap_buffers(window)

glfw.terminate()