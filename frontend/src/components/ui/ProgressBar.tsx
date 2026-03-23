import { useEffect, useState } from 'react';

interface ProgressBarProps {
  value: number;
  color?: string;
  animated?: boolean;
  height?: string;
}

export const ProgressBar = ({ value, color = '#E85D24', animated = false, height = 'h-2' }: ProgressBarProps) => {
  const [width, setWidth] = useState(animated ? 0 : value);

  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => {
        setWidth(value);
      }, 100);
      return () => clearTimeout(timer);
    } else {
      setWidth(value);
    }
  }, [value, animated]);

  return (
    <div className={`w-full bg-gray-200 dark:bg-gray-700 rounded-full ${height} overflow-hidden`}>
      <div 
        className="h-full rounded-full transition-all duration-1000 ease-out"
        style={{ width: `${width}%`, backgroundColor: color }}
      />
    </div>
  );
};
