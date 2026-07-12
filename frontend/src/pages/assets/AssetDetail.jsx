import React from 'react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';

export default function AssetDetail() {
  // Mock data for preview
  const asset = {
    id: 1,
    name: 'Dell XPS 15',
    tag: 'AF-0001',
    category: 'Laptop',
    status: 'Available',
    serial: 'C02X8734M',
    acquisitionDate: '2025-01-15',
    acquisitionCost: '1500.00',
    condition: 'Good',
  };

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

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-ink">{asset.name}</h1>
          <p className="text-gray-500">Tag: {asset.tag}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusPillColor(asset.status)}`}>
            {asset.status}
          </span>
          <Button variant="outline">Edit</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Asset Information">
          <dl className="space-y-4">
            <div>
              <dt className="text-sm text-gray-500 font-medium">Category</dt>
              <dd className="text-ink">{asset.category}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500 font-medium">Serial Number</dt>
              <dd className="text-ink">{asset.serial}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500 font-medium">Acquisition Date</dt>
              <dd className="text-ink">{asset.acquisitionDate}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500 font-medium">Cost</dt>
              <dd className="text-ink">${asset.acquisitionCost}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-500 font-medium">Condition</dt>
              <dd className="text-ink">{asset.condition}</dd>
            </div>
          </dl>
        </Card>

        <div className="space-y-6">
          <Card title="Allocation History">
            {/* Empty for now, to be populated later */}
            <p className="text-gray-500 text-sm italic">No allocation history available.</p>
          </Card>

          <Card title="Maintenance History">
            {/* Empty for now, to be populated later */}
            <p className="text-gray-500 text-sm italic">No maintenance history available.</p>
          </Card>
        </div>
      </div>
    </div>
  );
}
