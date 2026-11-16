"""Entrena y evalua un clasificador de retrasos con separacion temporal.

Uso: python -m entrenamiento.entrenar_modelo
La muestra de 15 000 observaciones se incluye para reproducir el experimento.
"""
from __future__ import annotations

import json
import platform
import hashlib
from scripts.verificar_datos import verificar
from datetime import date
from pathlib import Path

import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, average_precision_score, confusion_matrix, f1_score,
    precision_recall_curve, precision_score, recall_score, roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import sklearn

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / 'data' / 'muestra_prestamos_mineros_15000.csv'
OUT = ROOT / 'modelos'
FIGS = ROOT / 'graficos'
NUMERIC = ['cantidad_prestada', 'dias_plazo', 'valor_unitario_pen', 'mes']
CATEGORICAL = [
    'tipo_personal', 'area_solicitante', 'region', 'tipo_operacion',
    'categoria_equipo', 'criticidad_equipo', 'condicion_entrega', 'turno',
    'motivo_prestamo', 'prioridad',
]
FEATURES = CATEGORICAL + NUMERIC
LABEL_MAP = {'A tiempo': 0, 'Con retraso': 1}
SEED = 42


def preprocessing():
    return ColumnTransformer(transformers=[
        ('cat', Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', min_frequency=3)),
        ]), CATEGORICAL),
        ('num', Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('standard', StandardScaler()),
        ]), NUMERIC),
    ])


def performance(y, prob, threshold):
    pred = (prob >= threshold).astype(int)
    return {
        'accuracy': round(float(accuracy_score(y, pred)), 4),
        'precision': round(float(precision_score(y, pred, zero_division=0)), 4),
        'recall': round(float(recall_score(y, pred, zero_division=0)), 4),
        'f1': round(float(f1_score(y, pred, zero_division=0)), 4),
        'roc_auc': round(float(roc_auc_score(y, prob)), 4),
        'average_precision': round(float(average_precision_score(y, prob)), 4),
        'confusion_matrix': confusion_matrix(y, pred, labels=[0, 1]).tolist(),
        'positive_rate': round(float(np.mean(y)), 4),
    }


def best_f1_threshold(y, prob):
    # El umbral se selecciona SOLO sobre validacion (no test).
    # Malla definida para evitar resultados fragiles en extremos.
    candidates = np.linspace(.05, .95, 181)
    scores = [f1_score(y, prob >= t, zero_division=0) for t in candidates]
    return float(candidates[int(np.argmax(scores))])


