# -*- coding: utf-8 -*-
"""
Created on Mon May 22 11:24:20 2017

@author: li yuming
"""
import pygame
import sys
import traceback
import car
from random import *
from pygame.locals import *
import numpy as np
import datetime

# ====================初始化====================
pygame.init()
bg_size = width, height = 960, 480  # 设计背景尺寸
screen = pygame.display.set_mode(bg_size)  # 设置背景对话框
pygame.display.set_caption("交通拥堵 Demo")
background = pygame.image.load("image/bg.png")  # 加载背景图片,并设置为不透明
glmark = np.arange(2880).reshape(6,480)  #汽车占位标识符 (4*960马路, 每2个像素一个占位,还需要增加1个像素,让车能出去)
                              
def add_cars(group, num):
    for i in range(num):
        for j in range(3):
            c = car.Cars(bg_size,i+1,glmark,i*16+j)
            group.add(c)

def init_glmark():
    for j in range(6):
        for i in range(480):
            if j==0 or j==5:
                glmark[j][i]=255
            else:
                glmark[j][i]=1
        
    for i in range(325,480):
       glmark[1][i]=255  
             
def main():
    clock = pygame.time.Clock()  # 设置帧率
    score_font = pygame.font.SysFont("arial", 48)  # 定义分数字体
    color_black = (0, 0, 0)
    #color_green = (0, 255, 0)
    #color_red = (255, 0, 0)
    #color_white = (255, 255, 255)    
    score = 0  # 统计用户得分
    paused = False  # 标志是否暂停
    
    pause_image = pygame.image.load("image/pause.png")  # 加载暂停相关按钮
    play_image = pygame.image.load("image/play.png")
    paused_or_play_image = pause_image  # 设置默认显示的暂停按钮
    paused_rect = pause_image.get_rect()
    paused_rect.left, paused_rect.top = 10, 10  # 设置暂停按钮位置    
    
    choose=0
    notmove_image = pygame.image.load("image/notmovechange.png")  
    slowchange_image = pygame.image.load("image/slowchange.png")  
    dlchange_image = pygame.image.load("image/dlchange.png") 
    dlchange_rect = dlchange_image.get_rect()
    slowchange_rect = slowchange_image.get_rect()
    notmove_rect = notmove_image.get_rect()
    dlchange_rect.left, dlchange_rect.top = 600, 400  
    slowchange_rect.left, slowchange_rect.top = 400, 400 
    notmove_rect.left, notmove_rect.top = 200, 400 
    
    isdeng = False
    dengcount = 0
    dengflag = 1
    deng_dis_image = pygame.image.load("image/deng_dis.png")  
    deng_en0_image = pygame.image.load("image/deng_en0.png") 
    deng_en1_image = pygame.image.load("image/deng_en1.png")  
    deng_image = deng_dis_image
    deng_rect = deng_dis_image.get_rect()
    deng_rect.left, deng_rect.top = 400, 150  
    
    init_glmark()
    
    # ====================实例化汽车====================
    cars = pygame.sprite.Group()  # 生成汽车组
    add_cars(cars, 4)  # 生成若干汽车
    total_out = 0
    all_out = 0
    initime = pretime = datetime.datetime.now() 
    fixwhich=-1
    while True:
        screen.blit(background, (0, 0))  # 将背景图片打印到内存的屏幕上
        screen.blit(notmove_image, notmove_rect)
        screen.blit(slowchange_image, slowchange_rect)
        screen.blit(dlchange_image, dlchange_rect)
        score_choose = score_font.render("_______", True, color_black)
             
        # ====================检测用户的退出及暂停操作====================
        for event in pygame.event.get():  # 响应用户的偶然操作
            if event.type == QUIT:  # 如果用户按下屏幕上的关闭按钮，触发QUIT事件，程序退出
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1 and paused_rect.collidepoint(event.pos):  # 如果检测到用户在指定按钮区域按下鼠标左键
                    paused = not paused
                    if paused:  # r如果当前的状态是暂停
                        pausetime = datetime.datetime.now()
                        paused_or_play_image = play_image
                    else:
                        initime+=datetime.datetime.now()-pausetime
                        pretime+=datetime.datetime.now()-pausetime
                        paused_or_play_image = pause_image
                        
                elif event.button == 1 and notmove_rect.collidepoint(event.pos):  # 如果检测到用户在指定按钮区域按下鼠标左键
                    choose = 0                       
                elif event.button == 1 and slowchange_rect.collidepoint(event.pos):  # 如果检测到用户在指定按钮区域按下鼠标左键
                    choose = 1     
                elif event.button == 1 and dlchange_rect.collidepoint(event.pos):  # 如果检测到用户在指定按钮区域按下鼠标左键
                    choose = 2   
                    
                elif event.button == 1 and deng_rect.collidepoint(event.pos):  # 如果检测到用户在指定按钮区域按下鼠标左键
                    isdeng = not isdeng  
                    if isdeng:
                        deng_image = deng_en1_image
                        dengflag = -1
                        dengcount = 9999999
                    else:
                        deng_image = deng_dis_image
                        
        screen.blit(paused_or_play_image, paused_rect)
        if choose ==0:
            screen.blit(score_choose,notmove_rect)
        elif choose ==1:
            screen.blit(score_choose,slowchange_rect)
        else:
            screen.blit(score_choose,dlchange_rect) 
            
        if not paused:
            score_text = score_font.render("Score : %s" % str(score)+'/s--'+str(all_out)+'/'+str((datetime.datetime.now()-initime).seconds)+'s', True, color_black)
            # ====================红绿灯要限制车辆=============
            if isdeng:
                dengcount+=1
                if dengcount>150:
                    dengcount = 0
                    dengflag = -1*dengflag
                    glmark[0][200] = -1*dengflag
                    glmark[1][200] = dengflag 
                    if (glmark[1][200]<0):
                        deng_image = deng_en0_image
                        fixwhich = 1  #第二个车道不能变道了,如果灯红
                    else:
                        deng_image = deng_en1_image
                        fixwhich = 0
                    
            else:
                glmark[0][200] = 1
                glmark[1][200] = 1                 
                fixwhich = -1
                dengcount = 0
                dengflag = 1
                
            # ====================绘制汽车====================
            for each in cars: 
                isout = each.move(choose,fixwhich)
                all_out+=isout
                total_out+=isout
                screen.blit(each.image, each.rect) 
                
            if (datetime.datetime.now()-pretime).seconds>1:
                pretime = datetime.datetime.now()  
                score = total_out
                total_out = 0
        else:
            for each in cars: 
                screen.blit(each.image, each.rect) 
                
        screen.blit(score_text, (80, 5))
        screen.blit(deng_image, deng_rect)
        pygame.display.flip()  # 将内存中绘制好的屏幕刷新到设备屏幕上
        clock.tick(60)  # 设置帧数为60

# ===============================================================================
# 主要功能：程序入口
# 算法流程：
# 注意事项：
# ===============================================================================
if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()