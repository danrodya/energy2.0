export const formatChartData = (data, label) => {
  return data.map(item => ({
    ...item,
    [label]: parseFloat((item[label] || 0).toFixed(2))
  }));
};

export const getColorByIndex = (index) => {
  const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b'];
  return colors[index % colors.length];
};

export const calculateAverage = (data, key) => {
  if (!data.length) return 0;
  return (data.reduce((sum, item) => sum + item[key], 0) / data.length).toFixed(2);
};

export const calculateTotal = (data, key) => {
  return data.reduce((sum, item) => sum + item[key], 0).toFixed(2);
};

export const calculatePeak = (data, key) => {
  if (!data.length) return 0;
  return Math.max(...data.map(item => item[key])).toFixed(2);
};
