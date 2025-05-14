from voicevox_core import AccelerationMode
from voicevox_core.blocking import Onnxruntime,Synthesizer,OpenJtalk,VoiceModelFile

ZUNDAMON_MODEL=0
ZUNDAMON_STYLE = 3

def main() -> None:
    onnx = Onnxruntime.load_once(filename="./voicevox_core/onnxruntime/lib/libvoicevox_onnxruntime.1.17.3.dylib")
    synth = Synthesizer(
        onnx,
        OpenJtalk("./voicevox_core/dict/open_jtalk_dic_utf_8-1.11")
    )
    with VoiceModelFile.open(f"./voicevox_core/models/vvms/{ZUNDAMON_MODEL}.vvm") as model:
        synth.load_voice_model(model)

    wav = synth.tts("こんにちは", ZUNDAMON_STYLE)
    with open("./output.wav", "wb") as f:
        f.write(wav)


if __name__ == "__main__":
    main()
