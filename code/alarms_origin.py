import re
from datetime import datetime, timedelta
from matplotlib import colors
import folium
import pandas as pd
import numpy as np
import os
# from ellipse_fit import guess_yemen, guess_iran
from sklearn.cluster import DBSCAN
from matplotlib import pyplot as plt

local = '/home/yuval/alarms/'
islocal = False
if os.path.isdir(local):
    os.chdir(local)
    islocal = True


def guess_origin(df_toguess):
    okcat = (df_toguess['description'].values == 'ירי רקטות וטילים') | \
            (df_toguess['description'].values == 'חדירת כלי טיס עוין')
    toguess = df_toguess['origin'].isnull().values & okcat
    row_lat = np.array([coo['lat'][coo['loc'] == x].values[0] for x in df_toguess['cities'].values])
    row_long = np.array([coo['long'][coo['loc'] == x].values[0] for x in df_toguess['cities'].values])
    # syria = toguess & (row_long > 35.63) & (row_lat < 33.1)
    lebanon = toguess & (row_lat > 32.5)
    yemen = toguess & (row_lat < 30)
    gaza = toguess & (row_lat < 31.7) & (row_long < 34.7)
    origin = df_toguess['origin'].values
    origin[gaza] = 'Gaza'
    origin[lebanon] = 'Lebanon'
    # origin[syria] = 'Syria'
    # origin[syria] = 'Iraq'  # Golan hit by Lebanon nowadays
    origin[yemen] = 'Yemen'
    df_toguess['origin'] = origin
    return df_toguess

def clusterize(points, eps_km=10, min_samples=10):
        """
        Identifies clusters using DBSCAN.
        Parameters:
            points: array of shape (N, 2) - lat/lon
            eps_km: radius for clustering (in km)
            min_samples: minimum points to form a dense region
        Returns:
            points
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
        return labels

def guess_lebanon26(df_toguess, eps_km=15, min_samples=1):
    ids = df_toguess['id'].unique()
    for ii in range(len(ids)):
        iuav = df_toguess.index[(df_toguess['id'] == ids[ii]) & (df_toguess['threat'] == 5)].values
        if len(iuav) > 0:
            row = np.where(coo['loc'] == df0['cities'][iuav[0]])[0][0]
            lat = coo['lat'][row]
            long = coo['long'][row]
            if lat > 32.98 and long < 35.72:
                for idx in iuav:
                    df_toguess.at[idx, 'origin'] = 'Lebanon'
        irocket = df_toguess.index[(df_toguess['id'] == ids[ii]) & (df_toguess['threat'] == 0)].values
        if len(irocket) > 0:
            points = np.zeros((len(irocket), 2))
            for jj in range(len(irocket)):
                row = np.where(coo['loc'] == df0['cities'][irocket[jj]])[0][0]
                lat = coo['lat'][row]
                long = coo['long'][row]
                points[jj, :] = [long, lat]
            labels = clusterize(points, eps_km=15, min_samples=1)
            unique_labels = np.unique(labels)
            for clust in unique_labels:
                pts = points[labels == clust, :]
                if np.median(pts[:, 1]) > 32.6:
                    if (pts[:, 1].max() - pts[:, 1].min()) * 111 < 25 and (pts[:, 0].max() - pts[:, 0].min()) * 95 < 25:
                        for idx in irocket:
                            df_toguess.at[idx, 'origin'] = 'Lebanon'
    return df_toguess




if __name__ == '__main__':
    coo = pd.read_csv('data/coord.csv')
    alarms = pd.read_csv('data/alarms.csv')
    df0 = alarms[(alarms['id'] >= 7158) & (alarms['id'] <= 7186)  & (alarms['time'] > '2023-03-08 03:04:00')]
    for iii in range(len(df0)):
        df0.iloc[iii, 5] = ''
    df1 = guess_lebanon26(df0)
    df1.to_csv('~/Documents/test_lebanon.csv', index=True)

    #
    # for idx in np.unique(labels):
    #      plt.plot(points[labels == idx, 0], points[labels == idx, 1], '.')

#
# def guess_roar(from_time='2026-02-28', to_time=None, eps_km=15, min_samples=1):
#     path2data = os.environ['HOME'] + '/alarms/data/'
#     loc = pd.read_csv(path2data + 'coord.csv')
#     if to_time is None:
#         # set to_time as a string representing the date of tomorrow
#         to_time = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
#     df = pd.read_csv(path2data + 'alarms.csv')
#     df = df[(df['time'].values < to_time) & (df['time'].values > from_time)]
#     df = df[df['threat'].isin([0, 5])]
#     df = df.reset_index(drop=True)
#
#     for id in df['id'].unique():
#         for threat in [0, 5]:
#             df0 = df[(df['id'] == id) & (df['threat'] == threat)]
#             if len(df0) == 0:
#                 continue
#             points = np.zeros((len(df0), 2))
#             for ii in range(len(df0)):
#                 row = np.where(loc['loc'] == df0['cities'].iloc[ii])[0][0]
#                 lat = loc['lat'][row]
#                 long = loc['long'][row]
#                 points[ii, :] = [long, lat]
#             labels = clusterize(points, eps_km=eps_km, min_samples=min_samples)
#
#             cluster_details = {}
#             error_found = False
#             unique_labels = np.unique(labels)
#
#             for idx in unique_labels:
#                 if idx == -1:
#                     continue
#
#                 current_cluster_mask = labels == idx
#
#                 # Estimate origin
#                 estimated_origin = ''
#                 if np.min(points[current_cluster_mask, 1]) > 32.67 and np.sum(current_cluster_mask) < 30:
#                     estimated_origin = 'Lebanon'
#                 elif np.sum(current_cluster_mask) > 30:
#                     estimated_origin = 'Iran'
#                 elif np.sum(current_cluster_mask) == 1 and df0['cities'].values[current_cluster_mask][0] == 'חוות עדן':
#                     estimated_origin = 'Iran'
#
#                 # Find actual origin
#                 existing_origins = df0['origin'].values[current_cluster_mask]
#                 meaningful_existing_origins = [o for o in existing_origins if pd.notna(o) and o != '']
#                 actual_origin = ''
#                 if meaningful_existing_origins:
#                     actual_origin = pd.Series(meaningful_existing_origins).mode()[0]
#
#                 cluster_details[idx] = {'estimated': estimated_origin, 'actual': actual_origin}
#
#                 if actual_origin and actual_origin != estimated_origin:
#                     error_found = True
#
#             if error_found:
#                 plt.figure()
#                 for idx in unique_labels:
#                     if idx == -1:
#                         plt.scatter(points[labels == idx, 0], points[labels == idx, 1], c='k', marker='x',
#                                     label='Noise')
#                     else:
#                         details = cluster_details.get(idx, {})
#                         est = details.get('estimated', '') or 'None'
#                         act = details.get('actual', '') or 'None'
#
#                         is_mislabeled = (act != 'None' and est != act)
#
#                         label = f'Cluster {idx} (Est: {est}, Act: {act})'
#                         if is_mislabeled:
#                             label += ' - MISLABELED'
#
#                         plt.scatter(points[labels == idx, 0], points[labels == idx, 1], label=label)
#
#                 plt.title(f'ID: {id}, Threat: {threat} - Error Detected')
#                 plt.legend()
#                 plt.show()