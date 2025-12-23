import pickle

with open("src/cowrie/data/fs.pickle", "rb") as f:
    fs = pickle.load(f)

print(fs)
