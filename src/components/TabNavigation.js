import { useTranslation } from '@/hooks/useTranslation';

export default function TabNavigation({ activeTab, onTabChange }) {
  const { t } = useTranslation();

  const tabs = [
    { id: 'rag', label: t('ask_ai') },
    { id: 'text-input', label: t('text_input') },
    { id: 'upload', label: t('upload_docs') },
  ];

  return (
    <div className="flex border-b-2 border-gray-200 mb-6">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`px-6 py-3 font-medium transition-all ${
            activeTab === tab.id
              ? 'text-primary-700 border-b-4 border-primary-700 -mb-0.5'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
