import React from 'react';

function Navigation({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'dashboard', label: 'Панель', icon: '📊' },
    { id: 'analytics', label: 'Аналитика', icon: '📈' },
    { id: 'history', label: 'История', icon: '🕐' },
    { id: 'schedule', label: 'Расписание', icon: '📅' },
  ];

  return (
    <div className="navigation">
      <div className="nav-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => onTabChange(tab.id)}
          >
            <span className="nav-icon">{tab.icon}</span>
            <span className="nav-label">{tab.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

export default Navigation;
