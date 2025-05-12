#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  4 18:25:59 2025

@author: innereye
"""

import numpy as np
from scipy.linalg import sqrtm
from numpy.linalg import eig
import matplotlib.pyplot as plt
import pandas as pd
# from scipy.linalg import sqrtm, eig


def get_minimum_enclosing_ellipse(points, tolerance=1e-5):
    """
    Find the minimum enclosing ellipse (MVEE) of a set of 2D points.
    Returns (center, shape_matrix), where shape_matrix defines the ellipse.
    """
    N, d = points.shape
    Q = np.vstack([points.T, np.ones(N)])
    QT = Q.T
    err = tolerance + 1.0
    u = np.ones(N) / N

    while err > tolerance:
        X = Q @ np.diag(u) @ QT
        M = np.diag(QT @ np.linalg.inv(X) @ Q)
        j = np.argmax(M)
        step_size = (M[j] - d - 1) / ((d + 1) * (M[j] - 1))
        new_u = (1 - step_size) * u
        new_u[j] += step_size
        err = np.linalg.norm(new_u - u)
        u = new_u

    # Center of ellipse
    center = points.T @ u
    A = np.linalg.inv(points.T @ np.diag(u) @ points - np.outer(center, center)) / d

    return center, A  # A is the ellipse's shape matrix

# Example usage:
points = np.array([[1, 1], [2, 0], [0, 2], [2, 3]])
center, A = get_minimum_enclosing_ellipse(points)

# Convert to ellipse parameters (semi-axes, rotation, etc.)

vals, vecs = eig(A)
axes_lengths = 1. / np.sqrt(vals)



# Sample points
points = np.array([[1, 1], [2, 0], [0, 2], [2, 3], [3, 1], [1.5, 2]])

def get_minimum_enclosing_ellipse(points, tolerance=1e-5):
    N, d = points.shape
    Q = np.vstack([points.T, np.ones(N)])
    QT = Q.T
    err = tolerance + 1.0
    u = np.ones(N) / N

    while err > tolerance:
        X = Q @ np.diag(u) @ QT
        M = np.diag(QT @ np.linalg.inv(X) @ Q)
        j = np.argmax(M)
        step_size = (M[j] - d - 1) / ((d + 1) * (M[j] - 1))
        new_u = (1 - step_size) * u
        new_u[j] += step_size
        err = np.linalg.norm(new_u - u)
        u = new_u

    center = points.T @ u
    A = np.linalg.inv(points.T @ np.diag(u) @ points - np.outer(center, center)) / d

    return center, A

def plot_ellipse(center, A, ax, edge_color='red'):
    vals, vecs = eig(A)
    order = np.argsort(vals)
    vals, vecs = vals[order], vecs[:, order]

    width, height = 2 / np.sqrt(vals)
    angle = np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0]))

    from matplotlib.patches import Ellipse
    ellipse = Ellipse(xy=center, width=width, height=height, angle=angle,
                      edgecolor=edge_color, fc='None', lw=2)
    ax.add_patch(ellipse)

# Compute MVEE
center, A = get_minimum_enclosing_ellipse(points)

# Plot
fig, ax = plt.subplots()
ax.scatter(points[:, 0], points[:, 1], label='Points')
plot_ellipse(center, A, ax)
ax.plot(center[0], center[1], 'ro', label='Center')
ax.set_aspect('equal')
ax.legend()
plt.title("Minimum Enclosing Ellipse")
plt.grid(True)
plt.show()

##
df = pd.read_csv('data/alarms.csv')
loc = pd.read_csv('data/coord.csv')
df0 = df[df['id'] == 5343]
df0 = df0.reset_index(drop=True)
points = np.zeros((len(df0), 2))
for ii in range(len(df0)):
    row = np.where(loc['loc'] == df0['cities'][ii])[0][0]
    lat = loc['lat'][row]
    long = loc['long'][row]
    points[ii, :] = [long, lat]

center, A = get_minimum_enclosing_ellipse(points, tolerance=1e-13)

fig, ax = plt.subplots()
ax.scatter(points[:, 0], points[:, 1], label='Points')
plot_ellipse(center, A, ax)
ax.plot(center[0], center[1], 'ro', label='Center')
ax.set_aspect('equal')
ax.legend()
plt.title("Minimum Enclosing Ellipse")
plt.grid(True)
plt.show()

