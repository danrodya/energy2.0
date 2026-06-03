# 🏠 Система мониторинга энергопотерь

Система управления умным домом с поддержкой расписания для розеток и анализом энергопотребления.  
Проект состоит из **Django backend** и **React frontend**.    

Находится на стадии **разработки**

---


## 🛠️ Стек технологий

Backend:
- Django 4.2  
- Django REST Framework  
- PostgreSQL  

Frontend:
- React 18  
- Create React App  

---

## Запуск проекта

### 1. Клонирование репозитория

git clone https://github.com/kollosvas/monitor-energy.git  
cd monitor-energy

---

### 2. Backend
cd backend  

#### 2.1 База данных postgreSQL  
1.1. Установить с официального сайта postgreSQL 18.  
1.2. Для пользователя postgres установить пароль 'admin437'.  
1.3. Инициализация бд: psql -U postgres -f db_init.sql  


cd backend  
python -m venv venv  
venv\Scripts\activate       (Windows)  
source venv/bin/activate    (Linux/macOS)  
pip install -r requirements.txt  

python manage.py makemigrations devices  
python manage.py makemigrations energy  
python manage.py migrate  

python manage.py createsuperuser

python manage.py generate_sample_data

(venv) python manage.py runserver  
→ http://localhost:8000

В новом терминале (для генерации данных):    

cd backend  
venv\Scripts\activate       (Windows)  
source venv/bin/activate    (Linux/macOS)  
(venv) python manage.py generate_realtime_data

---

### 3. Frontend
Скачать и установить node.js  

cd ../frontend/energy-monitor-frontend  
npm install -g serve    

serve -s build  

→ http://localhost:3000

---

## 🌐 API

Устройства:
- GET    /api/devices/
- GET    /api/devices/{id}/
- POST   /api/devices/
- PUT    /api/devices/{id}/
- DELETE /api/devices/{id}/
- POST   /api/devices/{id}/toggle/
- GET    /api/devices/summary/

Расписания:
- GET    /api/schedules/
- GET    /api/schedules/{id}/
- POST   /api/schedules/
- PUT    /api/schedules/{id}/
- DELETE /api/schedules/{id}/
- POST   /api/schedules/create_for_device/
- GET    /api/schedules/by_device/?device_id=<id>
- PATCH  /api/schedules/{id}/toggle_enabled/

Энергия:
- GET /api/energy/current/
- GET /api/energy/today/
- GET /api/energy/hourly/?date=YYYY-MM-DD
- GET /api/energy/daily/?year=YYYY&month=MM
- GET /api/energy/monthly/?year=YYYY
- GET /api/energy/statistics/
- GET /api/energy/top_consumers/
- GET /api/energy/forecast/
- GET /api/energy/export/?format=csv|json
- GET /api/energy/anomalies/
- POST /api/energy/detect_anomalies/
- POST /api/energy/resolve_anomaly/
- GET /api/energy/saving_scenarios/
- POST /api/energy/generate_scenarios/

---

## 🤖 ML-система детекции аномалий

Per-device модель Isolation Forest, обучается автоматически при создании устройства.

### Архитектура

- **Per-device модели**: `ml_models/anomaly_model_<slug>.pkl` (slug от `device.name`).
- **23 фичи** в порядке: `mean_norm, std_norm, min_norm, max_norm, median_norm, p25_norm, p75_norm, iqr_norm, diff_mean, diff_std, expected_dev_mean, expected_dev_max, high_outlier_ratio, low_outlier_ratio, peak_to_mean, cv, fft_energy, stuck_run_len, monotonic_run_len, hour_sin, hour_cos, dow_sin, dow_cos`.
- **Нормализация** на `rated_power` (паспортная мощность устройства), а не на `window.max()`.
- **Фильтрация «грязных» данных** при обучении: верхние 5% по мощности исключаются как выбросы.
- **Ожидаемый почасовой паттерн** строится из «чистых» сэмплов (`is_anomaly=False AND is_legal_spike=False`).
- **Fallback**: если модели для устройства нет, эвристики (`overload`, `forgotten`, `night_work`) всё равно работают.
- **Min 100 сэмплов** для обучения (иначе warning, модель не создаётся).

### Автообучение

Срабатывает через `post_save` сигнал на `Device` (см. `backend/devices/signals.py`). Синхронное — без Celery, в `ready()` `DevicesConfig`.

### Управление моделями

```bash
# Обучить модели для всех устройств (пропускает существующие)
python manage.py train_device_model

# Принудительное переобучение
python manage.py train_device_model --retrain

# Конкретное устройство
python manage.py train_device_model --device-id 1

# Инкрементальное обновление на последних 7 днях
python manage.py update_device_model
python manage.py update_device_model --device-id 1
```

### Синтетические данные и тесты

Генератор реалистичных профилей потребления с 4 типами аномалий (`point_outlier`, `contextual`, `stuck`, `drift`) и легальными всплесками:

```bash
# Сгенерировать синтетический датасет и обучить общую модель
python manage.py generate_synthetic_dataset --days 45

# Только CSV без обучения
python manage.py generate_synthetic_dataset --days 30 --save-csv ./data.csv --no-train

# Юнит-тесты (11 тестов, ~5 сек)
python ml_models/tests_synth.py
```

### Известные ограничения

- Isolation Forest — unsupervised, F1 ≈ 0.07 на синтетике (P=0.065, R=0.078).
- Хорошо ловит: stuck, point outliers, contextual (на всех устройствах).
- Плохо ловит: drift на слабых устройствах (малая амплитуда).
- Для supervised-обучения нужны метки; текущая модель использует `contamination=0.10` как априорное знание доли аномалий.

---
### ПРИМЕРЫ РАБОТЫ:
<img width="1057" height="1781" alt="image" src="https://github.com/user-attachments/assets/19f47327-614f-4239-9d2c-024ce1239046" />

<img width="1055" height="1786" alt="image" src="https://github.com/user-attachments/assets/39d80d2f-9907-4ccd-a379-cec8652df0e1" />

<img width="1075" height="1793" alt="image" src="https://github.com/user-attachments/assets/6ee20be8-dcb4-4b10-b665-ca15b73219ff" />

<img width="1074" height="1792" alt="image" src="https://github.com/user-attachments/assets/2ad3398b-8301-4604-9c14-4634172e7e48" />

<img width="1073" height="1793" alt="image" src="https://github.com/user-attachments/assets/96ca9ec3-ade9-4a03-a1a2-190d431178cd" />

---

Последнее обновление: 3 июня 2026 года

## Что нового (changelog)

### Beta-fixes + ML pipeline
- Per-device ML-модели (slug-based pkl) с автообучением при создании устройства.
- 23-мерный feature extractor, синхронизирован с `ml_models/features.py`.
- Синтетический генератор данных (45 дней, 4 типа аномалий) + 11 юнит-тестов.
- Management commands: `train_device_model`, `update_device_model`, `generate_synthetic_dataset`.
- Backend: фикс `manage.py:22`, `ScheduleViewSet` в роутере, убран невалидный `default='on'`, `prefetch_related`, добавлены `PresetSchedule/PresetScheduleEntry`.
- Frontend: убраны broken endpoints из `api.js`, переписан `scheduleAPI.js`, фикс даты в `RealTimeAnalytics.jsx`, `Schedule.jsx` подключён к API, добавлены `.errorBanner/.empty` стили.
