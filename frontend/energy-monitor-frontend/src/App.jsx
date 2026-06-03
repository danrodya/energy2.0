import React, { useState, useEffect } from 'react';
import './App.css';
import StatCard from './components/StatCard';
import DeviceGrid from './components/DeviceGrid';
import Header from './components/Header';
import HistoricalData from './components/Analytics/HistoricalData';
import Savings from './components/Analytics/Savings';
import AnomalyBanner from './components/AnomalyBanner';
import { devicesAPI, energyAPI } from './services/api';
import AddDeviceModal from './components/AddDeviceModal';
import TimeZoneSelector from './components/TimeSelectZone';


function App() {
  const [devices, setDevices] = useState([]);
  const [stats, setStats] = useState({
    totalPower: 0,
    todayEnergy: 0,
    todayCost: 0,
    activeDevices: 0,
    peakPower: 0,
    avgPower: 0,
  });
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [addLoading, setAddLoading] = useState(false);


  const fetchData = async () => {
    try {
      setError(null);

      const [currentRes, todayRes] = await Promise.all([
        energyAPI.getCurrent(),
        energyAPI.getToday(),
      ]);

      const currentData = currentRes.data;
      const todayData = todayRes.data;
      const devicesList = currentData.devices;

      setDevices(devicesList);
      setStats({
        totalPower: currentData.total_power,
        todayEnergy: todayData.total_energy,
        todayCost: todayData.total_cost,
        activeDevices: devicesList.filter(d => d.power_state === 'on').length,
        peakPower: Math.max(...devicesList.map(d => d.current_power), 0),
        avgPower: currentData.total_power / (devicesList.length || 1),
      });
    } catch (err) {
      console.error('Ошибка загрузки данных:', err);
      setError('Ошибка подключения к серверу. Проверьте что Django запущен на http://localhost:8000');
    }
  };


  const handleAddDeviceClick = () => {
    setIsAddModalOpen(true);
  };

  const handleCreateDevice = async (data) => {
    try {
      setAddLoading(true);
      setError(null);
      await devicesAPI.create(data);
      await fetchData();
      setIsAddModalOpen(false);
    } catch (err) {
      console.error('Ошибка при добавлении устройства:', err);
      setError('Ошибка при добавлении устройства');
    } finally {
      setAddLoading(false);
    }
  };


  const handleToggleDevice = async (deviceId) => {
    try {
      await devicesAPI.toggle(deviceId);
      await fetchData();
    } catch (err) {
      console.error('Ошибка при переключении устройства:', err);
      setError('Ошибка при переключении устройства');
    }
  };

  const handleDeleteDevice = async (deviceId) => {
    const prevDevices = [...devices];
    setDevices(prev => prev.filter(d => d.id !== deviceId));
    try {
      const res = await devicesAPI.remove(deviceId);
      if (res.status !== 204) {
        throw new Error('Unexpected response status: ' + res.status);
      }
    } catch (err) {
      console.error('Ошибка при удалении устройства:', err);
      setDevices(prevDevices);
      const msg = err.response?.data?.error || err.response?.data?.detail || 'Ошибка при удалении устройства';
      setError(msg);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />
      {error && (
        <div className="error-banner">
          <div className="error-content">
            <span className="error-text">{error}</span>
            <button className="error-close" onClick={() => setError(null)}>✕</button>
          </div>
        </div>
      )}

      <div className="container">
        <div className="app-context">
          <TimeZoneSelector />
        </div>
        {activeTab === 'dashboard' && (
          <>
            <div className="section-info">
              <div className="info-content">
                Добро пожаловать! <br /><br />
                В приложении вы сможете следить за потреблением энергии подключенными устройствами, управлять их энергопотреблением, получать полезные советы и уведомления о важных событиях.
              </div>
              <AnomalyBanner />
              <div className="stats-section">
                <h2 className="section-title">Статистика</h2>
                <div className="stats-grid">
                  <StatCard
                    title="Потребление сейчас"
                    value={stats.totalPower}
                    unit="кВт"
                    color="#667eea"
                  />
                  <StatCard
                    title="За сегодня"
                    value={stats.todayEnergy}
                    unit="кВт·ч"
                    color="#10b981"
                  />
                  <StatCard
                    title="Стоимость сегодня"
                    value={Math.round(stats.todayCost)}
                    unit="₽"
                    color="#f59e0b"
                  />
                  <StatCard
                    title="Активные устройства"
                    value={stats.activeDevices}
                    unit={`из ${devices.length}`}
                    color="#ef4444"
                  />
                  <StatCard
                    title="Пиковое потребление"
                    value={stats.peakPower}
                    unit="кВт"
                    color="#8b5cf6"
                  />
                  <StatCard
                    title="Среднее потребление"
                    value={stats.avgPower}
                    unit="кВт"
                    color="#06b6d4"
                  />
                </div>
              </div>
            </div>

            <DeviceGrid
              devices={devices}
              onToggleDevice={handleToggleDevice}
              onDeleteDevice={handleDeleteDevice}
              onAddDevice={handleAddDeviceClick}
            />

          </>
        )}

        {activeTab === 'history' && <HistoricalData />}
        {activeTab === 'savings' && <Savings />}
      </div>

      <footer className="footer">
        <span>
          Последнее обновление: {new Date().toLocaleTimeString('ru-RU')}
        </span>
      </footer>
      <AddDeviceModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSubmit={handleCreateDevice}
        loading={addLoading}
      />
    </div>
  );
}

export default App;
