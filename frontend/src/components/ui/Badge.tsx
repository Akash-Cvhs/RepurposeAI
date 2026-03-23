interface BadgeProps {
  label: string;
  variant: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
}

export const Badge = ({ label, variant }: BadgeProps) => {
  const baseClasses = "text-xs font-medium rounded-full px-2.5 py-1";
  
  const variants = {
    success: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
    warning: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
    danger: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
    info: "bg-[#FFF3EE] text-[#E85D24] dark:bg-[#2A1F1A] dark:text-[#E85D24]",
    neutral: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
  };

  return (
    <span className={`${baseClasses} ${variants[variant]}`}>
      {label}
    </span>
  );
};
