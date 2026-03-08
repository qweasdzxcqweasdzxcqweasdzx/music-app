import React, { useState, useEffect } from 'react';
import './Connect.css';

const Connect = ({ currentTrack, isPlaying, onPlayPause }) => {
  const [devices, setDevices] = useState([]);
  const [activeDevice, setActiveDevice] = useState('current');
  const [showDevices, setShowDevices] = useState(false);

  useEffect(() => {
    // Загрузка устройств из localStorage
    const savedDevices = localStorage.getItem('connectDevices');
    if (savedDevices) {
      setDevices(JSON.parse(savedDevices));
    }

    // Текущее устройство
    const currentDeviceId = localStorage.getItem('currentDeviceId') || 'current';
    setActiveDevice(currentDeviceId);

    // Регистрация текущего устройства
    const deviceId = navigator.userAgent + navigator.platform;
    const currentDevice = {
      id: 'current',
      name: 'Это устройство',
      type: 'browser',
      active: true
    };

    // Симуляция других устройств (для демонстрации)
    const simulatedDevices = [
      { id: 'phone', name: 'iPhone 15 Pro', type: 'mobile', active: false },
      { id: 'tablet', name: 'iPad Pro', type: 'tablet', active: false },
      { id: 'desktop', name: 'MacBook Pro', type: 'computer', active: false },
    ];

    setDevices([currentDevice, ...simulatedDevices]);
  }, []);

  const handleDeviceChange = (deviceId) => {
    setActiveDevice(deviceId);
    localStorage.setItem('currentDeviceId', deviceId);
    setShowDevices(false);

    // Здесь должна быть логика переключения устройств
    // Для демонстрации просто показываем уведомление
    alert(`Переключение на устройство: ${devices.find(d => d.id === deviceId)?.name}`);
  };

  const getDeviceIcon = (type) => {
    switch (type) {
      case 'mobile':
        return (
          <svg viewBox="0 0 16 16" width="20" height="20">
            <path fill="currentColor" d="M11 1H5a3 3 0 0 0-3 3v8a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3V4a3 3 0 0 0-3-3zM5 2h6a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"/>
            <circle cx="8" cy="12" r="1" fill="currentColor"/>
          </svg>
        );
      case 'tablet':
        return (
          <svg viewBox="0 0 16 16" width="20" height="20">
            <path fill="currentColor" d="M12 1H4a3 3 0 0 0-3 3v8a3 3 0 0 0 3 3h8a3 3 0 0 0 3-3V4a3 3 0 0 0-3-3zM4 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"/>
          </svg>
        );
      case 'computer':
        return (
          <svg viewBox="0 0 16 16" width="20" height="20">
            <path fill="currentColor" d="M14 1H2a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1zM2 2h12v8H2V2zm3 11h6a.5.5 0 0 1 0 1H5a.5.5 0 0 1 0-1z"/>
          </svg>
        );
      default:
        return (
          <svg viewBox="0 0 16 16" width="20" height="20">
            <path fill="currentColor" d="M8 1a3 3 0 0 0-3 3v2H2a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1H9V4a3 3 0 0 0-3-3zM6 4a2 2 0 1 1 4 0v2H6V4zm-4 7V8h12v3H2z"/>
          </svg>
        );
    }
  };

  return (
    <div className="connect">
      <button
        className="connect-btn"
        onClick={() => setShowDevices(!showDevices)}
      >
        <svg viewBox="0 0 16 16" width="20" height="20">
          <path fill="currentColor" d="M6 3.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm4 0a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm2 0a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm-8 4a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm4 0a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm4 0a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm-8 4a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm4 0a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm4 0a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/>
        </svg>
        Подключить устройство
      </button>

      {showDevices && (
        <div className="devices-modal">
          <div className="devices-header">
            <h3>Доступные устройства</h3>
            <button className="close-modal" onClick={() => setShowDevices(false)}>
              <svg viewBox="0 0 16 16" width="16" height="16">
                <path fill="currentColor" d="M3.478 3.478a.75.75 0 0 1 1.06 0L8 6.94l3.462-3.462a.75.75 0 1 1 1.06 1.06L9.06 8l3.462 3.462a.75.75 0 1 1-1.06 1.06L8 9.06l-3.462 3.462a.75.75 0 0 1-1.06-1.06L6.94 8 3.478 4.538a.75.75 0 0 1 0-1.06z"/>
              </svg>
            </button>
          </div>

          <div className="devices-list">
            {devices.map((device) => (
              <button
                key={device.id}
                className={`device-item ${activeDevice === device.id ? 'active' : ''}`}
                onClick={() => handleDeviceChange(device.id)}
              >
                <div className="device-icon">{getDeviceIcon(device.type)}</div>
                <div className="device-info">
                  <span className="device-name">{device.name}</span>
                  {activeDevice === device.id && (
                    <span className="device-status">Сейчас играет здесь</span>
                  )}
                </div>
                {activeDevice === device.id && (
                  <div className="device-eq">
                    <div className="eq-bar"></div>
                    <div className="eq-bar"></div>
                    <div className="eq-bar"></div>
                  </div>
                )}
              </button>
            ))}
          </div>

          <div className="connect-info">
            <p>Управление воспроизведением на других устройствах</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Connect;
