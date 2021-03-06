"""
作者：冬兽
时间：2020年11月13日
使用gym完成残缺棋盘覆盖的强化学习方案,创建相关的环境
可能存在的问题：
（1）可观测状态只有当前点的上下左右8个点，太少
"""
import time

import math
import numpy as np
import random
import gym
from gym import spaces,core
# from gym.envs.classic_control import rendering


class Policy1_1(gym.Env):
    def __init__(self,size):
        super(Policy1_1,self).__init__()
        self.size = size  #棋盘大小
        self.edege_size = 512
        self.loc =[0,0]
        self.target = np.ones(shape=[self.size,self.size])
        # self.state = self.init_state()
        self.action_space = spaces.Box(low=0,high=4.999,shape=(1,),dtype=np.float64)  # 动作空间,离散0：不动作，。。。。
        self.observation_space = spaces.Box(low=0,high=1,shape=(self.size*self.size,),dtype=np.float64) # 状态空间
        # self.viewer = rendering.Viewer(self.edege_size+30,self.edege_size+30)
        self.reward = 0

    def init_state(self):
        state = np.zeros(shape=(self.size,self.size))
        x,y = random.randint(0,self.size-1),random.randint(0,self.size-1)
        self.state_ = np.zeros(shape=(self.size,self.size))
        self.counter = [0,0,0,0]
        state[x][y] = 1
        self.state_[x][y]=5
        return state

    def reset(self):
        """
        重置环境的状态，返回观察
        :return:
        """
        self.state = self.init_state()
        self.loc=[0,0]
        self.done = False
        obs = self.get_observation()
        return np.reshape(self.state,(-1,))

    def get_observation(self,x=0,y=0):
        """
        返回周围8个点的状态
        :param x:
        :param y:
        :return:
        """
        obs =[-1]*8
        if x-1>=0 and y-1>=0:
            obs[0] = self.state[x-1][y-1]
            obs[1] = self.state[x-1][y]
            obs[3] = self.state[x][y-1]
        if x-1 >=0 and y+1<self.size:
            obs[1] = self.state[x-1][y]
            obs[2] = self.state[x-1][y+1]
            obs[4] = self.state[x][y+1]
        if x+1<self.size and y-1>=0:
            obs[3] = self.state[x][y-1]
            obs[5] = self.state[x+1][y-1]
            obs[6] = self.state[x+1][y]
        if x+1<self.size and y+1<self.size:
            obs[4] = self.state[x][y+1]
            obs[6] = self.state[x+1][y]
            obs[7] = self.state[x+1][y+1]

        return obs


    def step(self,action):
        """
        推进一个时间步长，返回observation，reward，done，info
        :param action:
        :return:
        """
        reward =0
        action =int(action[0])
        x,y = self.loc[0],self.loc[1]
        if self.state[x][y] ==0:
            obs =self.get_observation(x,y)  # 获取观测值
            if (obs[3] != 0 or obs[1] != 0) and (obs[1] != 0 or obs[4] != 0) and (obs[3] != 0 or obs[6] != 0) and (
                    obs[4] != 0 or obs[6] != 0):
                self.update_loc()
            elif action ==0:
                self.update_loc()
            elif action ==1:
                if obs[1] ==0 and obs[3] ==0:
                    self.state[x][y] =1
                    self.state[x-1][y] = 1
                    self.state[x][y-1] = 1
                    self.state_[x][y] = 1
                    self.state_[x - 1][y] = 1
                    self.state_[x][y - 1] = 1
                    self.counter[action-1]+=1
                    self.update_loc()
            elif action ==2:
                if obs[1]==0 and obs[4] ==0:
                    self.state[x][y] = 1
                    self.state[x-1][y] = 1
                    self.state[x][y+1] = 1
                    self.state_[x][y] = 2
                    self.state_[x - 1][y] = 2
                    self.state_[x][y + 1] = 2
                    self.counter[action - 1] += 1
                    self.update_loc()
            elif action ==3:
                if obs[3]==0 and obs[6]==0:
                    self.state[x][y] = 1
                    self.state[x][y-1] = 1
                    self.state[x+1][y] = 1
                    self.state_[x][y] = 3
                    self.state_[x][y - 1] = 3
                    self.state_[x + 1][y] = 3
                    self.counter[action - 1] += 1
                    self.update_loc()
            elif action ==4 :
                if obs[4] ==0 and obs[6] ==0:
                    self.state[x][y] = 1
                    self.state[x][y+1] = 1
                    self.state[x+1][y] = 1
                    self.state_[x][y] = 4
                    self.state_[x][y + 1] = 4
                    self.state_[x + 1][y] = 4
                    self.counter[action - 1] += 1
                    self.update_loc()
        elif self.state[x][y] !=0:
            self.update_loc()
        _r = self._reward()
        reward = _r-self.reward
        self.reward = _r
        reward += -0.01
        return np.reshape(self.state,(-1,)),reward,self.done,{}

    def update_loc(self):
        f = (self.loc[1]+1)%self.size
        if f==0:
            if (self.loc[0]+1)%self.size ==0:
                self.done = True
            else:
                self.loc[0]+=1
                self.loc[1] = 0
        else:
            self.loc[1] +=1

    def _reward(self):
        """
        通过self.state与E(2)的点乘实现卷积操作，从而实现reward的计算，stride=[1,2,2,1],padding = VALID
        :return:
        """
        reward_2 = np.zeros(shape = (int(self.size/2),int(self.size/2)))
        i,j =0,0
        while i<self.size:
            j=0
            while j<self.size:
                reward_2[int(i/2)][int(j/2)] = math.floor(np.sum(self.state[i:i+2,j:j+2])/4)
                j+=2
            i+=2
        _reward = int(np.sum(reward_2))
        if self.size>=4:
            reward_4 = np.zeros(shape=(int(self.size / 4), int(self.size / 4)))
            i, j = 0, 0
            while i < self.size:
                j = 0
                while j < self.size:
                    reward_4[int(i / 4)][int(j / 4)] = math.floor(np.sum(self.state[i:i + 4, j:j + 4]) / 16)
                    j += 4
                i += 4
            _reward += int(np.sum(reward_4))*1.1
        return _reward


    def render(self,mode="human",close=False):
        """
        重新绘制环境的一帧
        :param mode:
        :param close:
        :return:
        """
        w = self.edege_size/self.size
        for i in range(self.size+1):
            if i%2==0:
                c = (1,0,0)
            else:
                c = (0,0,0)
            self.viewer.draw_line((15,15+i*w),(15+self.edege_size,15+i*w),color = c)
        for j in range(self.size+1):
            if j%2==0:
                c = (1,0,0)
            else:
                c = (0,0,0)
            self.viewer.draw_line((15+j*w,15),(15+j*w,15+self.edege_size),color = c)
        for i in range(self.size):
            for j in range(self.size):
                if self.state[i][j] == 1:
                    self.viewer.draw_polygon([(15+j*w+1,15+self.edege_size-i*w-2),
                                              (15+(j+1)*w-2,15+self.edege_size-i*w-2),
                                              (15+(j+1)*w-2,15+self.edege_size-(i+1)*w+1),
                                              (15 + j* w+1, 15 +self.edege_size-(i+1) * w+1)])
        i,j = self.loc[0],self.loc[1]
        self.viewer.draw_polygon([(15 + j * w , 15 + self.edege_size - i * w),
                                  (15 + (j + 1) * w, 15 + self.edege_size - i * w),
                                  (15 + (j + 1) * w, 15 + self.edege_size - (i + 1) * w),
                                  (15 + j * w, 15 + self.edege_size - (i + 1) * w)],
                                 filled=False,
                                 color = (0,0,0.5),
                                 linewidth = 5)
        return self.viewer.render(return_rgb_array=mode == 'human')

    def close(self):
        if self.viewer:
            self.viewer.close()

if __name__ == '__main__':
    env = MyEnv(8)
    env.reset()
    env.render()
    while True:
        act = input("action:")
        obs,reward,dones,info = env.step(act)
        env._reward()
        print(reward,dones)
        env.render()
        if dones:
            env.reset()
            time.sleep(1)
            env.render()

