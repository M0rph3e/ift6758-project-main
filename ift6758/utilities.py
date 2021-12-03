import numpy as np
import collections
def angle(gp, p):
    """
        gp - goal coordinates
        p- puck coordinates
        returns angle in degrees
        Leg/ON/left Side for right hander has +ve angle
        OFF/Right Side for right hander has -ve angle
    """
    if gp[0] > 0:
        vector = (gp[0] - p[0])+((gp[1]-p[1])*1j)
        angle = np.angle(vector,deg=True)
    else:
        vector = (p[0]-gp[0])+((p[1]-gp[1])*1j)
        angle = np.angle(vector,deg=True)
    return angle

def distance(gp, p):
    """
        gp - goal coordinates
        p- puck coordinates
    """
    distance = np.sqrt((gp[0] - p[0])**2 + (gp[1] - p[1])**2)
    return distance

if __name__ == "__main__":
    a = (-89, 0)
    b = (-89, -15)
    c=(-89,30)
    a1 = (89, 0)
    b1 = (89, -15)
    c1=(89,30)
    print(angle(a, b),angle(a,c))
    print(angle(a1, b1),angle(a1,c1))
    print(distance(a,b))