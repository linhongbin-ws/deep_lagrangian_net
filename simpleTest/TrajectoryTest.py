import gym
import gym_acrobot
import time
from Controller import PD_Controller
from Trajectory import CosTraj

env = gym.make('acrobotBmt-v0')
controller = PD_Controller()
traj = CosTraj()


obsve = env.reset()
env.render()
time.sleep(2)
tCount = 0
for t in range(3000):
    tCount += env.dt
    env.render()
    q, qd, qdd = traj.forward(tCount)
    a = controller.forward(s=[obsve[0],obsve[1],obsve[2],obsve[3]], qDes=[q[0], q[1]])
    observation, reward, done, info = env.step(a[0],a[1])
    #time.sleep(0.05)