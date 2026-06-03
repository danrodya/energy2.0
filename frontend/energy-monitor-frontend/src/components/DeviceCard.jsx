import React, { useState } from 'react';

function DeviceCard({ device, onToggle, onDelete, loading }) {
  const [toggling, setToggling] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const handleToggle = async () => {
    setToggling(true);
    await onToggle(device.id);
    setToggling(false);
  };

  const handleDelete = async () => {
    await onDelete(device.id);
    setConfirmDelete(false);
  };

  const isOnline = device.status === 'online';
  const isOn = device.power_state === 'on';
  const powerPercent = (device.current_power / device.rated_power) * 100;

  if (confirmDelete) {
    return (
      <div className="device-card" style={{ border: '2px solid #ef4444', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12, minHeight: 200 }}>
        <div style={{ fontSize: 24 }}>🗑️</div>
        <div style={{ fontWeight: 600 }}>Удалить {device.name}?</div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button onClick={handleDelete} style={{ padding: '8px 20px', borderRadius: 8, border: 'none', background: '#ef4444', color: '#fff', cursor: 'pointer', fontWeight: 500 }}>
            Да, удалить
          </button>
          <button onClick={() => setConfirmDelete(false)} style={{ padding: '8px 20px', borderRadius: 8, border: '1px solid #d1d5db', background: '#fff', cursor: 'pointer' }}>
            Отмена
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`device-card ${!isOnline ? 'offline' : ''}`}>
      <div className="device-header">
        <h3 className="device-name">{device.name}</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <button
            onClick={() => setConfirmDelete(true)}
            title="Удалить устройство"
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              fontSize: 16, padding: '2px 6px', opacity: 0.5, color: '#ef4444',
            }}
          >
            🗑️
          </button>
        </div>
      </div>

      <div className="device-type">{device.device_type}</div>

      <div className="device-status-info">
        <span className={`power-status ${isOn ? 'on' : 'off'}`}>
          {isOn ? 'Включен' : 'Выключен'}
        </span>
        <span className={`device-badge ${isOnline ? 'online' : 'offline'}`}>
            {isOnline ? '🟢 В сети' : '🔴 Не в сети'}
          </span>
      </div>

      <div className="device-power-display">
        <div className="power-value">
          <span className="current-power">{device.current_power.toFixed(2)}</span>
          <span className="power-unit">кВт</span>
        </div>
        <div className="power-info">
          из {device.rated_power} кВт
        </div>
      </div>

      <div className="power-bar-container">
        <div className="power-bar">
          <div 
            className="power-bar-fill"
            style={{
              width: `${Math.min(powerPercent, 100)}%`,
              backgroundColor: powerPercent > 80 ? '#ef4444' : powerPercent > 50 ? '#f59e0b' : '#10b981'
            }}
          ></div>
        </div>
        <div className="power-percent">{Math.round(powerPercent)}%</div>
      </div>

      <div className="device-details">
        <div className="detail-item">
          <span className="detail-label">Последнее обновление:</span>
          <span className="detail-value">
            {new Date(device.last_update).toLocaleTimeString('ru-RU')}
          </span>
        </div>
      </div>

      <button
        className={`btn-toggle ${isOn ? 'btn-off' : 'btn-on'}`}
        onClick={handleToggle}
        disabled={toggling || !isOnline}
        title={!isOnline ? 'Устройство оффлайн' : ''}
      >
        {toggling ? '' : isOn ? 'Выключить' : 'Включить'}
      </button>
    </div>
  );
}

export default DeviceCard;
