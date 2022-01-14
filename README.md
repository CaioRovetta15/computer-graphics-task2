# computer-graphics-task2
Second group task for Computer Graphics subject using OpenGL tools.

## Install

The whole program was made in python3. Here is what you need to get to run our software:

```py
pip install numpy
pip install glfw
pip install pyopengl
```

And we execute by double clicking ``main.py`` or the terminal command ``python main.py`` 

## Execution

The program was a very interesting way to exercise OpenGL programming and to understand the way that everything is rendered in mostly computational screens.

First of all, when you start the program you will be inside the house, where you can see some forniture, like some chairs, a sofa, a table and a man:

![alt text](https://i.imgur.com/wRrG2nu.png)

On the outside you can see a police car chasing two outlaw cars while all of them dift near a group of people.


In the scene you can control the camera with the **WASD** keys and the mouse.
You can anter the "flight mode" by pressing the **F** key, witch enable you to leave the ground. While in the flight mode you can go up by pressing the **SPACE BAR** and go down pressing the **L SHIFT** key.
Besides that pressing the **P** key you enter the mesh view mode in witch you can see all the meshes without the textures.

![alt text](https://i.imgur.com/8PdQ7vL.gif)

## How it works?

This project were divided in two files:



### ``glhandler.py``

Holds all the specific OpenGL settings with the GPU buffer and the window. Sets the key bindings to the scene controls. It also reads all the Wavefront files and bind all textures.



### ``main.py``

Finally, this is the main file to use all those functions to set up the scene. The processes can be simplified to: Set the window; Load files and textures; Set the GPU; Transform and draw all the meshes.
