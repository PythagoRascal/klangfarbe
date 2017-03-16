from components.recorder import Recorder
from components.processor import Processor
from components.display import Display

# CONSTANTS
SIZE = 2**11
CHANNELS = 1
RATE = 24000
INTERVAL = 0.1

# INIT COMPONENTS
recorder = Recorder(SIZE, CHANNELS, RATE, INTERVAL)
processor = Processor(recorder)
display = Display(recorder, processor)

# START COMPONENTS
recorder.start()
processor.start()
display.show()

# STOP COMPONENTS
processor.stop()
recorder.stop()
