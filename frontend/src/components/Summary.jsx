function Summary({ summary, loading }) {
  if (loading || summary === null) {
    return (
      <section className="card">
        <h2>Summary</h2>
        <p className="muted">Loading summary...</p>
      </section>
    )
  }

  const hasData = summary.total_entries > 0

  return (
    <section className="card">
      <h2>Summary</h2>
      <div className="stats">
        <div className="stat">
          <span className="stat-label">Total entries</span>
          <span className="stat-value">{summary.total_entries}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Total hours</span>
          <span className="stat-value">{summary.total_hours}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Most active user</span>
          <span className="stat-value">{hasData ? summary.most_active_user : '-'}</span>
          {hasData && <span className="stat-sub">{summary.most_active_user_hours} hours</span>}
        </div>
      </div>
    </section>
  )
}

export default Summary
