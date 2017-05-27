# -*- coding: utf-8 -*-
"""
Created on Mon May 22 11:38:40 2017

@author: li yuming
"""

import pygame
from random import *
from ConvNetPy.deepqlearn  import *
import datetime
import numpy as np

#一辆车54个像素 , 也就是27个占位符
class Cars(pygame.sprite.Sprite):
    def __init__(self, bg_size,which,carmark,id):
        pygame.sprite.Sprite.__init__(self)
        if id==0:
            self.image = pygame.image.load("image/car1_dp.png")  
            self.dlinput = np.arange(3*200).reshape(3,200) 
        else:
            self.image = pygame.image.load("image/car"+str(which)+".png")  
        self.mask = pygame.mask.from_surface(self.image)
        self.toplist = [0,155,205,260,310,0]
        self.which = which
        self.iniwhich = which
        self.dqnwhich = which
        self.carmark = carmark
        self.rect = self.image.get_rect()
        self.width, self.height = bg_size[0], bg_size[1]
        self.reset()
        self.id=id
        self.initime = datetime.datetime.now() 
        
        '''
        http://www-cs-faculty.stanford.edu/people/karpathy/convnetjs/demo/rldemo.html  
        var brain = new deepqlearn.Brain(3, 2); // 3 inputs, 2 possible outputs (0,1)
        var state = [Math.random(), Math.random(), Math.random()];
        for(var k=0;k<10000;k++) {
            var action = brain.forward(state); // returns index of chosen action
            var reward = action === 0 ? 1.0 : 0.0;
            brain.backward([reward]); // <-- learning magic happens here
            state[Math.floor(Math.random()*3)] += Math.random()*2-0.5;
        }
        brain.epsilon_test_time = 0.0; // don't make any more random choices
        brain.learning = false;
        // get an optimal action from the learned policy
        var action = brain.forward(array_with_num_inputs_numbers);
        '''

        num_inputs = 600
        num_actions = 3
        temporal_window = 0
        network_size = num_inputs * temporal_window + num_actions * temporal_window + num_inputs
        layers=[]
        layers.append({'type': 'input', 'out_sx': 1, 'out_sy': 1, 'out_depth': network_size})
        layers.append({'type': 'fc', 'num_neurons': 36, 'activation': 'tanh'})
        layers.append({'type': 'fc', 'num_neurons': 24, 'activation': 'tanh'})
        layers.append({'type': 'fc', 'num_neurons': 24, 'activation': 'tanh'})
        layers.append({'type': 'fc', 'num_neurons': 24, 'activation': 'tanh'})
        layers.append({'type': 'regression', 'num_neurons': num_actions}) #value function output    
        tdtrainer_options = {'learning_rate': 0.001, 'momentum': 0.0, 'batch_size': 128, 'l2_decay': 0.01}
        opt = {'temporal_window': temporal_window, \
               'experience_size': 100000, \
               'start_learn_threshold':20000, \
               'gamma':0.98, \
               'learning_steps_total':500000, \
               'learning_steps_burnin':1000, \
               'epsilon_min':0.0, \
               'epsilon_test_time':0.0, \
               'layers':layers, \
               'tdtrainer_options':tdtrainer_options}
        if(self.id==0):
            self.brain = Brain(num_inputs, num_actions, opt)
        
    def distance(self):
        index = -1
        cur = self.rect.left+self.rect.width
        cur = self.checkpos(cur)/2
        for i in range(cur,self.carmark[self.which].size):
            if self.carmark[self.which][i]<=0 or self.carmark[self.which][i]>=255:
                index =i
                break
        if index<0:
            return 99999
        else:
            return index-cur   
    
    def checkpos(self,pos):
        if pos<0:
            pos=0
        elif pos>=960:
            pos=959   
        return pos
    
    def updatemark(self,which,flag):
        left = self.rect.left
        left = self.checkpos(left)/2
        right = self.rect.left+self.rect.width-1
        right = self.checkpos(right)/2
        for i in range(left,right):
            if self.carmark[which][i]>=0 and self.carmark[which][i]<255:
                self.carmark[which][i]=flag        
    
    def updatepos(self,dis):
        self.updatemark(self.which,1)
        
        if dis>30:
            self.speed+=0.2
            if self.speed>12:
                self.speed = 12
        else:
            self.speed-=0.5
            if self.speed<1 :
                self.speed = 1
            elif self.speed>2*dis:
                self.speed = 0
        
        self.rect.left = (int)(self.rect.left + self.speed)
        
        self.updatemark(self.which,0)
                        
    def change(self,left,right,curdis):
        which=self.which
        self.which-=1
        if self.which>0 and left:
            dis = self.distance()
            if dis>2 and dis>curdis:
                self.updatemark(which,1)
                self.updatemark(self.which,0)
                self.rect.top = self.toplist[self.which]
                return
        #########################################
        self.which =which+1
        if self.which<=4 and right:
            dis = self.distance()
            if dis>2 and dis>curdis:
                self.updatemark(which,1)
                self.updatemark(self.which,0)
                self.rect.top = self.toplist[self.which]
                return
        self.which = which            
                        
    def move(self,movechoose,fixwhich): 
        deepq=False
        action = -1
        if (self.id!=0 and movechoose==2):
            movechoose = 0
            
        if movechoose==0:
            movetofast = False
        elif movechoose==1:
            movetofast = True
        else:
            if (datetime.datetime.now() -self.initime).seconds >600:
                self.brain.learning = False
            movetofast = False
            deepq = True
            if self.rect.left>=0:
                right = self.rect.left+self.rect.width-1
                right = self.checkpos(right)/2
                for j in range(3):
                    for i in range(200):
                        if right+i<480:
                            self.dlinput[j][i]=self.carmark[self.which-1+j][right+i]
                        else:
                            self.dlinput[j][i]=255
                action = self.brain.forward(self.dlinput.reshape(600,1))
                print action
                if action == 0:
                    pass #不变道
                elif action == 1: #向左边变道
                    self.dqnwhich = self.which-1
                    if self.dqnwhich<=0 or (self.dqnwhich==1 and self.rect.left>600):
                        self.brain.backward(-1)
                        self.speed = 0
                        return 0
                        #pass 
                    else:
                        self.updatemark(self.which,1)
                        self.updatemark(self.dqnwhich,0)
                        self.rect.top = self.toplist[self.dqnwhich]
                        self.which = self.dqnwhich  
                elif action == 2: #向右边变道
                    self.dqnwhich = self.which+1
                    if self.dqnwhich>4:
                        self.brain.backward(-1)
                        self.speed = 0
                        return 0
                        #pass
                    else:
                        self.updatemark(self.which,1)
                        self.updatemark(self.dqnwhich,0)
                        self.rect.top = self.toplist[self.dqnwhich]
                        self.which = self.dqnwhich                          
            
        if self.rect.left == -1*self.rect.width:
            dis = self.distance()
            if dis>randint(60,200) or (deepq and self.id==0 and dis>2):
                self.updatepos(dis)            
        elif self.rect.left < 960:
            if movetofast and self.which!=fixwhich and not deepq:
                if False: #(fixwhich==0 and self.which==1 and self.speed<1):
                    pass  #第一道红绿灯堵住了, 第二道不要随便变道, 要速度到一定程度才能变道
                else:
                    dis = self.distance()
                    speedwhich = [0,0,0,0,0,0]        
                    for j in range(4):
                        for i in range(self.carmark[self.which].size):
                            if self.carmark[j][i]>0:
                                speedwhich[j+1]+=1            
                    if speedwhich[self.which+1]<speedwhich[self.which]-80: #往左变道, 左边快
                        self.change(True,False,dis)
                    elif  speedwhich[self.which+1]<speedwhich[self.which+2]-80:  #往右变道, 右边快
                        self.change(False,True,dis)
                    
            dis = self.distance()
            if dis>2:
                self.updatepos(dis)
            else: #动不了, 堵住了, 变道
                if self.which!=fixwhich and not deepq:
                    self.change(True,True,1)
                    
            if deepq and action>=0:
                if action>0:
                    actionreward = 0.9
                else:
                    actionreward = 1
                disdnq = self.distance()*1.0
                if disdnq>999:
                    disdnq = 1*actionreward
                else:
                    disdnq = disdnq/240
                    if disdnq>=1:
                        disdnq = 0.99
                    disdnq = disdnq*actionreward
                #self.brain.backward(disdnq)
                dnqspeed = (self.speed-6)/6.0
                self.brain.backward(dnqspeed)
        else:
            if deepq and action>=0:
                if action>0:
                    actionreward = 0.9
                else:
                    actionreward = 1                
                #self.brain.backward(1*actionreward)   
                dnqspeed = (self.speed-6)/6.0
                self.brain.backward(dnqspeed) 
                self.rect.left, self.rect.top = (-1*self.rect.width,self.toplist[self.which])
            else:
                self.reset()
            return 1
        
        return 0

    def reset(self): 
        self.which = self.iniwhich
        self.rect.left, self.rect.top = (-1*self.rect.width,self.toplist[self.which])
        self.speed = 6