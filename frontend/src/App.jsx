import { useState } from 'react'
import './App.css'

const API_URL = 'http://localhost:5000/predict'

function App() {
  const [search, setSearch] = useState('')
  const [currentSong, setCurrentSong] = useState('')
  const [history, setHistory] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function fetchRecommendations(songTitle, nextHistory) {
    setLoading(true)
    setError('')

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ song: songTitle }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Unable to get recommendations.')
      }

      const resolvedSong = data.song || songTitle
      const resolvedHistory = [...nextHistory]
      resolvedHistory[resolvedHistory.length - 1] = resolvedSong

      setCurrentSong(resolvedSong)
      setHistory(resolvedHistory)
      setRecommendations(data.recommendations || [])
    } catch (requestError) {
      const message =
        requestError instanceof TypeError
          ? 'Backend API is not reachable. Start Flask on http://localhost:5000 and try again.'
          : requestError.message

      setError(message)
      setRecommendations([])
    } finally {
      setLoading(false)
    }
  }

  function handleSearch(event) {
    event.preventDefault()
    const songTitle = search.trim()

    if (!songTitle) {
      setError('Enter a song title to start a chain.')
      return
    }

    fetchRecommendations(songTitle, [songTitle])
  }

  function handleRecommendationClick(recommendation) {
    fetchRecommendations(recommendation.title, [...history, recommendation.title])
    setSearch(recommendation.title)
  }

  function handleRestart() {
    setSearch('')
    setCurrentSong('')
    setHistory([])
    setRecommendations([])
    setError('')
  }

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <p className="hero-title">CueChain</p>
        <p className="subtitle">
          Search songs. Get fast recs to choose from. Store on-chain for even faster recs.  
        </p>

        <form className="search-form" onSubmit={handleSearch}>
          <input
            type="text"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="What's the Move?"
            aria-label="Song title"
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Finding...' : 'Search'}
          </button>
        </form>

        <button type="button" className="restart-button" onClick={handleRestart}>
          Restart
        </button>
      </section>

      <section className="chain-panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Current Selection</p>
            <h2>{currentSong || 'Start with a song search!'}</h2>
          </div>
        </div>

        {history.length > 0 && (
          <div className="history">
            {history.map((song, index) => (
              <span className="history-item" key={`${song}-${index}`}>
                {song}
              </span>
            ))}
          </div>
        )}

        {error && <p className="error-message">{error}</p>}

        {history.length > 0 && (
          <p className="transition-memory-line">
            <strong>Transition Memory:</strong> {history.join(' > ')}
          </p>
        )}

        {recommendations.length > 0 && (
          <>
            <div className="recommendations-header">
              <h3>Recommended Tracks</h3>
            </div>
            <div className="recommendation-grid">
              {recommendations.map((recommendation) => (
                <button
                  type="button"
                  className="recommendation-card"
                  key={`${recommendation.title}-${recommendation.artist}`}
                  onClick={() => handleRecommendationClick(recommendation)}
                  disabled={loading}
                >
                  <span className="score">
                    Score {Number(recommendation.score).toFixed(3)}
                  </span>
                  <h3>{recommendation.title}</h3>
                  <p>{recommendation.artist}</p>
                  <p className="transition-edge">
                    {recommendation.from_song || currentSong} &gt; {recommendation.title}
                  </p>
                  <div className="metadata">
                    <span>{recommendation.genre}</span>
                    <span>{recommendation.bpm} BPM</span>
                  </div>
                  <div className="chain-status">
                    {recommendation.stored_on_chain
                      ? 'Stored to transition memory'
                      : 'Available as a transition'}
                  </div>
                  {recommendation.signature && (
                    <a
                      href={`https://explorer.solana.com/tx/${recommendation.signature}?cluster=devnet`}
                      target="_blank"
                      rel="noreferrer"
                      onClick={(event) => event.stopPropagation()}
                    >
                      View Solana transaction
                    </a>
                  )}
                </button>
              ))}
            </div>
          </>
        )}
      </section>
    </main>
  )
}

export default App
