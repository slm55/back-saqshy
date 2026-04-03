from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import json
from typing import List, Dict, Optional
import random
from datetime import datetime, timedelta


app = FastAPI()
GOOGLE_API_KEY = "AIzaSyCiqmsQW7qY9JhAS5H2xZFglGl7n3R7hco"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow everything for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SafetyIndex(BaseModel):
    current: float
    previous_24h: float
    trend: str  # "increasing", "decreasing", "stable"

# Модель для AI-инсайтов
class AIExecutiveInsight(BaseModel):
    what_is_happening: str
    criticality_level: str
    recommended_actions: List[str]

# Результирующая модель эндпоинта
class DashboardSummary(BaseModel):
    timestamp: str
    safety_index: SafetyIndex
    active_alerts_count: int
    ai_executive_insight: AIExecutiveInsight

@app.get("/api/v1/dashboard/summary", response_model=DashboardSummary)
async def get_dashboard_summary():
    # Имитация динамических данных
    current_val = round(random.uniform(6.5, 8.5), 1)
    prev_val = 7.8
    trend_status = "decreasing" if current_val < prev_val else "increasing"
    
    # Список возможных сценариев для ИИ (для разнообразия при тестах)
    scenarios = [
        {
            "event": "Аномальный рост мелкого хулиганства в Бостандыкском районе (район ТРЦ Mega).",
            "level": "High (Level 4/5)",
            "actions": [
                "Усилить пешее патрулирование ул. Розыбакиева",
                "Проверить работоспособность камер 'Сергек' в секторе B-4",
                "Запросить отчет у службы безопасности ТРЦ"
            ]
        },
        {
            "event": "Высокая вероятность краж в Медеуском районе в связи с массовым мероприятием на Кок-Тобе.",
            "level": "Medium (Level 3/5)",
            "actions": [
                "Передислокация мобильного пункта полиции к станции канатной дороги",
                "Увеличение освещенности прилегающих парковых зон",
                "Мониторинг соцсетей на предмет подозрительной активности"
            ]
        }
    ]
    
    selected = random.choice(scenarios)

    return {
        "timestamp": datetime.now().isoformat(),
        "safety_index": {
            "current": current_val,
            "previous_24h": prev_val,
            "trend": trend_status
        },
        "active_alerts_count": random.randint(1, 5),
        "ai_executive_insight": {
            "what_is_happening": selected["event"],
            "criticality_level": selected["level"],
            "recommended_actions": selected["actions"]
        }
    }

class HexagonRisk(BaseModel):
    hex_id: str
    centroid: List[float] # [lat, lng]
    risk_probability: float
    primary_factor: str
    incident_prediction: str

class RiskLayerResponse(BaseModel):
    projection_time: str
    hexagons: List[HexagonRisk]

@app.get("/api/v1/map/risk-layers", response_model=RiskLayerResponse)
async def get_risk_layers():
    # Координаты центра Алматы
    base_lat, base_lng = 43.238, 76.945
    
    factors = [
        "Недостаточное освещение", 
        "Массовое скопление людей", 
        "Слепая зона видеонаблюдения", 
        "Исторический очаг правонарушений"
    ]
    predictions = [
        "Кража из автотранспорта", 
        "Карманная кража", 
        "Вандализм", 
        "Нарушение общественного порядка"
    ]
    
    hex_data = []
    # Сетка 8x8 вокруг центра города
    for i in range(8):
        for j in range(8):
            lat = round(base_lat + (i - 4) * 0.006, 5)
            lng = round(base_lng + (j - 4) * 0.008, 5)
            risk = round(random.uniform(0.1, 0.98), 2)
            
            is_high_risk = risk > 0.65
            
            hex_data.append(HexagonRisk(
                hex_id=f"HEX-ALM-{i}{j}",
                centroid=[lat, lng],
                risk_probability=risk,
                primary_factor=random.choice(factors) if is_high_risk else "Норма",
                incident_prediction=random.choice(predictions) if is_high_risk else "Нет угроз"
            ))
            
    projection = (datetime.now() + timedelta(hours=1)).strftime("%H:%M")

    return {
        "projection_time": f"Прогноз до {projection}",
        "hexagons": hex_data
    }

class TimePoint(BaseModel):
    time: str
    actual: int
    baseline: int
    is_anomaly: bool

class AnomalyMetadata(BaseModel):
    detected_at: str
    deviation_percent: float
    context: str

class AnomalyResponse(BaseModel):
    metric: str
    timeseries: List[TimePoint]
    anomaly_metadata: AnomalyMetadata

