import { useEffect, useState, useCallback } from 'react';
import EditableField from '../components/account/EditableField';
import PasswordRequirements from '../components/account/PasswordRequirements';
import EmailManager from '../components/account/EmailManager';
import Loader from '../components/common/Loader';
import useAuthToken from '../hooks/useAuthToken';
import { showNotification } from '../components/utils/showNotification';

export default function AccountPage() {
  const token = useAuthToken();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(true);
  const [editingUsername, setEditingUsername] = useState(false);
  const [editingPassword, setEditingPassword] = useState(false);

  useEffect(() => {
    if (!token) return;

    fetch('/api/me', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => {
        if (!res.ok) throw new Error('Failed to load user data');
        return res.json();
      })
      .then(userData => {
        setUsername(userData.username);
        setLoading(false);
      })
      .catch(() => {
        showNotification({ type: 'error', message: 'Failed to load user data' });
        setLoading(false);
      });
  }, [token]);

  const updateAccount = useCallback(async (body) => {
    const res = await fetch('/api/me', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(body)
    });
    return res;
  }, [token]);

  const handleUpdate = async (field) => {
    if (!token) {
      showNotification({ type: 'error', message: 'Token not available' });
      return;
    }
    if (field === 'password') {
      // Solo actualiza, la confirmación visual ya la gestiona EditableField
      const res = await updateAccount({ username, password });
      if (res.ok) {
        showNotification({ type: 'success', message: 'Password updated successfully' });
        setPassword('');
        setEditingPassword(false);
      } else {
        const data = await res.json();
        showNotification({ type: 'error', message: data.error || 'Failed to update password' });
      }
    } else if (field === 'username') {
      const res = await updateAccount({ username });
      if (res.ok) {
        showNotification({ type: 'success', message: 'Username updated successfully' });
        setEditingUsername(false);
      } else {
        const data = await res.json();
        showNotification({ type: 'error', message: data.error || 'Failed to update username' });
      }
    }
  };

  if (loading) {
    return <Loader />;
  }

  return (
    <div className="max-w-xl mx-auto p-6 space-y-6 bg-white rounded-xl shadow">
      <h2 className="text-xl font-bold text-gray-800">My account</h2>

      <EditableField
        label="Username"
        value={username}
        onChange={e => setUsername(e.target.value)}
        onSave={() => handleUpdate('username')}
        isEditing={editingUsername}
        setIsEditing={setEditingUsername}
      />

      <EditableField
        label="Password"
        type="password"
        placeholder="New password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        onSave={() => handleUpdate('password')}
        isEditing={editingPassword}
        setIsEditing={setEditingPassword}
      >
        <PasswordRequirements password={password} />
      </EditableField>

      <EmailManager token={token} />
    </div>
  );
}