import React, { useState, useEffect } from 'react';
import { energyAPI, anomalyAPI } from '../../services/api';
import { exportToCSV, exportToJSON } from '../../utils/exportUtils';

const anomalyTypeLabels = {
  overload: 'Перегрузка',
  forgotten: 'Забытое устройство',
  night_work: 'Ночная работа',
  high_baseline: 'Высокий фон',
  spike: 'Резкий скачок',
};

const severityLabels = { high: 'Высокая', medium: 'Средняя', low: 'Низкая' };

function HistoricalData() {
  const [energyData, setEnergyData] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      const now = new Date();
      const year = now.getFullYear();
      const month = now.getMonth() + 1;

      await anomalyAPI.detectAnomalies();

      const [dailyRes, anomaliesRes] = await Promise.all([
        energyAPI.getDaily(year, month),
        anomalyAPI.getAnomalies(),
      ]);

      setEnergyData(dailyRes.data || []);
      setAnomalies(anomaliesRes.data || []);
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
      setEnergyData([]);
      setAnomalies([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleExport = (format) => {
    const now = new Date();
    const name = `energy_${now.getFullYear()}_${now.getMonth() + 1}`;
    if (format === 'csv') {
      exportToCSV(energyData, `${name}.csv`);
    } else if (format === 'json') {
      exportToJSON(energyData, `${name}.json`);
    }
  };

  const handleClear = () => {
    setEnergyData([]);
    setAnomalies([]);
  };

  return (
    <div className="historical-section">
      <h2>Исторические данные</h2>

      <div className="export-controls">
        <button className="btn-export" onClick={fetchData} disabled={loading}>
          {loading ? 'Обновление...' : 'Обновить'}
        </button>
        <button className="btn-export" onClick={() => handleExport('csv')}>
          CSV
        </button>
        <button className="btn-export" onClick={() => handleExport('json')}>
          JSON
        </button>
        <button className="btn-export btn-clear" onClick={handleClear}>
          Очистить
        </button>
      </div>

      {loading && <div className="empty-state"><p>Загрузка...</p></div>}

      {!loading && energyData.length > 0 && (
        <div className="data-table">
          <table>
            <thead>
              <tr>
                <th>Дата</th>
                <th>Потребление (кВт·ч)</th>
                <th>Средняя мощность (кВт)</th>
                <th>Пиковая мощность (кВт)</th>
                <th>Стоимость (₽)</th>
              </tr>
            </thead>
            <tbody>
              {energyData.map((row, idx) => (
                <tr key={idx}>
                  <td>{row.date || row.month || 'N/A'}</td>
                  <td>{parseFloat(row.total_energy || 0).toFixed(2)}</td>
                  <td>{parseFloat(row.avg_power || 0).toFixed(2)}</td>
                  <td>{parseFloat(row.peak_power || 0).toFixed(2)}</td>
                  <td>{parseFloat(row.cost || 0).toFixed(0)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && anomalies.length > 0 && (
        <div className="anomaly-history">
          <h3>Выявленные аномалии</h3>
          <div className="data-table">
            <table>
              <thead>
                <tr>
                  <th>Дата</th>
                  <th>Устройство</th>
                  <th>Тип</th>
                  <th>Серьёзность</th>
                  <th>Описание</th>
                  <th>Статус</th>
                </tr>
              </thead>
              <tbody>
                {anomalies.map((a) => (
                  <tr key={a.id} className={`anomaly-row severity-${a.severity}`}>
                    <td>{new Date(a.detected_at).toLocaleString('ru-RU')}</td>
                    <td>{a.device_name}</td>
                    <td>{anomalyTypeLabels[a.anomaly_type] || a.anomaly_type}</td>
                    <td>
                      <span className={`severity-badge severity-${a.severity}`}>
                        {severityLabels[a.severity]}
                      </span>
                    </td>
                    <td>{a.description}</td>
                    <td>{a.resolved_at ? 'Решена' : 'Активна'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {!loading && energyData.length === 0 && anomalies.length === 0 && (
        <div className="empty-state">
          <p>Нет данных</p>
        </div>
      )}
    </div>
  );
}

export default HistoricalData;