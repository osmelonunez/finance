import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PasswordRequirements from '../components/account/PasswordRequirements';
import { isPasswordComplex, isEmailValid } from '../components/utils/validation';

const ERROR_MESSAGES = {
  MISSING_FIELDS: 'All fields are required.',
  USERNAME_EXISTS: 'A user with that name already exists.',
  EMAIL_EXISTS: 'There is already a user with that email.',
  REGISTER_SUCCESS: 'User registered successfully.',
  REGISTER_ERROR: 'Registration error.',
  INVALID_EMAIL: 'Invalid email address.',
  INVALID_PASSWORD: 'Password does not meet the minimum requirements.',
};

function getErrorMessage(error) {
  return ERROR_MESSAGES[error] || error || 'Registration error.';
}

export default function RegisterPage() {
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [emailTouched, setEmailTouched] = useState(false);
  const [passwordTouched, setPasswordTouched] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.username || !form.email || !form.password) {
      setError(getErrorMessage('MISSING_FIELDS'));
      return;
    }

    if (!isEmailValid(form.email)) {
      setError(getErrorMessage('INVALID_EMAIL'));
      return;
    }

    if (!isPasswordComplex(form.password)) {
      setError(getErrorMessage('INVALID_PASSWORD'));
      return;
    }

    try {
      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });

      const data = await res.json();

      if (res.ok) {
        setSuccess(getErrorMessage(data.message || 'REGISTER_SUCCESS'));
        setTimeout(() => navigate('/login'), 1500);
      } else {
        setError(getErrorMessage(data.error));
      }
    } catch {
      setError(getErrorMessage('REGISTER_ERROR'));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-8 max-w-md mx-auto space-y-4">
      <h1 className="text-2xl mb-4">Register</h1>

      <input
        type="text"
        placeholder="Username"
        className="block w-full p-2 border"
        value={form.username}
        onChange={(e) => setForm({ ...form, username: e.target.value })}
        autoComplete="username"
      />

      <input
        type="email"
        placeholder="Email"
        className="block w-full p-2 border"
        value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
        onBlur={() => setEmailTouched(true)}
        autoComplete="email"
      />
      {emailTouched && form.email && !isEmailValid(form.email) && (
        <div className="text-xs text-red-500 mt-1">Enter a valid email address</div>
      )}

      <input
        type="password"
        placeholder="Password"
        className="block w-full p-2 border"
        value={form.password}
        onChange={(e) => setForm({ ...form, password: e.target.value })}
        onFocus={() => setPasswordTouched(true)}
        autoComplete="new-password"
      />
      {passwordTouched && form.password && (
        <>
          <PasswordRequirements password={form.password} />
          {!isPasswordComplex(form.password) && (
            <div className="text-xs text-red-500 mt-1">
              Password does not meet the minimum requirements.
            </div>
          )}
        </>
      )}

      {success && (
        <div className="bg-green-100 text-green-700 p-2 rounded text-sm border border-green-300 mt-2">
          {success}
        </div>
      )}
      {error && (
        <div className="bg-red-100 text-red-700 p-2 rounded text-sm border border-red-300 mt-2">
          {error}
        </div>
      )}

      <button
        type="submit"
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Register
      </button>
    </form>
  );
}
