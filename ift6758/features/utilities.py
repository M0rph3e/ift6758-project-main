import numpy as np

def angle(gp, p):
    """
        gp - goal coordinates
        p- puck coordinates
        angle in degrees
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
    print(angle(a, b))
    print(distance(a,b))