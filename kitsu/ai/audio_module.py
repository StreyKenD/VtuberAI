import sounddevice as sd
import numpy as np
import threading
import queue

class StreamingAudioPlayer:
    def __init__(self, sample_rate=24000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_queue = queue.Queue()
        self.playback_thread = threading.Thread(target=self._playback_worker, daemon=True)
        self.playing = False

    def start(self):
        if not self.playing:
            self.playing = True
            self.playback_thread.start()

    def stop(self):
        self.playing = False

    def enqueue(self, audio_chunk: np.ndarray):
        """
        Add a chunk of audio samples (numpy array) to the playback queue.
        """
        self.audio_queue.put(audio_chunk)

    def _playback_worker(self):
        """
        Worker thread to continuously pull audio chunks and play them.
        """
        with sd.OutputStream(samplerate=self.sample_rate, channels=self.channels, dtype='float32') as stream:
            while self.playing:
                try:
                    chunk = self.audio_queue.get(timeout=0.1)
                    if chunk.dtype != np.float32:
                        chunk = chunk.astype(np.float32)
                    stream.write(chunk)
                    self.audio_queue.task_done()
                except queue.Empty:
                    continue