def train():
    datos_version = verificar()
    OUT.mkdir(exist_ok=True, parents=True)
    FIGS.mkdir(exist_ok=True, parents=True)
    df = pd.read_csv(FILE, encoding='utf-8-sig')
    raw_label_counts = {str(k): int(v) for k, v in df.cumplimiento_plazo.value_counts().items()}
    df = df[df['cumplimiento_plazo'].isin(LABEL_MAP)].copy()
    df['fecha_prestamo'] = pd.to_datetime(df['fecha_prestamo'], errors='coerce')
    df = df.dropna(subset=['fecha_prestamo']).sort_values('fecha_prestamo', kind='stable').reset_index(drop=True)
    df['objetivo'] = df['cumplimiento_plazo'].map(LABEL_MAP).astype(int)
    for name in NUMERIC:
        df[name] = pd.to_numeric(df[name], errors='coerce')
    total = len(df)
    n_train = int(total * .70)
    n_valid = int(total * .15)
    subsets = {'train': df.iloc[:n_train], 'valid': df.iloc[n_train:n_train+n_valid], 'test': df.iloc[n_train+n_valid:]}
    Xtr, ytr = subsets['train'][FEATURES], subsets['train']['objetivo']
    Xv, yv = subsets['valid'][FEATURES], subsets['valid']['objetivo']
    Xt, yt = subsets['test'][FEATURES], subsets['test']['objetivo']

    candidates = {
        'RegresionLogistica': LogisticRegression(max_iter=2000, class_weight='balanced', random_state=SEED),
        'BosqueAleatorio': RandomForestClassifier(
            n_estimators=130, max_depth=13, min_samples_leaf=6,
            class_weight='balanced_subsample', random_state=SEED, n_jobs=-1,
        ),
    }
    fitted = {}
    selection = {}
    for name, classifier in candidates.items():
        pipe = Pipeline([('preprocesamiento', preprocessing()), ('clasificador', classifier)])
        pipe.fit(Xtr, ytr)
        pv = pipe.predict_proba(Xv)[:, 1]
        th = best_f1_threshold(yv, pv)
        selection[name] = {
            'validacion_average_precision': round(float(average_precision_score(yv, pv)), 4),
            'validacion_f1': round(float(f1_score(yv, pv >= th, zero_division=0)), 4),
            'umbral_validacion': round(th, 4),
        }
        fitted[name] = pipe
    best_name = max(selection, key=lambda n: selection[n]['validacion_average_precision'])
    model = fitted[best_name]
    threshold = selection[best_name]['umbral_validacion']
    ptest = model.predict_proba(Xt)[:, 1]
    ptrain = model.predict_proba(Xtr)[:, 1]
    test_metrics = performance(yt, ptest, threshold)
    baseline = DummyClassifier(strategy='prior').fit(Xtr, ytr)
    pbase = baseline.predict_proba(Xt)[:, 1]
    baseline_metrics = performance(yt, pbase, 0.5)

    dates = {name: {'inicio': item.fecha_prestamo.min().strftime('%Y-%m-%d'),
                    'fin': item.fecha_prestamo.max().strftime('%Y-%m-%d')}
             for name, item in subsets.items()}
    metadata = {
        'datos_version': datos_version['version'],
        'datos_sha256': datos_version['sha256'],
        'semilla_entrenamiento': SEED,
        'version_python': platform.python_version(),
        'fecha_ejecucion': date.today().isoformat(),
        'nombre_proyecto': 'Prediccion de retraso en devolucion de equipos mineros',
        'version_modelo': '1.0.0', 'fecha_elaboracion': '2026-11-06',
        'archivo_origen': 'prestamos_mineria_500000.csv',
        'procedencia': 'Muestra obtenida del archivo de datos de trabajo del usuario; no se ha validado su origen operacional ni su representatividad',
        'observaciones_muestra': len(pd.read_csv(FILE, encoding='utf-8-sig')),
        'observaciones_etiquetadas': total, 'conteos_etiquetas_originales': raw_label_counts,
        'objetivo': 'Con retraso = 1; A tiempo = 0. Pendiente y Perdida excluidos.',
        'exclusion': "Se excluyen pendientes y perdidas: no representan un resultado binario confirmado de devolucion.",
        'columnas_numericas': NUMERIC, 'columnas_categoricas': CATEGORICAL,
        'columnas_modelo': FEATURES,
        'particion_temporal': {name: len(v) for name, v in subsets.items()},
        'periodos_particion': dates,
        'modelos_evaluados': selection, 'modelo_seleccionado': best_name,
        'criterio_seleccion': 'average_precision en validacion',
        'criterio_umbral': 'maximizar F1 en validacion, entre 0.05 y 0.95',
        'umbral': threshold,
        'resultados_test': test_metrics, 'baseline_test': baseline_metrics,
        'version_sklearn': sklearn.__version__, 'version_pandas': pd.__version__,
        'interpretacion': 'Riesgo estimado para analisis academico; no es certeza, no se ha validado en produccion.',
        'filtracion_evitada': ['fecha_devolucion_real', 'dias_uso_real', 'dias_retraso', 'condicion_devolucion', 'tipo_incidencia', 'costos posteriores', 'estado_prestamo'],
    }
    joblib.dump(model, OUT / 'modelo_retrasos.joblib', compress=3)
    metadata['modelo_sha256'] = hashlib.sha256((OUT / 'modelo_retrasos.joblib').read_bytes()).hexdigest()
    (OUT / 'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')

    # Curva precision-recall: el promedio de precision tiene sentido con una clase minoritaria.
    pr, re, _ = precision_recall_curve(yt, ptest)
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    ax.plot(re, pr, lw=2.4, label=f'Modelo (AP={test_metrics["average_precision"]:.3f})')
    ax.axhline(np.mean(yt), color='gray', ls='--', label=f'Prevalencia={np.mean(yt):.3f}')
    ax.set(xlabel='Sensibilidad (recall)', ylabel='Precision', title='Curva precision-recall · conjunto de prueba')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.legend(loc='upper right')
    fig.tight_layout(); fig.savefig(FIGS / 'curva_precision_recall.png', dpi=175); plt.close(fig)

    cm = np.asarray(test_metrics['confusion_matrix'])
    fig, ax = plt.subplots(figsize=(6.0, 4.6))
    im = ax.imshow(cm, cmap='Blues')
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha='center', va='center',
                    color='white' if cm[i, j] > cm.max()*.55 else '#17324D', fontsize=16, fontweight='bold')
    ax.set_xticks([0, 1], ['A tiempo', 'Con retraso'])
    ax.set_yticks([0, 1], ['A tiempo', 'Con retraso'])
    ax.set_xlabel('Prediccion');ax.set_ylabel('Real');ax.set_title('Matriz de confusion · conjunto de prueba')
    fig.colorbar(im, ax=ax, fraction=.046, pad=.04);fig.tight_layout()
    fig.savefig(FIGS / 'matriz_confusion.png',dpi=175);plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 2.3))
    positions = [0.10, .36, .64, .90]
    labels = ['Cliente HTTP\nSwagger / curl', 'FastAPI +\nPydantic', 'Pipeline de ML\n.joblib', 'JSON con riesgo\ny probabilidad']
    for x, lab in zip(positions, labels):
        ax.text(x, .5, lab, transform=ax.transAxes, ha='center', va='center',
                fontsize=10, color='#102E43', bbox={'boxstyle':'round,pad=.65','facecolor':'#E6F2F8','edgecolor':'#80AFC5'})
    for a,b in zip(positions,positions[1:]):
        ax.annotate('',xy=(b-.12,.5),xytext=(a+.12,.5),xycoords='axes fraction',textcoords='axes fraction',arrowprops={'arrowstyle':'->','color':'#26709E','lw':2})
    ax.axis('off');fig.tight_layout();fig.savefig(FIGS / 'arquitectura_api.png',dpi=185);plt.close(fig)

    # Ejemplo valido basado en una observacion existente, sin datos personales.
    ex = Xv.iloc[0].to_dict()
    ex = {k: (int(v) if k in {'mes','cantidad_prestada','dias_plazo'} else float(v) if k=='valor_unitario_pen' else str(v)) for k,v in ex.items()}
    (ROOT/'ejemplos'/'solicitud.json').write_text(json.dumps(ex, ensure_ascii=False, indent=2), encoding='utf-8')
    (ROOT/'ejemplos'/'solicitud_lote.json').write_text(json.dumps({'registros':[ex,ex]},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'eleccion':best_name,'umbral':threshold,'n':len(df),'validacion':selection,'test':test_metrics,'baseline':baseline_metrics},ensure_ascii=False,indent=2))
    return metadata


if __name__ == '__main__':
    train()
