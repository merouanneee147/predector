"use client";

import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell } from 'recharts';

interface FiliereData {
  filiere: string;
  etudiants: number;
  moyenne: number;
  tauxRisque: number;
}

interface ProfilData {
  name: string;
  fullName: string;
  value: number;
  color: string;
  [key: string]: string | number;
}

interface FiliereChartProps {
  data: FiliereData[];
}

interface ProfilChartProps {
  data: ProfilData[];
  totalEtudiants: number;
}

export function FiliereBarChart({ data }: FiliereChartProps) {
  const [mounted, setMounted] = useState(false);
  const [chartWidth, setChartWidth] = useState(500);

  useEffect(() => {
    setMounted(true);
    const updateWidth = () => {
      const container = document.getElementById('filiere-chart-container');
      if (container) {
        setChartWidth(container.offsetWidth || 500);
      }
    };
    setTimeout(updateWidth, 100);
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, []);

  if (!mounted) {
    return (
      <div id="filiere-chart-container" className="w-full h-[280px] flex items-center justify-center bg-slate-50 rounded-xl animate-pulse">
        <span className="text-slate-400">Chargement...</span>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div id="filiere-chart-container" className="w-full h-[280px] flex items-center justify-center bg-slate-50 rounded-xl">
        <span className="text-slate-400">Aucune donnee</span>
      </div>
    );
  }

  return (
    <div id="filiere-chart-container" className="w-full h-[280px]">
      <BarChart width={chartWidth} height={280} data={data} margin={{ top: 10, right: 10, left: -15, bottom: 60 }} barCategoryGap="20%">
        <defs>
          <linearGradient id="blueGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3B82F6" />
            <stop offset="100%" stopColor="#1D4ED8" />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
        <XAxis dataKey="filiere" stroke="#64748B" fontSize={11} tickLine={false} axisLine={{ stroke: '#E2E8F0' }} interval={0} angle={-45} textAnchor="end" height={60} />
        <YAxis stroke="#64748B" fontSize={11} tickLine={false} axisLine={false} />
        <Tooltip contentStyle={{ backgroundColor: 'white', border: 'none', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }} />
        <Bar dataKey="etudiants" fill="url(#blueGradient)" radius={[6, 6, 0, 0]} maxBarSize={50} />
      </BarChart>
    </div>
  );
}

export function ProfilPieChart({ data, totalEtudiants }: ProfilChartProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-full h-[220px] flex items-center justify-center animate-pulse">
        <span className="text-slate-400">Chargement...</span>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="w-full h-[220px] flex items-center justify-center">
        <span className="text-slate-400">Aucune donnee</span>
      </div>
    );
  }

  return (
    <div className="w-full h-[220px] flex items-center justify-center">
      <PieChart width={200} height={200}>
        <Pie data={data} cx={100} cy={100} innerRadius={50} outerRadius={80} paddingAngle={3} dataKey="value" strokeWidth={0}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip contentStyle={{ backgroundColor: 'white', border: 'none', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }} />
      </PieChart>
    </div>
  );
}
