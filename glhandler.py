
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

# Posicao inicial do jogador
cameraPos,cameraFront,cameraUp = glm.vec3(.2,.43,.7),glm.vec3(0,0,1),glm.vec3(0,1,0)

# Opcoes especiais inicialmente desativadas
polygonal_mode = False
flyMode = False
isRightButtonPressed =  False

# Coef de Reflexao e Difusao padrao
ka_inc, kd_inc = 0.5, 0.5

# Tamanho base de janela
altura = 350
largura = 350

firstMouse = True

yaw, pitch = 90.0, 0.0
FOV = 90
lastX, lastY = largura/2, altura/2

# Configura os limites do cenario
heightMinLimit = .43
heightMaxLimit = 10
scenaryLimit = 15

def setWindow(height, width, name):

    altura, largura = height, width
    glfw.init()
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    window = glfw.create_window(width, height, name, None, None)
    glfw.make_context_current(window)

    return window

def setGPU():

    vertex_code = """
            attribute vec3 position;
            attribute vec2 texture_coord;
            attribute vec3 normals;
           
            varying vec2 out_texture;
            varying vec3 out_fragPos;
            varying vec3 out_normal;
                    
            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;        
            
            void main(){
                gl_Position = projection * view * model * vec4(position,1.0);
                out_texture = vec2(texture_coord);
                out_fragPos = vec3(position);
                out_normal = normals;
            }
            """

    fragment_code = """
            uniform vec3 lightPos; // define coordenadas de posicao da luz
            uniform float ka; // coeficiente de reflexao ambiente
            uniform float kd; // coeficiente de reflexao difusa
            
            vec3 lightColor = vec3(1.0, 1.0, 1.0);

            varying vec2 out_texture; // recebido do vertex shader
            varying vec3 out_normal; // recebido do vertex shader
            varying vec3 out_fragPos; // recebido do vertex shader
            uniform sampler2D samplerTexture;
             
            void main(){
                vec3 ambient = ka * lightColor;             
            
                vec3 norm = normalize(out_normal); // normaliza vetores perpendiculares
                vec3 lightDir = normalize(lightPos - out_fragPos); // direcao da luz
                float diff = max(dot(norm, lightDir), 0.0); // verifica limite angular (entre 0 e 90)
                vec3 diffuse = kd * diff * lightColor; // iluminacao difusa
                
                vec4 texture = texture2D(samplerTexture, out_texture);
                vec4 result = vec4((ambient + diffuse),1.0) * texture; // aplica iluminacao
                gl_FragColor = result;

            }
            """

    # Requisitando slot para a GPU para nossos programas Vertex e Fragment Shaders

    # Request a program and shader slots from GPU
    program = glCreateProgram()
    vertex = glCreateShader(GL_VERTEX_SHADER)
    fragment = glCreateShader(GL_FRAGMENT_SHADER)

    # Associando nosso código-fonte aos slots solicitados

    # Set shaders source
    glShaderSource(vertex, vertex_code)
    glShaderSource(fragment, fragment_code)

    # Compilando o Vertex Shader
    # Se há algum erro em nosso programa Vertex Shader, nosso app para por aqui.

    # Compile shaders
    glCompileShader(vertex)
    if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(vertex).decode()
        print(error)
        raise RuntimeError("Erro de compilacao do Vertex Shader")

    # Compilando o Fragment Shader
    # Se há algum erro em nosso programa Fragment Shader, nosso app para por aqui.

    glCompileShader(fragment)
    if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(fragment).decode()
        print(error)
        raise RuntimeError("Erro de compilacao do Fragment Shader")

    # Associando os programas compilado ao programa principal

    # Attach shader objects to the program
    glAttachShader(program, vertex)
    glAttachShader(program, fragment)

    # Linkagem do programa

    # Build program
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        print(glGetProgramInfoLog(program))
        raise RuntimeError('Linking error')

    # Make program the default program
    glUseProgram(program)

    return program

