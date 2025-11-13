import { useState } from 'react';
import Layout from '@/components/Layout';
import TabNavigation from '@/components/TabNavigation';
import RAGSearch from '@/components/RAGSearch';
import FileUpload from '@/components/FileUpload';
import TextInput from '@/components/TextInput';
import Notification from '@/components/Notification';

export default function Home() {
  const [activeTab, setActiveTab] = useState('rag');
  const [notification, setNotification] = useState(null);

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
  };

  const closeNotification = () => {
    setNotification(null);
  };

  return (
    <Layout>
      {/* Notification */}
      {notification && (
        <Notification
          message={notification.message}
          type={notification.type}
          onClose={closeNotification}
        />
      )}

      {/* Tab Navigation */}
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'rag' && <RAGSearch onNotification={showNotification} onTabChange={setActiveTab} />}
        {activeTab === 'text-input' && <TextInput onNotification={showNotification} />}
        {activeTab === 'upload' && <FileUpload onNotification={showNotification} />}
      </div>
    </Layout>
  );
}
