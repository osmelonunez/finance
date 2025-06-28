import { useEffect, useState } from 'react';
import { Trash2, Wrench } from 'lucide-react';

export default function CategoryManager() {
  const [categories, setCategories] = useState([]);
  const [newCategory, setNewCategory] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editingName, setEditingName] = useState('');
  const [editingDescription, setEditingDescription] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [categoryToDelete, setCategoryToDelete] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');
  const [statusType, setStatusType] = useState(''); // 'success' or 'error'

  const fetchCategories = async () => {
    const res = await fetch('/api/categories');
    if (res.ok) {
      const data = await res.json();
      const sorted = data.sort((a, b) => a.name.localeCompare(b.name));
      setCategories(sorted);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  const showStatus = (message, type = 'success') => {
    setStatusMessage(message);
    setStatusType(type);
    setTimeout(() => setStatusMessage(''), 3000);
  };

  const handleAddCategory = async () => {
    if (!newCategory.trim()) return;

    try {
      const res = await fetch('/api/categories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newCategory.trim(), description: newDescription.trim() })
      });

      const data = await res.json();

      if (!res.ok) {
        showStatus(data.error || 'Error adding category', 'error');
        return;
      }

      setNewCategory('');
      setNewDescription('');
      setShowModal(false);
      fetchCategories();
      showStatus('Category added successfully');
    } catch (err) {
      console.error('Error:', err);
      showStatus('Unexpected error', 'error');
    }
  };

  const handleEditCategory = async (id) => {
    if (!editingName.trim()) return;
    const res = await fetch(`/api/categories/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: editingName.trim(), description: editingDescription.trim() })
    });
    if (res.ok) {
      setEditingId(null);
      setEditingName('');
      setEditingDescription('');
      fetchCategories();
      showStatus('Category updated successfully');
    } else {
      const data = await res.json();
      showStatus(data.error || 'Error updating category', 'error');
    }
  };

  const handleDeleteCategory = async () => {
    if (!categoryToDelete) return;
    const res = await fetch(`/api/categories/${categoryToDelete.id}`, { method: 'DELETE' });
    if (res.ok) {
      fetchCategories();
      showStatus('Category deleted successfully');
    } else {
      const data = await res.json();
      showStatus(data.error || 'Error deleting category', 'error');
    }
    setShowDeleteModal(false);
    setCategoryToDelete(null);
  };

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-gray-800">Manage Categories</h2>

      {statusMessage && (
        <div className={`p-4 rounded text-sm font-medium ${statusType === 'success' ? 'bg-green-100 text-green-800 border border-green-300' : 'bg-red-100 text-red-800 border border-red-300'}`}>
          {statusMessage}
        </div>
      )}

      <div className="bg-white p-6 rounded-xl shadow space-y-4">
        <div className="flex justify-end">
          <button onClick={() => setShowModal(true)} className="bg-green-600 text-white px-6 py-2 rounded hover:bg-blue-700">
            Add Category
          </button>
        </div>

        <table className="min-w-full bg-white shadow rounded-xl">
          <thead className="bg-gray-50 text-left">
            <tr>
              <th className="p-3">Name</th>
              <th className="p-3">Description</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {categories.map(cat => (
              <tr key={cat.id} className="border-t hover:bg-gray-50">
                <td className="p-3">{
                  editingId === cat.id ? (
                    <input
                      value={editingName}
                      onChange={(e) => setEditingName(e.target.value)}
                      className="border rounded px-2 py-1"
                    />
                  ) : (
                    cat.name
                  )
                }</td>
                <td className="p-3">{
                  editingId === cat.id ? (
                    <input
                      value={editingDescription}
                      onChange={(e) => setEditingDescription(e.target.value)}
                      className="border rounded px-2 py-1"
                    />
                  ) : (
                    cat.description || '—'
                  )
                }</td>
                <td className="p-3 text-right">
                  <div className="inline-flex gap-1">
                    {editingId === cat.id ? (
                      <button
                        onClick={() => handleEditCategory(cat.id)}
                        className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                      >
                        Save
                      </button>
                    ) : (
                      <button
                        className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                        onClick={() => {
                          setEditingId(cat.id);
                          setEditingName(cat.name);
                          setEditingDescription(cat.description || '');
                        }}
                        title="Editar"
                      >
                        <Wrench size={16} />
                      </button>
                    )}
                    <button
                      className="p-2 bg-red-500 text-white rounded hover:bg-red-600"
                      onClick={() => { setCategoryToDelete(cat); setShowDeleteModal(true); }}
                      title="Eliminar"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-xl w-full max-w-md shadow-lg space-y-4">
            <h3 className="text-lg font-semibold">Add New Category</h3>
            <input
              type="text"
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
              placeholder="Category name"
              className="w-full border rounded px-3 py-2"
            />
            <textarea
              value={newDescription}
              onChange={(e) => setNewDescription(e.target.value)}
              placeholder="Category description"
              className="w-full border rounded px-3 py-2"
            />
            <div className="flex justify-end gap-4">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 border rounded text-gray-600">Cancel</button>
              <button onClick={handleAddCategory} className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
                Add
              </button>
            </div>
          </div>
        </div>
      )}

      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-xl w-full max-w-md">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Confirm Delete</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete <strong>{categoryToDelete?.name}</strong>?
            </p>
            <div className="flex justify-end gap-4">
              <button className="px-4 py-2 rounded border text-gray-600 hover:bg-gray-100" onClick={() => { setShowDeleteModal(false); setCategoryToDelete(null); }}>Cancel</button>
              <button className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700" onClick={handleDeleteCategory}>Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
