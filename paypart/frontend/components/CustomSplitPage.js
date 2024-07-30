import React, { useState } from 'react';
import { useLocation, useHistory } from 'react-router-dom';

function CustomSplitPage() {
  const location = useLocation();
  const history = useHistory();
  const query = new URLSearchParams(location.search);
  const numPeople = parseInt(query.get('people'), 10);
  const [amounts, setAmounts] = useState(Array(numPeople).fill(0));

  const handleBack = () => {
    history.push('/');
  };

  const handleAmountChange = (index, value) => {
    const newAmounts = [...amounts];
    newAmounts[index] = parseFloat(value);
    setAmounts(newAmounts);
  };

  const totalAmount = amounts.reduce((total, amount) => total + amount, 0);

  return (
    <div>
      <button onClick={handleBack}>Back</button>
      <h1>Custom Split</h1>
      {Array.from({ length: numPeople }, (_, i) => (
        <div key={i}>
          <h2>Person {i + 1}:</h2>
          <input
            type="number"
            placeholder="Amount"
            value={amounts[i]}
            onChange={(e) => handleAmountChange(i, e.target.value)}
          />
          <input type="email" placeholder="Email" />
          <input type="text" placeholder="Bank Name" />
        </div>
      ))}
      <div>
        <span>Amount Due: ${totalAmount.toFixed(2)}</span>
        <span>Total Pay: ${100.toFixed(2)}</span>
      </div>
      <button>Send Requests</button>
    </div>
  );
}

export default CustomSplitPage;
