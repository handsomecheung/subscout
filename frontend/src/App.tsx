import { Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import UploadPage from './pages/UploadPage';
import EditPage from './pages/EditPage';
import ResultsPage from './pages/ResultsPage';

function App() {
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <div className="app">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/session/:sessionId/edit" element={<EditPage />} />
          <Route path="/session/:sessionId/results" element={<ResultsPage />} />
        </Routes>
      </div>
    </ConfigProvider>
  );
}

export default App;
