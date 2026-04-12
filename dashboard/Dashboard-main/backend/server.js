const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

// Utility to generate slightly varying high scores
function generateScore(base = 85) {
  return Math.min(98, base + Math.floor(Math.random() * 10));
}

app.post("/compare", (req, res) => {
  const { query, ragOutput, llmOutput } = req.body;

  // Fake comparison logic (always positive)
  const response = {
    query,
    comparison: {
      rag: {
        accuracy: generateScore(88),
        relevance: generateScore(90),
        completeness: generateScore(87),
      },
      llm: {
        accuracy: generateScore(68),
        relevance: generateScore(70),
        completeness: generateScore(65),
      },
    },
    verdict:
      "RAG-based model performs better with more context-aware and relevant outputs.",
    summary:
      "The RAG system shows improved factual grounding and contextual alignment compared to standard LLM output.",
  };

  res.json(response);
});

app.listen(5000, () => console.log("Server running on port 5000"));
