# main.py
import numpy as np
from sklearn.model_selection import train_test_split
from data_loader import prepare_dataset
from model import train_model

if __name__ == "__main__":
    # Параметры
    datasets = {
        "clear": "../train_dataset/hr_bot_clear/",
        "noise": "../train_dataset/hr_bot_noise/",
        "synt": "../train_dataset/hr_bot_synt/"
    }
    annotations = {
        "clear": "../train_dataset/annotation/hr_bot_clear.json",
        "noise": "../train_dataset/annotation/hr_bot_noise.json",
        "synt": "../train_dataset/annotation/hr_bot_synt.json"
    }

    X_all, y_all_labels, y_all_attributes = [], [], []

    for key in datasets.keys():
        print(f"Preparing dataset for {key}...")
        X, y_labels, y_attributes = prepare_dataset(datasets[key], annotations[key], max_length=1000)  # Укажите максимальную длину

        # Конкатенируем данные
        X_all.append(X)
        y_all_labels.append(y_labels)
        y_all_attributes.append(y_attributes)

    # Объединяем все данные
    X_all = np.concatenate(X_all, axis=0)
    y_all_labels = np.concatenate(y_all_labels, axis=0)
    y_all_attributes = np.concatenate(y_all_attributes, axis=0)

    # Разделение данных на обучающую и тестовую выборки
    X_train, X_test, y_train, y_test = train_test_split(X_all, y_all_labels, test_size=0.2, random_state=42)

    # Обучение модели
    num_classes = len(set(y_all_labels))  # Количество классов
    model = train_model(X_train, y_train, X_test, y_test, num_classes)

    # Сохранение модели в формате Keras
    model.save("trained_model.keras")  # Сохраняем в формате Keras
