
import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  hoverEffect?: boolean;
}

const GlassCard: React.FC<GlassCardProps> = ({ children, className = '', hoverEffect = true }) => {
  return (
    <div className={`glass rounded-3xl p-8 transition-all duration-300 ${hoverEffect ? 'hover:bg-white/5 hover:-translate-y-1' : ''} ${className}`}>
      {children}
    </div>
  );
};

export default GlassCard;
