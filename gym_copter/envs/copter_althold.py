'''
gym-copter Environment class for altitude-hold

Copyright (C) 2019 Simon D. Levy

MIT License
'''

from gym_copter.envs.copter_env import CopterEnv
from gym import spaces
import numpy as np

class CopterAltHold(CopterEnv):
    '''
    A GymCopter class with continous state and action space.
    Action space is [0,1], with all motors set to the same value.
    State space is altitude,vertical_velocity.
    Reward is proximity to a target altitude.
    '''

    def __init__(self, dt=.001, target=10, timeout=10):

        CopterEnv.__init__(self)

        self.dt = dt
        self.target = target
        self.timeout = timeout

        # Action space = motors
        self.action_space = spaces.Box(np.array([0]), np.array([1]))

        # Observation space = altitude, vertical_velocity
        self.observation_space = spaces.Box(np.array([0,-np.inf]), np.array([np.inf,np.inf]))
        
    def step(self, action):

        # Convert discrete action index to array of floating-point number values
        motors = [float(action)]*4

        # Call parent-class step() to do basic update
        state, _, episode_over, info = CopterEnv.step(self, motors)

        # Dynamics uses NED coordinates, so negate to get altitude and vertical velocity
        altitude = -state[4]
        velocity = -state[5]

        # Too many ticks elapsed: set episode-over flag
        if self.ticks*self.dt > self.timeout:
            episode_over = True

        # Reward is proximity to target altitude
        reward = -np.log(np.abs(self.target-altitude))

        # Only one state; reward is altitude
        return (altitude,velocity), reward, episode_over, info

    def reset(self):
        CopterEnv.reset(self)
        return 0

