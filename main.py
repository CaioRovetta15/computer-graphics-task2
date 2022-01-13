
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
from glhandler import *
from PIL import Image

# Inicializando janela
altura = 960
largura = 1280
window = setWindow(largura, altura, "Trabalho 2")

program = setGPU()

glEnable(GL_TEXTURE_2D)
qtd_texturas = 10
textures = glGenTextures(qtd_texturas)

# A lista abaixo armazena todos os vertices carregados dos arquivos

vertices_list = []
normals_list = []
textures_coord_list = []

# Vamos carregar cada modelo e definir funções para desenhá-los

modelo = load_model_from_file('caixa2.obj')

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

load_texture_from_file(0, 'caixa_madeira.jpg')

vertices = np.zeros(len(vertices_list), [("position", np.float32, 3)])
vertices['position'] = vertices_list

textures = np.zeros(len(textures_coord_list), [("position", np.float32, 2)])  # duas coordenadas
textures['position'] = textures_coord_list

# Dados de iluminação: vetores normais
normals = np.zeros(len(normals_list), [("position", np.float32, 3)])  # três coordenadas
normals['position'] = normals_list

#  Enviando coordenadas de vértices, texturas e dados de iluminacao para a GPU
loc_light_pos = setGPUBuffer(program, vertices, textures, normals)

def desenha_caixa():

    # aplica a matriz model
    angle = 45.0

    # rotacao
    r_x, r_y, r_z = 1.0, 1.0, 0.0

    # translacao
    t_x, t_y, t_z = 0.0, 0.0, 0.0

    # escala
    s_x, s_y, s_z = 0.1, 0.1, 0.1

    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)

    # define parametros de ilumincao do modelo
    ka = ka_inc  # coeficiente de reflexao ambiente do modelo
    kd = kd_inc  # coeficiente de reflexao difusa do modelo

    loc_ka = glGetUniformLocation(program, "ka")  # recuperando localizacao da variavel ka na GPU
    glUniform1f(loc_ka, ka)  # envia ka pra gpu

    loc_kd = glGetUniformLocation(program, "kd")  # recuperando localizacao da variavel ka na GPU
    glUniform1f(loc_kd, kd)  # envia kd pra gpu

    # define id da textura do modelo
    glBindTexture(GL_TEXTURE_2D, 0)

    # desenha o modelo
    glDrawArrays(GL_TRIANGLES, 0, 36)  # renderizando

cameraPos = glm.vec3(0.0,  0.0,  1.0)
cameraFront = glm.vec3(0.0,  0.0, -1.0)
cameraUp = glm.vec3(0.0,  1.0,  0.0)

polygonal_mode = False

ka_inc = 0.3
kd_inc = 0.5

def key_event(window, key, scancode, action, mods):
    global cameraPos, cameraFront, cameraUp, polygonal_mode
    global ka_inc, kd_inc

    cameraSpeed = 0.05
    if key == 87 and (action == 1 or action == 2):  # tecla W
        cameraPos += cameraSpeed * cameraFront

    if key == 83 and (action == 1 or action == 2):  # tecla S
        cameraPos -= cameraSpeed * cameraFront

    if key == 65 and (action == 1 or action == 2):  # tecla A
        cameraPos -= glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed

    if key == 68 and (action == 1 or action == 2):  # tecla D
        cameraPos += glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed

    if key == 80 and action == 1 and polygonal_mode == True:
        polygonal_mode = False
    else:
        if key == 80 and action == 1 and polygonal_mode == False:
            polygonal_mode = True

    if key == 265 and (action == 1 or action == 2):  # tecla cima
        ka_inc += 0.05

    if key == 264 and (action == 1 or action == 2):  # tecla baixo
        kd_inc += 0.05


firstMouse = True
isRightButtonPressed = False
yaw = -90.0
pitch = 0.0
lastX = largura/2
lastY = altura/2

def mouse_event(window, xpos, ypos):
    global firstMouse, cameraFront, yaw, pitch, lastX, lastY, isRightButtonPressed
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
    cameraFront = glm.normalize(front)

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

# Matrizes Model, View e Projection
# Teremos uma aula específica para entender o seu funcionamento.

def model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z):

    angle = math.radians(angle)

    matrix_transform = glm.mat4(1.0)  # instanciando uma matriz identidade

    # aplicando rotacao
    matrix_transform = glm.rotate(matrix_transform, angle, glm.vec3(r_x, r_y, r_z))

    # aplicando translacao
    matrix_transform = glm.translate(matrix_transform, glm.vec3(t_x, t_y, t_z))

    # aplicando escala
    matrix_transform = glm.scale(matrix_transform, glm.vec3(s_x, s_y, s_z))

    matrix_transform = np.array(matrix_transform).T  # pegando a transposta da matriz (glm trabalha com ela invertida)

    return matrix_transform

def view():
    global cameraPos, cameraFront, cameraUp
    mat_view = glm.lookAt(cameraPos, cameraPos + cameraFront, cameraUp)
    mat_view = np.array(mat_view).T
    return mat_view


def projection():
    global altura, largura
    # perspective parameters: fovy, aspect, near, far
    mat_projection = glm.perspective(glm.radians(90.0), largura/altura, 0.1, 1000.0)
    mat_projection = np.array(mat_projection).T
    return mat_projection

# Nesse momento, exibimos a janela.
glfw.show_window(window)
glfw.set_cursor_pos(window, lastX, lastY)

# Loop principal da janela.
# Enquanto a janela não for fechada, esse laço será executado. É neste espaço que trabalhamos com algumas interações com a OpenGL.

glEnable(GL_DEPTH_TEST)  # importante para 3D

ang = 0.0

while not glfw.window_should_close(window):

    glfw.poll_events()

    ang += 0.005

    glUniform3f(loc_light_pos, math.cos(ang)*4, 0.0, math.sin(ang)*4)  # posicao da fonte de luz

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glClearColor(0.2, 0.2, 0.2, 1.0)

    if polygonal_mode == True:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    if polygonal_mode == False:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    desenha_caixa()

    mat_view = view()
    loc_view = glGetUniformLocation(program, "view")
    glUniformMatrix4fv(loc_view, 1, GL_FALSE, mat_view)

    mat_projection = projection()
    loc_projection = glGetUniformLocation(program, "projection")
    glUniformMatrix4fv(loc_projection, 1, GL_FALSE, mat_projection)

    glfw.swap_buffers(window)

glfw.terminate()