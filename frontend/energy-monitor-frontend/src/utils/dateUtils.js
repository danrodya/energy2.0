export const formatDate = (date) => {
  return new Date(date).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

export const formatTime = (date) => {
  return new Date(date).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatDateTime = (date) => {
  return new Date(date).toLocaleString('ru-RU');
};

export const getDaysInMonth = (year, month) => {
  return new Date(year, month + 1, 0).getDate();
};

export const getMonthName = (month) => {
  const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
  return months[month];
};

export const getCurrentMonth = () => {
  const date = new Date();
  return { year: date.getFullYear(), month: date.getMonth() };
};

export const getPreviousMonth = () => {
  const date = new Date();
  if (date.getMonth() === 0) {
    return { year: date.getFullYear() - 1, month: 11 };
  }
  return { year: date.getFullYear(), month: date.getMonth() - 1 };
};
