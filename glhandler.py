
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

def setWindow(width, height, name):

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

def load_model_from_file(filename):
    """Loads a Wavefront OBJ file. """
    objects = {}
    vertices = []
    normals = []
    texture_coords = []
    faces = []

    material = None

    # abre o arquivo obj para leitura
    for line in open(filename, "r"):  # para cada linha do arquivo .obj
        if line.startswith('#'):
            continue  # ignora comentarios
        values = line.split()  # quebra a linha por espaço
        if not values:
            continue

        # recuperando vertices
        if values[0] == 'v':
            vertices.append(values[1:4])

        # recuperando vertices
        if values[0] == 'vn':
            normals.append(values[1:4])

        # recuperando coordenadas de textura
        elif values[0] == 'vt':
            texture_coords.append(values[1:3])

        # recuperando faces
        elif values[0] in ('usemtl', 'usemat'):
            material = values[1]
        elif values[0] == 'f':
            face = []
            face_texture = []
            face_normals = []
            for v in values[1:]:
                w = v.split('/')
                face.append(int(w[0]))
                face_normals.append(int(w[2]))
                if len(w) >= 2 and len(w[1]) > 0:
                    face_texture.append(int(w[1]))
                else:
                    face_texture.append(0)

            faces.append((face, face_texture, face_normals, material))

    model = {}
    model['vertices'] = vertices
    model['texture'] = texture_coords
    model['faces'] = faces
    model['normals'] = normals

    return model

def load_texture_from_file(texture_id, img_textura):
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    img = Image.open(img_textura)
    img_width = img.size[0]
    img_height = img.size[1]
    image_data = img.tobytes("raw", "RGB", 0, -1)
    #image_data = np.array(list(img.getdata()), np.uint8)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_width, img_height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

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
    glUniform3f(loc_light_pos, -1.5, 1.7, 2.5)  # posicao da fonte de luz

    return loc_light_pos

# dt_x, dt_y = 0, 0
# dtheta = 0

# # Catching keyboard events 
# def key_event(window,key,scancode,action,mods):
    
#     # Ship states
#     global dt_x, dt_y, dtheta
#     if action!=0:
#         if (key == 265) | (key == 87):
#             dt_y = +0.02
#         if (key == 264) | (key == 83):
#             dt_y = -0.02
#         if (key == 263) | (key == 65):
#             dt_x = -0.02
#         if (key == 262) | (key == 68):
#             dt_x = +0.02
#         if (key == 81):
#             dtheta = +0.1
#         if (key == 69):
#             dtheta = -0.1

#     print('[key event] key=',key)
#     print('[key event] scancode=',scancode)
#     print('[key event] action=',action)
#     print('[key event] mods=',mods)
#     print('-------')

# # Catching mouse events
# def mouse_event(window,button,action,mods):
#     print('[mouse event] button=',button)
#     print('[mouse event] action=',action)
#     print('[mouse event] mods=',mods)
#     print('-------')




