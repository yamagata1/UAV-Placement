from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
from PIL.Image import *
import common
import sys
import shaderProg
import loadtexture
import numpy as ny
import particle
from get_location import UAV_path_list,user_path_list

window = None


#UAV覆盖半径
UAVradius = 30
# 飞机高度
plane_height = 2.6
# 地图长宽
plane_size = 110

plane_list = []
people_list = []

#用户初始位置，从user_path_list中读取
for index, i in enumerate(user_path_list):
    people_list.append(common.sphere(16, 16, 0.1, i[0] / 120 - 5, i[1] / 120 - 5))

# 用户数量
people_num = len(user_path_list)

camera = common.camera()
# 地形
plane = common.plane(plane_size,plane_size,0.1,0.1)
#the shaderall,colorMap,hightMap Should be placed after gl init,otherwise all 0
shaderall = None
tf = None
ps = None
colorMap = 0 
hightMap = 0
x = 0
z = 0


#users 用户位置list UAVs 无人机位置list
def planningUAV(users,UAVs):
    pass

def distance(a,b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

#center 当前中心点
#firstL 第一优先级的点的list 函数被调用前为 必须被 覆盖 调用后为已覆盖
#secondL 第二优先级的点的list 尽可能多 覆盖
def localCover(center,firstL,secondL):
    #UAV覆盖半径
    global UAVradius
    #循环直到secondL为空或return
    while secondL:
        for second in secondL.copy():
            for first in firstL:
                #距离大于2倍半径 无法覆盖
                if distance(second,first) > 2 * UAVradius:
                    secondL.remove(second)
        for user in secondL.copy():
            #能够被覆盖
            if distance(user,center) < UAVradius:
                firstL.append(user)
                secondL.remove(user)

        #不需要排序，因为每次调用oneCenter后center位置会改变
        min = float('inf')
        k = None
        t = 0
        for user in secondL:
            t = distance(user,u)
            if t < min:
                k = user
                min = t

        #此时k为距离center最近的点
        firstL.append(k)
        #先将k放入firstL中，调用oneCenter尝试观察：能否将firstL全部覆盖
        if oneCenter(firstL,center):
            #此时k已在firstL中，把k从secondL中删去，继续循环
            secondL.remove(k)
        else:
            #无法满足当前条件，将k从firstL中删去，返回
            firstL.remove(k)
            return

#解决凸包问题
#outs 凸包位置list
def convexHull(users,outs):
    pass

def oneCenter(users,center):
    pass



def make_plane(plane):
    plane.move_active += 1
    if plane.move_active == 250:
        plane.move_active = 0
        plane.x_speed = 0
        plane.z_speed = 0
    # 程序对象program作为当前渲染状态的一部分
    x1 = plane.x
    z1 = plane.z
    x1 += plane.x_speed
    z1 += plane.z_speed
    plane.change(x1, z1)

    # 高度关联
    # glUniform
    # location：指明要更改的uniform变量的位置
    # v0, v1, v2, v3：指明在指定的uniform变量中要使用的新值
    # 利用x, y坐标确认高度
    glUniform1f(shaderall.updateProgram.xl, 0)
    glUniform1f(shaderall.updateProgram.yl, 0)
    # 补偿高度
    glUniform1f(shaderall.updateProgram.sphereRadius, plane_height)
    glUniform1i(shaderall.updateProgram.tex0, 1)
    glUniform2f(shaderall.updateProgram.xz, 0, 0)
    getMVP(x1, z1)
    plane.draw()

def make_people(people):
    people.move_active += 1
    if people.move_active == 250:
        people.move_active = 0
        people.x_speed = 0
        people.z_speed = 0
    # 程序对象program作为当前渲染状态的一部分
    x1 = people.x
    z1 = people.z
    x1 += people.x_speed
    z1 += people.z_speed
    people.change(x1, z1)
    # 高度关联
    # glUniform
    # location：指明要更改的uniform变量的位置
    # v0, v1, v2, v3：指明在指定的uniform变量中要使用的新值
    # 利用x, y坐标确认高度
    glUniform1f(shaderall.updateProgram.xl, plane.xl)
    glUniform1f(shaderall.updateProgram.yl, plane.yl)
    # 补偿半径
    glUniform1f(shaderall.updateProgram.sphereRadius, people.radius)
    glUniform1i(shaderall.updateProgram.tex0, 1)
    glUniform2f(shaderall.updateProgram.xz, x1, z1)
    getMVP(x1, z1)
    people.draw()

def plane_move(plane, x, z):
    plane.move_active += 1
    if plane.move_active == 250:
        plane.move_active = 0
        plane.x_speed = 0
        plane.z_speed = 0
    # 程序对象program作为当前渲染状态的一部分
    x1 = plane.x
    z1 = plane.z
    x_cha = x - x1
    z_cha = z - z1
    x_speed = x_cha / 250
    z_speed = z_cha / 250
    x1 += plane.x_speed
    z1 += plane.z_speed
    plane.change(x1, z1)
    glUseProgram(shaderall.updateProgram)
    # 高度关联
    # glUniform
    # location：指明要更改的uniform变量的位置
    # v0, v1, v2, v3：指明在指定的uniform变量中要使用的新值
    # 利用x, y坐标确认高度
    glUniform1f(shaderall.updateProgram.xl, 0)
    glUniform1f(shaderall.updateProgram.yl, 0)
    # 补偿半径
    glUniform1f(shaderall.updateProgram.sphereRadius, plane_height)
    glUniform1i(shaderall.updateProgram.tex0, 1)
    glUniform2f(shaderall.updateProgram.xz, 0, 0)
    getMVP(x1, z1)
    plane.draw()

def people_move(people, x, z):
    people.move_active += 1
    if people.move_active == 250:
        people.move_active = 0
        people.x_speed = 0
        people.z_speed = 0
    # 程序对象program作为当前渲染状态的一部分
    x1 = people.x
    z1 = people.z
    x_cha = x - x1
    z_cha = z - z1
    x_speed = x_cha / 250
    z_speed = z_cha / 250
    x1 += people.x_speed
    z1 += people.z_speed
    people.change(x1, z1)
    glUseProgram(shaderall.updateProgram)
    # 高度关联
    # glUniform
    # location：指明要更改的uniform变量的位置
    # v0, v1, v2, v3：指明在指定的uniform变量中要使用的新值
    # 利用x, y坐标确认高度
    glUniform1f(shaderall.updateProgram.xl, plane.xl)
    glUniform1f(shaderall.updateProgram.yl, plane.yl)
    # 补偿半径
    glUniform1f(shaderall.updateProgram.sphereRadius, people.radius)
    glUniform1i(shaderall.updateProgram.tex0, 1)
    glUniform2f(shaderall.updateProgram.xz, x1, z1)
    getMVP(x1, z1)
    people.draw()

def DrawGLScene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # 将当前矩阵指定为投影矩阵。参数是GL_MODELVIEW，这个是对模型视景的操作，接下来的语句描绘一个以模型为基础的适应，这样来设置参数
    glMatrixMode(GL_MODELVIEW)
    # 链接无人机和人
    camera.setLookat()
    # 设置激活的纹理单元
    glActiveTexture(GL_TEXTURE0)
    # 将一个命名的纹理绑定到一个纹理目标上
    glBindTexture(GL_TEXTURE_2D, colorMap)
    # 设置激活的纹理单元
    glActiveTexture(GL_TEXTURE1)
    # 将一个命名的纹理绑定到一个纹理目标上
    glBindTexture(GL_TEXTURE_2D, hightMap)     
    #plane
    # 程序对象program作为当前渲染状态的一部分
    glUseProgram(shaderall.planeProgram)
    #设置uniform采样器的位置值，或者说纹理单元，保证每个uniform采样器对应着正确的纹理单元
    glUniform1i(shaderall.planeProgram.tex0, 0)
    plane.draw()

    glUseProgram(0)
    glColor3f(0.9, 0.9, 0.9)
    glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('a'))
    glLineWidth(2)
    glBegin(GL_LINES)
    for peo in people_list:
        dis = []
        #计算距离
        for _, pla in enumerate(plane_list):
            dis.append((pla.x - peo.x) * (pla.x - peo.x) + (pla.z - peo.z) * (pla.z - peo.z))
        # print(dis)
        #根据无人机与人的距离，选择距离最近的无人机连线，目前只有两架无人机
        if dis[0] < dis[1]:
            glVertex3f(plane_list[0].x, 0.7 + plane_height, plane_list[0].z)
            glVertex3f(peo.x, plane.getHeight(peo.x, peo.z) + 0.1, peo.z)
        else:
            glVertex3f(plane_list[1].x, 0.7 + plane_height, plane_list[1].z)
            glVertex3f(peo.x, plane.getHeight(peo.x, peo.z) + 0.1, peo.z)
    glEnd()
    #sphare

    glUseProgram(shaderall.updateProgram)
    for pla in plane_list:
        make_plane(pla)
    for peo in people_list:
        make_people(peo)

    #glUseProgram(0)
    #glUseProgram(shaderall.particleProgram)
    #glUniform1i(shaderall.particleProgram.plane, 1)
    #glUniform2f(shaderall.particleProgram.planeSacle,plane.xl,plane.yl)
    #glUniform3f(shaderall.particleProgram.sphere,eyeLoc[0],sph.radius,eyeLoc[2])
    #ps.render(shaderall.particleProgram)
    #glUseProgram(0)

    # 设置激活的纹理单元
    glActiveTexture(GL_TEXTURE0)
    # 将一个命名的纹理绑定到一个纹理目标上
    glBindTexture(GL_TEXTURE_2D, 0)
    # 开启和关闭服务器端GL功能
    glDisable(GL_TEXTURE_2D)
    # 设置激活的纹理单元
    glActiveTexture(GL_TEXTURE1)
    # 将一个命名的纹理绑定到一个纹理目标上
    glBindTexture(GL_TEXTURE_2D, 0)
    # 开启和关闭服务器端GL功能
    glDisable(GL_TEXTURE_2D)

    # 是OpenGL中GLUT工具包中用于实现双缓冲技术的一个重要函数。该函数的功能是交换两个缓冲区指针。
    # 但当我们进行复杂的绘图操作时，画面便可能有明显的闪烁。解决这个问题的关键在于使绘制的东西同时出现在屏幕上。
    # 所谓双缓冲技术， 是指使用两个缓冲区： 前台缓冲和后台缓冲。前台缓冲即我们看到的屏幕，后台缓冲则在内存当中，
    # 对我们来说是不可见的。每次的所有绘图操作都在后台缓冲中进行， 当绘制完成时， 把绘制的最终结果复制到屏幕上，
    # 这样， 我们看到所有GDI元素同时出现在屏幕上，从而解决了频繁刷新导致的画面闪烁问题。
    glutSwapBuffers()