def setGPUBuffer(program, vertices, textures, normals):

    # Request a buffer slot from GPU
    buffer = glGenBuffers(3)

    # Upload vertices data
    glBindBuffer(GL_ARRAY_BUFFER, buffer[0])
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    stride = vertices.strides[0]
    offset = ctypes.c_void_p(0)
    loc_vertices = glGetAttribLocation(program, "position")
    glEnableVertexAttribArray(loc_vertices)
    glVertexAttribPointer(loc_vertices, 3, GL_FLOAT, False, stride, offset)

    # Upload texture data
    glBindBuffer(GL_ARRAY_BUFFER, buffer[1])
    glBufferData(GL_ARRAY_BUFFER, textures.nbytes, textures, GL_STATIC_DRAW)
    stride = textures.strides[0]
    offset = ctypes.c_void_p(0)
    loc_texture_coord = glGetAttribLocation(program, "texture_coord")
    glEnableVertexAttribArray(loc_texture_coord)
    glVertexAttribPointer(loc_texture_coord, 2, GL_FLOAT, False, stride, offset)

    # Upload normals data
    glBindBuffer(GL_ARRAY_BUFFER, buffer[2])
    glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
    stride = normals.strides[0]
    offset = ctypes.c_void_p(0)
    loc_normals_coord = glGetAttribLocation(program, "normals")
    glEnableVertexAttribArray(loc_normals_coord)
    glVertexAttribPointer(loc_normals_coord, 3, GL_FLOAT, False, stride, offset)

    #  Dados de iluminação: posição da fonte de luz
    loc_light_pos = glGetUniformLocation(program, "lightPos")  # recuperando localizacao da variavel lightPos na GPU
    glUniform3f(loc_light_pos, 10.0, 30.0, -10.0)  # posicao da fonte de luz

def model( r, t, s, angle = 0):

    angle = math.radians(angle)

    matrix_transform = glm.mat4(1.0)  # instanciando uma matriz identidade

    # translacao
    matrix_transform = glm.translate(matrix_transform, t )

    # eixo de rotacao + angulo
    matrix_transform = glm.rotate(matrix_transform, angle, r )

    # escala
    matrix_transform = glm.scale(matrix_transform, s )

    matrix_transform = np.array(matrix_transform)  # pegando a transposta da matriz (glm trabalha com ela invertida)

    return matrix_transform

def view():
    global cameraPos, cameraFront, cameraUp
    mat_view = glm.lookAt(cameraPos, cameraPos + cameraFront, cameraUp)
    mat_view = np.array(mat_view).T
    return mat_view

def projection():
    global altura, largura, FOV

    # perspective parameters: fovy, aspect, near, far
    mat_projection = glm.perspective(glm.radians(FOV), largura/altura, 0.01, 1000.0)
    mat_projection = np.array(mat_projection).T
    return mat_projection

def draw_model(program, mat_model, ka, kd, begin, end, texture_id):
    global ka_inc, kd_inc

    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)

    # define parametros de ilumincao do modelo
    ka += ka_inc  # coeficiente de reflexao ambiente do modelo
    kd += kd_inc  # coeficiente de reflexao difusa do modelo

    loc_ka = glGetUniformLocation(program, "ka")  # recuperando localizacao da variavel ka na GPU
    glUniform1f(loc_ka, ka)  # envia ka pra gpu

    loc_kd = glGetUniformLocation(program, "kd")  # recuperando localizacao da variavel ka na GPU
    glUniform1f(loc_kd, kd)  # envia kd pra gpu

    # define id da textura do modelo
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # desenha o modelo
    glDrawArrays(GL_TRIANGLES, begin, end)  # renderizando

