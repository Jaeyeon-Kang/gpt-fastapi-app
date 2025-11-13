import { useEffect } from 'react';

export default function Notification({ message, type = 'info', onClose }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 5000);

    return () => clearTimeout(timer);
  }, [onClose]);

  const bgColors = {
    info: 'bg-blue-100 border-blue-300 text-blue-800',
    success: 'bg-green-100 border-green-300 text-green-800',
    error: 'bg-red-100 border-red-300 text-red-800',
    warning: 'bg-yellow-100 border-yellow-300 text-yellow-800',
  };

  return (
    <div className={`fixed top-5 right-5 max-w-md rounded-lg border-2 shadow-lg animate-slideIn z-50 ${bgColors[type]}`}>
      <div className="flex items-center justify-between p-4">
        <span className="flex-1 mr-4">{message}</span>
        <button
          onClick={onClose}
          className="text-xl font-bold opacity-70 hover:opacity-100 transition"
        >
          ×
        </button>
      </div>
    </div>
  );
}
