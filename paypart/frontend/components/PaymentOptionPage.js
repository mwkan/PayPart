import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';

function PaymentOptionPage() {
  const [numPeople, setNumPeople] = useState(2);
  const history = useHistory();

  const handleNext = (splitType) => {
    history.push(`/${splitType}?people=${numPeople}`);
  };

  return (
    <div>
      <h1>PayPart</h1>
      <label>
        How many ways would you like to share?
        <select value={numPeople} onChange={(e) => setNumPeople(e.target.value)}>
          {Array.from({ length: 49 }, (_, i) => i + 2).map((num) => (
            <option key={num} value={num}>
              {num}
            </option>
          ))}
        </select>
      </label>
      <button onClick={() => handleNext('even-split')}>Even Split</button>
      <button onClick={() => handleNext('custom-split')}>Custom Split</button>
    </div>
  );
}

export default PaymentOptionPage;
