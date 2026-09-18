#!/usr/bin/python3

import os
import json
import random
import asyncio
import numpy as np
from sklearn.preprocessing import LabelEncoder
# Modelos
from sklearn.naive_bayes import ComplementNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
# Para validacion cruzada estratificada
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

# Banner inicial
print("/n----------------------------------------------------------------")
print("Ricky Chatbot Copyright (C) 2026  Hazel Azucena Calderon Bonilla")
print("This program comes with ABSOLUTELY NO WARRANTY.")
print("This is free software, and you are welcome to redistribute it")
print("under certain conditions.")
print("----------------------------------------------------------------")

# Hacer que intents.json sea cargado por ruta absoluta
rutaCerebro = os.path.dirname(os.path.abspath(__file__))
rutaIntents = os.path.join(rutaCerebro, "intents.json")

# Importar datos
with open(rutaIntents, 'r',encoding='utf-8') as dataset:
    data = json.load(dataset)

tags = []
preguntas = []
respuestas = {}

# Preparar dataset
for intent in data.get("intents", []):
    tag = intent.get("tag")
    patterns = intent.get("patterns", [])
    responseIntent = intent.get("responses", [])
    # Validar si no hay tag
    if not tag:
        print("Warning: intent sin tag")
        continue
    # Validar si no hay preguntas
    if not patterns:
        print(f"Warning: {tag} sin preguntas")
        continue
    # Validar si no hay respuestas
    if not responseIntent:
        print(f"Warning: {tag} sin respuestas")
    # Validar si hay menos de 3 preguntas
    if len(patterns) < 3:
        print(f"Warning: {tag} tiene menos de 3 preguntas")

    respuestas[tag] = responseIntent

    for pattern in patterns:
        if not isinstance(pattern, str) or not pattern.strip():
            print(f"Warning: patrón inválido en {tag}")
            continue

        preguntas.append(pattern)
        tags.append(tag)

# Comprobar que existan datos
if not preguntas:
    raise ValueError("No hay preguntas válidas para entrenar.")

if len(set(tags)) < 2:
    raise ValueError("Se necesitan al menos dos intents diferentes.")

# Codificar etiquetas
labelEncoder = LabelEncoder()
y = labelEncoder.fit_transform(tags)

print(f"\nTotal de preguntas: {len(preguntas)}")
print(f"Total de intents: {len(labelEncoder.classes_)}")

# Pipeline con vectorizador y modelo
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        lowercase=True,
        strip_accents="unicode"
    )),
    ("modelo", LinearSVC(
        C=1.0,
        class_weight=None,
        max_iter=2000,
        dual=True
    ))
])

# Validación cruzada (nomas para evaluacion del pipeline)
cv = StratifiedKFold( n_splits=5, shuffle=True, random_state=42)

resultados = cross_validate(
    pipeline,
    preguntas,
    y,
    cv=cv,
    scoring={
        "accuracy": "accuracy", "f1_macro": "f1_macro"},
    n_jobs=-1
)

print("\nValidación cruzada ")
print(f"Accuracy: {resultados['test_accuracy'].mean():.3f} ± {resultados['test_accuracy'].std():.3f}")
print(f"F1 Macro:{resultados['test_f1_macro'].mean():.3f} ± {resultados['test_f1_macro'].std():.3f}")

# Entrenar modelo
pipeline.fit(preguntas,y)

print("\nModelo final entrenado correctamente :)")

# Funcion responder
async def responder(textoEntrada, umbral=0.3):
    # Con strip para limpiar posibles espacios en blanco
    textoEntrada = str(textoEntrada).strip()

    # Esperar entre 2 y 3 segundos
    await asyncio.sleep(random.randint(2, 3))

    # Por si el usuario no escribe nada
    if not textoEntrada:
        return "No escribiste ninguna pregunta. ¿En qué puedo ayudarte?"

    # Extraer del pipeline el vectorizador y el modelo
    vectorizador = pipeline.named_steps["tfidf"]
    modeloSVC = pipeline.named_steps["modelo"]

    # Mandar entrada de usuario a vectorizador
    entradaUsuario = vectorizador.transform([textoEntrada])

    # Por si el modelo no entiende la entrada del usuario
    if entradaUsuario.nnz == 0:
        return "Que me estas queriendo decir?..."

    # Obtener probabilidades
    scores = modeloSVC.decision_function(entradaUsuario)[0]
    indice_pred = int(np.argmax(scores))
    confianza = float(scores[indice_pred])

    # Si la confianza es baja, no responder con seguridad
    if confianza < umbral:
        return "No estoy seguro de haber entendido. ¿Puedes reformularlo?"

    # Obtener el tag predicho
    tag_predicho = labelEncoder.inverse_transform([indice_pred])[0]

    opciones = respuestas.get(tag_predicho, [])

    if opciones:
        respuesta = random.choice(opciones)
        return respuesta
    else:
        return "Lo siento no tengo una respuesta para eso"

# print("----------------------------------------------------")
# print(asyncio.run(responder("ola")))