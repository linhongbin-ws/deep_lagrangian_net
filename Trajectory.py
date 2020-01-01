import numpy as np
import gym
import gym_acrobot
import time
from Controller import PD_Controller
import matplotlib.pyplot as plt
from os import path, mkdir
class CosTraj():
    def __init__(self):
        self.A = np.pi
        self.w = np.array([1.0,1.0])
        self.b = np.array([0.,0.])
        self.dof = 2
    def forward(self, t):
        q = np.cos(self.w * t + self.b)*self.A
        qd = -self.w * np.sin(self.w * t + self.b)*self.A
        qdd = -self.w * self.w * np.cos(self.w * t + self.b) *self.A
        return q, qd, qdd


def runTrajectory(controller, traj, sampleNum = 20000, savePath='.',saveFig=True, dt=0.01, isShowPlot=True,isRender=True, saveName=None, isReturnAllForce=False):
    env = gym.make('acrobotBmt-v0')
    env.dt = dt
    obsve = env.reset()
    if isRender:
        env.render()
    time.sleep(2)
    tCount = 0

    t_list = []
    q_des_dict= {}
    q_dict = {}
    qdot_dict = {}
    qddot_dict = {}
    a_dict = {}
    q_des_dict['J1'] = []
    q_des_dict['J2'] = []
    q_dict['J1'] = []
    q_dict['J2'] = []
    qdot_dict['J1'] = []
    qdot_dict['J2'] = []
    qddot_dict['J1'] = []
    qddot_dict['J2'] = []
    a_dict['J1'] = []
    a_dict['J2'] = []

    if isReturnAllForce:
        m_dict = {}
        c_dict = {}
        g_dict = {}
        m_dict['J1'] = []
        m_dict['J2'] = []
        c_dict['J1'] = []
        c_dict['J2'] = []
        g_dict['J1'] = []
        g_dict['J2'] = []
        m_dict['J1_pred'] = []
        m_dict['J2_pred'] = []
        c_dict['J1_pred'] = []
        c_dict['J2_pred'] = []
        g_dict['J1_pred'] = []
        g_dict['J2_pred'] = []
        a_dict['J1_pred'] = []
        a_dict['J2_pred'] = []
    progress_cnt = 0
    for t in range(sampleNum):
        tCount += env.dt
        if isRender:
            env.render()
        q, qd, qdd = traj.forward(tCount)
        a = controller.forward(s=[obsve[0, 0], obsve[1, 0], obsve[2, 0], obsve[3, 0], obsve[4, 0], obsve[5, 0]], sDes=[q[0], q[1], qd[0], qd[1], qdd[0], qdd[1]])
        obsve, _, _, _ = env.step(a[0], a[1])
        t_list.append(tCount)
        q_des_dict['J1'].append(q[0])
        q_des_dict['J2'].append(q[1])
        q_dict['J1'].append(obsve[0, 0])
        q_dict['J2'].append(obsve[1, 0])
        qdot_dict['J1'].append(obsve[2, 0])
        qdot_dict['J2'].append(obsve[3, 0])
        a_dict['J1'].append(a[0])
        a_dict['J2'].append(a[1])
        qddot_dict['J1'].append(obsve[4, 0])
        qddot_dict['J2'].append(obsve[5, 0])
        progress = int((t+1)*100/sampleNum)
        progress_cnt = progress if progress_cnt<progress else progress
        print("run trajectory(",progress_cnt,"/100)")

        if isReturnAllForce:
            s = []
            s.extend(q)
            s.extend(qd)
            s.extend(qdd)
            m, c, g = env.model.inverse_all(s)
            m_dict['J1'].append(m[0])
            m_dict['J2'].append(m[1])
            c_dict['J1'].append(c[0])
            c_dict['J2'].append(c[1])
            g_dict['J1'].append(g[0])
            g_dict['J2'].append(g[1])
            m, c, g = controller.dynamic_controller.forward_all(s)
            m_dict['J1_pred'].append(m[0])
            m_dict['J2_pred'].append(m[1])
            c_dict['J1_pred'].append(c[0])
            c_dict['J2_pred'].append(c[1])
            g_dict['J1_pred'].append(g[0])
            g_dict['J2_pred'].append(g[1])
            a_dict['J1_pred'].append(m[0]+c[0]+g[0])
            a_dict['J2_pred'].append(m[1]+c[1]+g[1])



        #time.sleep(0.05)
    env.close()
    fig = plt.figure()
    plt.subplot(211)
    plt.plot(t_list, q_des_dict['J1'], 'r')
    plt.plot(t_list, q_dict['J1'], 'k')
    plt.legend(['Desired Trajectory','Measured Trajectory'],loc='upper right')
    plt.subplot(212)
    plt.plot(t_list, q_des_dict['J2'], 'r')
    plt.plot(t_list, q_dict['J2'], 'k')
    plt.legend(['Desired Trajectory','Measured Trajectory'],loc='upper right')
    if isShowPlot:
        plt.show()
    if saveFig:
        if not path.isdir(savePath):
            mkdir(savePath)
        if saveName is None:
            saveName = 'tractory'
        fig.savefig(path.join(savePath,saveName+'.png'))



    if isReturnAllForce:
        y1LabelList = ['J1','J2']
        y2LabelList = ['J1_pred', 'J2_pred']

        for j in range(2):
            fig = plt.figure()
            x = t_list
            y1_list = [m_dict[y1LabelList[j]], c_dict[y1LabelList[j]],g_dict[y1LabelList[j]],a_dict[y1LabelList[j]]]
            y2_list = [m_dict[y2LabelList[j]], c_dict[y2LabelList[j]], g_dict[y2LabelList[j]], a_dict[y2LabelList[j]]]
            for i in range(4):
                plt.subplot(411+i)
                plt.plot(x, y1_list[i], 'r')
                plt.plot(x, y2_list[i], 'k')
                if i==0:
                    plt.legend(['Ground Truth', 'Predict'], loc='upper right')
                if i is not 3:
                    plt.tick_params(
                        axis='x',  # changes apply to the x-axis
                        which='both',  # both major and minor ticks are affected
                        bottom=False,  # ticks along the bottom edge are off
                        top=False,  # ticks along the top edge are off
                        labelbottom=False)
            if isShowPlot:
                plt.show()
            fig.savefig(path.join(savePath, saveName + '_torque_'+y1LabelList[j]+'.png'))




        return q_dict, qdot_dict, qddot_dict, a_dict, (m_dict, c_dict, g_dict)
    else:
        return q_dict, qdot_dict, qddot_dict, a_dict