export const exportToCSV = (data, filename = 'export.csv') => {
  if (!data || data.length === 0) {
    alert('Нет данных для экспорта');
    return;
  }

  // Получить ключи из первого объекта
  const keys = Object.keys(data);
  
  // Создать строку заголовков
  let csv = keys.join(',') + '\n';
  
  // Добавить строки данных
  data.forEach(row => {
    csv += keys.map(key => {
      const value = row[key];
      if (typeof value === 'string' && value.includes(',')) {
        return `"${value}"`;
      }
      return value;
    }).join(',') + '\n';
  });

  // Создать blob и скачать
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const exportToJSON = (data, filename = 'export.json') => {
  if (!data) {
    alert('Нет данных для экспорта');
    return;
  }

  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const exportToExcel = (data, filename = 'export.xlsx') => {
  exportToCSV(data, filename.replace('.xlsx', '.csv'));
};
