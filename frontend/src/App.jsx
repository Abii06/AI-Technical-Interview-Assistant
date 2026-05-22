import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = Recognition ? new Recognition() : null;

if (recognition) {
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-US';
}

function App() {
  const [activeTab, setActiveTab] = useState('explain');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [explainerData, setExplainerData] = useState(null);
  
  // Interview State
  const [interviewTopic, setInterviewTopic] = useState('Universal Study');
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [evaluation, setEvaluation] = useState(null);
  const [error, setError] = useState(null);
  
  // Voice State
  const [isListening, setIsListening] = useState(false);

  useEffect(() => {
    if (recognition) {
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (activeTab === 'explain') {
          setQuery(transcript);
        } else {
          setUserAnswer(transcript);
        }
        setIsListening(false);
      };
      
      recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };
    }
  }, [activeTab]);

  const toggleListen = () => {
    if (!recognition) {
      alert("Speech recognition is not supported in your browser. Please try using Google Chrome or Microsoft Edge, and ensure you have granted microphone permissions.");
      return;
    }
    if (isListening) {
      try {
        recognition.stop();
      } catch (err) {
        console.error("Speech recognition stop error:", err);
      }
    } else {
      try {
        recognition.start();
        setIsListening(true);
      } catch (err) {
        console.error("Speech recognition start error:", err);
      }
    }
  };

  const speakText = (text) => {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    synth.speak(utterance);
  };

  // Agent Actions
  const getExplanation = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(`${API_BASE}/explain`, { query });
      setExplainerData(res.data.answer);
    } catch (err) {
      setError("Failed to get explanation. Please check your connection.");
    }
    setLoading(false);
  };

  const startInterview = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(`${API_BASE}/interview/start`, { 
        topic: interviewTopic, 
        difficulty: "medium" 
      });
      setCurrentQuestion(res.data.question);
      setEvaluation(null);
      setUserAnswer('');
      speakText(res.data.question);
    } catch (err) {
      setError("Failed to start session. Check if backend is running.");
    }
    setLoading(false);
  };

  const submitAnswer = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(`${API_BASE}/interview/evaluate`, {
        question: currentQuestion,
        user_answer: userAnswer
      });
      
      if (res.data && res.data.evaluation) {
        setEvaluation(res.data.evaluation);
      } else {
        setError("AI returned an empty evaluation. Please try again.");
      }
    } catch (err) {
      setError("Evaluation failed. The AI might be busy or your quota is exceeded.");
    }
    setLoading(false);
  };

  const renderExplainer = (text) => {
    if (!text) return null;
    const sections = text.split(/🔴|🟢|🔵|🟡|🟣|💻/);
    return (
      <div className="answer-section">
        {sections[1] && <div className="layer layer-green"><h3>Simple Explanation</h3><ReactMarkdown remarkPlugins={[remarkGfm]}>{sections[1].replace("Simple Explanation:", "").trim()}</ReactMarkdown></div>}
        {sections[2] && <div className="layer layer-blue"><h3>Technical Explanation</h3><ReactMarkdown remarkPlugins={[remarkGfm]}>{sections[2].replace("Technical Explanation:", "").trim()}</ReactMarkdown></div>}
        {sections[3] && <div className="layer layer-yellow"><h3>Interview Answer</h3><ReactMarkdown remarkPlugins={[remarkGfm]}>{sections[3].replace("Interview Answer:", "").trim()}</ReactMarkdown></div>}
        {sections[4] && <div className="layer layer-purple"><h3>Real-world Example</h3><ReactMarkdown remarkPlugins={[remarkGfm]}>{sections[4].replace("Real-world Example:", "").trim()}</ReactMarkdown></div>}
        {sections[5] && <div className="layer layer-code"><h3>Code Implementation</h3><ReactMarkdown remarkPlugins={[remarkGfm]}>{sections[5].replace("Code Implementation / Solution:", "").replace("Code Implementation:", "").trim()}</ReactMarkdown></div>}
      </div>
    );
  };

  return (
    <div className="dashboard">
      <div className="header">
        <h1>AI Interview Expert</h1>
        <p>Master your core Computer Science concepts with RAG & Multi-Agents</p>
      </div>

      <div className="tabs">
        <button className={`tab-btn ${activeTab === 'explain' ? 'active' : ''}`} onClick={() => setActiveTab('explain')}>
          Explainer Mode
        </button>
        <button className={`tab-btn ${activeTab === 'interview' ? 'active' : ''}`} onClick={() => setActiveTab('interview')}>
          Interview Mode
        </button>
      </div>

      {activeTab === 'explain' ? (
        <div className="glass-card">
          <div className="input-container">
            <input 
              type="text" 
              placeholder="What do you want to master today?" 
              value={query} 
              onChange={(e) => setQuery(e.target.value)} 
            />
            <div className={`voice-btn ${isListening ? 'active' : ''}`} onClick={toggleListen}>
              {isListening ? '●' : '🎤'}
            </div>
            <button className="action-btn" onClick={getExplanation} disabled={loading}>
              EXPLAIN
            </button>
          </div>
          {loading ? (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>Analyzing knowledge base...</p>
            </div>
          ) : renderExplainer(explainerData)}
        </div>
      ) : (
        <div className="glass-card">
          {!currentQuestion ? (
            <div className="input-container">
              <select value={interviewTopic} onChange={(e) => setInterviewTopic(e.target.value)}>
                <option value="Universal Study">Universal Study (Any Topic)</option>
                <option value="Operating Systems">Operating Systems</option>
                <option value="DBMS">DBMS</option>
                <option value="Networking">Networking</option>
                <option value="Data Structures">Data Structures</option>
              </select>
              <button className="action-btn" onClick={startInterview} disabled={loading}>
                BEGIN SESSION
              </button>
            </div>
          ) : (
            <div className="interview-flow">
              <div className="layer layer-blue">
                <h3>Interviewer's Challenge</h3>
                <p>{currentQuestion}</p>
              </div>
              
              <div style={{ marginTop: '2rem' }}>
                <textarea 
                  placeholder="Record your technical response..." 
                  value={userAnswer} 
                  onChange={(e) => setUserAnswer(e.target.value)} 
                  rows="6" 
                />
              </div>
              
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', justifyContent: 'flex-end' }}>
                <div className={`voice-btn ${isListening ? 'active' : ''}`} onClick={toggleListen}>
                  {isListening ? '●' : '🎤'}
                </div>
                <button className="action-btn" onClick={submitAnswer} disabled={loading}>
                  SUBMIT FOR EVALUATION
                </button>
                <button className="tab-btn" onClick={() => setCurrentQuestion(null)}>QUIT</button>
              </div>

              {loading && (
                <div className="loading-container">
                  <div className="spinner"></div>
                  <p>Evaluating depth and accuracy...</p>
                </div>
              )}

              {error && (
                <div className="layer" style={{ borderColor: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.05)' }}>
                  <h3 style={{ color: '#ef4444' }}>System Error</h3>
                  <p>{error}</p>
                </div>
              )}
              
              {evaluation && !loading && (
                <div className="layer layer-purple" style={{ marginTop: '3rem' }}>
                  <h3>Expert Feedback Report</h3>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{evaluation}</ReactMarkdown>
                </div>
              )}
            </div>
          )}
        </div>
      )}
      
      {error && activeTab === 'explain' && (
        <div className="glass-card" style={{ marginTop: '1rem', borderColor: '#ef4444', padding: '1rem 3rem' }}>
          <p style={{ color: '#ef4444', margin: 0 }}>{error}</p>
        </div>
      )}
      
      <div className="header" style={{ opacity: 0.4, fontSize: '0.8rem', marginTop: '2rem' }}>
        SYSTEM STATUS: ONLINE | RAG ENGINE: ACTIVE | GEMINI 2.0 FLASH
      </div>
    </div>
  );
}

export default App;
