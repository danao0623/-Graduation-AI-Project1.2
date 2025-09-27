import React, { useState } from 'react';
import { Button, TextField, Typography } from '@mui/material';

interface ReplyUIProps {
  replyContent: string;
  replyChannel: string;
}

const ReplyUI: React.FC<ReplyUIProps> = ({ replyContent, replyChannel }) => {
  const [sendStatus, setSendStatus] = useState('');
  const [error, setError] = useState('');

  const handleSendReply = async () => {
    setSendStatus('Sending...');
    setError('');
    try {
      // Simulate sending reply - Replace with actual API call using Axios
      const response = await new Promise<boolean>((resolve) => {
        setTimeout(() => resolve(true), 1000); // Simulate API delay
      });
      setSendStatus('Sent!');
      displayReplyResult(response);
    } catch (error: any) {
      setError(error.message);
      displayError(error.message);
    } finally {
      setSendStatus('');
    }
  };

  const displayReplyResult = (result: boolean) => {
    if (result) {
      console.log('Reply sent successfully!');
    } else {
      console.error('Failed to send reply.');
    }
  };

  const displaySendStatus = (status: string) => {
    setSendStatus(status);
  };

  const displayError = (message: string) => {
    setError(message);
  };

  const getReplyContent = () => replyContent;
  const getReplyChannel = () => replyChannel;

  return (
    <div>
      <Typography variant="h6">Reply Content: {getReplyContent()}</Typography>
      <Typography variant="h6">Reply Channel: {getReplyChannel()}</Typography>
      <TextField label="Reply Content" value={replyContent} disabled />
      <TextField label="Reply Channel" value={replyChannel} disabled />
      <Button variant="contained" onClick={handleSendReply}>Send Reply</Button>
      {sendStatus && <Typography>{sendStatus}</Typography>}
      {error && <Typography color="error">{error}</Typography>}
    </div>
  );
};

export default ReplyUI;