def key_event(window, key, scancode, action, mods):
    global flyMode
    global ka_inc, kd_inc
    global cameraPos, cameraFront, cameraUp
    global polygonal_mode
    global FOV

    cameraSpeed = 0.06

    # TECLA S - Anda para frente
    if key == 87 and (action == 1 or action == 2):  # tecla W
        if not flyMode:
            aux = cameraSpeed * cameraFront
            aux = glm.vec3(aux.x, 0, aux.z)
            cameraPos += aux
        else:
            cameraPos += cameraSpeed * cameraFront
            if cameraPos.y < heightMinLimit : cameraPos.y = heightMinLimit
            if cameraPos.y > heightMaxLimit : cameraPos.y = heightMaxLimit

        # Limitacao de cenario ( parede invisivel )
        if cameraPos.x < -scenaryLimit : cameraPos.x = scenaryLimit
        if cameraPos.x > scenaryLimit : cameraPos.x = scenaryLimit
        if cameraPos.z < -scenaryLimit : cameraPos.z = scenaryLimit
        if cameraPos.z > scenaryLimit : cameraPos.z = scenaryLimit

    # TECLA S - Anda para atras
    if key == 83 and (action == 1 or action == 2):  # tecla S
        if not flyMode:
            aux = cameraSpeed * cameraFront
            aux = glm.vec3(aux.x, 0, aux.z)
            cameraPos -= aux
        else:
            cameraPos -= cameraSpeed * cameraFront
            if cameraPos.y < heightMinLimit : cameraPos.y = heightMinLimit
            if cameraPos.y > heightMaxLimit : cameraPos.y = heightMaxLimit
        
        # Limitacao de cenario ( parede invisivel )
        if cameraPos.x < -scenaryLimit : cameraPos.x = scenaryLimit
        if cameraPos.x > scenaryLimit : cameraPos.x = scenaryLimit
        if cameraPos.z < -scenaryLimit : cameraPos.z = scenaryLimit
        if cameraPos.z > scenaryLimit : cameraPos.z = scenaryLimit

    # TECLA A - Anda para a esquerda
    if key == 65 and (action == 1 or action == 2): 
        cameraPos -= glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed
        # Limitacao de cenario ( parede invisivel )
        if cameraPos.x < -scenaryLimit : cameraPos.x = scenaryLimit
        if cameraPos.x > scenaryLimit : cameraPos.x = scenaryLimit
        if cameraPos.z < -scenaryLimit : cameraPos.z = scenaryLimit
        if cameraPos.z > scenaryLimit : cameraPos.z = scenaryLimit

    # TECLA D - Anda para a direita
    if key == 68 and (action == 1 or action == 2):  
        cameraPos += glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed
        # Limitacao de cenario ( parede invisivel )
        if cameraPos.x < -scenaryLimit : cameraPos.x = scenaryLimit
        if cameraPos.x > scenaryLimit : cameraPos.x = scenaryLimit
        if cameraPos.z < -scenaryLimit : cameraPos.z = scenaryLimit
        if cameraPos.z > scenaryLimit : cameraPos.z = scenaryLimit

    # TECLA P - Ativa e desativa Visualizador de Malhas
    if key == 80 and action == 1 and polygonal_mode == True:
        polygonal_mode = False
    else:
        if key == 80 and action == 1 and polygonal_mode == False:
            polygonal_mode = True

    # TECLA F - Ativa e desativa modo FLY
    if key == 70 and action == 1 and flyMode == True:
        flyMode = False
    else:
        if key == 70 and action == 1 and flyMode == False:
            flyMode = True

    # TECLA UP - Aumenta o FOV
    if key == 265 and (action == 1 or action == 2):  # tecla cima
        FOV += 0.5
        if FOV < 30 : FOV = 30
        if FOV > 120 : FOV = 120

    # TECLA DOWN -  Diminui o FOV
    if key == 264 and (action == 1 or action == 2):  # tecla baixo
        FOV -= 0.5
        if FOV < 30 : FOV = 30
        if FOV > 120 : FOV = 120

    # TECLA SPACE - Voa para cima
    if key == 32 and (action == 1 or action == 2) and flyMode:  # tecla espaco
        cameraPos += cameraSpeed * cameraUp
        if cameraPos.y < heightMinLimit : cameraPos.y = heightMinLimit
        if cameraPos.y > heightMaxLimit : cameraPos.y = heightMaxLimit

    # TECLA LSHIFT - Voa para baixo
    if key == 340 and (action == 1 or action == 2) and flyMode:  # tecla shift direito
        cameraPos -= cameraSpeed * cameraUp 
        if cameraPos.y < heightMinLimit : cameraPos.y = heightMinLimit
        if cameraPos.y > heightMaxLimit : cameraPos.y = heightMaxLimit

def mouse_event(window, xpos, ypos):
    global firstMouse, yaw, pitch, lastX, lastY, isRightButtonPressed, cameraFront
    if firstMouse:
        lastX = xpos
        lastY = ypos
        firstMouse = False

    if not isRightButtonPressed:
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

    # Movimentacao invertida ( efeito scroll/touchscreen )
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
