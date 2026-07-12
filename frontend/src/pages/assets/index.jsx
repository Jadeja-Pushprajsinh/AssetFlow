import React, { useState } from 'react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';

export default function AssetRegistry() {
  const [showRegistration, setShowRegistration] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [assets, setAssets] = useState([
    // Mock data for preview
    { id: 1, name: 'Dell XPS 15', tag: 'AF-0001', category: 'Laptop', status: 'Available' },
    { id: 2, name: 'Herman Miller Chair', tag: 'AF-0002', category: 'Furniture', status: 'Reserved' },
    { id: 3, name: 'Projector', tag: 'AF-0003', category: 'Electronics', status: 'Under Maintenance' },
    { id: 4, name: 'Old Monitor', tag: 'AF-0004', category: 'Electronics', status: 'Retired' },
    { id: 5, name: 'Lost Mouse', tag: 'AF-0005', category: 'Electronics', status: 'Lost' },
  ]);

  const getStatusPillColor = (status) => {
    switch (status) {
      case 'Available': return 'bg-teal text-white';
      case 'Reserved': return 'bg-teal-lighter text-teal-darker';
      case 'Under Maintenance': return 'bg-amber-light text-amber';
      case 'Lost': return 'bg-red-light text-red';
      case 'Retired':
      case 'Disposed': return 'bg-gray-200 text-gray-700';
      default: return 'bg-surface text-ink';
    }
  };

  const filteredAssets = assets.filter(asset => {
    const matchesSearch = asset.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          asset.tag.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter ? asset.status === statusFilter : true;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-ink">Asset Registry</h1>
        <Button variant="primary" onClick={() => setShowRegistration(!showRegistration)}>
          {showRegistration ? 'Cancel Registration' : 'Register New Asset'}
        </Button>
      </div>

      {showRegistration && (
        <Card title="Register New Asset">
          <form className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input id="name" label="Asset Name" placeholder="e.g. MacBook Pro M3" />
            <Input id="category" label="Category" placeholder="e.g. Electronics" />
            <Input id="serial" label="Serial Number" placeholder="e.g. C02X..." />
            <Input id="acquisitionDate" label="Acquisition Date" type="date" />
            <Input id="acquisitionCost" label="Cost" type="number" placeholder="0.00" />
            <Input id="condition" label="Condition" placeholder="e.g. Good" />
            
            <div className="md:col-span-2 flex justify-end gap-3 mt-4">
              <Button variant="outline" onClick={() => setShowRegistration(false)} type="button">Cancel</Button>
              <Button variant="primary" type="button">Save Asset</Button>
            </div>
          </form>
        </Card>
      )}

      <Card title="Search & Filter">
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <Input 
              id="search" 
              placeholder="Search by name or tag..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="w-full sm:w-64">
            <select 
              className="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-teal outline-none"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="Available">Available</option>
              <option value="Reserved">Reserved</option>
              <option value="Under Maintenance">Under Maintenance</option>
              <option value="Lost">Lost</option>
              <option value="Retired">Retired</option>
              <option value="Disposed">Disposed</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="py-3 px-4 font-semibold text-ink">Tag</th>
                <th className="py-3 px-4 font-semibold text-ink">Name</th>
                <th className="py-3 px-4 font-semibold text-ink">Category</th>
                <th className="py-3 px-4 font-semibold text-ink">Status</th>
                <th className="py-3 px-4 font-semibold text-ink text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredAssets.length > 0 ? filteredAssets.map(asset => (
                <tr key={asset.id} className="hover:bg-gray-50 transition-colors">
                  <td className="py-3 px-4 text-sm font-medium">{asset.tag}</td>
                  <td className="py-3 px-4 text-sm">{asset.name}</td>
                  <td className="py-3 px-4 text-sm text-gray-600">{asset.category}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusPillColor(asset.status)}`}>
                      {asset.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right space-x-2">
                    <Button variant="outline">View</Button>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="5" className="py-6 text-center text-gray-500">No assets found matching your criteria.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
