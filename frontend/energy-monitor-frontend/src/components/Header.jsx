import React from 'react';

function Header({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'dashboard', label: 'Панель управления' },
    { id: 'history', label: 'История' },
    { id: 'savings', label: 'Экономия' },
  ];

  return (
    <div className="header">
      <div className="header-content">
        <h1 className="header-title">
          ELMS
        </h1>
        <div className="navigation">
          <div className="nav-tabs">
            {tabs.map(tab => (
              <button
                key={tab.id}
                className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => onTabChange(tab.id)}
              >
                <span className="nav-label">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Header;
