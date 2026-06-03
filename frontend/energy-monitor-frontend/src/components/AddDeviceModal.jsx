import React, { useState } from 'react';

function AddDeviceModal({ isOpen, onClose, onSubmit, loading }) {
  const [form, setForm] = useState({
    name: '',
    description: '',
    device_type: 'socket',
    status: 'online',
    power_state: 'off',
    current_power: 0,
    rated_power: 1.5,
  });

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;

    // числа приводим к number
    if (name === 'current_power' || name === 'rated_power') {
      setForm((prev) => ({ ...prev, [name]: Number(value) || 0 }));
    } else {
      setForm((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    onSubmit(form);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content add-device-modal">
        <div className="modal-header">
          <h2>Добавить устройство</h2>
          <button className="modal-close" onClick={onClose} disabled={loading}>
            ✕
          </button>
        </div>

        <form className="modal-body add-device-form" onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Название устройства</label>
              <input
                type="text"
                name="name"
                placeholder="Например: Розетка в гостиной"
                value={form.name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Тип устройства</label>
              <select
                name="device_type"
                value={form.device_type}
                onChange={handleChange}
              >
                <option value="socket">Розетка</option>
                <option value="light">Освещение</option>
                <option value="climate">Климат</option>
                <option value="appliance">Бытовая техника</option>
                <option value="other">Другое</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Описание (необязательно)</label>
            <textarea
              name="description"
              rows={3}
              placeholder="Например: Розетка для кондиционера в гостиной"
              value={form.description}
              onChange={handleChange}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Статус устройства</label>
              <select
                name="status"
                value={form.status}
                onChange={handleChange}
              >
                <option value="online">Онлайн</option>
                <option value="offline">Оффлайн</option>
              </select>
            </div>

            <div className="form-group">
              <label>Состояние питания</label>
              <select
                name="power_state"
                value={form.power_state}
                onChange={handleChange}
              >
                <option value="off">Выключено</option>
                <option value="on">Включено</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Текущая мощность, кВт</label>
              <input
                type="number"
                name="current_power"
                min="0"
                step="0.01"
                value={form.current_power}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Номинальная мощность, кВт</label>
              <input
                type="number"
                name="rated_power"
                min="0.1"
                step="0.1"
                value={form.rated_power}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="modal-footer" style={{ padding: 0, border: 'none' }}>
            <button
              type="button"
              className="btn-toggle btn-off"
              onClick={onClose}
              disabled={loading}
            >
              Отмена
            </button>
            <button
              type="button"
              className="btn-toggle btn-on"
              onClick={() => onSubmit(form)}
              disabled={loading}
            >
              {loading ? 'Сохранение...' : 'Сохранить'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddDeviceModal;
