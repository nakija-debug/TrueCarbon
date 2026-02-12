'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Chart as ChartJS } from 'chart.js/auto';
import { FarmForm } from '@/components/farm-form';
import '@/true_carbon/style.css';
import '@/true_carbon/login/auth.css';

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userEmail, setUserEmail] = useState('');
  const [showFarmForm, setShowFarmForm] = useState(false);

  const chartsRef = useRef<{ co2?: ChartJS; project?: ChartJS; forest?: ChartJS; satellite?: ChartJS; credits?: ChartJS }>({});

  useEffect(() => {
    // Load external scripts
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
    document.head.appendChild(link);

    const chartScript = document.createElement('script');
    chartScript.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    document.body.appendChild(chartScript);

    // Initialize CO2 Chart
    const co2Ctx = document.getElementById('co2Chart') as HTMLCanvasElement;
    if (co2Ctx) {
      // Destroy existing chart if it exists
      if (chartsRef.current.co2) {
        chartsRef.current.co2.destroy();
      }
      chartsRef.current.co2 = new ChartJS(co2Ctx, {
        type: 'line',
        data: {
          labels: ['2020', '2021', '2022', '2023', '2024'],
          datasets: [
            {
              label: 'Global CO2 Emissions (Gigatons)',
              data: [36.5, 36.7, 37.1, 37.3, 37.8],
              borderColor: '#ff6b6b',
              backgroundColor: 'rgba(255, 107, 107, 0.1)',
              borderWidth: 2,
              fill: true,
              tension: 0.4,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: true,
              labels: {
                color: '#333',
              },
            },
          },
          scales: {
            y: {
              beginAtZero: false,
              ticks: {
                color: '#666',
              },
            },
            x: {
              ticks: {
                color: '#666',
              },
            },
          },
        },
      });
    }

    // Initialize Project Chart
    const projectCtx = document.getElementById('projectChart') as HTMLCanvasElement;
    if (projectCtx) {
      // Destroy existing chart if it exists
      if (chartsRef.current.project) {
        chartsRef.current.project.destroy();
      }
      chartsRef.current.project = new ChartJS(projectCtx, {
        type: 'doughnut',
        data: {
          labels: ['Reforestation', 'Renewable Energy', 'Methane Reduction', 'Soil Carbon'],
          datasets: [
            {
              data: [30, 25, 25, 20],
              backgroundColor: [
                '#52c41a',
                '#1890ff',
                '#faad14',
                '#f5222d',
              ],
              borderColor: '#fff',
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: true,
              labels: {
                color: '#333',
              },
            },
          },
        },
      });
    }

    // Initialize Forest Chart
    const forestCtx = document.getElementById('forestChart') as HTMLCanvasElement;
    if (forestCtx) {
      // Destroy existing chart if it exists
      if (chartsRef.current.forest) {
        chartsRef.current.forest.destroy();
      }
      chartsRef.current.forest = new ChartJS(forestCtx, {
        type: 'bar',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          datasets: [
            {
              label: 'Deforestation (Hectares)',
              data: [1200, 1400, 1300, 1600, 1500, 1400],
              backgroundColor: '#ff6b6b',
              borderColor: '#ff4d4f',
              borderWidth: 1,
            },
            {
              label: 'Reforestation (Hectares)',
              data: [900, 1100, 1000, 1300, 1200, 1100],
              backgroundColor: '#52c41a',
              borderColor: '#389e0d',
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: true,
              labels: {
                color: '#333',
              },
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                color: '#666',
              },
            },
            x: {
              ticks: {
                color: '#666',
              },
            },
          },
        },
      });
    }

    // Initialize Satellite Health Dashboard Chart
    const satelliteCtx = document.getElementById('satelliteChart') as HTMLCanvasElement;
    if (satelliteCtx) {
      if (chartsRef.current.satellite) {
        chartsRef.current.satellite.destroy();
      }
      chartsRef.current.satellite = new ChartJS(satelliteCtx, {
        type: 'radar',
        data: {
          labels: ['Health', 'Coverage', 'Accuracy', 'Frequency', 'Data Quality', 'Uptime'],
          datasets: [
            {
              label: 'Sentinel-2',
              data: [95, 92, 94, 88, 96, 99],
              borderColor: '#1890ff',
              backgroundColor: 'rgba(24, 144, 255, 0.1)',
              borderWidth: 2,
            },
            {
              label: 'Landsat-8',
              data: [92, 90, 93, 85, 94, 97],
              borderColor: '#52c41a',
              backgroundColor: 'rgba(82, 196, 26, 0.1)',
              borderWidth: 2,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: true,
              labels: {
                color: '#333',
              },
            },
          },
          scales: {
            r: {
              beginAtZero: true,
              max: 100,
              ticks: {
                color: '#666',
              },
            },
          },
        },
      });
    }

    // Initialize Carbon Credits Chart
    const creditsCtx = document.getElementById('creditsChart') as HTMLCanvasElement;
    if (creditsCtx) {
      if (chartsRef.current.credits) {
        chartsRef.current.credits.destroy();
      }
      chartsRef.current.credits = new ChartJS(creditsCtx, {
        type: 'line',
        data: {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
          datasets: [
            {
              label: 'Credits Issued',
              data: [1200, 1500, 1800, 2100, 2400, 2800],
              borderColor: '#faad14',
              backgroundColor: 'rgba(250, 173, 20, 0.1)',
              borderWidth: 2,
              fill: true,
            },
            {
              label: 'Credits Retired',
              data: [400, 600, 800, 1000, 1200, 1400],
              borderColor: '#f5222d',
              backgroundColor: 'rgba(245, 34, 45, 0.1)',
              borderWidth: 2,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              display: true,
              labels: {
                color: '#333',
              },
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                color: '#666',
              },
            },
            x: {
              ticks: {
                color: '#666',
              },
            },
          },
        },
      });
    }

    // Modal and event listeners
    const setupAuthHandlers = () => {
      const authModal = document.getElementById('auth-modal');
      const loginBtn = document.getElementById('login-btn');
      const signupBtn = document.getElementById('signup-btn');
      const heroSignup = document.getElementById('hero-signup');
      const finalSignup = document.getElementById('final-signup');
      const closeModal = document.querySelector('.close-modal');
      const tabs = document.querySelectorAll('.tab-btn');
      const tabContents = document.querySelectorAll('.tab-content');
      const loginForm = document.getElementById('login-form') as HTMLFormElement;

      const openAuth = (tab: string) => {
        if (authModal) authModal.style.display = 'block';
        if (tab) switchToTab(tab);
      };

      const closeAuth = () => {
        if (authModal) authModal.style.display = 'none';
      };

      const switchToTab = (tab: string) => {
        tabs.forEach((b) => {
          if ((b as HTMLElement).dataset.tab === tab) {
            b.classList.add('active');
          } else {
            b.classList.remove('active');
          }
        });
        tabContents.forEach((c) => {
          if (c.id === tab + '-tab') {
            c.classList.add('active');
          } else {
            c.classList.remove('active');
          }
        });
      };

      // Handle login form submission
      if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          const emailInput = document.getElementById('email') as HTMLInputElement;
          const passwordInput = document.getElementById('password') as HTMLInputElement;

          const email = emailInput?.value || '';
          const password = passwordInput?.value || '';

          // Try backend first
          if (email && password) {
            try {
              const res = await fetch('/api/auth/jwt/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: email, password })
              });

              if (res.ok) {
                const data = await res.json();
                // Backend login successful
                localStorage.setItem('authToken', data.access_token || data.token);
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('userEmail', email);
                setIsLoggedIn(true);
                setUserEmail(email);
                if (authModal) authModal.style.display = 'none';
                return;
              }
            } catch (err) {
              // Continue to mock check if backend fails
              console.log('Backend unavailable, checking mock credentials');
            }
          }

          // Fall back to mock credentials for demo/development
          if (email === 'nakija540@gmail.com' && password === '123456') {
            setIsLoggedIn(true);
            setUserEmail(email);
            if (authModal) authModal.style.display = 'none';
          } else {
            alert('Invalid credentials. For demo, use: nakija540@gmail.com / 123456');
          }
        });
      }

      // Handle signup form submission
      const signupFormElement = document.getElementById('signup-form') as HTMLFormElement;
      if (signupFormElement) {
        signupFormElement.addEventListener('submit', async (e) => {
          e.preventDefault();
          const nameInput = document.getElementById('signup-name') as HTMLInputElement;
          const emailInput = document.getElementById('signup-email') as HTMLInputElement;
          const passwordInput = document.getElementById('signup-password') as HTMLInputElement;
          const companyInput = document.getElementById('signup-company') as HTMLInputElement;

          const name = nameInput?.value || '';
          const email = emailInput?.value || '';
          const password = passwordInput?.value || '';
          const company = companyInput?.value || '';

          if (!name || !email || !password || !company) {
            alert('Please fill in all fields');
            return;
          }

          // Try backend registration
          try {
            const res = await fetch('/api/auth/register', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                full_name: name,
                email: email,
                password: password,
                company_name: company
              })
            });

            if (res.ok) {
              const data = await res.json();
              // Store auth token if provided
              if (data.access_token || data.token) {
                localStorage.setItem('authToken', data.access_token || data.token);
              }

              // Set up for farm form
              setUserEmail(email);

              setShowFarmForm(true);

              // Close modal
              if (authModal) authModal.style.display = 'none';

              // Clear form
              signupFormElement.reset();
              return;
            } else {
              const error = await res.json();
              alert('Registration failed: ' + (error.detail || 'Unknown error'));
            }
          } catch (err) {
            alert('Unable to reach server. Please try again later.');
            console.error(err);
          }
        });
      }

      if (loginBtn) loginBtn.addEventListener('click', () => openAuth('login'));
      if (signupBtn) signupBtn.addEventListener('click', () => openAuth('signup'));
      if (heroSignup) heroSignup.addEventListener('click', () => openAuth('signup'));
      if (finalSignup) finalSignup.addEventListener('click', () => openAuth('signup'));
      if (closeModal) closeModal.addEventListener('click', closeAuth);

      document.querySelectorAll('.switch-tab').forEach((el) => {
        el.addEventListener('click', function (this: HTMLElement, e: Event) {
          e.preventDefault();
          switchToTab(this.dataset.tab || '');
        });
      });

      window.addEventListener('click', function (e) {
        if (e.target === authModal) closeAuth();
      });
    };

    // Small delay to ensure DOM is ready
    const timer = setTimeout(setupAuthHandlers, 0);
    return () => {
      clearTimeout(timer);
      // Destroy all charts on cleanup
      if (chartsRef.current.co2) {
        chartsRef.current.co2.destroy();
      }
      if (chartsRef.current.project) {
        chartsRef.current.project.destroy();
      }
      if (chartsRef.current.forest) {
        chartsRef.current.forest.destroy();
      }
      if (chartsRef.current.satellite) {
        chartsRef.current.satellite.destroy();
      }
      if (chartsRef.current.credits) {
        chartsRef.current.credits.destroy();
      }
    };
  }, [isLoggedIn, userEmail]);

  // Mock data for dashboard
  const mockDashboardData = {
    satellites: [
      { id: 1, name: 'Sentinel-2', status: 'Active', coverage: '92%', lastUpdate: '2 min ago', accuracy: '94%' },
      { id: 2, name: 'Landsat-8', status: 'Active', coverage: '90%', lastUpdate: '5 min ago', accuracy: '93%' },
      { id: 3, name: 'Copernicus', status: 'Active', coverage: '88%', lastUpdate: '3 min ago', accuracy: '91%' },
    ],
    carbonProjects: [
      { id: 1, name: 'Amazon Reforestation', area: '15,230 ha', credits: '45,690', status: 'Verified', co2Sequestered: '1.2M tons' },
      { id: 2, name: 'Coastal Mangrove', area: '8,450 ha', credits: '25,350', status: 'Verified', co2Sequestered: '860K tons' },
      { id: 3, name: 'African Savanna', area: '22,100 ha', credits: '66,300', status: 'Monitoring', co2Sequestered: '1.8M tons' },
      { id: 4, name: 'Asian Forest Corridor', area: '18,900 ha', credits: '56,700', status: 'Verified', co2Sequestered: '1.5M tons' },
    ],
    measurements: [
      { date: '2025-02-12', ndvi: '0.78', biomass: '245 t/ha', temperature: '24.5°C', humidity: '72%', project: 'Amazon Reforestation' },
      { date: '2025-02-11', ndvi: '0.76', biomass: '243 t/ha', temperature: '23.8°C', humidity: '70%', project: 'Coastal Mangrove' },
      { date: '2025-02-10', ndvi: '0.82', biomass: '268 t/ha', temperature: '25.2°C', humidity: '75%', project: 'African Savanna' },
      { date: '2025-02-09', ndvi: '0.75', biomass: '239 t/ha', temperature: '23.1°C', humidity: '68%', project: 'Asian Forest Corridor' },
    ],
    reports: [
      { id: 1, type: 'Monthly Report', date: '2025-02-12', status: 'Complete', projects: 4, credits: '194,040', fileName: 'Monthly_Report_Feb_2025.pdf' },
      { id: 2, type: 'Satellite Data', date: '2025-02-11', status: 'Processing', projects: 4, credits: 'N/A', fileName: 'Satellite_Data_Feb_11.csv' },
      { id: 3, type: 'Verification Report', date: '2025-02-10', status: 'Complete', projects: 3, credits: '88,350', fileName: 'Verification_Feb_2025.pdf' },
    ],
    kpis: [
      { label: 'Total Carbon Credits', value: '194,040', change: '+12,450', trend: 'up' },
      { label: 'Area Monitored', value: '64,680 ha', change: '+2,340 ha', trend: 'up' },
      { label: 'CO2 Sequestered', value: '5.36M tons', change: '+420K tons', trend: 'up' },
      { label: 'Active Satellites', value: '3', change: 'All Healthy', trend: 'neutral' },
    ],
  };

  // Dashboard Component
  const Dashboard = () => (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5', paddingTop: '20px' }}>
      {/* Header */}
      <div style={{ backgroundColor: '#fff', padding: '20px', borderBottom: '1px solid #e0e0e0', marginBottom: '20px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ margin: '0', color: '#1890ff', fontSize: '28px' }}>TRUE CARBON Dashboard</h1>
            <p style={{ margin: '5px 0 0 0', color: '#666', fontSize: '14px' }}>Welcome, {userEmail}</p>
          </div>
          <button onClick={() => { setIsLoggedIn(false); setUserEmail(''); }} style={{ padding: '10px 20px', backgroundColor: '#ff4d4f', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '14px' }}>Logout</button>
        </div>
      </div>

      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 20px' }}>
        {/* KPI Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
          {mockDashboardData.kpis.map((kpi) => (
            <div key={kpi.label} style={{ backgroundColor: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
              <p style={{ margin: '0 0 10px 0', color: '#666', fontSize: '12px', textTransform: 'uppercase' }}>{kpi.label}</p>
              <h3 style={{ margin: '0 0 5px 0', fontSize: '28px', color: '#1890ff' }}>{kpi.value}</h3>
              <p style={{ margin: '0', color: kpi.trend === 'up' ? '#52c41a' : '#666', fontSize: '12px' }}>{kpi.change}</p>
            </div>
          ))}
        </div>

        {/* Farm Location Map */}
        <div style={{ marginBottom: '30px' }}>
          <FarmMap userEmail={userEmail} />
        </div>

        {/* Charts Row 1 */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px', marginBottom: '30px' }}>
          <div style={{ backgroundColor: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
            <h3 style={{ marginTop: 0, color: '#333' }}>Satellite Health Status</h3>
            <canvas id="satelliteChart"></canvas>
          </div>
          <div style={{ backgroundColor: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
            <h3 style={{ marginTop: 0, color: '#333' }}>Carbon Credits Trend</h3>
            <canvas id="creditsChart"></canvas>
          </div>
        </div>

        {/* Satellites Table */}
        <div style={{ backgroundColor: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', marginBottom: '30px' }}>
          <h3 style={{ marginTop: 0, color: '#333' }}>Active Satellites</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e0e0e0', backgroundColor: '#fafafa' }}>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Satellite Name</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Status</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Coverage</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Accuracy</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Last Update</th>
              </tr>
            </thead>
            <tbody>
              {mockDashboardData.satellites.map((sat) => (
                <tr key={sat.id} style={{ borderBottom: '1px solid #e0e0e0' }}>
                  <td style={{ padding: '12px' }}>{sat.name}</td>
                  <td style={{ padding: '12px' }}><span style={{ backgroundColor: '#52c41a', color: '#fff', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>{sat.status}</span></td>
                  <td style={{ padding: '12px' }}>{sat.coverage}</td>
                  <td style={{ padding: '12px' }}>{sat.accuracy}</td>
                  <td style={{ padding: '12px', color: '#666' }}>{sat.lastUpdate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Carbon Projects Table */}
        <div style={{ backgroundColor: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', marginBottom: '30px' }}>
          <h3 style={{ marginTop: 0, color: '#333' }}>Carbon Credit Projects</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e0e0e0', backgroundColor: '#fafafa' }}>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Project Name</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Area (ha)</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Credits Issued</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>CO2 Sequestered</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Verification Status</th>
              </tr>
            </thead>
            <tbody>
              {mockDashboardData.carbonProjects.map((project) => (
                <tr key={project.id} style={{ borderBottom: '1px solid #e0e0e0' }}>
                  <td style={{ padding: '12px' }}>{project.name}</td>
                  <td style={{ padding: '12px' }}>{project.area}</td>
                  <td style={{ padding: '12px', fontWeight: 'bold', color: '#1890ff' }}>{project.credits}</td>
                  <td style={{ padding: '12px' }}>{project.co2Sequestered}</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{ backgroundColor: project.status === 'Verified' ? '#52c41a' : '#faad14', color: '#fff', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
                      {project.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Satellite Measurements Table */}
        <div style={{ backgroundColor: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', marginBottom: '30px' }}>
          <h3 style={{ marginTop: 0, color: '#333' }}>Latest Satellite Measurements</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e0e0e0', backgroundColor: '#fafafa' }}>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Date</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Project</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>NDVI</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Biomass</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Temperature</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Humidity</th>
              </tr>
            </thead>
            <tbody>
              {mockDashboardData.measurements.map((measurement, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #e0e0e0' }}>
                  <td style={{ padding: '12px' }}>{measurement.date}</td>
                  <td style={{ padding: '12px' }}>{measurement.project}</td>
                  <td style={{ padding: '12px', fontWeight: 'bold', color: '#52c41a' }}>{measurement.ndvi}</td>
                  <td style={{ padding: '12px' }}>{measurement.biomass}</td>
                  <td style={{ padding: '12px' }}>{measurement.temperature}</td>
                  <td style={{ padding: '12px' }}>{measurement.humidity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Reports Table */}
        <div style={{ backgroundColor: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', marginBottom: '30px' }}>
          <h3 style={{ marginTop: 0, color: '#333' }}>Generated Reports</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e0e0e0', backgroundColor: '#fafafa' }}>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Report Type</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Date</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Projects Analyzed</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Credits Processed</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Status</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {mockDashboardData.reports.map((report) => (
                <tr key={report.id} style={{ borderBottom: '1px solid #e0e0e0' }}>
                  <td style={{ padding: '12px' }}>{report.type}</td>
                  <td style={{ padding: '12px' }}>{report.date}</td>
                  <td style={{ padding: '12px' }}>{report.projects}</td>
                  <td style={{ padding: '12px' }}>{report.credits}</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{ backgroundColor: report.status === 'Complete' ? '#52c41a' : '#1890ff', color: '#fff', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
                      {report.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <a href="#" style={{ color: '#1890ff', textDecoration: 'none', fontSize: '12px' }}>Download</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  // Conditional Rendering
  if (showFarmForm) {
    return <FarmForm
      onSuccess={() => {
        setShowFarmForm(false);
        setIsLoggedIn(true);
      }}
    />;
  }

  if (isLoggedIn) {
    return <Dashboard />;
  }

  return (
    <>
      <nav className="navbar">
        <div className="container">
          <div className="logo">
            <i className="fas fa-satellite"></i>
            <h1>TRUE CARBON</h1>
          </div>
          <ul className="nav-links">
            <li><a href="#features">Features</a></li>
            <li><a href="#how-it-works">How It Works</a></li>
            <li><a href="#visualizations">Data Insights</a></li>
            <li><a href="#solutions">Solutions</a></li>
            <li><a href="#contact">Contact</a></li>
          </ul>
          <div className="auth-buttons">
            <button id="login-btn" className="btn-secondary">Login</button>
            <button id="signup-btn" className="btn-primary">Sign Up</button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <h1>Unleash <span className="highlight">Trust & Transparency</span> in Carbon Credits</h1>
            <p className="hero-subtitle">A digital MRV platform that uses satellite data to continuously monitor, report, and verify post-registry carbon credit projects. It prevents greenwashing by ensuring real, measurable impact, builds buyer trust through transparent verification, and helps companies confidently invest in credible, high-integrity carbon credits.</p>
            <div className="cta-buttons">
              <button id="hero-signup" className="btn-primary btn-large">Start 15-Day Free Trial</button>
              <button id="demo-btn" className="btn-secondary btn-large">Request a Demo</button>
            </div>
          </div>
          <div className="hero-image">
            <div className="satellite-visual">
              <i className="fas fa-satellite-dish"></i>
              <div className="orbit"></div>
              <img
                src="/image/earth.png"
                alt="Earth"
                style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  width: '150px',
                  height: '150px',
                  borderRadius: '50%',
                  objectFit: 'cover'
                }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Pollution Data Visualization Section */}
      <section className="data-section" id="visualizations">
        <div className="container">
          <h2 className="section-title">Global Carbon & Pollution Insights</h2>
          <p className="section-subtitle">Real-time monitoring of carbon emissions and environmental impact data</p>

          <div className="charts-container">
            <div className="chart-box">
              <h3>Global CO2 Emissions (2020-2024)</h3>
              <canvas id="co2Chart"></canvas>
              <p className="chart-note">Source: Satellite data aggregation</p>
            </div>
            <div className="chart-box">
              <h3>Carbon Credit Project Types</h3>
              <canvas id="projectChart"></canvas>
              <p className="chart-note">Verified by TRUE CARBON</p>
            </div>
            <div className="chart-box">
              <h3>Deforestation vs Reforestation (Hectares)</h3>
              <canvas id="forestChart"></canvas>
              <p className="chart-note">Monthly satellite monitoring</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features" id="features">
        <div className="container">
          <h2 className="section-title">Advanced Digital MRV Platform</h2>
          <p className="section-subtitle">Comprehensive Monitoring, Reporting, and Verification</p>

          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-satellite"></i>
              </div>
              <h3>Satellite Monitoring</h3>
              <p>Continuous, real-time tracking of carbon projects using satellite imagery and remote sensing technology.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-shield-alt"></i>
              </div>
              <h3>Greenwashing Prevention</h3>
              <p>Ensure real, measurable impact with verified data to prevent misleading environmental claims.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-chart-line"></i>
              </div>
              <h3>Real-Time Analytics</h3>
              <p>Monitor carbon sequestration metrics as they happen and respond quickly to changes.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-file-contract"></i>
              </div>
              <h3>Transparent Reporting</h3>
              <p>Build buyer trust through transparent verification and detailed impact reporting.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-certificate"></i>
              </div>
              <h3>High-Integrity Credits</h3>
              <p>Verify and validate carbon credits to ensure they represent genuine, additional emissions reductions.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <i className="fas fa-cogs"></i>
              </div>
              <h3>Custom Dashboards</h3>
              <p>Tailored reporting and visualization tools to meet your specific monitoring needs.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works" id="how-it-works">
        <div className="container">
          <h2 className="section-title">How TRUE CARBON Works</h2>
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <h3>Satellite Data Collection</h3>
              <p>Our system aggregates data from multiple satellite sources to monitor carbon projects globally.</p>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <h3>Continuous Monitoring</h3>
              <p>AI-powered algorithms analyze changes in vegetation, land use, and carbon sequestration.</p>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <h3>Verification & Reporting</h3>
              <p>Automated verification against established protocols with transparent reporting.</p>
            </div>
            <div className="step">
              <div className="step-number">4</div>
              <h3>Trusted Carbon Credits</h3>
              <p>Investors purchase verified credits with complete confidence in their environmental impact.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Solutions Section */}
      <section className="solutions" id="solutions">
        <div className="container">
          <h2 className="section-title">Tailored MRV Solutions</h2>
          <p className="section-subtitle">Flexible plans for every investment horizon</p>

          <div className="solutions-grid">
            <div className="solution-card">
              <h3>Short-Term</h3>
              <p className="price">Starting at <span>$499</span>/month</p>
              <ul>
                <li><i className="fas fa-check"></i> Project Verification</li>
                <li><i className="fas fa-check"></i> Basic Monitoring</li>
                <li><i className="fas fa-check"></i> Standard Reports</li>
                <li><i className="fas fa-check"></i> Quarterly Audits</li>
              </ul>
              <button className="btn-secondary">Learn More</button>
            </div>
            <div className="solution-card featured">
              <div className="popular-tag">MOST POPULAR</div>
              <h3>Medium-Term</h3>
              <p className="price">Starting at <span>$1,299</span>/month</p>
              <ul>
                <li><i className="fas fa-check"></i> Everything in Short-Term</li>
                <li><i className="fas fa-check"></i> Real-Time Analytics</li>
                <li><i className="fas fa-check"></i> Custom Dashboards</li>
                <li><i className="fas fa-check"></i> Monthly Audits</li>
                <li><i className="fas fa-check"></i> API Access</li>
              </ul>
              <button className="btn-primary">Start Free Trial</button>
            </div>
            <div className="solution-card">
              <h3>Long-Term</h3>
              <p className="price">Custom <span>Enterprise</span> Pricing</p>
              <ul>
                <li><i className="fas fa-check"></i> Everything in Medium-Term</li>
                <li><i className="fas fa-check"></i> Advanced Predictive Analytics</li>
                <li><i className="fas fa-check"></i> Full Customization</li>
                <li><i className="fas fa-check"></i> Weekly Audits</li>
                <li><i className="fas fa-check"></i> Dedicated Support</li>
                <li><i className="fas fa-check"></i> White-label Solutions</li>
              </ul>
              <button className="btn-secondary">Contact Sales</button>
            </div>
          </div>
        </div>
      </section>

      {/* Trial Section */}
      <section className="trial-section">
        <div className="container">
          <div className="trial-content">
            <h2>Get Started with 15-Day Free Trial</h2>
            <p>Sign up now and start leveraging the power of satellite-verified carbon credits. We'll give you access to all the tools and resources you need to verify and invest with confidence.</p>
            <button id="final-signup" className="btn-primary btn-large">Start Your Free Trial</button>
          </div>
        </div>
      </section>

      {/* Login/Signup Modal */}
      <div id="auth-modal" className="modal">
        <div className="modal-content">
          <span className="close-modal">&times;</span>
          <div className="modal-tabs">
            <button className="tab-btn active" data-tab="login">Login</button>
            <button className="tab-btn" data-tab="signup">Sign Up</button>
          </div>

          <div id="login-tab" className="tab-content active">
            <h3>Login to TRUE CARBON</h3>
            <form id="login-form">
              <div className="form-group">
                <label htmlFor="email">Email Address</label>
                <input type="email" id="email" placeholder="Enter your email" required />
              </div>
              <div className="form-group">
                <label htmlFor="password">Password</label>
                <input type="password" id="password" placeholder="Enter your password" required />
              </div>
              <button type="submit" className="btn-primary btn-full">Login</button>
            </form>
            <p className="modal-footer">Don't have an account? <a href="#" className="switch-tab" data-tab="signup">Sign up here</a></p>
          </div>

          <div id="signup-tab" className="tab-content">
            <h3>Create Your TRUE CARBON Account</h3>
            {/* BACKEND: On submit, call your backend registration endpoint (e.g. POST /auth/register). The example in login/auth.js shows commented fetch code and guidance for storing the returned token/credentials. */}
            <form id="signup-form">
              <div className="form-group">
                <label htmlFor="signup-name">Full Name</label>
                <input type="text" id="signup-name" placeholder="Enter your full name" required />
              </div>
              <div className="form-group">
                <label htmlFor="signup-email">Email Address</label>
                <input type="email" id="signup-email" placeholder="Enter your email" required />
              </div>
              <div className="form-group">
                <label htmlFor="signup-password">Password</label>
                <input type="password" id="signup-password" placeholder="Create a password" required />
              </div>
              <div className="form-group">
                <label htmlFor="signup-company">Company Name</label>
                <input type="text" id="signup-company" placeholder="Enter your company name" required />
              </div>
              <button type="submit" className="btn-primary btn-full">Start Free Trial</button>
            </form>
            <p className="modal-footer">Already have an account? <a href="#" className="switch-tab" data-tab="login">Login here</a></p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="footer" id="contact">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <div className="logo">
                <i className="fas fa-satellite"></i>
                <h2>TRUE CARBON</h2>
              </div>
              <p>A digital MRV platform using satellite data to monitor, report, and verify carbon credit projects with transparency and integrity.</p>
            </div>
            <div className="footer-section">
              <h3>Contact Us</h3>
              <p><i className="fas fa-envelope"></i> contact@truecarbon.com</p>
              <p><i className="fas fa-phone"></i> +1 (555) 123-4567</p>
              <p><i className="fas fa-map-marker-alt"></i> 123 Green Street, Eco City, EC 12345</p>
            </div>
            <div className="footer-section">
              <h3>Quick Links</h3>
              <ul>
                <li><a href="#features">Features</a></li>
                <li><a href="#how-it-works">How It Works</a></li>
                <li><a href="#solutions">Pricing</a></li>
                <li><a href="#contact">Contact</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h3>Subscribe to Our Newsletter</h3>
              <form id="newsletter-form">
                <input type="email" placeholder="Your email address" required />
                <button type="submit" className="btn-primary">Subscribe</button>
              </form>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2023 TRUE CARBON. All rights reserved. | <a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a></p>
          </div>
        </div>
      </footer>

    </>
  );
}