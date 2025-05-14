from voicevox_core.blocking import Onnxruntime, Synthesizer, OpenJtalk, VoiceModelFile
import subprocess

class Tts:
    ZUNDAMON_MODEL=0
    ZUNDAMON_STYLE = 3

    def __init__(self) -> None:
        onnx = Onnxruntime.load_once(filename="./voicevox_core/onnxruntime/lib/libvoicevox_onnxruntime.1.17.3.dylib")
        synth = Synthesizer(
            onnx,
            OpenJtalk("./voicevox_core/dict/open_jtalk_dic_utf_8-1.11")
        )
        with VoiceModelFile.open(f"./voicevox_core/models/vvms/{self.ZUNDAMON_MODEL}.vvm") as model:
            synth.load_voice_model(model)

        self.synth = synth

    def speak(self, txt: str) -> None:
        wav = self.synth.tts(txt, self.ZUNDAMON_STYLE)
        proc = subprocess.Popen(["ffplay", "-autoexit", "-hide_banner", "-"], stdin=subprocess.PIPE)
        proc.stdin.write(wav)
        proc.stdin.flush()
        proc.stdin.close()
        proc.wait()


def main():
    Tts().speak("こんにちは")

if __name__ == "__main__":
    main()
