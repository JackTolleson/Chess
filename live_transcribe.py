import sys
import queue
import sounddevice as sd
import vosk
import json
import subprocess
vosk.SetLogLevel(-1)
# Start chess program
chess = subprocess.Popen(
    ["python", "play.py"],
    stdin=subprocess.PIPE,
    text=True
)

#print(sd.query_devices())

model_path = "vosk-model-small-en-us-0.15"
model = vosk.Model(model_path)

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

samplerate = 48000
device = 1
channels = 1

grammar = [
    "a","b","c","d","e","f","g","h",
    "one","two","three","four","five","six","seven","eight",
    "resign","exit","quit","chess","move"
]

num_map = {
    "one":"1","two":"2","three":"3","four":"4",
    "five":"5","six":"6","seven":"7","eight":"8"
}

rec = vosk.KaldiRecognizer(model, samplerate, json.dumps(grammar))

with sd.RawInputStream(
        samplerate=samplerate,
        blocksize=8000,
        dtype="int16",
        channels=channels,
        callback=callback,
        device=device):

    print("Listening...")

    while True:
        data = q.get()

        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "")
            tokens = text.split()

            if tokens and tokens[0] in {"chess", "move"}:

                move_tokens = tokens[1:]
                converted = [num_map.get(t, t) for t in move_tokens]

                # chess move
                if len(converted) == 4:
                    move = "".join(converted)
                    print("Move:", move)

                    chess.stdin.write(move + "\n")
                    chess.stdin.flush()

                # resign / quit
                elif converted and converted[0] in {"exit","resign","quit"}:
                    cmd = converted[0]
                    print("Command:", cmd)

                    chess.stdin.write(cmd + "\n")
                    chess.stdin.flush()

                    if cmd in {"exit","quit","resign"}:
                        break
