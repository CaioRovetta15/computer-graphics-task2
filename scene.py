import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import glm

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
        self.model = glm.mat4(1.0)
    
    def draw_model(self):
        glDrawArrays(GL_TRIANGLE, self.begin_ind, self.end_ind)
    
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
        # se existir apenas 1 objeto, o model_id desse objeto é 0. 
        obj.model_id = len(self.objects) - 1
        obj.texture_id = len(self.objects) - 1
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