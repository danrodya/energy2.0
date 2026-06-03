import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function PowerChart({ data, loading }) {
  if (loading) {
    return <div className="chart-loading">Загрузка графика...</div>;
  }

  if (!data || data.length === 0) {
    return <div className="chart-empty">Нет данных для отображения</div>;
  }

  return (
    <div className="chart-container">
      <h3>Нагрузка по часам</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip 
            formatter={(value) => value.toFixed(2)}
            labelFormatter={(label) => `Время: ${label}`}
          />
          <Legend />
          <Line type="monotone" dataKey="power" stroke="#667eea" name="Мощность (кВт)" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default PowerChart;
