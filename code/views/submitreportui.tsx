```tsx
import React, { useState } from 'react';
import { TestItemInfo } from './TestItemInfo'; // Assuming TestItemInfo is defined elsewhere

interface SubmitReportUIProps {
  onSubmit: (testItems: string[], reportContent: string) => Promise<string | null>;
}

const SubmitReportUI: React.FC<SubmitReportUIProps> = ({ onSubmit }) => {
  const [selectedTestItems, setSelectedTestItems] = useState<string[]>([]);
  const [reportContent, setReportContent] = useState('');
  const [reportNumber, setReportNumber] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSelectedTestItemsChange = (items: string[]) => {
    setSelectedTestItems(items);
  };

  const handleReportContentChange = (content: string) => {
    setReportContent(content);
  };

  const handleSubmit = async () => {
    if (selectedTestItems.length === 0 || reportContent.trim() === '') {
      setError('Missing fields');
      return;
    }

    try {
      const newReportNumber = await onSubmit(selectedTestItems, reportContent);
      if (newReportNumber) {
        setReportNumber(newReportNumber);
        setError(null);
      } else {
        setError('System error');
      }
    } catch (e: any) {
      if (e.message === 'Permission denied') {
        setError('Permission error');
      } else if (e.message.startsWith('Format error')) {
        setError(`Format error: ${e.message.substring('Format error: '.length)}`);
      } else if (e.message === 'Network error'){
        setError('Network error');
      } else {
        setError('System error');
      }
    }
  };

  const getSelectedTestItems = () => selectedTestItems;
  const getReportContent = () => reportContent;
  const displayReportInfo = (testItemInfo: TestItemInfo) => {
    //Implementation for displaying testItemInfo
  };
  const displaySubmissionSuccess = (reportNumber: string) => {
    //Implementation for displaying success message
  };
  const displayNetworkError = () => {
    setError('Network error');
  };
  const displayMissingFieldsError = () => {
    setError('Missing fields');
  };
  const displayFormatError = (errorMessage: string) => {
    setError(`Format error: ${errorMessage}`);
  };
  const displaySystemError = () => {
    setError('System error');
  };
  const displayPermissionError = () => {
    setError('Permission error');
  };


  return (
    <div>
      {/* Input fields for selectedTestItems and reportContent */}
      <button onClick={handleSubmit}>Submit Report</button>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {reportNumber && <div>Report submitted successfully. Report number: {reportNumber}</div>}
    </div>
  );
};

export default SubmitReportUI;