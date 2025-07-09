export default function PasswordRequirements({ password }) {
  const requirements = [
    { label: "• Lowercase letter", test: /[a-z]/ },
    { label: "• Uppercase letter", test: /[A-Z]/ },
    { label: "• Number", test: /\d/ },
    { label: "• Special character", test: /[^A-Za-z\d]/ },
    { label: "• 13 or more characters", test: /^.{13,}$/ },
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
