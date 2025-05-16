#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fit an elipse to alarm clusters, see if from yemen.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import alphashape
from shapely.geometry import Point
from sklearn.linear_model import RANSACRegressor
from sklearn.cluster import DBSCAN
from matplotlib.patches import Ellipse
import cv2
from geopy.distance import geodesic
import os
path2data = os.environ['HOME']+'/alarms/data/'
coast = pd.read_csv(path2data+'israel_mediterranean_coast_0.5km.csv').values
coast = np.array(coast)[:, ::-1]
def filter_points_away_from_coast_fast(edge_points, coast, min_distance_km=0.3):
    lat_km = 111.2
    lon_km = 94.6
    mins = []
    filtered = []
    for pt in edge_points:
        dlat = (coast[:, 0] - pt[0]) * lat_km
        dlon = (coast[:, 1] - pt[1]) * lon_km
        distances = np.sqrt(dlat**2 + dlon**2)
        mins.append(min(distances))
        if np.min(distances) > min_distance_km:
            filtered.append(pt)
    return np.array(filtered), np.array(mins)


def detect_main_cluster(points, eps_km=10, min_samples=10):
    """
    Identifies the largest cluster using DBSCAN and filters out noise or small clusters.
    
    Parameters:
        points: array of shape (N, 2) - lat/lon
        eps_km: radius for clustering (in km)
        min_samples: minimum points to form a dense region
    
    Returns:
        main_cluster_points: points in the largest cluster
    """
    # Approximate lat/lon to km scale (around Israel)
    lat_km = 111.2
    lon_km = 94.6
    scaled_points = np.copy(points)
    scaled_points[:, 0] *= lat_km
    scaled_points[:, 1] *= lon_km

    # DBSCAN clustering
    db = DBSCAN(eps=eps_km, min_samples=min_samples)
    labels = db.fit_predict(scaled_points)

    # Identify the largest cluster (excluding noise: label -1)
    unique, counts = np.unique(labels[labels >= 0], return_counts=True)
    if len(counts) == 0:
        return np.empty((0, 2))  # No cluster found
    largest_cluster_label = unique[np.argmax(counts)]

    # Filter points belonging to the largest cluster
    return points[labels == largest_cluster_label]


# coast = pd.read_csv('data/israel_mediterranean_coast_0.5km.csv')
def fit_ellipse(points, plot=True):
    points = detect_main_cluster(points, eps_km=10, min_samples=10)
    if len(points) < 6:
        return None


    # points is a list of (x, y) tuples or numpy array
    alpha = 0.1  # Smaller alpha = tighter boundary; you may need to tune this
    boundary_shape = alphashape.alphashape(points, alpha)
    threshold = 0.03
    # Identify edge points
    edge_points = np.array([pt for pt in points if boundary_shape.exterior.distance(Point(pt)) < threshold])

    filt, _ = filter_points_away_from_coast_fast(edge_points, coast, min_distance_km=4)
    plt.plot(filt[:, 0], filt[:, 1], '.k')
    
    
    # Ensure points are in the right format: Nx1x2 array
    filtered_points_cv = filt.reshape(-1, 1, 2).astype(np.float32)
    
    ellipse = cv2.fitEllipse(filtered_points_cv)
    if plot:
        # ellipse = (center(x,y), (major_axis, minor_axis), angle)
        
        # Draw original points
        plt.scatter(points[:, 0], points[:, 1], s=10)
        
        # Draw filtered edge
        plt.scatter(edge_points[:, 0], edge_points[:, 1], color='red')
        
        # Draw ellipse
        ellipse_patch = Ellipse(xy=ellipse[0], width=ellipse[1][0], height=ellipse[1][1],                                angle=ellipse[2], edgecolor='blue', fc='None', lw=2)
        plt.gca().add_patch(ellipse_patch)
        
        plt.axis('equal')
        plt.show()
    return ellipse

if __name__ == '__main__':
    df = pd.read_csv(path2data+'alarms.csv')
    loc = pd.read_csv(path2data+'coord.csv')
    df0 = df[df['id'] == 5343]
    df0 = df0.reset_index(drop=True)
    points = np.zeros((len(df0), 2))
    for ii in range(len(df0)):
        row = np.where(loc['loc'] == df0['cities'][ii])[0][0]
        lat = loc['lat'][row]
        long = loc['long'][row]
        points[ii, :] = [long, lat]
    ellipse = fit_ellipse(points)

# def filter_points_away_from_coast(edge_points, coast, min_distance_km=0.3):
#     """
#     Exclude edge points that are closer than `min_distance_km` to the coastline.
#     """
#     filtered_points = []
#     for pt in edge_points:
#         min_dist = min(geodesic(pt, coast_pt).km for coast_pt in coast)
#         if min_dist > min_distance_km:
#             filtered_points.append(pt)
#     return np.array(filtered_points)
# '
# def compute_pairwise_approx_distances_km(edge_points, coast):
#     lat_km = 111.2
#     lon_km = 94.6

#     dlat = ((edge_points[:, None, 0] - coast[None, :, 0])) * lat_km
#     dlon = ((edge_points[:, None, 1] - coast[None, :, 1])) * lon_km
#     d = np.sqrt(dlat**2 + dlon**2)  # shape: (num_edge_points, num_coast_points)
#     return d

# def filter_by_min_distance(edge_points, coast, min_distance_km=0.3):
#     distances = compute_pairwise_approx_distances_km(edge_points, coast)
#     keep_mask = np.min(distances, axis=1) > min_distance_km
#     return edge_points[keep_mask]'

# filtered_edge_points = filter_points_away_from_coast(edge_points, coast, min_distance_km=0.3)
# # Assuming edge_points is an Nx2 numpy array
# model = RANSACRegressor().fit(edge_points[:, 0].reshape(-1, 1), edge_points[:, 1])

# # Predict and calculate residuals
# predicted = model.predict(edge_points[:, 0].reshape(-1, 1))
# residuals = np.abs(predicted - edge_points[:, 1])

# # Define a threshold for what is “too close to a line”
# linear_mask = residuals < 0.2

# # Remove sea-cut straight line points
# filtered_edge_points = edge_points[~linear_mask]
