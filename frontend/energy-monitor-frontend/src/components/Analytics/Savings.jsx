import React, { useState, useEffect } from 'react';
import { anomalyAPI } from '../../services/api';

const typeIcons = {
  schedule: '🕐',
  night_shift: '🌙',
  replacement: '💡',
  preset: '📋',
};

const typeLabels = {
  schedule: 'Расписание',
  night_shift: 'Ночной тариф',
  replacement: 'Замена',
  preset: 'Сценарий',
};

function Savings() {
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ totalSavings: 0, count: 0, implemented: 0 });

  const fetchScenarios = async () => {
    try {
      setLoading(true);
      const res = await anomalyAPI.getScenarios();
      const data = res.data;
      setScenarios(data);
      setStats({
        totalSavings: data.reduce((s, sc) => s + sc.estimated_savings, 0),
        count: data.length,
        implemented: data.filter(sc => sc.implemented).length,
      });
    } catch {
      console.error('Ошибка загрузки сценариев');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setLoading(true);
      await anomalyAPI.generateScenarios();
      await fetchScenarios();
    } catch {
      console.error('Ошибка генерации');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScenarios();
  }, []);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2 style={{ margin: 0 }}>💡 Сценарии экономии</h2>
        <button
          onClick={handleGenerate}
          disabled={loading}
          style={{
            padding: '8px 18px', borderRadius: 8, border: 'none',
            background: '#10b981', color: '#fff', fontSize: 14,
            cursor: 'pointer', fontWeight: 500,
          }}
        >
          🔄 Сгенерировать
        </button>
      </div>

      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, marginBottom: 24,
      }}>
        <div style={{ background: '#f0fdf4', padding: 16, borderRadius: 10 }}>
          <div style={{ fontSize: 12, color: '#6b7280' }}>Потенциальная экономия</div>
          <div style={{ fontSize: 24, fontWeight: 700, color: '#10b981' }}>
            {stats.totalSavings.toFixed(0)} ₽/мес
          </div>
        </div>
        <div style={{ background: '#eff6ff', padding: 16, borderRadius: 10 }}>
          <div style={{ fontSize: 12, color: '#6b7280' }}>Рекомендаций</div>
          <div style={{ fontSize: 24, fontWeight: 700, color: '#3b82f6' }}>
            {stats.count}
          </div>
        </div>
        <div style={{ background: '#fef3c7', padding: 16, borderRadius: 10 }}>
          <div style={{ fontSize: 12, color: '#6b7280' }}>Внедрено</div>
          <div style={{ fontSize: 24, fontWeight: 700, color: '#f59e0b' }}>
            {stats.implemented}
          </div>
        </div>
      </div>

      {loading && <div style={{ textAlign: 'center', padding: 20, color: '#9ca3af' }}>Загрузка...</div>}

      {!loading && scenarios.length === 0 && (
        <div style={{
          textAlign: 'center', padding: 40, color: '#9ca3af',
          background: '#f9fafb', borderRadius: 10,
        }}>
          <div style={{ fontSize: 32, marginBottom: 10 }}>💡</div>
          <div>Нет рекомендаций. Нажмите «Сгенерировать» для анализа.</div>
        </div>
      )}

      <div style={{ display: 'grid', gap: 10 }}>
        {scenarios.map(sc => (
          <div
            key={sc.id}
            style={{
              display: 'flex', alignItems: 'center', gap: 14,
              padding: '14px 18px', borderRadius: 10,
              background: sc.implemented ? '#f0fdf4' : '#fff',
              border: '1px solid #e5e7eb',
            }}
          >
            <div style={{ fontSize: 24 }}>{typeIcons[sc.scenario_type] || '⚡'}</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600, fontSize: 14 }}>{sc.title}</div>
              <div style={{ fontSize: 13, color: '#6b7280' }}>{sc.description}</div>
              <div style={{ fontSize: 12, color: '#9ca3af', marginTop: 2 }}>
                {typeLabels[sc.scenario_type] || sc.scenario_type} · {sc.device_name}
              </div>
            </div>
            <div style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
              <div style={{ fontWeight: 700, color: '#10b981' }}>
                -{sc.estimated_savings.toFixed(0)} ₽
              </div>
              <div style={{ fontSize: 12, color: '#6b7280' }}>
                {sc.savings_percent}%
              </div>
            </div>
            <div style={{
              padding: '4px 10px', borderRadius: 12, fontSize: 12,
              background: sc.implemented ? '#d1fae5' : '#fef3c7',
              color: sc.implemented ? '#065f46' : '#92400e',
            }}>
              {sc.implemented ? '✓ Применено' : 'Готово'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Savings;
