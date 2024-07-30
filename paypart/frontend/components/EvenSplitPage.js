import React from 'react';
import { useLocation, useHistory } from 'react-router-dom';

function EvenSplitPage() {
// Example amount to split
    const location = useLocation(), history = useHistory(), query = new URLSearchParams(location.search),
        numPeople = parseInt(query.get('people'), 10), amountPerPerson = 100 / numPeople, handleBack = () => {
            history.push('/');
        };

    return (
    <div>
      <button onClick={handleBack}>Back</button>
      <h1>Even Split</h1>
      {Array.from({ length: numPeople }, (_, i) => (
        <div key={i}>
          <h2>Person {i + 1}:</h2>
          <p>Amount to Pay: ${amountPerPerson.toFixed(2)}</p>
          <input type="email" placeholder="Email" />
          <input type="text" placeholder="Bank Name" />
        </div>
      ))}
        Amount Due: ${100.toFixed(2)}
        <span>Total Pay: ${100.toFixed(2)}</span>
        <button>Send Requests</button>
    </div>
  );
}
export default EvenSplitPage();
