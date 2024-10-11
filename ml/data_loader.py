# data_loader.py
import os
import json
import librosa
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences

def load_audio_file(file_path, sr=22050, n_mfcc=13):
    """
    Загружает аудиофайл и извлекает MFCC.
    :param file_path: Путь к аудиофайлу.
    :param sr: Частота дискретизации.
    :param n_mfcc: Количество MFCC.
    :return: MFCC и частота дискретизации.
    """
    audio, _ = librosa.load(file_path, sr=sr)
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
    return mfccs.T  # Транспонируем для соответствия входу нейросети

def load_annotations(annotations_file):
    """
    Загружает аннотации из файла JSON.
    :param annotations_file: Путь к файлу аннотаций.
    :return: Список аннотаций.
    """
    with open(annotations_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def prepare_dataset(data_dir, annotations_file, max_length=None):
    """
    Подготавливает датасет.
    :param data_dir: Директория с аудиофайлами.
    :param annotations_file: Файл с аннотациями.
    :param max_length: Максимальная длина последовательностей.
    :return: Массив MFCC, массив меток и массив атрибутов.
    """
    annotations = load_annotations(annotations_file)
    X, y_labels, y_attributes = [], [], []

    for entry in annotations:
        file_name = entry['audio_filepath']
        full_path = os.path.join(data_dir, file_name)

        if os.path.exists(full_path):
            mfccs = load_audio_file(full_path)
            X.append(mfccs)  # Добавляем MFCC в список
            y_labels.append(entry['label'])
            y_attributes.append(entry['attribute'])

    # Паддинг MFCC последовательностей
    X = pad_sequences(X, padding='post', dtype='float32', maxlen=max_length)

    return np.array(X), np.array(y_labels), np.array(y_attributes)
