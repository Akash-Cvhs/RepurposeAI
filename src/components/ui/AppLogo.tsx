import { useState } from 'react';

interface AppLogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
}

const AppLogo = ({ size = 'md', showText = true }: AppLogoProps) => {
  const [imgError, setImgError] = useState(false);

  const sizeClasses = {
    sm: { img: 'h-6', text: 'text-base', icon: 'w-6 h-6' },
    md: { img: 'h-8', text: 'text-lg', icon: 'w-8 h-8' },
    lg: { img: 'h-10', text: 'text-xl', icon: 'w-10 h-10' }
  };

  const { img: heightClass, text: textClass, icon: iconSizeClass } = sizeClasses[size];

  if (!imgError) {
    return (
      <div className="flex items-center gap-2">
        <img
          src="/logo.svg"
          alt="RepurposeAI"
          className={`object-contain ${heightClass}`}
          onError={() => setImgError(true)}
        />
        {showText && (
          <span className={`font-bold text-gray-900 dark:text-white ${textClass}`}>
            RepurposeAI
          </span>
        )}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <div className={`${iconSizeClass} rounded-lg bg-[#E85D24] flex items-center justify-center flex-shrink-0`}>
        <svg viewBox="0 0 24 24" fill="none" className="w-3/4 h-3/4" stroke="white" strokeWidth="2.5" strokeLinecap="round">
          <path d="M9 3H5a2 2 0 00-2 2v4"/>
          <path d="M15 3h4a2 2 0 012 2v4"/>
          <path d="M9 21H5a2 2 0 01-2-2v-4"/>
          <path d="M15 21h4a2 2 0 002-2v-4"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
      </div>
      {showText && (
        <span className={`font-bold text-gray-900 dark:text-white ${textClass}`}>
          RepurposeAI
        </span>
      )}
    </div>
  );
};

export default AppLogo;
