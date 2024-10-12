import os
import speech_recognition as sr
from pydub import AudioSegment

_label2id = {
    "отказ": 0,
    "отмена": 1,
    "подтверждение": 2,
    "начать осаживание": 3,
    "осадить на (количество) вагон": 4,
    "продолжаем осаживание": 5,
    "зарядка тормозной магистрали": 6,
    "вышел из межвагонного пространства": 7,
    "продолжаем роспуск": 8,
    "растянуть автосцепки": 9,
    "протянуть на (количество) вагон": 10
}


def transcribe_audio(audio_path):
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data, language='ru-RU')
            return text
        except sr.RequestError as e:
            print(f"Ошибка при обращении к сервису: {e}")
            return None
        except sr.UnknownValueError:
            print("Не удалось распознать аудио")
            return None

def classify_text(text):
    for label, label_id in _label2id.items():
        if label in text:
            return label_id
    return -1

def process_audio_files(audio_files):
    results = []
    for audio_path in audio_files:
        text = transcribe_audio(audio_path)
        if text:
            label = classify_text(text)
            result = {
                "audio": os.path.basename(audio_path),
                "text": text,
                "label": label,
                "attribute": -1  # здесь можно добавить логики для атрибутов, если нужно
            }
            results.append(result)
    return results


def main():
    # Пример использования
    audio_file_path = "..\data\\train\hr_bot_synt\\3a0cb44f-76ff-11ee-844c-c09bf4619c03_2.wav"
    result = transcribe_audio(audio_file_path)
    if result:
        print(result)
    else:
        print("Не удалось обработать аудиофайл.")


if __name__=='__main__':
    main()