def getMVP(x, z):
    v = ny.array(glGetFloatv(GL_MODELVIEW_MATRIX), ny.float32)
    p = ny.array(glGetFloatv(GL_PROJECTION_MATRIX), ny.float32)
    m = ny.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [x, 0, z, 1]], ny.float32)
    #print(m)
    # glUniformMatrix4fv函数向其传递数据。
    # location：指明要更改的uniform变量的位置
    # count：指明要更改的矩阵个数
    # transpose：指明是否要转置矩阵，并将它作为uniform变量的值。必须为GL_FALSE。
    # value：指明一个指向count个元素的指针，用来更新指定的uniform变量。
    glUniformMatrix4fv(shaderall.updateProgram.pMatrix, 1, GL_FALSE, p)
    glUniformMatrix4fv(shaderall.updateProgram.vMatrix, 1, GL_FALSE, v)
    glUniformMatrix4fv(shaderall.updateProgram.mMatrix, 1, GL_FALSE, m)
    #glgetfloat
def mouseButton(button, mode, x, y):	
	if button == GLUT_RIGHT_BUTTON:
		camera.mouselocation = [x,y]

def ReSizeGLScene(Width, Height): 
    glViewport(0, 0, Width, Height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width) / float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

#无人机移动 时钟信号回调
def timerProc(id):
    for index, i in enumerate(UAV_path_list):
        #print(index, i)
        plane_list[index].move_location(plane_list[index].x,
        plane_list[index].z, float(i[0]) / 120 - 5, float(i[1]) / 120 - 5)
    glutTimerFunc(1000, timerProc, 1)

