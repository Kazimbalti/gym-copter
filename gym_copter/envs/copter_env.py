'''
Copyright (C) 2019 Simon D. Levy

MIT License
'''

import gym
from gym import spaces
import numpy as np

import pyglet

from gym_copter.dynamics.phantom import DJIPhantomDynamics

from sys import stdout

# https://stackoverflow.com/questions/56744840/pyglet-label-not-showing-on-screen-on-draw-with-openai-gym-render
class _DrawText:
    def __init__(self, label:pyglet.text.Label):
        self.label=label
    def render(self):
        self.label.draw()

class CopterEnv(gym.Env):

    metadata = {'render.modes': ['human']}

    def __init__(self, dt=.001):

        self.action_space = spaces.Box(np.array([0,0,0,0]), np.array([1,1,1,1]))  # motors
        self.dt = dt
        self.dynamics = DJIPhantomDynamics()
        self.viewer = None
        self.heading_widgets = []

        self.heading = 0
        self.altitude = 0

    def step(self, action):

        self.dynamics.setMotors(action)
        self.dynamics.update(self.dt)

        # an environment-specific object representing your observation of the environment
        obs = self.dynamics.getState()

        reward       = 0.0   # floating-point reward value from previous action
        episode_over = False # whether it's time to reset the environment again (e.g., circle tipped over)
        info         = {}    # diagnostic info for debugging

        self.dynamics.update(self.dt)

        return obs, reward, episode_over, info

    def reset(self):
        pass

    def render(self, mode='human'):

        # Adapted from https://raw.githubusercontent.com/openai/gym/master/gym/envs/classic_control/cartcircle.py

        from gym.envs.classic_control import rendering

        # Screen size, pixels
        W = 800
        H = 500

        # Altitude
        ALTITUDE_SPAN_METERS    = 200
        ALTITUDE_STEP_METERS    = 5
        ALTITUDE_SPACING_PIXELS = 40

        self.w = W
        self.h = H

        self.heading_spacing = 80

        if self.viewer is None:

            self.viewer = rendering.Viewer(W, H)

            # Add sky as backround
            sky = rendering.FilledPolygon([(0,H), (0,0), (W,0), (W,H)])
            sky.set_color(0.5,0.8,1.0)
            self.viewer.add_geom(sky)

            # Create labels for heading
            self.heading_labels = [pyglet.text.Label(('%d'%(c*15)).center(3), font_size=20, y=H-17, 
                color=(255,255,255,255), anchor_x='center', anchor_y='center') for c in range(24)]

        # Detect window close
        if not self.viewer.isopen: return None

        # Get vehicle state
        state = self.dynamics.getState()
        pose = state.pose
        location = pose.location
        rotation = pose.rotation

        # Center top of ground quadrilateral depends on pitch
        y = H/2 * (1 + np.sin(rotation[1]))

        # Left and right top of ground quadrilateral depend on roll
        dy = W/2 * np.sin(rotation[0])
        ury = y + dy
        uly = y - dy

        # Draw new ground quadrilateral:         LL     LR     UR       UL
        self.viewer.draw_polygon([(0,0), (W,0), (W,ury), (0,uly),], color=(0.5, 0.7, 0.3) )

        # Add a horizontal line and pointer at the top for the heading display
        self.viewer.draw_line((0,H-35), (W,H-35), color=(1.0,1.0,1.0))
        self.viewer.draw_polygon([(self.w/2-5,self.h-40), (self.w/2+5,self.h-40), (400,self.h-30)], color=(1.0,0.0,0.0))

        # Display heading
        for i,heading_label in enumerate(self.heading_labels):
            x = (self.w/2 - self.heading * 5.333333 + self.heading_spacing*i) % 1920
            self.viewer.add_onetime(_DrawText(heading_label))
            heading_label.x = x

        # Add a box on and pointer on the right side for the altitude gauge
        h2 = 100
        l = self.w - 100
        r = self.w - 10
        b = self.h/2 - h2
        t = self.h/2 + h2
        self.viewer.draw_polygon([(l,t),(r,t),(r,b),(l,b)], color=(1.0, 1.0, 1.0), linewidth=2, filled=False)
        self.viewer.draw_polygon([(l,self.h/2-8), (l,self.h/2+8), (l+8,self.h/2)], color=(1.0,0.0,0.0))

        # Display altitude
        closest = self.altitude // 5 * 5
        for k in range(-2,3):
            tickval = closest+k*5
            #dy = k * 40
            dy = 8*(tickval-self.altitude)
            #print('%+3.2f %+3.2f %d' % (tickval-self.altitude, 8*(tickval-self.altitude), dy))
            #stdout.flush()
            altitude_label = pyglet.text.Label(('%3d'%tickval).center(3), x=W-60, y=self.h/2+dy,
                    font_size=20, color=(255,255,255,255), anchor_x='center', anchor_y='center') 
            self.viewer.add_onetime(_DrawText(altitude_label))

        #exit(0)

        self.altitude += .05
        self.heading = (self.heading + 1) % 360

        return self.viewer.render(return_rgb_array = mode=='rgb_array')

    def close(self):

        pass
