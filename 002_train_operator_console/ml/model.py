# model.py
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

def create_model(input_shape, num_classes):
    """
    Создает модель нейронной сети.
    :param input_shape: Форма входных данных.
    :param num_classes: Количество классов для классификации.
    :return: Скомпилированная модель.
    """
    model = models.Sequential()
    model.add(layers.Input(shape=input_shape))
    model.add(layers.Conv1D(64, kernel_size=3, activation='relu'))
    model.add(layers.MaxPooling1D(pool_size=2))
    model.add(layers.Conv1D(128, kernel_size=3, activation='relu'))
    model.add(layers.MaxPooling1D(pool_size=2))
    model.add(layers.Flatten())
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(num_classes, activation='softmax'))  # Для классификации команд
    return model

def train_model(X_train, y_train, X_test, y_test, num_classes):
    """
    Обучает модель на тренировочных данных.
    :param X_train: Тренировочные данные.
    :param y_train: Метки для тренировочных данных.
    :param X_test: Тестовые данные.
    :param y_test: Метки для тестовых данных.
    :param num_classes: Количество классов.
    :return: Обученная модель.
    """
    model = create_model((X_train.shape[1], X_train.shape[2]), num_classes)
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))
    return model
