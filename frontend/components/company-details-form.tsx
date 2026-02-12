'use client';

import React, { useState } from 'react';

interface CompanyDetailsFormProps {
  initialName: string;
  onSuccess: (companyDetails: CompanyDetailsData) => void;
  onBack?: () => void;
}

interface CompanyDetailsData {
  companyName: string;
  industry: string;
  country: string;
  region: string;
  numberOfProjects: string;
  totalArea: string;
  targetCredits: string;
}

export function CompanyDetailsForm({ initialName, onSuccess, onBack }: CompanyDetailsFormProps) {
  const [formData, setFormData] = useState<CompanyDetailsData>({
    companyName: initialName,
    industry: '',
    country: 'Kenya',
    region: '',
    numberOfProjects: '1',
    totalArea: '',
    targetCredits: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validate required fields
    if (!formData.companyName || !formData.industry || !formData.region || !formData.totalArea || !formData.targetCredits) {
      setError('Please fill in all required fields');
      setLoading(false);
      return;
    }

    try {
      // Store company details in localStorage
      localStorage.setItem('companyDetails', JSON.stringify(formData));
      
      // In a real app, you would POST this to your backend
      // const response = await fetch('/api/v1/companies', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     Authorization: `Bearer ${localStorage.getItem('authToken')}`,
      //   },
      //   body: JSON.stringify(formData),
      // });

      // For now, we'll just proceed with the frontend
      setLoading(false);
      onSuccess(formData);
    } catch (err) {
      console.error('Error saving company details:', err);
      setError('Failed to save company details. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <div style={{ backgroundColor: '#fff', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)', maxWidth: '600px', width: '100%', padding: '40px' }}>
        {/* Header */}
        <div style={{ marginBottom: '30px', textAlign: 'center' }}>
          <h2 style={{ margin: '0 0 10px 0', color: '#1890ff', fontSize: '28px' }}>Company Details</h2>
          <p style={{ margin: '0', color: '#666', fontSize: '14px' }}>Tell us about your organization to get started</p>
        </div>

        {error && (
          <div style={{ backgroundColor: '#fee2e2', color: '#991b1b', padding: '12px', borderRadius: '6px', marginBottom: '20px', fontSize: '14px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Company Name */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontWeight: '500', fontSize: '14px' }}>
              Company Name *
            </label>
            <input
              type="text"
              name="companyName"
              value={formData.companyName}
              onChange={handleChange}
              placeholder="Enter company name"
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '14px',
                boxSizing: 'border-box',
              }}
            />
          </div>

          {/* Industry */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontWeight: '500', fontSize: '14px' }}>
              Industry *
            </label>
            <select
              name="industry"
              value={formData.industry}
              onChange={handleChange}
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '14px',
                boxSizing: 'border-box',
                backgroundColor: '#fff',
              }}
            >
              <option value="">Select an industry</option>
              <option value="agriculture">Agriculture</option>
              <option value="forestry">Forestry</option>
              <option value="energy">Renewable Energy</option>
              <option value="conservation">Conservation</option>
              <option value="reforestation">Reforestation</option>
              <option value="technology">Technology</option>
              <option value="other">Other</option>
            </select>
          </div>

          {/* Country */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontWeight: '500', fontSize: '14px' }}>
              Country *
            </label>
            <input
              type="text"
              name="country"
              value={formData.country}
              onChange={handleChange}
              placeholder="Enter country"
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '14px',
                boxSizing: 'border-box',
              }}
            />
          </div>

          {/* Region */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontWeight: '500', fontSize: '14px' }}>
              Region/State *
            </label>
            <input
              type="text"
              name="region"
              value={formData.region}
              onChange={handleChange}
              placeholder="Enter region or state"
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '14px',
                boxSizing: 'border-box',
              }}
            />
          </div>

          {/* Number of Projects */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontWeight: '500', fontSize: '14px' }}>
              Number of Projects
            </label>
            <input
              type="number"
              name="numberOfProjects"
              value={formData.numberOfProjects}
              onChange={handleChange}
              placeholder="1"
              min="1"
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '14px',
                boxSizing: 'border-box',
              }}
            />
          </div>

          {/* Total Land Area */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontWeight: '500', fontSize: '14px' }}>
              Total Land Area (hectares) *
            </label>
            <input
              type="number"
              name="totalArea"
              value={formData.totalArea}
              onChange={handleChange}
              placeholder="Enter total area in hectares"
              required
              min="0"
              step="0.1"
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '14px',
                boxSizing: 'border-box',
              }}
            />
          </div>

          {/* Target Carbon Credits */}
          <div style={{ marginBottom: '30px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontWeight: '500', fontSize: '14px' }}>
              Target Carbon Credits *
            </label>
            <input
              type="number"
              name="targetCredits"
              value={formData.targetCredits}
              onChange={handleChange}
              placeholder="Enter target number of credits"
              required
              min="0"
              step="100"
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '14px',
                boxSizing: 'border-box',
              }}
            />
          </div>

          {/* Buttons */}
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'space-between' }}>
            {onBack && (
              <button
                type="button"
                onClick={onBack}
                disabled={loading}
                style={{
                  flex: 1,
                  padding: '12px 24px',
                  backgroundColor: '#f0f0f0',
                  color: '#333',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                  fontWeight: '600',
                  opacity: loading ? 0.6 : 1,
                }}
              >
                Back
              </button>
            )}
            <button
              type="submit"
              disabled={loading}
              style={{
                flex: 2,
                padding: '12px 24px',
                backgroundColor: loading ? '#ccc' : '#1890ff',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                fontWeight: '600',
              }}
            >
              {loading ? 'Saving...' : 'Continue to Farm Details'}
            </button>
          </div>

          {/* Info Text */}
          <p style={{ marginTop: '15px', fontSize: '12px', color: '#999', textAlign: 'center' }}>
            Your information is secure and will be used to personalize your dashboard and carbon monitoring
          </p>
        </form>
      </div>
    </div>
  );
}
