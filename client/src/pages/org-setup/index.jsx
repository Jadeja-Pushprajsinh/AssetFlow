import React, { useState, useEffect } from 'react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';

export default function OrgSetup() {
  const [activeTab, setActiveTab] = useState('departments');
  const [departments, setDepartments] = useState([]);
  const [categories, setCategories] = useState([]);

  // Mock fetching - in real app would use fetch to /api/org/
  useEffect(() => {
    fetch('/api/org/departments/')
      .then(res => res.json())
      .then(data => setDepartments(Array.isArray(data) ? data : []))
      .catch(err => console.error(err));

    fetch('/api/org/categories/')
      .then(res => res.json())
      .then(data => setCategories(Array.isArray(data) ? data : []))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-ink mb-6">Organization Setup</h1>
      
      {/* Tab Switcher */}
      <div className="flex bg-surface rounded-md p-1 mb-6 w-fit">
        <button
          onClick={() => setActiveTab('departments')}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            activeTab === 'departments' 
              ? 'bg-teal-lighter text-teal-darker shadow-sm' 
              : 'text-ink hover:bg-gray-200'
          }`}
        >
          Departments
        </button>
        <button
          onClick={() => setActiveTab('categories')}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            activeTab === 'categories' 
              ? 'bg-teal-lighter text-teal-darker shadow-sm' 
              : 'text-ink hover:bg-gray-200'
          }`}
        >
          Asset Categories
        </button>
      </div>

      {activeTab === 'departments' && (
        <Card title="Departments" footer={<Button variant="primary">Add Department</Button>}>
          {departments.length > 0 ? (
            <ul className="divide-y divide-gray-100">
              {departments.map(dept => (
                <li key={dept.id} className="py-3 flex justify-between items-center">
                  <span className="font-medium text-ink">{dept.name}</span>
                  <div className="space-x-2">
                    <Button variant="outline">Edit</Button>
                    <Button variant="danger">Delete</Button>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">No departments configured yet.</p>
          )}
        </Card>
      )}

      {activeTab === 'categories' && (
        <Card title="Asset Categories" footer={<Button variant="primary">Add Category</Button>}>
          {categories.length > 0 ? (
            <ul className="divide-y divide-gray-100">
              {categories.map(cat => (
                <li key={cat.id} className="py-3 flex justify-between items-center">
                  <div>
                    <span className="font-medium text-ink block">{cat.name}</span>
                    {cat.description && <span className="text-sm text-gray-500">{cat.description}</span>}
                  </div>
                  <div className="space-x-2">
                    <Button variant="outline">Edit</Button>
                    <Button variant="danger">Delete</Button>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">No asset categories configured yet.</p>
          )}
        </Card>
      )}
    </div>
  );
}