@app.get("/api/v1/analytics/anomalies", response_model=AnomalyResponse)
async def get_anomalies():
    metric_name = "Индекс криминальной активности (ИКА)"
    timeseries = []
    
    # Генерируем данные за последние 12 часов
    now = datetime.now()
    anomaly_hour_index = 8  # Сделаем аномалию 4 часа назад
    
    actual_anomaly_value = 0
    baseline_anomaly_value = 0
    detected_time = ""

    for i in range(12):
        time_point = now - timedelta(hours=(11 - i))
        time_str = time_point.strftime("%H:00")
        
        # Базовая линия (норма для этого часа)
        baseline = random.randint(12, 18)
        
        # Текущее значение (обычно близко к норме)
        actual = baseline + random.randint(-3, 3)
        
        # Искусственный всплеск (аномалия)
        is_anomaly = False
        if i == anomaly_hour_index:
            actual = baseline * 3  # Резкий скачок в 3 раза
            is_anomaly = True
            actual_anomaly_value = actual
            baseline_anomaly_value = baseline
            detected_time = time_str
        elif i > anomaly_hour_index and i < anomaly_hour_index + 3:
            # Плавное затухание аномалии
            actual = baseline + random.randint(10, 15)
            is_anomaly = True

        timeseries.append(TimePoint(
            time=time_str,
            actual=actual,
            baseline=baseline,
            is_anomaly=is_anomaly
        ))

    # Расчет метаданных аномалии
    deviation = round(((actual_anomaly_value - baseline_anomaly_value) / baseline_anomaly_value) * 100, 1)
    
    contexts = [
        "Несанкционированное массовое скопление людей в районе Медео",
        "Технический сбой системы уличного освещения в Турксибском районе",
        "Крупное культурно-массовое мероприятие без должного оцепления",
        "Внезапное снижение плотности патрулирования в квадрате А"
    ]

    return {
        "metric": metric_name,
        "timeseries": timeseries,
        "anomaly_metadata": {
            "detected_at": detected_time,
            "deviation_percent": deviation,
            "context": random.choice(contexts)
        }
    }

class DistrictPoint(BaseModel):
    district: str
    lighting_coverage: int  # % освещенности района
    crime_rate: int         # Условный индекс преступности на 10к населения

class ROIAnalysis(BaseModel):
    investment_zone: str
    expected_crime_reduction: str
    priority: str

class InfrastructureImpactResponse(BaseModel):
    correlation_factor: float
    data_points: List[DistrictPoint]
    roi_analysis: ROIAnalysis

@app.get("/api/v1/analytics/infrastructure-impact", response_model=InfrastructureImpactResponse)
async def get_infrastructure_impact():
    # Реальные районы Алматы
    districts = [
        "Алмалинский", "Бостандыкский", "Медеуский", "Ауэзовский", 
        "Жетысуский", "Турксибский", "Наурызбайский", "Алатауский"
    ]
    
    data_points = []
    
    # Генерируем данные с логикой: больше света -> меньше криминала
    for dist in districts:
        # Имитируем реальную ситуацию: центральные районы освещены лучше
        if dist in ["Медеуский", "Алмалинский", "Бостандыкский"]:
            light = random.randint(75, 95)
            crime = random.randint(5, 15)
        elif dist in ["Алатауский", "Турксибский"]:
            light = random.randint(30, 55)
            crime = random.randint(35, 60)
        else:
            light = random.randint(50, 75)
            crime = random.randint(15, 35)
            
        data_points.append(DistrictPoint(
            district=dist,
            lighting_coverage=light,
            crime_rate=crime
        ))

    # ROI Анализ: выбираем район с худшим освещением
    worst_district = min(data_points, key=lambda x: x.lighting_coverage)

    return {
        "correlation_factor": -0.87, # Сильная обратная связь
        "data_points": data_points,
        "roi_analysis": {
            "investment_zone": f"Район {worst_district.district}",
            "expected_crime_reduction": "15-25% при доведении освещения до 85%",
            "priority": "Критический" if worst_district.lighting_coverage < 40 else "Высокий"
        }
    }

class IncidentItem(BaseModel):
    id: str
    type: str
    status: str
    location_name: str
    coordinates: List[float] # [lat, lng]
    time_ago: str
    priority: str # Добавим для визуальной фильтрации на фронтенде

class RecentIncidentsResponse(BaseModel):
    count: int
    items: List[IncidentItem]

