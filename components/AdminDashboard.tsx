/**
 * AdminDashboard Component
 * Displays system administration dashboard
 * Phase 3: Updated with blue color theme and glassmorphism
 */

import React, { useState, useEffect } from 'react';
import { Activity, Shield, Server, Database, Brain, AlertTriangle, CheckCircle, RefreshCw, LogOut, Settings as SettingsIcon } from 'lucide-react';
import { Card, Badge, Button } from './ui';
import PilotRequests from './dashboard/PilotRequests';

const AdminDashboard: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState({
    api: 'healthy',
    database: 'healthy',
    aiService: 'mock_mode',
    uptime: '99.9%'
  });

  const [recentJobs, setRecentJobs] = useState([
    { id: 'job_1', agent: 'visual', status: 'completed', duration: '12s', timestamp: new Date().toISOString() },
    { id: 'job_2', agent: 'video', status: 'processing', duration: '45s', timestamp: new Date().toISOString() },
    { id: 'job_3', agent: 'copywriter', status: 'failed', error: 'Rate limit exceeded', timestamp: new Date().toISOString() },
  ]);

  const [isMocking, setIsMocking] = useState(true);

  const stats = [
    { label: 'Total API Calls', value: '14,285', icon: Server, color: 'indigo' },
    { label: 'AI Tokens Used', value: '1.2M', icon: Brain, color: 'purple' },
    { label: 'Active Jobs', value: '12', icon: Activity, color: 'emerald' },
    { label: 'Database Size', value: '245 MB', icon: Database, color: 'amber' },
  ];

  return (
    <div className="max-w-7xl mx-auto p-4 md:p-6 space-y-8 animate-in fade-in duration-500">
      <PilotRequests />
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-extrabold text-[#0f172a] tracking-tight">System Administration</h2>
          <p className="text-[#64748b]">Monitor system health, manage AI agents, and view logs.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="flex items-center gap-2">
            <RefreshCw className="w-4 h-4" /> Refresh Data
          </Button>
          <Button className="bg-gradient-to-r from-[#1863d6] to-[#151983] hover:shadow-md flex items-center gap-2">
            <SettingsIcon className="w-4 h-4" /> System Settings
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <Card key={i} className="p-6 border-[#e2e8f0]">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-xl bg-[#1863d6]/10 text-[#1863d6]`}>
                <stat.icon className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-[#64748b] uppercase tracking-wider">{stat.label}</p>
                <p className="text-2xl font-bold text-[#0f172a]">{stat.value}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* System Health */}
        <Card className="lg:col-span-1 p-6 border-slate-200">
          <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
            <Shield className="w-5 h-5 text-indigo-600" /> System Health
          </h3>
          <div className="space-y-6">
            <HealthItem 
              label="Backend API" 
              status={systemStatus.api === 'healthy' ? 'online' : 'offline'} 
              detail="v1.0.0 running on port 8000"
            />
            <HealthItem 
              label="SQLite Database" 
              status={systemStatus.database === 'healthy' ? 'online' : 'error'} 
              detail="sme_toolkit.db (indexed)"
            />
            <HealthItem 
              label="AI Integration" 
              status={isMocking ? 'warning' : 'online'} 
              statusLabel={isMocking ? 'Mock Mode' : 'Connected'}
              detail={isMocking ? "Gemini fallback active" : "Gemini 2.0 Pro connected"}
            />
            <div className="pt-4 border-t border-slate-100">
               <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-slate-600">Development Mode</span>
                  <button 
                    onClick={() => setIsMocking(!isMocking)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${isMocking ? 'bg-indigo-600' : 'bg-slate-200'}`}
                  >
                    <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${isMocking ? 'translate-x-6' : 'translate-x-1'}`} />
                  </button>
               </div>
               <p className="text-xs text-slate-400 leading-relaxed italic">
                 Mock mode prevents real API calls to save costs during testing.
               </p>
            </div>
          </div>
        </Card>

        {/* Async Job Monitor */}
        <Card className="lg:col-span-2 p-6 border-[#e2e8f0]">
          <h3 className="text-lg font-bold text-[#0f172a] mb-6 flex items-center gap-2">
            <Activity className="w-5 h-5 text-[#1863d6]" /> Recent AI Jobs
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-[#64748b] font-medium border-b border-[#e2e8f0]">
                <tr>
                  <th className="pb-3 px-2">Job ID</th>
                  <th className="pb-3 px-2">Agent</th>
                  <th className="pb-3 px-2">Status</th>
                  <th className="pb-3 px-2">Duration</th>
                  <th className="pb-3 px-2">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#f8fafc]">
                {recentJobs.map((job) => (
                  <tr key={job.id} className="hover:bg-[#f8fafc]/50 transition-colors">
                    <td className="py-4 px-2 font-mono text-xs text-[#64748b]">{job.id}</td>
                    <td className="py-4 px-2">
                      <Badge variant="default" className="capitalize">{job.agent}</Badge>
                    </td>
                    <td className="py-4 px-2">
                      <div className="flex items-center gap-1.5">
                        {job.status === 'completed' && <CheckCircle className="w-4 h-4 text-[#10b981]" />}
                        {job.status === 'processing' && <RefreshCw className="w-4 h-4 text-[#1863d6] animate-spin" />}
                        {job.status === 'failed' && <AlertTriangle className="w-4 h-4 text-[#ef4444]" />}
                        <span className={`font-medium ${job.status === 'completed' ? 'text-[#10b981]' : job.status === 'failed' ? 'text-[#ef4444]' : 'text-[#1863d6]'}`}>
                          {job.status}
                        </span>
                      </div>
                    </td>
                    <td className="py-4 px-2 text-[#64748b]">{job.duration}</td>
                    <td className="py-4 px-2 text-[#94a3b8]">{new Date(job.timestamp).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-6 text-center">
            <button className="text-sm text-[#1863d6] font-semibold hover:underline">View All System Logs</button>
          </div>
        </Card>
      </div>
    </div>
  );
};

const HealthItem: React.FC<{ label: string; status: 'online' | 'warning' | 'error' | 'offline'; statusLabel?: string; detail: string }> = ({ label, status, statusLabel, detail }) => {
  const colors = {
    online: 'bg-[#10b981]',
    warning: 'bg-[#f59e0b]',
    error: 'bg-[#ef4444]',
    offline: 'bg-[#94a3b8]'
  };

  return (
    <div className="flex items-start gap-4">
      <div className={`w-2.5 h-2.5 rounded-full mt-1.5 ${colors[status]}`} />
      <div className="flex-1">
        <div className="flex justify-between">
          <span className="text-sm font-bold text-[#0f172a]">{label}</span>
          <span className="text-xs font-semibold uppercase tracking-wide text-[#94a3b8]">{statusLabel || status}</span>
        </div>
        <p className="text-xs text-[#64748b] mt-0.5">{detail}</p>
      </div>
    </div>
  );
};

export default AdminDashboard;