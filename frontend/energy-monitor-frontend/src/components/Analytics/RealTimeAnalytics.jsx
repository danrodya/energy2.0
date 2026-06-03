import React, { useState, useEffect } from 'react';
import PowerChart from '../Charts/PowerChart';
import TopConsumersChart from '../Charts/TopConsumersChart';
import StatCard from '../StatCard';
import { energyAPI } from '../../services/api';
import { calculateAverage, calculatePeak, calculateTotal } from '../../utils/chartUtils';

function RealTimeAnalytics() {
  const [hourlyData, setHourlyData] = useState([]);
  const [topConsumers, setTopConsumers] = useState([]);
  const [stats, setStats] = useState({
    avgPower: 0,
    peakPower: 0,
    totalEnergy: 0,
  });
  const [loading, setLoading] = useState(false);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);

      const today = new Date().toISOString().split('T');
      const [hourlyRes, topRes] = await Promise.all([
        energyAPI.getHourly(today),
        energyAPI.getTopConsumers(),
      ]);

      const hourly = hourlyRes.data;
      const top = topRes.data;

      setHourlyData(hourly);
      setTopConsumers(top);

      setStats({
        avgPower: calculateAverage(hourly, 'power'),
        peakPower: calculatePeak(hourly, 'power'),
        totalEnergy: calculateTotal(hourly, 'energy'),
      });
    } catch (error) {
      console.error('Ошибка загрузки аналитики:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 30000); // Обновлять каждые 30 сек
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="analytics-section">
      <h2>Аналитика в реальном времени</h2>

      <div className="stats-grid-compact">
        <StatCard
          title="Средняя мощность"
          value={stats.avgPower}
          unit="кВт"
          icon="📊"
          color="#667eea"
        />
        <StatCard
          title="Пиковая мощность"
          value={stats.peakPower}
          unit="кВт"
          icon="📈"
          color="#f59e0b"
        />
        <StatCard
          title="Потребление сегодня"
          value={stats.totalEnergy}
          unit="кВт·ч"
          icon="⚡"
          color="#10b981"
        />
      </div>

      <div className="charts-grid">
        <PowerChart data={hourlyData} loading={loading} />
        <TopConsumersChart data={topConsumers} loading={loading} />
      </div>

      <button className="btn-refresh-analytics" onClick={fetchAnalytics}>
        🔄 Обновить
      </button>
    </div>
  );
}

export default RealTimeAnalytics;