@app.get("/api/v1/incidents/recent", response_model=RecentIncidentsResponse)
async def get_recent_incidents():
    # Справочники для генерации реалистичных данных
    incident_types = {
        "Вандализм": "Low",
        "Кража": "Medium",
        "Нарушение тишины": "Low",
        "ДТП": "Medium",
        "Подозрительное лицо": "Medium",
        "Драка": "High",
        "Грабеж": "High"
    }
    
    locations = [
        {"name": "Парк им. 28 гвардейцев-панфиловцев", "coords": [43.259, 76.953]},
        {"name": "ТРЦ 'Достык Плаза'", "coords": [43.233, 76.957]},
        {"name": "Арбат (ул. Панфилова)", "coords": [43.262, 76.942]},
        {"name": "Станция метро 'Алмалы'", "coords": [43.250, 76.945]},
        {"name": "Парк Первого Президента", "coords": [43.189, 76.883]},
        {"name": "Площадь Республики", "coords": [43.238, 76.945]},
        {"name": "Район Зеленого базара", "coords": [43.264, 76.955]},
        {"name": "Атакент", "coords": [43.224, 76.907]}
    ]
    
    statuses = ["Активно", "Проверка", "Завершено", "Направлен патруль"]
    
    items = []
    
    # Генерируем 12 последних событий
    for i in range(12):
        loc = random.choice(locations)
        inc_type = random.choice(list(incident_types.keys()))
        
        # Генерируем случайное время назад (от 2 до 120 минут)
        minutes = random.randint(2, 120)
        time_str = f"{minutes} мин. назад" if minutes < 60 else f"{minutes // 60} ч. назад"
        
        items.append(IncidentItem(
            id=f"INC-{1000 - i}",
            type=inc_type,
            status=random.choice(statuses) if i < 5 else "Завершено",
            location_name=loc["name"],
            coordinates=loc["coords"],
            time_ago=time_str,
            priority=incident_types[inc_type]
        ))
    
    # Сортируем: сначала новые (условно, по ID)
    items.sort(key=lambda x: x.id, reverse=True)

    return {
        "count": len(items),
        "items": items
    }

class SimulationRequest(BaseModel):
    district: str                    # Район Алматы
    additional_patrols: int          # Кол-во новых патрулей
    improved_lighting_zones: List[str] # Конкретные улицы/сектора
    event_context: Optional[str]     # Например: "Концерт на Астана Квадрате"
    date_time: str                   # "2026-04-03T22:00:00"
    additional_notes: Optional[str]  # Любые доп. данные от оператора

@app.post("/api/v1/simulation/predict")
async def simulate_prediction(req: SimulationRequest):
    # --- ШАГ 1: Собираем внутренние данные сервера (Server-side Context) ---
    # В реальности тут были бы запросы к БД. Для хакатона имитируем:
    server_context = {
        "current_crime_rate": 6.8, 
        "active_incidents_in_district": 4,
        "historical_impact_of_patrols": "Увеличение патрулей на 1 ед. обычно снижает риск на 3-5%",
        "weather": "Дождь (снижает уличную активность, но ухудшает видимость)"
    }

    # --- ШАГ 2: Формируем "Жирный" Промпт для Gemini ---
    prompt = f"""
    Ты — продвинутый ИИ-аналитик системы Smart City Almaty 'SAQSHY'. 
    Твоя задача: провести What-if анализ безопасности.

    ВХОДНЫЕ ДАННЫЕ ОТ ПОЛЬЗОВАТЕЛЯ:
    - Район: {req.district}
    - Доп. патрули: {req.additional_patrols}
    - Улучшение освещения: {", ".join(req.improved_lighting_zones)}
    - Контекст события: {req.event_context}
    - Время: {req.date_time}
    - Заметки: {req.additional_notes}

    ТЕКУЩИЙ КОНТЕКСТ СИСТЕМЫ (SERVER DATA):
    - Текущий индекс безопасности района: {server_context['current_crime_rate']}
    - Активных инцидентов сейчас: {server_context['active_incidents_in_district']}
    - Погода: {server_context['weather']}

    ЗАДАНИЕ:
    Рассчитай новый индекс безопасности (от 0 до 10) и дельту изменений. 
    Напиши краткое профессиональное резюме на русском языке.

    ОТВЕТЬ СТРОГО В ФОРМАТЕ JSON:
    {{
      "simulated_safety_score": float,
      "score_delta": "string (например +0.5)",
      "risk_mitigation_summary": "string"
    }}
    """

    try:
        # --- ШАГ 3: Запрос к Gemini ---
        response = model.generate_content(prompt)
        
        # Очистка ответа от возможных markdown-тегов ```json
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        
        return eval(clean_json) # В продакшене лучше использовать json.loads()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка симуляции: {str(e)}")