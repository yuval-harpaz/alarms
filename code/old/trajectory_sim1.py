# https://scipython.com/book2/chapter-8-scipy/examples/a-projectile-with-air-resistance/
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# Drag coefficient, projectile radius (m), area (m2) and mass (kg).
c = 0.47
r = 1/61
A = np.pi * r**2
m = 40
# Air density (kg.m-3), acceleration due to gravity (m.s-2).
rho_air = 1.28
g = 9.81
# For convenience, define  this constant.
k = 0.5 * c * rho_air * A
# %matplotlib tk
##
# Initial speed and launch angle (from the horizontal).

def proj(ang=65, v0=50, col='auto'):
    phi0 = np.radians(ang)
    def deriv(t, u):
        x, xdot, z, zdot = u
        speed = np.hypot(xdot, zdot)
        xdotdot = -k/m * speed * xdot
        zdotdot = -k/m * speed * zdot - g
        return xdot, xdotdot, zdot, zdotdot
    # Initial conditions: x0, v0_x, z0, v0_z.
    u0 = 0, v0 * np.cos(phi0), 0., v0 * np.sin(phi0)
    # Integrate up to tf unless we hit the target sooner.
    t0, tf = 0, 500
    def hit_target(t, u):
        # We've hit the target if the z-coordinate is 0.
        return u[2]
    # Stop the integration when we hit the target.
    hit_target.terminal = True
    # We must be moving downwards (don't stop before we begin moving upwards!)
    hit_target.direction = -1

    def max_height(t, u):
        # The maximum height is obtained when the z-velocity is zero.
        return u[3]

    soln = solve_ivp(deriv, (t0, tf), u0, dense_output=True,
                     events=(hit_target, max_height))
    # print(soln)
    print('Time to target = {:.2f} s'.format(soln.t_events[0][0]))
    # print('Time to highest point = {:.2f} s'.format(soln.t_events[1][0]))
    # A fine grid of time points from 0 until impact time.
    t = np.linspace(0, soln.t_events[0][0], 100)
    # Retrieve the solution for the time grid and plot the trajectory.
    sol = soln.sol(t)
    x, z = sol[0], sol[2]
    # print('Range to target, xmax = {:.2f} m'.format(x[-1]))
    # print('Maximum height, zmax = {:.2f} m'.format(max(z)))
    slope = (z[-2] - z[-1]) / (x[-2] - x[-1])
    hit_ang = int(np.abs(np.round(np.rad2deg(np.arctan(1*(slope))))))
    plt.plot(x/1000, z/1000, color=col, label=str(ang)+' '+str(hit_ang))
angs = np.arange(20, 90, 5)
col = matplotlib.cm.jet(np.arange(len(angs))/(len(angs)-1))[:, :3]
plt.figure()
for iang, ang in enumerate(angs):
    proj(ang=ang, v0=690, col=col[iang, :])
plt.legend()
plt.xlabel('distance (km)')
plt.ylabel('height (km)')
plt.title('trajectory (exit angle, hit angle)')
plt.axis('equal')
plt.grid()
plt.show()
# import numpy
# from matplotlib import pyplot as plt
#
# %matplotlib tk
# # Initial conditions
# ##
# x0 = 0
# y0 = 0.0001
# dt = 0.005
# alpha = 0.5
# g = 10.0
#
# # Input the length and velocity
# # length = float(input("Input the overal length: "))
# # v0 = float(input("Input the initial velocity: "))
# length = 75
# v0 = length * 0.5
# # Guess the initial angle based on the motion without air friction
# if g * length / (v0 * v0) > 1:
#     print("The input is not right. Please put a proper one!")
#     exit(1)
# else:
#     angle0 = 0.5 * numpy.arcsin(g * length / (v0 * v0))
# print("Initial angle in degrees is: ", angle0 / numpy.pi * 180.0)
#
# x_old = x0
# y_old = y0
# angle_old = angle0
#
# fig = plt.figure()
# # fig.gca().set_aspect("equal")
# angle_old = np.pi/20
# for iter in range(0, 10):
#     vx_old = v0 * numpy.cos(angle_old)
#     vy_old = v0 * numpy.sin(angle_old)
#     traj_x = []
#     traj_y = []
#     theor_x = []
#     theor_y = []
#
#     t = 0.0
#     x_theor = x0
#     y_theor = y0
#
#     while y_old > 0:
#         traj_x.append(x_old)
#         traj_y.append(y_old)
#         theor_x.append(x_theor)
#         theor_y.append(y_theor)
#         t = t + dt
#
#         vx_new = vx_old - alpha * vx_old * dt
#         vy_new = vy_old - g * dt - alpha * vy_old * dt
#         x_new = x_old + vx_old * dt
#         y_new = y_old + vy_old * dt
#
#         # Analytical solution
#         vx_theor = v0 * numpy.cos(angle_old) * numpy.exp(-alpha * t)
#         vy_theor = (v0 * numpy.sin(angle_old) + g / alpha) * numpy.exp(-alpha * t) - g / alpha
#         x_theor = x_theor + vx_theor * dt
#         y_theor = y_theor + vy_theor * dt
#
#         vx_old = vx_new
#         vy_old = vy_new
#         x_old = x_new
#         y_old = y_new
#
#     plt.figure(1)
#     plt.plot(traj_x, traj_y)
#     # plt.plot(theor_x, theor_y, "+")
#     angle_old = angle_old + np.pi/20
#     # angle_new = angle_old - (x_old - length) / (2.0 * v0 * v0 * numpy.cos(2.0 * angle_old) / g)
#     #
#     # print("Prediction and length = ", x_old, length)
#     print("Old angle = ", angle_old * 180.0 / numpy.pi)
#     # print("Predicted angle = ", angle_new * 180.0 / numpy.pi)
#     x_old = x0
#     y_old = y0
#     # angle_old = angle_new
# plt.axis('equal')
# plt.show()
#
