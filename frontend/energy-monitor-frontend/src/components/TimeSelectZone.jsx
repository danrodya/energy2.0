import React, { useState, useEffect } from 'react';

const russianTimeZones = [
    { value: 'Europe/Kaliningrad', label: 'Калининград (UTC+2)', offset: '+2' },
    { value: 'Europe/Moscow', label: 'Москва (UTC+3)', offset: '+3' },
    { value: 'Europe/Samara', label: 'Самара (UTC+4)', offset: '+4' },
    { value: 'Asia/Yekaterinburg', label: 'Екатеринбург (UTC+5)', offset: '+5' },
    { value: 'Asia/Omsk', label: 'Омск (UTC+6)', offset: '+6' },
    { value: 'Asia/Novosibirsk', label: 'Новосибирск (UTC+7)', offset: '+7' },
    { value: 'Asia/Krasnoyarsk', label: 'Красноярск (UTC+7)', offset: '+7' },
    { value: 'Asia/Irkutsk', label: 'Иркутск (UTC+8)', offset: '+8' },
    { value: 'Asia/Yakutsk', label: 'Якутск (UTC+9)', offset: '+9' },
    { value: 'Asia/Vladivostok', label: 'Владивосток (UTC+10)', offset: '+10' },
    { value: 'Asia/Magadan', label: 'Магадан (UTC+11)', offset: '+11' },
    { value: 'Asia/Kamchatka', label: 'Камчатка (UTC+12)', offset: '+12' },
];

const TimeZoneSelector = ({ onTimeZoneChange }) => {
    const [selectedTimeZone, setSelectedTimeZone] = useState(() => {
        return localStorage.getItem('userTimeZone') || 'Europe/Moscow';
    });
    const [currentTime, setCurrentTime] = useState(new Date());

    const getFormattedCurrentTime = () => {
        try {
            return new Date().toLocaleString('ru-RU', {
                timeZone: selectedTimeZone,
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        } catch (e) {
            return new Date().toLocaleString('ru-RU');
        }
    };

    const handleChange = (event) => {
        const newTimeZone = event.target.value;
        setSelectedTimeZone(newTimeZone);
        localStorage.setItem('userTimeZone', newTimeZone);
        if (onTimeZoneChange) {
            onTimeZoneChange(newTimeZone);
        }
    };

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    return (
        <div className="timezone-selector">
            <label htmlFor="timezone" className="timezone-label">
                Часовой пояс:
            </label>
            <select
                id="timezone"
                className="timezone-select"
                value={selectedTimeZone}
                onChange={handleChange}
            >
                {russianTimeZones.map(tz => (
                    <option key={tz.value} value={tz.value}>
                        {tz.label}
                    </option>
                ))}
            </select>
            <div className="current-time">
                {getFormattedCurrentTime()}
            </div>
        </div>
    );
};

export default TimeZoneSelector;