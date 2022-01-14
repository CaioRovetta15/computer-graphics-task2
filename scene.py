import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import glm
import numpy as np

from PIL import Image

class Object:
    def __init__(self):
        # indices para desenhar
        self.name = ""
        self.model_id = None
        self.begin_ind = None
        self.end_ind = None
        # indice da textura
        self.texture_id = None
        # transformação
        self.model_mat = glm.mat4(1.0)
        self.ka = 0.7
        self.kd = 0.7
    
    def drawModel(self, program):

        # define id da textura do modelo
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        loc_ka = glGetUniformLocation(program, "ka")  # recuperando localizacao da variavel ka na GPU
        glUniform1f(loc_ka, self.ka)  # envia ka pra gpu

        loc_kd = glGetUniformLocation(program, "kd")  # recuperando localizacao da variavel ka na GPU
        glUniform1f(loc_kd, self.kd)  # envia kd pra gpu
        loc_model = glGetUniformLocation(program, "model")
        glUniformMatrix4fv(loc_model, 1, GL_TRUE, self.model_mat)
        glDrawArrays(GL_TRIANGLES, self.begin_ind, self.end_ind-self.begin_ind+1)
    
class Scene:
    def __init__(self):
        self.vertices_list = list()
        self.textures_coord_list = list()
        self.normals_list = list()
        
        self.objects = list()
    
    def appendModel(self, name, mesh, texture):
        
        obj = Object()
        obj.name = name
        # model_id guarda o número do objeto.
        # se existir apenas 1 objeto, o model_id do objeto anterior é 0 e do novo é 1. 
        obj.model_id = len(self.objects) 
        obj.texture_id = len(self.objects)
        obj.begin_ind = len(self.vertices_list)

        self.load_texture_from_file(obj.texture_id, texture)
        modelo = self.load_model_from_file(mesh)

        # inserindo vertices do modelo no vetor de vertices
        for face in modelo['faces']:
            for vertice_id in face[0]:
                self.vertices_list.append(modelo['vertices'][vertice_id-1])
            for texture_id in face[1]:
                self.textures_coord_list.append(modelo['texture'][texture_id-1])
            for normal_id in face[2]:
                self.normals_list.append(modelo['normals'][normal_id-1])
        
        obj.end_ind = len(self.vertices_list) - 1

        self.objects.append(obj)

    def load_model_from_file(self, filename):
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

    def load_texture_from_file(self, texture_id, img_textura):

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
    
    def getVTN(self):

        vertices = np.zeros(len(self.vertices_list), [("position", np.float32, 3)])
        vertices['position'] = self.vertices_list

        textures = np.zeros(len(self.textures_coord_list), [("position", np.float32, 2)])  # duas coordenadas
        textures['position'] = self.textures_coord_list

        # Dados de iluminação: vetores normais
        normals = np.zeros(len(self.normals_list), [("position", np.float32, 3)])  # três coordenadas
        normals['position'] = self.normals_list

        return vertices, textures, normals
    
    def drawModelbyName(self, program, name, model_mat = glm.mat4(1.0), ka = 0.7, kd = 0.7):
        
        model_mat = np.array(model_mat)
        for obj in self.objects:
            if obj.name == name:
                obj.ka = ka
                obj.kd = kd
                obj.model_mat = model_mat
                obj.drawModel(program)
    

