export default function PasswordRequirements({ password }) {
  const requirements = [
    { label: "• Minúscula", test: /[a-z]/ },
    { label: "• Mayúscula", test: /[A-Z]/ },
    { label: "• Número", test: /\d/ },
    { label: "• Carácter especial", test: /[^A-Za-z\d]/ },
    { label: "• 13 o más caracteres", test: /^.{13,}$/ },
  ];

  return (
    <div className="text-sm text-gray-600 mt-2 space-y-1">
      {requirements.map(({ label, test }, index) => (
        <p key={index} className={test.test(password) ? 'text-green-600' : 'text-gray-400'}>
          {label}
        </p>
      ))}
    </div>
  );
}
