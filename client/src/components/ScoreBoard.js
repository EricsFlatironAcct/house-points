import React from "react";

function ScoreBoard({ family }) {
  if (family) return <h1>COMING SOON!</h1>;
  else return <h1>Login to view your family's score board.</h1>;
}

export default ScoreBoard;
