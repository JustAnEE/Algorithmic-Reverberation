# Algorithmic-Reverberation
Implementing a Schroeder reverberator in Python. 

NOTE: I would recommend using algorithmicreverb.py for reverbing your own float 32 .wav files not the Jupyter notebook. The Python script uses scipy's lfilter function for a much faster implementation and the sound artifacts through this implementation seem to be greatly reduced compared to the time difference equation implementation used in the notebook. Also for best results it's probably best to test this program on short audio files with simple melodies.  
