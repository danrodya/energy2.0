import React, { useState, useEffect } from 'react';
import { devicesAPI } from '../../services/api';
import { scheduleAPI } from '../../services/scheduleAPI';
import styles from './Schedule.module.css';

const Schedule = () => {
  const [devices, setDevices] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [newSchedule, setNewSchedule] = useState({ deviceId: '', time: '', action: 'off' });
  const [expandedDevice, setExpandedDevice] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [devicesRes, schedulesRes] = await Promise.all([
        devicesAPI.getAll(),
        scheduleAPI.getAll(),
      ]);
      setDevices(devicesRes.data || []);
      setSchedules(schedulesRes.data || []);
    } catch (err) {
      console.error('Schedule fetch error:', err);
      setError('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const getDeviceSchedules = (deviceId) =>
    schedules.filter((s) => s.device === deviceId);

  const addSchedule = async (deviceId) => {
    if (!newSchedule.time) {
      alert('Укажите время!');
      return;
    }
    try {
      const res = await scheduleAPI.create({
        device: deviceId,
        time: newSchedule.time,
        action: newSchedule.action,
      });
      setSchedules((prev) => [...prev, res.data]);
      setNewSchedule({ deviceId: '', time: '', action: 'off' });
    } catch (err) {
      console.error('Add schedule error:', err);
      setError('Ошибка при добавлении расписания');
    }
  };

  const removeSchedule = async (deviceId, scheduleId) => {
    try {
      await scheduleAPI.delete(scheduleId);
      setSchedules((prev) => prev.filter((s) => s.id !== scheduleId));
    } catch (err) {
      console.error('Delete schedule error:', err);
      setError('Ошибка при удалении расписания');
    }
  };

  const toggleSchedule = async (deviceId, scheduleId) => {
    try {
      const res = await scheduleAPI.toggleEnabled(scheduleId);
      setSchedules((prev) =>
        prev.map((s) => (s.id === scheduleId ? res.data : s))
      );
    } catch (err) {
      console.error('Toggle schedule error:', err);
      setError('Ошибка при переключении расписания');
    }
  };

  const toggleDevice = async (deviceId) => {
    try {
      await devicesAPI.toggle(deviceId);
      const res = await devicesAPI.getAll();
      setDevices(res.data || []);
    } catch (err) {
      console.error('Toggle device error:', err);
      setError('Ошибка при переключении устройства');
    }
  };

  const getDeviceType = (device) => device.device_type || 'other';

  const getDeviceIcon = (type) => {
    switch (type) {
      case 'climate':
        return '❄️';
      case 'light':
        return '💡';
      case 'appliance':
        return '🧊';
      default:
        return '⚡';
    }
  };

  if (loading && devices.length === 0) {
    return <div className={styles.container}><p>Загрузка...</p></div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>📅 Расписание розеток</h2>
        <p className={styles.subtitle}>Настрой автоматическое включение/отключение устройств</p>
      </div>

      {error && (
        <div className="error-banner">
          <div className="error-content">
            <span className="error-text">{error}</span>
            <button className="error-close" onClick={() => setError(null)}>✕</button>
          </div>
        </div>
      )}

      <div className={styles.devicesList}>
        {devices.map((device) => {
          const deviceSchedules = getDeviceSchedules(device.id);
          return (
            <div key={device.id} className={styles.deviceCard}>
              <div className={styles.deviceHeader}>
                <div className={styles.deviceInfo}>
                  <span className={styles.deviceIcon}>{getDeviceIcon(getDeviceType(device))}</span>
                  <div className={styles.deviceName}>
                    <h3>{device.name}</h3>
                    <span className={`${styles.status} ${styles[`status-${device.power_state}`]}`}>
                      {device.power_state === 'on' ? '🟢 Включено' : '🔴 Отключено'}
                    </span>
                  </div>
                </div>

                <div className={styles.deviceActions}>
                  <button
                    className={`${styles.toggleBtn} ${styles[`toggle-${device.power_state}`]}`}
                    onClick={() => toggleDevice(device.id)}
                  >
                    {device.power_state === 'on' ? 'Отключить' : 'Включить'}
                  </button>
                  <button
                    className={styles.expandBtn}
                    onClick={() => setExpandedDevice(expandedDevice === device.id ? null : device.id)}
                  >
                    {expandedDevice === device.id ? '▼' : '▶'}
                  </button>
                </div>
              </div>

              {expandedDevice === device.id && (
                <div className={styles.deviceExpanded}>
                  <div className={styles.schedulesList}>
                    <h4>Текущее расписание:</h4>
                    {deviceSchedules.length > 0 ? (
                      <div className={styles.scheduleItems}>
                        {deviceSchedules.map((schedule) => (
                          <div key={schedule.id} className={styles.scheduleItem}>
                            <input
                              type="checkbox"
                              checked={schedule.enabled}
                              onChange={() => toggleSchedule(device.id, schedule.id)}
                              className={styles.checkbox}
                            />
                            <div className={styles.scheduleInfo}>
                              <span className={styles.time}>🕐 {schedule.time}</span>
                              <span className={`${styles.action} ${styles[`action-${schedule.action}`]}`}>
                                {schedule.action === 'on' ? '✅ Включить' : '❌ Отключить'}
                              </span>
                            </div>
                            <button
                              className={styles.deleteBtn}
                              onClick={() => removeSchedule(device.id, schedule.id)}
                            >
                              🗑️ Удалить
                            </button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className={styles.noSchedule}>Расписание не установлено</p>
                    )}
                  </div>

                  <div className={styles.addScheduleForm}>
                    <h4>Добавить расписание:</h4>
                    <div className={styles.formRow}>
                      <div className={styles.formGroup}>
                        <label>Время:</label>
                        <input
                          type="time"
                          value={newSchedule.deviceId === device.id ? newSchedule.time : ''}
                          onChange={(e) =>
                            setNewSchedule({
                              ...newSchedule,
                              deviceId: device.id,
                              time: e.target.value,
                            })
                          }
                          className={styles.timeInput}
                        />
                      </div>

                      <div className={styles.formGroup}>
                        <label>Действие:</label>
                        <select
                          value={newSchedule.deviceId === device.id ? newSchedule.action : 'off'}
                          onChange={(e) =>
                            setNewSchedule({
                              ...newSchedule,
                              deviceId: device.id,
                              action: e.target.value,
                            })
                          }
                          className={styles.actionSelect}
                        >
                          <option value="on">✅ Включить</option>
                          <option value="off">❌ Отключить</option>
                        </select>
                      </div>

                      <button
                        className={styles.addBtn}
                        onClick={() => addSchedule(device.id)}
                      >
                        ➕ Добавить
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className={styles.stats}>
        <div className={styles.statCard}>
          <h4>Всего устройств</h4>
          <p className={styles.statValue}>{devices.length}</p>
        </div>
        <div className={styles.statCard}>
          <h4>Включено</h4>
          <p className={styles.statValue}>{devices.filter((d) => d.power_state === 'on').length}</p>
        </div>
        <div className={styles.statCard}>
          <h4>Расписаний установлено</h4>
          <p className={styles.statValue}>{schedules.length}</p>
        </div>
        <div className={styles.statCard}>
          <h4>Активных расписаний</h4>
          <p className={styles.statValue}>{schedules.filter((s) => s.enabled).length}</p>
        </div>
      </div>
    </div>
  );
};

export default Schedule;