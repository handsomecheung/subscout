import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Upload, Button, Card, Typography, Select, message, Spin } from "antd";
import { InboxOutlined } from "@ant-design/icons";
import { uploadSubtitle, processSession } from "../services/api";
import type { Session } from "../types";

const { Title, Paragraph } = Typography;
const { Dragger } = Upload;

export default function UploadPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [session, setSession] = useState<Session | null>(null);
  const [selectedStyle, setSelectedStyle] = useState<string>("");

  const handleFileUpload = async (file: File) => {
    setLoading(true);
    try {
      const sessionData = await uploadSubtitle(file);
      setSession(sessionData);

      message.success(
        `File uploaded successfully! Detected language: ${sessionData.language === "en" ? "English" : "Japanese"}`,
      );

      // If not .ass file, or only one style, auto-process
      if (!sessionData.styles || sessionData.styles.length === 0) {
        await handleProcess(sessionData.id);
      } else if (sessionData.styles.length === 1) {
        setSelectedStyle(sessionData.styles[0]);
        await handleProcess(sessionData.id, sessionData.styles[0]);
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || "Upload failed");
    } finally {
      setLoading(false);
    }
    return false;
  };

  const handleProcess = async (sessionId: string, style?: string) => {
    setLoading(true);
    try {
      await processSession(sessionId, style);
      // Navigate to edit page after processing
      navigate(`/session/${sessionId}/edit`);
    } catch (error: any) {
      message.error(error.response?.data?.detail || "Processing failed");
      setLoading(false);
    }
  };

  const handleStyleSelect = () => {
    if (!selectedStyle) {
      message.warning("Please select a subtitle style");
      return;
    }
    handleProcess(session!.id, selectedStyle);
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <Title>SubScout - Subtitle Learning Tool</Title>
        <Paragraph>Upload subtitle files to learn new vocabulary</Paragraph>
      </div>

      <Card style={{ maxWidth: 600, margin: "0 auto" }}>
        <Spin spinning={loading}>
          <Dragger
            name="file"
            multiple={false}
            accept=".srt,.ass"
            beforeUpload={handleFileUpload}
            showUploadList={false}
            disabled={loading}
          >
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">Click or drag file to upload</p>
            <p className="ant-upload-hint">
              Supports .srt and .ass subtitle formats
            </p>
          </Dragger>

          {session && session.styles && session.styles.length > 1 && (
            <div style={{ marginTop: 24 }}>
              <Title level={5}>Select Subtitle Style</Title>
              <Select
                style={{ width: "100%", marginBottom: 16 }}
                placeholder="Please select a style"
                value={selectedStyle}
                onChange={setSelectedStyle}
              >
                {session.styles.map((style) => (
                  <Select.Option key={style} value={style}>
                    {style}
                  </Select.Option>
                ))}
              </Select>
              <Button
                type="primary"
                block
                onClick={handleStyleSelect}
                disabled={!selectedStyle}
              >
                Start Processing
              </Button>
            </div>
          )}
        </Spin>
      </Card>
    </div>
  );
}
