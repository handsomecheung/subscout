import { useNavigate, useLocation } from 'react-router-dom';
import { Card, Typography, List, Button, Tag } from 'antd';
import { CheckCircleOutlined } from '@ant-design/icons';
import type { FinalizeResponse } from '../types';

const { Title, Paragraph } = Typography;

export default function ResultsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const result = location.state as FinalizeResponse;

  if (!result) {
    return (
      <div className="page-container">
        <Card>
          <Title level={3}>No Result Data</Title>
          <Button type="primary" onClick={() => navigate('/')}>
            Back to Home
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <Title>
          <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
          Learning Completed!
        </Title>
      </div>

      <Card style={{ marginBottom: 24 }}>
        <div style={{ textAlign: 'center', padding: '24px 0' }}>
          <Paragraph style={{ fontSize: '18px', marginBottom: 16 }}>
            <Tag color="green" style={{ fontSize: '16px', padding: '4px 16px' }}>
              Learned {result.learned_count} words
            </Tag>
          </Paragraph>
          <Paragraph style={{ fontSize: '16px', color: '#666' }}>
            Processed {result.total_count} words in total
          </Paragraph>
        </div>
      </Card>

      {result.top_words.length > 0 && (
        <Card title="Top 20 Words to Learn" style={{ marginBottom: 24 }}>
          <List
            grid={{ gutter: 16, column: 4, xs: 1, sm: 2, md: 3, lg: 4 }}
            dataSource={result.top_words}
            renderItem={(word, index) => (
              <List.Item>
                <Card
                  size="small"
                  style={{
                    textAlign: 'center',
                    backgroundColor: index < 5 ? '#fff7e6' : '#fff',
                  }}
                >
                  <div style={{ fontSize: '12px', color: '#999' }}>
                    #{index + 1}
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                    {word}
                  </div>
                </Card>
              </List.Item>
            )}
          />
        </Card>
      )}

      <div style={{ textAlign: 'center' }}>
        <Button type="primary" size="large" onClick={() => navigate('/')}>
          Start New Learning
        </Button>
      </div>
    </div>
  );
}
