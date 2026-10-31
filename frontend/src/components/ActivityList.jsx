function ActivityList({ activities, loading, onDelete }) {
  let content

  if (loading) {
    content = <p className="muted">Loading activities...</p>
  } else if (activities.length === 0) {
    content = <p className="muted">No activities yet. Add the first one using the form.</p>
  } else {
    content = (
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Activity</th>
              <th className="num">Hours</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {activities.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.name}</td>
                <td>{item.activity}</td>
                <td className="num">{item.hours}</td>
                <td className="actions">
                  <button
                    className="btn danger small"
                    onClick={() => onDelete(item.id)}
                    aria-label={`Delete activity ${item.activity} by ${item.name}`}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  return (
    <section className="card">
      <h2>Activities</h2>
      {content}
    </section>
  )
}

export default ActivityList
