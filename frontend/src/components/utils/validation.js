// utils/validation.js

// Validar complejidad de contraseña:
// Al menos una minúscula, una mayúscula, un número, un carácter especial, y mínimo 13 caracteres.
export function isPasswordComplex(pwd) {
  const complexityRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{13,}$/;
  return complexityRegex.test(pwd);
}

// Validar email con patrón básico.
export function isEmailValid(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isValidExpense(expense) {
  return (
    expense.name &&
    expense.cost &&
    expense.month_id &&
    expense.year_id &&
    expense.category_id
  );
}
