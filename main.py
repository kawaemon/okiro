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

"""
以下 Claude 3.7 Sonnet で半バイブスコーディング

以下のようなデータが与えられます。
```
9:00 学校
20m 移動
20m 飯
10m シャワー
10m 起床
```
一般には、1行にスペース区切りで2つのデータが入っている
データの1行目は、[hh:mm形式の時間, イベント名]
それ以降の行は、[かかる時間 \d+[m or h], イベント名]
の形式です。
1行目はその日最初の予定、それ以降は最初の予定に必要な準備とそれにかかる時間を示しています。
また、最初の予定に間に合わせるために、起きていなければならない最も遅い時間を起床時間と定義します。
あなたのタスクは、以下の疑似コードの示す処理を Python で実装することです。
コードは厳密に下の形に従う必要はなく、同じ処理が実現できれば良いです。なるべく簡潔で読みやすいコードを目指してください。

```
spec = parse_data_from("./spec.txt")
time.wait_until(spec.起床時間)
while True:
    予定, それまでの分数 = spec.get_next_event(time.now())
    if 予定 is None:
        break
    print(f"{time.now()} {予定}まであと{それまでの分数}です")
    time.sleep(1 minutes)
```

最初に与えた例だとこう表示されるべきです。
```
8:00 シャワーまであと10分です
8:01 シャワーまであと9分です
~省略~
8:10 飯まであと10分です
8:11 飯まであと9分です
```
"""

from datetime import datetime, timedelta
import time

class Schedule:
    def __init__(self, filename):
        self.events = []
        self.parse_data_from(filename)
        self.calculate_wake_up_time()

    def parse_data_from(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()

        # 最初の行は目標時間とイベント名
        first_line = lines[0].strip().split()
        target_time = datetime.strptime(first_line[0], '%H:%M').time()
        target_event = ' '.join(first_line[1:])

        # 残りの行は準備イベントとそれぞれにかかる時間
        prep_events = []
        for line in reversed(lines[1:]):
            parts = line.strip().split()
            duration_str = parts[0]
            event_name = ' '.join(parts[1:])

            # 時間単位の変換
            if 'h' in duration_str:
                duration_minutes = int(duration_str.replace('h', '')) * 60
            else:
                duration_minutes = int(duration_str.replace('m', ''))

            prep_events.append((event_name, duration_minutes))

        # イベントリストの構築（目標時間から逆算）
        current_time = datetime.combine(datetime.today(), target_time)
        self.events.append((current_time, target_event))

        for event_name, duration in prep_events:
            current_time = current_time - timedelta(minutes=duration)
            self.events.append((current_time, event_name))

        # 時間順に並び替え
        self.events.sort(key=lambda x: x[0])

    def calculate_wake_up_time(self):
        # 起床時間は最初のイベントの時間
        self.wake_up_time = self.events[0][0]

    def get_next_event(self, current_time):
        for event_time, event_name in self.events:
            if event_time > current_time:
                # 次のイベントまでの分数を計算
                minutes_until = (event_time - current_time).total_seconds() / 60
                return event_name, int(minutes_until)
        return None, None

def wait_until(target_time):
    """指定された時間まで待機する"""
    now = datetime.now()

    if now > target_time:
        # 既に目標時間を過ぎている場合は、翌日の同時刻まで待機
        target_time = target_time.replace(day=now.day + 1)

    wait_seconds = (target_time - now).total_seconds()

    if wait_seconds > 0:
        print(f"Waiting until {target_time.strftime('%H:%M')} ({wait_seconds:.0f} seconds)")
        time.sleep(wait_seconds)

def main():
    tts = Tts()
    # スケジュール読み込み
    spec = Schedule("spec.txt")

    print(f"起床時間: {spec.wake_up_time.strftime('%H:%M')}")

    # 起床時間まで待機（実際に使用する場合）
    wait_until(spec.wake_up_time)

    while True:
        current_time = datetime.now()
        event, minutes_until = spec.get_next_event(current_time)

        if event is None:
            print("すべての予定が終了しました")
            break

        before = datetime.now()
        for _ in range(5):
            tts.speak(f"{event}まであと{minutes_until}分です")
        after = datetime.now()

        # 1分待機
        waitsecs = 60 - (after-before).seconds
        print(f"waiting for {waitsecs}secs")
        time.sleep(waitsecs)


if __name__ == "__main__":
    main()
