import os

for k, v in os.environ.items():
    globals()[k] = v
