import pandas as pd


def read_song_csv(path_to_song):
    return pd.read_csv(path_to_song, sep='ÿ', engine='python', quoting=3)
