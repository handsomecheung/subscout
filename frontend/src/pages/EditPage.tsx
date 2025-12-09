import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Card,
  Typography,
  Button,
  List,
  Tag,
  message,
  Spin,
} from "antd";
import {
  getSessionWords,
  updateSessionWords,
  finalizeSession,
} from "../services/api";
import type { WordItem } from "../types";

const { Title, Paragraph } = Typography;

export default function EditPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [words, setWords] = useState<WordItem[]>([]);
  const [removedWords, setRemovedWords] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (sessionId) {
      loadWords();
    }
  }, [sessionId]);

  const loadWords = async () => {
    if (!sessionId) return;

    setLoading(true);
    try {
      const response = await getSessionWords(sessionId);
      setWords(response.words);

      // Initialize removed words from existing data
      const removed = new Set(
        response.words.filter((w) => w.is_removed).map((w) => w.word),
      );
      setRemovedWords(removed);
    } catch (error: any) {
      message.error(error.response?.data?.detail || "failed to load words");
    } finally {
      setLoading(false);
    }
  };

  const toggleWord = (word: string) => {
    setRemovedWords((prev) => {
      const next = new Set(prev);
      if (next.has(word)) {
        next.delete(word);
      } else {
        next.add(word);
      }
      return next;
    });
  };

  const handleFinalize = async () => {
    if (!sessionId) return;

    setLoading(true);
    try {
      await updateSessionWords(sessionId, Array.from(removedWords));

      const result = await finalizeSession(sessionId);

      message.success(`Learning completed! Learned ${result.learned_count} words`);
      navigate(`/session/${sessionId}/results`, { state: result });
    } catch (error: any) {
      message.error(error.response?.data?.detail || "Failed to complete");
      setLoading(false);
    }
  };

  const unknownWords = words.filter((w) => !removedWords.has(w.word));
  const learnedWords = words.filter((w) => removedWords.has(w.word));

  return (
    <div className="page-container">
      <div className="page-header">
        <Title>Edit Word List</Title>
        <Paragraph>
          Click words to mark as "learned" (green). Learned words will be added to the known vocabulary
        </Paragraph>
        <Paragraph>
          Unknown words: {unknownWords.length} | Learned: {learnedWords.length}
        </Paragraph>
      </div>

      <Card>
        <Spin spinning={loading}>
          <List
            dataSource={words}
            renderItem={(item) => {
              const isLearned = removedWords.has(item.word);
              return (
                <List.Item
                  className={`word-item ${isLearned ? "learned" : ""}`}
                  onClick={() => toggleWord(item.word)}
                  style={{
                    cursor: "pointer",
                    padding: "12px 16px",
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <span
                      style={{
                        fontSize: "16px",
                        fontWeight: isLearned ? "normal" : "bold",
                        textDecoration: isLearned ? "line-through" : "none",
                      }}
                    >
                      {item.word}
                    </span>
                  </div>
                  <div>
                    <Tag color={isLearned ? "green" : "blue"}>
                      {item.frequency} times
                    </Tag>
                    {isLearned && <Tag color="green">Learned</Tag>}
                  </div>
                </List.Item>
              );
            }}
          />

          <div style={{ marginTop: 24, textAlign: "center" }}>
            <Button
              type="primary"
              size="large"
              onClick={handleFinalize}
              disabled={words.length === 0}
            >
              Complete Learning
            </Button>
          </div>
        </Spin>
      </Card>
    </div>
  );
}
