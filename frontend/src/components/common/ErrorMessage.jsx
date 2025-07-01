// components/common/ErrorMessage.jsx
export default function ErrorMessage({ message }) {
  if (!message) return null;
  return (
    <p className="text-red-600 text-center py-2">
      {message}
    </p>
  );
}
