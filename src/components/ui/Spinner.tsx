interface SpinnerProps {
  className?: string;
}
export const Spinner = ({ className = "w-5 h-5" }: SpinnerProps) => {
  return (
    <div className={`animate-spin rounded-full border-2 border-gray-200 dark:border-gray-700 border-t-[#E85D24] ${className}`}></div>
  );
};
