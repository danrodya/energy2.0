import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function TopConsumersChart({ data, loading }) {
  if (loading) {
    return <div className="chart-loading">Загрузка...</div>;
  }

  if (!data || data.length === 0) {
    return <div className="chart-empty">Нет данных</div>;
  }

  return (
    <div className="chart-container">
      <h3>Топ потребителей</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip formatter={(value) => value.toFixed(2)} />
          <Legend />
          <Bar dataKey="power" fill="#667eea" name="Потребление (кВт)" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TopConsumersChart;
