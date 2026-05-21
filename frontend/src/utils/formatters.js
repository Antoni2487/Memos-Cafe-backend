// Formatea moneda en soles peruanos
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat("es-PE", {
    style: "currency",
    currency: "PEN",
  }).format(amount);
};

// Formatea fecha legible
export const formatDate = (dateString) => {
  return new Intl.DateTimeFormat("es-PE", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(dateString));
};

// Formatea fecha y hora
export const formatDateTime = (dateString) => {
  return new Intl.DateTimeFormat("es-PE", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(dateString));
};

// Formatea fecha para inputs tipo date
export const formatDateInput = (dateString) => {
  return new Date(dateString).toISOString().split("T")[0];
};