##location_index = 0
##用户移动 时钟信号回调
#def timerProc(id):

#    #global location_index
#    #location_index += 1
#    #for index, i in enumerate(UAV_path_list[location_index]):
#      # print(index, i)
#      # plane_list[index].move_location(plane_list[index].x,
#      # plane_list[index].z, float(i[0])/120 - 5, float(i[1])/120 - 5)
    
#    pass

#    for index, i in enumerate(user_path_list[0]):
#        #print(index, i)
#        people_list[index].move_location(people_list[index].x,
#        people_list[index].z, float(i[0]) / 120 - 5, float(i[1]) / 120 - 5)
#    glutTimerFunc(1000, timerProc, 1)



def main():
    global UAV_path_list
    planningUAV(user_path_list,UAV_path_list)
    #无人机初始位置
    for i in range(len(UAV_path_list)):
        plane_list.append(common.sphere(16, 16, 0.1, 0, 0))
    global window
    #glutInit(sys.argv)
    # 初始化
    glutInit([])
    # 设置图形显示模式
    # GLUT_RGBA建立RGBA模式的窗口
    # GLUT_DOUBLE使用双缓存，以避免把计算机作图的过程都表现出来，或者为了平滑地实现动画
    # GLUT_DEPTH使用深度缓存
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    # 窗口大小设置
    glutInitWindowSize(1920,1080)
    glutInitWindowPosition(0,0)
    window = glutCreateWindow(b"opengl")

    # 为当前窗口设置显示回调函数
    glutDisplayFunc(DrawGLScene)
    # 设置空闲回调函数
    glutIdleFunc(DrawGLScene)
    # 指定当窗口的大小改变时调用的函数
    glutReshapeFunc(ReSizeGLScene)
    # 注册当前窗口的鼠标回调函数
    glutMouseFunc(mouseButton)
    # 设置移动回调函数
    glutMotionFunc(camera.mouse)
    # 定时器回调函数
    glutTimerFunc(1000, timerProc, 1)

    # gluLookAt(0, 15, 0, 0, 0, 0, 1.0, 0, 0.0)
    def keypress(key, x, y):
        if key == GLUT_KEY_UP:
            camera.move(0., 0., 1 * camera.offest)
        if key == GLUT_KEY_RIGHT:
            camera.move(-1 * camera.offest, 0., 0.)
        if key == GLUT_KEY_LEFT:
            camera.move(1 * camera.offest, 0., 0.)
        if key == GLUT_KEY_DOWN:
            camera.move(0., 0., -1 * camera.offest)
        if key == GLUT_KEY_F12:
            camera.change_overlook()


    # 注册当前窗口的键盘回调函数
    # glutKeyboardFunc(camera.keypress)
    # 设置当前窗口的特定键的回调函数
    # glutSpecialFunc(camera.keypress)

    # 注册当前窗口的键盘回调函数
    # glutKeyboardFunc(keypress2)
    # 设置当前窗口的特定键的回调函数
    glutSpecialFunc(keypress)
    # 背景颜色
    glClearColor(0.1, 0.1, 1, 0.1)
    # 设置深度缓存的清除值
    glClearDepth(1.0)
    # 开启GL_DEPTH_TEST，进行深度比较并更新深度缓冲区
    glEnable(GL_DEPTH_TEST)
    # GL_SMOOTH采用光滑着色，独立的处理图元中各个顶点的颜色
    glShadeModel(GL_SMOOTH)
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    camera.move(0.0, 1.3, 0)
    camera.setthree(True)
    camera.length = 5
    global shaderall
    shaderall = shaderProg.allshader()
    #global tf
    #tf = common.transformFeedback(shaderall.tfProgram)
    #global ps
    #ps = particle.particleSystem(1)
    global colorMap
    global hightMap
    colorMap = loadtexture.Texture.loadmap("ground2.bmp")
    # hight map for cpu to gpu
    hightMap = loadtexture.Texture.loadmap("hight.gif")
    # create terrain use cpu
    hightimage = loadtexture.Texture.loadterrain("hight.gif")
    # image = open("ground2.bmp").convert("RGBA")
    plane.setHeight(hightimage)

    glutMainLoop()

main()

