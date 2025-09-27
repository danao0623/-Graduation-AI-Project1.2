```tsx
import React from 'react';

interface TestResultUIProps {
  message: string;
}

const TestResultUI: React.FC<TestResultUIProps> = ({ message }) => {
  return (
    <div>
      {message}
    </div>
  );
};

export default TestResultUI;